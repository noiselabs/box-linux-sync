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

import getopt
import sys

from .config import ConfigDict
from .db import DatabaseManager
from .defaults import *
from .logger import GlobalLogger
from .util import FilesystemUtils, partition

__all__ = ('BoxSyncd')

class BoxSyncd(object):

    def __init__(self, argv):
        self.argv = list([arg.decode('utf-8') for arg in argv])
        self.config = None
        self.boxsync_data_path = DEFAULT_BOXSYNC_DATA_PATH
        self.debug = False
        self.default_box_path = DEFAULT_BOX_PATH
        self.default_box_folder_name = DEFAULT_BOX_FOLDER_NAME
        self.fs = FilesystemUtils()
        self.verbose = False

    def get_box_path(self):
        path = None
        if self.config:
            path = self.config.get('box_path')

        return path if path else self.default_box_path

    def run(self):
        # Parse command line options (flags)
        flags, logthis = self._parse_command_line()

        # Setup the logger
        self.verbose = u'--verbose' in flags
        self.debug = u'--debug' in flags
        gl = GlobalLogger(verbose=self.verbose, debug=self.debug)
        self.logger = gl.getLogger()
        self.logger.info('BoxSync starting...')
        for msg in logthis:
            self.logger.debug(msg)

        # Create the boxsync data dir
        self.fs.makedirs(self.boxsync_data_path, 448)


    def _parse_command_line(self):
        log_msg = []
        log_msg.append('Command line: %r' % self.argv)
        flags, self.argv = partition(lambda arg: arg.startswith('--'), self.argv)
        log_msg.append('Command flags: %r' % flags)
        optlist, remaining = getopt.getopt(flags, '', [
            'debug',
            'key=',
            'verbose'])
        self.argv += remaining
        return (dict(optlist), log_msg)


def main():
    bsd = BoxSyncd(sys.argv)
    bsd.run()
