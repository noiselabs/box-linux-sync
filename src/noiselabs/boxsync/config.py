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

from .db import Config

__all__ = [
    'ConfigDict'
]


class ConfigDict(dict):
    """A class that simulates a dictionary, containing user settings fetched
    from config.db."""

    def __init__(self, model):
        """
        :param model: A peewee `Model <http://peewee.readthedocs
        .org/en/latest/peewee/api.html#Model>`_
        instance.
        :type model: peewee.Model
        @return: None

        ..note: The database should be fully initialized before calling
        __init__().
        """
        self.model = model
        dict.__init__(self)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        self.model._meta.fields[key] = value
        dict.__setitem__(self, key, value)


    def import_from_database(self):
        pass


def load_box_config(box_path):
    config = ConfigDict(Config)
    config['box_path'] = box_path

    return config
