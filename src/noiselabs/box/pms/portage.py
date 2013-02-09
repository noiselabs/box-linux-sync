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

class Portage(BasePMS):
    """Portage is a package management system used by Gentoo Linux."""

    def __str__(self):
        return 'Portage'

    def search(self, pkg):
        return "emerge  --searchdesc %s" % pkg

    def install(self, pkg):
        return "emerge %s" % pkg

    def remove(self, pkg):
        return "emerge --unmerge %s" % pkg
