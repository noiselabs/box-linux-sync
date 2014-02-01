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
from noiselabs.boxsync.webdav import __prog__, __version__
from noiselabs.boxsync.webdav.output import BoxConsole
from noiselabs.boxsync.webdav.setup import BoxSetup

class NoiselabsOptionParser(OptionParser):
    """
    A quick'n'dirty version of optparse OptionParser that redefines
    format_epilog to allow newlines at will,
    """
    def format_epilog(self, formatter):
        return self.epilog

def box_main(args=None):
    """
    @param args: command arguments (default: sys.argv[1:])
    @type args: list
    """

    if args is None:
        args = sys.argv[1:]

    prog = __prog__
    version = __version__
    description = "Box.com command-line interface"
    usage = "Usage: %prog [options] <command>"

    force_help = "forces the execution of every procedure even if the component " +\
    "is already installed and/or configured"
    log_help = "log output to ~/.noiselabs/boxsync/boxsync-sync.log"

    parser = NoiselabsOptionParser(
        usage=usage,
        prog=prog,
        version=version,
        description=description,
        epilog=
"""
Commands:
  check       check boxsync-sync setup and dependencies
  setup       launch a setup wizard
  start       start sync service
  stop        stop sync service
  help        show this help message and exit
  uninstall   removes all configuration and cache files installed by boxsync-sync

Workflow:
  $ boxsync-sync check && boxsync-sync setup
  $ boxsync-sync start
"""
    )

    parser.add_option("-f", "--force", help=force_help, action="store_true",
        dest="force")
    parser.add_option("-l", "--log", help=log_help, action="store_true",
        dest="log")
    parser.add_option("-v", "--verbose", help="be verbose", action="store_true",
        dest="verbose")

    opts, pargs = parser.parse_args(args=args)

    commands = ['check', 'help', 'start', 'stop', 'setup', 'uninstall']

    nargs = len(pargs)
    # Parse commands
    if nargs == 0:
        parser.error("no command given")
    elif pargs[0] not in commands:
        parser.error("unknown command '%s'" % pargs[0])
    else:
        command = pargs[0]
        if command == 'help':
            parser.print_help()
            sys.exit(0)

    bc = BoxConsole(opts, __prog__)
    setup = BoxSetup(bc)

    if command == 'check':
        setup.check()
    elif command == 'setup':
        setup.wizard()
    elif command == 'start':
        box_dir = setup.get_box_dir()
        bc.debug("Mounting '%s'..." % box_dir)
        cmd = "mount %s" % box_dir
        if subprocess.call(cmd, shell=True) != 0:
            bc.error("Failed to mount sync dir.")
            sys.exit(-1)
    elif command == 'stop':
        box_dir = setup.get_box_dir()
        bc.debug("Unmounting '%s'..." % box_dir)
        cmd = "umount %s" % box_dir
        if subprocess.call(cmd, shell=True) != 0:
            bc.error("Failed to unmount sync dir.")
            sys.exit(-1)
    elif command == 'uninstall':
        setup = BoxSetup(bc)
        setup.uninstall()
