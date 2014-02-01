#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2012-2014 Vítor Brandão <vitor@noiselabs.org>
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

import warnings
import functools

__title__ = 'BoxSync'
__prog__ = 'boxsync'
__version__ = '0.1.0'
__author__ = 'Vítor Brandão'
__license__ = 'LGPL-3'
__copyright__ = u'Copyright 2012-2014 Vítor Brandão'

def deprecated(func):
    """This is a decorator which can be used to mark functions as deprecated.
    It will result in a warning being emitted when the function is used.

    Reference: http://wiki.python.org/moin/PythonDecoratorLibrary

    .. code-block:: python
        :emphasize-lines: 4

        from noiselabs.boxsync.syncd import deprecated

        class SomeClass(object):
            @deprecated
            def some_old_method(self, x, y):
                return x + y
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func


class lazyproperty(object):
    """Meant to be used for lazy evaluation of an object attribute.
    Property should represent non-mutable data, as it replaces itself.

    .. code-block:: python
        :emphasize-lines: 4

        from noiselabs.boxsync.syncd import lazyproperty

        class SomeClass(object):
            @lazyproperty
            def some_lazy_prop(self):
                return range(5)

    """

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value
