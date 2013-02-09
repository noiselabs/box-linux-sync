#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2013 Vítor Brandão <noisebleed@noiselabs.org>
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

from noiselabs.box.pms.pms import BasePMS

class YUM(BasePMS):
    """The Yellowdog Updater, Modified (YUM) is an open-source command-line
    package-management utility for RPM-compatible Linux operating systems"""

    def __str__(self):
        return 'Yum'

    def search(self, pkg):
        return "yum search %s" % pkg

    def install(self, pkg):
        return "yum install %s" % pkg

    def remove(self, pkg):
        return "yum remove %s" % pkg
