#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import argparse

import logbook

from ._const import TcCoomandOutput


class ArgparseWrapper(object):
    """
    wrapper class of argparse
    """

    def __init__(self, version, description="", epilog=""):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=description, epilog=epilog)
        self.parser.add_argument(
            "--version", action="version", version="%(prog)s " + version)

        self._add_tc_command_arg_group()
        self._add_log_level_argument_group()

    def _add_log_level_argument_group(self):
        dest = "log_level"

        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "--debug", dest=dest, action="store_const",
            const=logbook.DEBUG, default=logbook.INFO,
            help="for debug print.")
        group.add_argument(
            "--quiet", dest=dest, action="store_const",
            const=logbook.NOTSET, default=logbook.INFO,
            help="suppress execution log messages.")

        return group

    def _add_tc_command_arg_group(self):
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "--tc-command", dest="tc_command_output", action="store_const",
            const=TcCoomandOutput.STDOUT, default=TcCoomandOutput.NOT_SET,
            help="""
            display tc commands to be executed and exit.
            commands are not actually executed.
            """)

        group.add_argument(
            "--tc-script", dest="tc_command_output", action="store_const",
            const=TcCoomandOutput.SCRIPT, default=TcCoomandOutput.NOT_SET,
            help="""
            generate a script file that described tc commands to be executed
            by this command.
            """)
