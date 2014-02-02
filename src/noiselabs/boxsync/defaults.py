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

import locale
import unicodedata
import os


DEFAULT_BOX_FOLDER_NAME = 'Box'

# Core paths
DEFAULT_BOX_PATH = unicodedata.normalize('NFC', os.path.expanduser(u'~/' +
                                                                   DEFAULT_BOX_FOLDER_NAME))
DEFAULT_BOXSYNC_DATA_PATH = unicodedata.normalize('NFC', os.path.expanduser(u'~/.noiselabs/boxsync'))

# Databases
DEFAULT_CONFIG_DB_PATH = os.path.join(DEFAULT_BOXSYNC_DATA_PATH, 'config.db')

# Log file
DEFAULT_LOG_PATH = os.path.join(DEFAULT_BOXSYNC_DATA_PATH, 'boxsyncd.log')

ENCODING = locale.getpreferredencoding()