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

from .config import ConfigDict
from .db import DatabaseManager
from .defaults import *

class BoxSyncDaemon(object):

    def __init__(self):
        self.config = None
        self.data_path = DEFAULT_BOXSYNC_DATA_PATH
        self.default_box_path = DEFAULT_BOX_PATH

    def get_box_path(self):
        path = None
        if self.config:
            path = self.config.get('box_path')

        return path if path else self.default_box_path

    def run(self):
        db = DatabaseManager(DEFAULT_BOXSYNC_DATA_PATH)


def main():
    bsd = BoxSyncDaemon()
    bsd.config = ConfigDict()
    bsd.run()