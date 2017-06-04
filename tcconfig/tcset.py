#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import print_function

import errno
import sys

import logbook
import pyparsing as pp
import six
import subprocrunner
import typepy

from ._argparse_wrapper import ArgparseWrapper
from ._common import write_tc_script
from ._const import (
    VERSION,
    Network,
    TcCoomandOutput,
)
from ._error import (
    ModuleNotFoundError,
    NetworkInterfaceNotFoundError,
)
from ._logger import (
    LOG_FORMAT_STRING,
    logger,
    set_log_level,
)
from ._traffic_direction import TrafficDirection
from .traffic_control import TrafficControl

logbook.StderrHandler(
    level=logbook.DEBUG, format_string=LOG_FORMAT_STRING).push_application()


def parse_option():
    parser = ArgparseWrapper(VERSION)

    group = parser.parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--device",
        help="network device name (e.g. eth0)")
    group.add_argument(
        "-f", "--config-file",
        help="""setting traffic controls from a configuration file.
        output file of the tcshow.""")

    group = parser.parser.add_mutually_exclusive_group()
    group.add_argument(
        "--overwrite", action="store_true", default=False,
        help="overwrite existing settings")
    group.add_argument(
        "--add", dest="is_add_shaper", action="store_true", default=False,
        help="add a traffic shaping rule in addition to existing rules.")

    group = parser.parser.add_argument_group("Traffic Control")
    group.add_argument(
        "--direction", choices=TrafficDirection.LIST,
        default=TrafficDirection.OUTGOING,
        help="""the direction of network communication that impose traffic control.
        ``incoming`` requires Linux kernel version 2.6.20 or later.
        (default = ``%(default)s``)
        """)
    group.add_argument(
        "--rate", dest="bandwidth_rate",
        help="network bandwidth rate [K|M|G bit per second]")
    group.add_argument(
        "--delay", dest="network_latency", type=float, default=0,
        help="""
        round trip network delay [ms]. the valid range is {:d} to {:d}.
        (default=%(default)s)
        """.format(
            TrafficControl.MIN_LATENCY_MS, TrafficControl.MAX_LATENCY_MS))
    group.add_argument(
        "--delay-distro", dest="latency_distro_ms", type=float, default=0,
        help="""
        distribution of network latency becomes X +- Y [ms]
        (normal distribution). Here X is the value of --delay option and
        Y is the value of --delay-dist option).
        network latency distribution will be uniform without this option.
        """)
    group.add_argument(
        "--loss", dest="packet_loss_rate", type=float, default=0,
        help="""
        round trip packet loss rate [%%]. the valid range is {:d} to {:d}.
        (default=%(default)s)
        """.format(
            TrafficControl.MIN_PACKET_LOSS_RATE,
            TrafficControl.MAX_PACKET_LOSS_RATE))
    group.add_argument(
        "--duplicate", dest="packet_duplicate_rate", type=float, default=0,
        help="""
        round trip packet duplicate rate [%%]. the valid range is {:d} to {:d}.
        (default=%(default)s)
        """.format(
            TrafficControl.MIN_PACKET_DUPLICATE_RATE,
            TrafficControl.MAX_PACKET_DUPLICATE_RATE))
    group.add_argument(
        "--corrupt", dest="corruption_rate", type=float, default=0,
        help="""
        packet corruption rate [%%]. the valid range is {:d} to {:d}.
        packet corruption means single bit error at a random offset in
        the packet. (default=%(default)s)
        """.format(
            TrafficControl.MIN_CORRUPTION_RATE,
            TrafficControl.MAX_CORRUPTION_RATE))
    group.add_argument(
        "--reordering", dest="reordering_rate", type=float, default=0,
        help="""
        packet reordering rate [%%]. the valid range is {:d} to {:d}.
        (default=%(default)s)
        """.format(
            TrafficControl.MIN_REORDERING_RATE,
            TrafficControl.MAX_REORDERING_RATE))
    group.add_argument(
        "--network", "--dst-network",
        help="target IP address/network to control traffic")
    group.add_argument(
        "--port", "--dst-port", dest="dst_port", type=int,
        help="target destination port number to control traffic.")
    group.add_argument(
        "--src-port", type=int,
        help="target source port number to control traffic.")
    group.add_argument(
        "--ipv6", dest="is_ipv6", action="store_true", default=False,
        help="apply traffic control to IPv6 packets rather than IPv4.")
    group.add_argument(
        "--shaping-algo", dest="shaping_algorithm",
        choices=["tbf", "htb"], default="htb",
        help="shaping algorithm. defaults to %(default)s (recommended).")

    group = parser.parser.add_argument_group("Routing")
    group.add_argument(
        "--iptables", dest="is_enable_iptables",
        action="store_true", default=False,
        help="use iptables to traffic shaping.")
    group.add_argument(
        "--src-network",
        help="""
        set traffic shaping rule to a specific packets that routed from
        --src-network to --network. This option required to execute with
        the --iptables option.
        the shaping rule only affect to outgoing packets
        (no effect to if you execute with "--direction incoming" option)
        """)

    return parser.parser.parse_args()


def verify_netem_module():
    import re

    runner = subprocrunner.SubprocessRunner("lsmod")
    if runner.run() != 0:
        raise OSError("failed to execute lsmod")

    if re.search(r"\bsch_netem\b", runner.stdout) is None:
        raise ModuleNotFoundError("sch_netem module not found")


class TcConfigLoader(object):
    def __init__(self, logger):
        self.__logger = logger
        self.__config_table = None
        self.is_overwrite = False

    def load_tcconfig(self, config_file_path):
        import json
        from voluptuous import Schema, Required, Any, ALLOW_EXTRA

        schema = Schema({
            Required(six.text_type): {
                Any(*TrafficDirection.LIST): {
                    six.text_type: {
                        six.text_type: six.text_type,
                    },
                }
            },
        }, extra=ALLOW_EXTRA)

        with open(config_file_path) as fp:
            self.__config_table = json.load(fp)

        schema(self.__config_table)
        self.__logger.debug("tc config file: {:s}".format(
            json.dumps(self.__config_table, indent=4)))

    def get_tcconfig_command_list(self):
        command_list = []

        for device, device_table in six.iteritems(self.__config_table):
            device_option = "--device={:s}".format(device)

            if self.is_overwrite:
                command_list.append("tcdel {:s}".format(device_option))

            for direction, direction_table in six.iteritems(device_table):
                is_first_set = True

                for tc_filter, filter_table in six.iteritems(direction_table):
                    self.__logger.debug(
                        "is_first_set={}, filter='{}', table={}".format(
                            is_first_set, tc_filter, filter_table))

                    if not filter_table:
                        continue

                    option_list = [device_option,
                                   "--direction={:s}".format(direction), ] + [
                                      "--{:s}={:s}".format(k, v) for k, v in
                                      six.iteritems(filter_table)]

                    try:
                        network = self.__parse_tc_filter_network(tc_filter)
                        if network not in (
                                Network.Ipv4.ANYWHERE, Network.Ipv6.ANYWHERE):
                            option_list.append(
                                "--network={:s}".format(network))
                    except pp.ParseException:
                        pass

                    try:
                        src_port = self.__parse_tc_filter_src_port(tc_filter)
                        option_list.append("--src-port={}".format(src_port))
                    except pp.ParseException:
                        pass

                    try:
                        dst_port = self.__parse_tc_filter_dst_port(tc_filter)
                        option_list.append("--dst-port={}".format(dst_port))
                    except pp.ParseException:
                        pass

                    if not is_first_set:
                        option_list.append("--add")

                    is_first_set = False

                    command_list.append(" ".join(["tcset"] + option_list))

        return command_list

    @staticmethod
    def __parse_tc_filter_network(text):
        network_pattern = (
            pp.SkipTo("network=", include=True) +
            pp.Word(pp.alphanums + "." + "/"))

        return network_pattern.parseString(text)[-1]

    @staticmethod
    def __parse_tc_filter_src_port(text):
        port_pattern = (
            pp.SkipTo("src-port=", include=True) +
            pp.Word(pp.nums))

        return port_pattern.parseString(text)[-1]

    @staticmethod
    def __parse_tc_filter_dst_port(text):
        port_pattern = (
            pp.SkipTo("dst-port=", include=True) +
            pp.Word(pp.nums))

        return port_pattern.parseString(text)[-1]


def set_tc_from_file(logger, config_file_path, is_overwrite):
    return_code = 0

    loader = TcConfigLoader(logger)
    loader.is_overwrite = is_overwrite
    loader.load_tcconfig(config_file_path)

    for tcconfig_command in loader.get_tcconfig_command_list():
        return_code |= subprocrunner.SubprocessRunner(
            tcconfig_command).run()

    return return_code


def main():
    options = parse_option()

    set_log_level(options.log_level)

    subprocrunner.Which("tc").verify()
    try:
        verify_netem_module()
    except ModuleNotFoundError as e:
        logger.debug(str(e))
    except subprocrunner.CommandNotFoundError as e:
        logger.error(str(e))

    if typepy.is_not_null_string(options.config_file):
        return set_tc_from_file(logger, options.config_file, options.overwrite)

    tc = TrafficControl(
        options.device,
        direction=options.direction,
        bandwidth_rate=options.bandwidth_rate,
        latency_ms=options.network_latency,
        latency_distro_ms=options.latency_distro_ms,
        packet_loss_rate=options.packet_loss_rate,
        packet_duplicate_rate=options.packet_duplicate_rate,
        corruption_rate=options.corruption_rate,
        reordering_rate=options.reordering_rate,
        network=options.network,
        src_network=options.src_network,
        src_port=options.src_port,
        dst_port=options.dst_port,
        is_ipv6=options.is_ipv6,
        is_add_shaper=options.is_add_shaper,
        is_enable_iptables=options.is_enable_iptables,
        shaping_algorithm=options.shaping_algorithm,
        tc_command_output=options.tc_command_output,
    )

    try:
        tc.validate()
    except (NetworkInterfaceNotFoundError) as e:
        logger.error(str(e))
        return errno.EINVAL
    except ValueError as e:
        logger.error(
            "{}. ".format(e) +
            "--ipv6 option will be required to use IPv6 address.")
        return errno.EINVAL

    subprocrunner.SubprocessRunner.is_save_history = True
    if options.tc_command_output != TcCoomandOutput.NOT_SET:
        subprocrunner.SubprocessRunner.default_is_dry_run = True

    if options.overwrite:
        if options.log_level == logbook.INFO:
            set_log_level(logbook.ERROR)

        try:
            tc.delete_tc()
        except NetworkInterfaceNotFoundError:
            pass

        set_log_level(options.log_level)

    tc.set_tc()
    command_history = "\n".join(tc.get_command_history())

    if options.tc_command_output == TcCoomandOutput.STDOUT:
        print(command_history)
        return 0

    if options.tc_command_output == TcCoomandOutput.SCRIPT:
        write_tc_script(
            "tcset", command_history, filename_suffix=options.device)
        return 0

    logger.debug("command history\n{}".format(command_history))

    return 0


if __name__ == '__main__':
    sys.exit(main())
