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

import os, errno
from peewee import *

BOXSYNC_DATA_DIR = os.path.join(os.path.expanduser('~'), '.noiselabs/boxsync')
BOXSYNC_DB = {
    'config': SqliteDatabase(os.path.join(BOXSYNC_DATA_DIR, 'config.db'))
}

class Preference(Model):
    """
    Preferences like Box location and configuration of a network proxy.
    """
    key = CharField()
    value = CharField()

    class Meta:
        database = BOXSYNC_DB['config']

class SelectiveSync(Model):
    """
    Folders to exclude from the sync.
    """
    path = CharField()

    class Meta:
        database = BOXSYNC_DB['config']


class BoxSyncConfig(object):
    """
    Configuration for the BoxSync daemon.
    """
    _preferences = {
        'app_name': 'box-linux-sync',
        'api_key': 'ot76edrq3atpfb6x11t88bsuzf9oq8cb',
        'redirect_uri': 'http://127.0.0.1:8888/',
        'authorization_code': '',
        'box_location': os.path.join(os.path.expanduser('~'), 'Box'),
        'proxy_setting': 'auto-detect',
        'proxy_type': 'http',
        'proxy_server': '',
        'proxy_port': '8080',
        'proxy_server_required_a_password': str(False),
        'proxy_username': '',
        'proxy_password': ''
    }
    _selective_sync = []

    def __init__(self):
        self.init()

    def init(self):
        try:
            os.makedirs(BOXSYNC_DATA_DIR, 0700)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(BOXSYNC_DATA_DIR):
                pass
            else:
                print("Can't create boxsyncd config dir at '%s'!" % BOXSYNC_DATA_DIR)
                raise

        BOXSYNC_DB['config'].create_table(Preference, True)
        BOXSYNC_DB['config'].create_table(SelectiveSync, True)
        os.chmod(BOXSYNC_DB['config'].database, 0600)

        db_keys = []
        for preference in Preference.select():
            self._preferences[preference.key] = preference.value
            db_keys.append(preference.key)

        for k,v in self._preferences.iteritems():
            if k not in db_keys:
                Preference.create(key=k, value=v).save()

    def get_box_location(self):
        return self._preferences['box_location']

    def get_exclude_list(self):
        return [d.path for d in SelectiveSync.select()]

    def get_data_dir(self):
        """
        Return the path to directory used to hold boxsync data (configuration and cache).
        @return:
        """
        return BOXSYNC_DATA_DIR

    def exclude(self, exclude_list):
        """
        Paths are relative to Box location, not full paths!

        @param exclude_list:
        @return:
        """
        for dir in exclude_list:
            SelectiveSync.create(path=dir).save()

    def get(self, key):
        return self._preferences[key]

    def save(self, key, value):
        self._preferences[key] = value


