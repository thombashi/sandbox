#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import copy
import json
import sys

import logbook
from subprocrunner import SubprocessRunner
import subprocrunner
import typepy
from typepy.type import Integer

from ._argparse_wrapper import ArgparseWrapper
from ._common import (
    verify_network_interface,
    run_tc_show,
    write_tc_script,
)
from ._const import (
    VERSION,
    Tc,
    TcCoomandOutput,
)
from ._error import NetworkInterfaceNotFoundError
from ._iptables import IptablesMangleController
from ._logger import (
    LOG_FORMAT_STRING,
    logger,
    set_log_level,
)
from ._traffic_direction import TrafficDirection
from .parser import (
    TcFilterParser,
    TcQdiscParser,
    TcClassParser,
)

logbook.StderrHandler(
    level=logbook.DEBUG, format_string=LOG_FORMAT_STRING).push_application()


def parse_option():
    parser = ArgparseWrapper(VERSION)

    group = parser.parser.add_argument_group("Traffic Control")
    group.add_argument(
        "--device", action="append", required=True,
        help="network device name (e.g. eth0)")
    group.add_argument(
        "--ipv6", dest="ip_version", action="store_const",
        const=6, default=4,
        help="""
        Display IPv6 shaping rules.
        Defaults to show IPv4 shaping rules.
        """)

    return parser.parser.parse_args()


class TcShapingRuleParser(object):
    @property
    def device(self):
        return self.__device

    def __init__(self, device, ip_version, logger):
        self.__device = device
        self.__ip_version = ip_version
        self.__logger = logger

        self.__iptables_ctrl = IptablesMangleController(True, ip_version)

    def get_tc_parameter(self):
        return {
            self.device: {
                TrafficDirection.OUTGOING: self.__get_shaping_rule(
                    self.device),
                TrafficDirection.INCOMING: self.__get_shaping_rule(
                    self.__get_ifb_from_device()),
            },
        }

    def __get_ifb_from_device(self):
        filter_runner = SubprocessRunner(
            "tc filter show dev {:s} root".format(self.device), dry_run=False)
        filter_runner.run()

        return TcFilterParser(self.__ip_version).parse_incoming_device(
            filter_runner.stdout)

    def __get_filter_key(self, filter_param):
        network_format = Tc.Param.NETWORK + "={:s}"
        protocol_format = Tc.Param.PROTOCOL + "={:s}"
        key_item_list = []

        if Tc.Param.HANDLE in filter_param:
            handle = filter_param.get(Tc.Param.HANDLE)
            Integer(handle).validate()
            handle = int(handle)

            for mangle in self.__iptables_ctrl.parse():
                if mangle.mark_id != handle:
                    continue

                key_item_list.append(network_format.format(mangle.destination))
                if typepy.is_not_null_string(mangle.source):
                    key_item_list.append(
                        "src-network={:s}".format(mangle.source))
                key_item_list.append(protocol_format.format(mangle.protocol))

                break
            else:
                raise ValueError("mangle mark not found: {}".format(mangle))
        else:
            network = filter_param.get(Tc.Param.NETWORK)
            if typepy.is_not_null_string(network):
                key_item_list.append(network_format.format(network))

            src_port = filter_param.get(Tc.Param.SRC_PORT)
            if Integer(src_port).is_type():
                port_format = Tc.Param.SRC_PORT + "={:d}"
                key_item_list.append(port_format.format(src_port))

            dst_port = filter_param.get(Tc.Param.DST_PORT)
            if Integer(dst_port).is_type():
                port_format = Tc.Param.DST_PORT + "={:d}"
                key_item_list.append(port_format.format(dst_port))

            protocol = filter_param.get(Tc.Param.PROTOCOL)
            if typepy.is_not_null_string(protocol):
                key_item_list.append(protocol_format.format(protocol))

        return ", ".join(key_item_list)

    def __get_shaping_rule(self, device):
        if typepy.is_null_string(device):
            return {}

        class_param_list = self.__parse_tc_class(device)
        filter_param_list = self.__parse_tc_filter(device)
        qdisc_param_list = self.__parse_tc_qdisc(device)

        shaping_rule_mapping = {}

        for filter_param in filter_param_list:
            logger.debug(
                "{:s} param: {}".format(Tc.Subcommand.FILTER, filter_param))
            shaping_rule = {}

            filter_key = self.__get_filter_key(filter_param)
            if typepy.is_null_string(filter_key):
                logger.debug("empty filter key: {}".format(filter_param))
                continue

            for qdisc_param in qdisc_param_list:
                logger.debug(
                    "{:s} param: {}".format(Tc.Subcommand.QDISC, qdisc_param))

                if qdisc_param.get(Tc.Param.PARENT) not in (
                        filter_param.get(Tc.Param.FLOW_ID),
                        filter_param.get(Tc.Param.CLASS_ID)):
                    continue

                work_qdisc_param = copy.deepcopy(qdisc_param)
                del work_qdisc_param[Tc.Param.PARENT]
                shaping_rule.update(work_qdisc_param)

            for class_param in class_param_list:
                logger.debug(
                    "{:s} param: {}".format(Tc.Subcommand.CLASS, class_param))

                if class_param.get(Tc.Param.CLASS_ID) not in (
                        filter_param.get(Tc.Param.FLOW_ID),
                        filter_param.get(Tc.Param.CLASS_ID)):
                    continue

                work_class_param = copy.deepcopy(class_param)
                del work_class_param[Tc.Param.CLASS_ID]
                shaping_rule.update(work_class_param)

            if not shaping_rule:
                continue

            logger.debug(
                "rule found: {} {}".format(filter_key, shaping_rule))

            shaping_rule_mapping[filter_key] = shaping_rule

        return shaping_rule_mapping

    def __parse_tc_qdisc(self, device):
        try:
            param_list = list(TcQdiscParser().parse(
                run_tc_show(Tc.Subcommand.QDISC, device)))
        except ValueError:
            return []

        logger.debug("tc qdisc parse result: {}".format(param_list))

        return param_list

    def __parse_tc_filter(self, device):
        param_list = list(TcFilterParser(self.__ip_version).parse_filter(
            run_tc_show(Tc.Subcommand.FILTER, device)))
        logger.debug("tc filter parse result: {}".format(param_list))

        return param_list

    def __parse_tc_class(self, device):
        param_list = list(TcClassParser().parse(
            run_tc_show(Tc.Subcommand.CLASS, device)))
        logger.debug("tc class parse result: {}".format(param_list))

        return param_list


def main():
    options = parse_option()

    set_log_level(options.log_level)

    subprocrunner.Which("tc").verify()

    subprocrunner.SubprocessRunner.is_save_history = True
    if options.tc_command_output != TcCoomandOutput.NOT_SET:
        subprocrunner.SubprocessRunner.default_is_dry_run = True

    tc_param = {}
    for device in options.device:
        try:
            verify_network_interface(device)
        except NetworkInterfaceNotFoundError as e:
            logger.debug(str(e))
            continue

        tc_param.update(TcShapingRuleParser(device, options.ip_version,
                                            logger).get_tc_parameter())

    command_history = "\n".join(SubprocessRunner.get_history())

    if options.tc_command_output == TcCoomandOutput.STDOUT:
        print(command_history)
        return 0

    if options.tc_command_output == TcCoomandOutput.SCRIPT:
        write_tc_script("tcshow", command_history)
        return 0

    logger.debug("command history\n{}".format(command_history))
    print(json.dumps(tc_param, indent=4))

    return 0


if __name__ == '__main__':
    sys.exit(main())
