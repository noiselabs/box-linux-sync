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

import errno
import itertools
import os
from posixpath import curdir, sep, pardir, join, abspath, commonprefix
import sys


def methodcaller(name, *args, **kwargs):
    def caller(obj):
        return getattr(obj, name)(*args, **kwargs)
    return caller


def unicode_abspath(path):
    assert type(path) is unicode
    # shouldn't pass unicode to this craphead, it appends with os.getcwd()
    # which is always a str
    return os.path.abspath(path.encode(sys.getfilesystemencoding())).decode(
        sys.getfilesystemencoding())


def partition(f, iterable, lazy=False):
    iter1, iter2 = itertools.tee(iterable, 2)
    true, false = itertools.ifilter(f, iter1), itertools.ifilterfalse(f, iter2)
    if not lazy:
        true, false = list(true), list(false)
    return (true, false)


def relpath(path, start=curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    if type(start) is unicode:
        start_list = unicode_abspath(start).split(sep)
    else:
        start_list = abspath(start).split(sep)

    if type(path) is unicode:
        path_list = unicode_abspath(path).split(sep)
    else:
        path_list = abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)


class FilesystemUtils(object):
    def makedirs(self, path, mode=None, override=True):
        try:
            os.makedirs(path, mode if mode is not None else 511)
        except Exception as e:
            if e.errno == errno.EEXIST:
                if not override:
                    mode = None
            else:
                raise

        if mode is not None:
            os.chmod(path, mode)
