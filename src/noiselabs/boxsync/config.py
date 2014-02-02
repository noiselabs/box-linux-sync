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

__all__ = ('ConfigDict')


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
