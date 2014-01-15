#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2014 Vítor Brandão <vitor@noiselabs.org>
#
# box-linux-sync is free software; you can redistribute it  and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# box-linux-sync is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with box-linux-sync; if not, see
# <http://www.gnu.org/licenses/>.

from __future__ import print_function

import subprocess
import sys

from optparse import OptionParser
from noiselabs.box.syncd import __prog__, __version__
from noiselabs.box.webdav.output import BoxConsole
from noiselabs.box.webdav.setup import BoxSetup

class NoiselabsOptionParser(OptionParser):
    """
    A quick'n'dirty version of optparse OptionParser that redefines
    format_epilog to allow newlines at will,
    """
    def format_epilog(self, formatter):
        return self.epilog

def syncd_main(args=None):
    pass

def sync_main(args=None):
    """
    @param args: command arguments (default: sys.argv[1:])
    @type args: list
    """

    if args is None:
        args = sys.argv[1:]

    prog = __prog__
    version = __version__
    description = "boxsync command-line interface"
    usage = "Usage: %prog [options] <command>"

    log_help = "log output to ~/.noiselabs/box/boxsyncd.log"

    parser = NoiselabsOptionParser(
        usage=usage,
        prog=prog,
        version=version,
        description=description,
        epilog=
"""
Commands:
  status       get current status of the boxsyncd
  help         provide help
  stop         stop boxsyncd
  running      return whether boxsyncd is running
  start        start boxsyncd
  filestatus   get current sync status of one or more files
  ls           list directory contents with current sync status
  autostart    automatically start boxsync at login
  exclude      ignores/excludes a directory from syncing

"""
    )

    parser.add_option("-l", "--log", help=log_help, action="store_true",
        dest="log")
    parser.add_option("-v", "--verbose", help="be verbose", action="store_true",
        dest="verbose")

    opts, pargs = parser.parse_args(args=args)

    commands = ['status', 'help', 'stop', 'running', 'start', 'filestatus',
                'ls', 'autostart', 'exclude']

    nargs = len(pargs)
    if nargs == 0:
        parser.print_help()
        sys.exit(0)
    elif pargs[0] not in commands:
        parser.print_help()
        sys.exit(0)
    else:
        command = pargs[0]
        if command == 'help':
            parser.print_help()
            sys.exit(0)

    bc = BoxConsole(opts, __prog__)
