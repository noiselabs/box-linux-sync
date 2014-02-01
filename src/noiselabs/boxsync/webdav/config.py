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

import os
import ConfigParser

from noiselabs.boxsync.webdav import __prog__, __version__
from noiselabs.boxsync.webdav.utils import create_file

BASEDIR = os.path.expanduser('~/.noiselabs/boxsync')

class BoxConfig(object):
    """
    Handles noiselabs/box-linux-sync configuration file.
    """
    filepath = os.path.join(BASEDIR, 'boxsync-sync.cfg')
    options = {'boxsync_main': ['box_dir', 'use_davfs']}

    def __init__(self, box_console):
        self.out = box_console
        self.cfgparser = ConfigParser.SafeConfigParser()

    def check_file(self):
        """
        Check for config file existence and create if it doesn't
        """
        if create_file(self.filepath):
            self.out.info("Created configuration file '%s'" % self.filepath)
            self.write_default_config(self.filepath)

        sample_filepath = self.filepath+'.sample'
        if create_file(sample_filepath):
            self.out.info("Created example configuration file '%s'" % sample_filepath)
            self.write_default_config(sample_filepath)

        # Add all configured sections
        self.cfgparser = ConfigParser.SafeConfigParser()
        for section, options in self.options.items():
            self.cfgparser.add_section(section)
        self.cfgparser.read(self.filepath)        

    def check_config(self):
        """
        Check for sections and options available in the configuration file.
        """

        self.cfgparser.read(self.filepath)
        for section, options in self.options.items():
            loaded_options = self.cfgparser.options(section)
            for option in options:
                if option not in loaded_options:
                    return False
        return True        

    def write_default_config(self, filepath):
        data = "; " + os.path.basename(filepath) + "\n" + \
        "[boxsync_main]\n\n" + \
        "; Path to your Box sync dir. Use a relative path to place this dir\n" + \
        "; inside $HOME or an absolute path. Default: Box\n" + \
        "box_dir = Box\n\n" + \
        "; Wether to use a WebDAV filesystem to synchronize your local and\n" + \
        "; remote files. Default: true\n" + \
        "use_davfs = true\n"
        try:
            f = open(filepath, 'w')
            try:
                f.write(data)
            finally:
                f.close()
        except IOError:
            self.out.error("Failed to write default configuration to '%s'" % filepath)
        
    def save(self):
        """
        Writes sections and options to the configuration file.
        """
        with open(self.filepath, 'wb') as configfile:
            self.cfgparser.write(configfile)
        