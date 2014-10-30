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
import time
import sys

from tornado.ioloop import IOLoop

from .config import load_box_config
from .db import DatabaseManager
from .defaults import *
from .logger import GlobalLogger
from .proc import kill_process_by_pid, there_can_be_only_one
from .fs_watcher import FilesystemWatcher
from .util import FilesystemUtils, partition


__all__ = [
    'BoxSyncd', 'main'
]

class BoxSyncd(object):

    def __init__(self, argv):
        self.argv = list([arg.decode('utf-8') for arg in argv])
        self.boxsync_data_path = DEFAULT_BOXSYNC_DATA_PATH
        self.config = None
        self.dbm = None
        self.debug = False
        self.default_box_folder_name = DEFAULT_BOX_FOLDER_NAME
        self.default_box_path = DEFAULT_BOX_PATH
        self.fs = FilesystemUtils()
        self.ioloop = None
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
        self.logger.info('%s starting...' % BOXSYNC)
        for msg in logthis:
            self.logger.debug(msg)

        # Create the boxsync data dir
        self.fs.makedirs(self.boxsync_data_path, 448)

        # Check startup arguments
        try:
            restart = self.argv.index('/restart')
        except ValueError:
            pass
        except Exception as e:
            self.logger.error(str(e))
        else:
            del self.argv[restart]
            try:
                pid = int(self.argv[restart])
                del self.argv[restart]
                kill_process_by_pid(pid)
                time.sleep(0)
            except Exception as e:
                self.logger.error(str(e))

        # Check if there other instances of boxsyncd already running
        if there_can_be_only_one(self.boxsync_data_path, self.logger) is \
                False:
            sys.exit(-1)

        # Create an instance of DatabaseManager and load the configuration
        self.logger.debug('Initializing databases...')
        self.dbm = DatabaseManager(self.boxsync_data_path)
        self.logger.debug('Loading config...')
        self.config = load_box_config(self.default_box_path)
        self.logger.debug('Box path: %s' % self.get_box_path())
        self.logger.debug('%s data path: %s' % (BOXSYNC,
                                                self.boxsync_data_path))

        # Good to go. Dispatch all agents:
        # - FileWatcherAgent() // file_events
        # - AuthenticationAgent()
        # - UpstreamAgent() // sync_engine
        # - UserConfigurationAgent()
        # - CommandSocketAgent()

        self.ioloop = IOLoop.instance()

        #fs_watcher = FilesystemWatcher(self.ioloop, self.get_box_path())
        #fs_watcher.start()

        try:
            self.ioloop.start()
        except KeyboardInterrupt:
            self.logger.debug('Shutting down3...')
            sys.stdout.write('\r')
            sys.stdout.flush()

        self.logger.debug('Shutting down2...')
        self.shutdown()
        self.ioloop.stop()
        self.ioloop.close()

    def shutdown(self):
        self.logger.debug('Shutting down...')


    def _parse_command_line(self):
        log_msg = []
        log_msg.append('Command line: %r' % self.argv)
        flags, self.argv = partition(lambda arg: arg.startswith('--'),
                                     self.argv)
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
