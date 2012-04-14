#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2012 Vítor Brandão <noisebleed@noiselabs.org>
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

import sys
from optparse import OptionParser
from noiselabs.box import __prog__, __version__
from noiselabs.box.setup import BoxSetup

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

    parser = NoiselabsOptionParser(
        usage="Usage: %prog [options] <command>",
        prog=prog,
        version=version,
        description=description,
        epilog=
"""
Commands:
  help        show this help message and exit
  setup       launch a setup wizard
"""
    )
    
    opts, pargs = parser.parse_args(args=args)

    commands = ['help', 'pull', 'push', 'setup']

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

    setup = BoxSetup()
    setup.check()

    if command == 'setup':
        setup.wizard()
    elif command == 'pull':
        pass
    elif command == 'push':
        pass