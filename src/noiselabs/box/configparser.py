#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2012 Vítor Brandão <noisebleed@noiselabs.org>
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

import csv

class WhitespaceDelimitedConfigParser(object):
    """A really simple, stupid, class to parse whitespace delimited files
    like /etc/fstab or /etc/davfs2/davfs.conf"""

    def read(self, filepath):
        self.f = open(filepath, 'rb')
        self.reader = csv.reader(self.f, delimiter=' ', skipinitialspace=True)
    
    def get_option(self, option, index=0):
        for row in self.reader:
            if row and option == row[0]:
                return row
        return False
            
    def close(self):
        self.f.close()