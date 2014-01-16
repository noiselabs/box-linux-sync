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
import sqlite3

from noiselabs.box.syncd import lazyproperty

class BoxSyncConfig(object):
    """
    Configuration for the BoxSync daemon.
    """
    _conn = None

    def __init__(self, basedir):
        self.basedir = basedir
        self.filepath = os.path.join(basedir, 'config.db')

    def get_cfgdir(self):
        return self.basedir

    def get_boxdir(self):
        return os.path.join(os.path.expanduser('~'), 'Box')

    @lazyproperty
    def conn(self):
        if not os.path.isfile(self.filepath):
            with open(self.filepath, 'w+') as f:
                f.write('')
            os.chmod(self.filepath, 0600)
            self._conn = sqlite3.connect(self.filepath)
        else:
            self._conn = sqlite3.connect(self.filepath)

        return self._conn

    def _create_schema(self):
       pass

