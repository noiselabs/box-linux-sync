#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2014 Vítor Brandão <vitor@noiselabs.org>
#
# box-linux-sync is free software; you can redistribute it  and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# box-linux-sync is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with box-linux-sync; if not, see <http://www.gnu.org/licenses/>.

import os
import sys
from peewee import (
    BlobField, Model, OperationalError, SqliteDatabase, TextField
    )

__all__ = ('Config', 'DatabaseManager')

_DB_MAPPINGS = {
    'config.db': {
        'db': SqliteDatabase(None),
        'models': ['Config']
    }
}


class BaseConfig(Model):
    class Meta:
        database = _DB_MAPPINGS['config.db']['db']


class Config(BaseConfig):
    key = TextField(primary_key=True)
    value = BlobField()


class DatabaseManager(object):
    def __init__(self, database_dir):
        self.database_dir = database_dir
        self.init_all()

    def get_connection(self, db_name):
        return _DB_MAPPINGS[db_name]['db']

    def init(self, db_name):
        db_name = self._normalize_db_name(db_name)
        _DB_MAPPINGS[db_name]['db'].init(os.path.join(self.database_dir,
                                                      db_name))
        _DB_MAPPINGS[db_name]['db'].connect()
        os.chmod(_DB_MAPPINGS[db_name]['db'].database, 0600)
        for m in _DB_MAPPINGS[db_name]['models']:
            try:
                getattr(sys.modules[__name__], m).create_table(True)
            except OperationalError:
                pass

    def init_all(self):
        for k in _DB_MAPPINGS.iterkeys():
            self.init(k)

    def close(self, db_name):
        db_name = self._normalize_db_name(db_name)
        _DB_MAPPINGS[db_name]['db'].close()

    def close_all(self):
        for k in _DB_MAPPINGS.itervalues():
            self.close(k)

    def remove(self, db_name):
        db_name = self._normalize_db_name(db_name)
        _DB_MAPPINGS[db_name]['db'].close()
        os.remove(_DB_MAPPINGS[db_name]['db'].database)

    def remove_all(self):
        for k in _DB_MAPPINGS.itervalues():
            self.remove(k)

    def _normalize_db_name(self, db_name):
        return db_name if db_name.endswith('.db') else db_name + '.db'
