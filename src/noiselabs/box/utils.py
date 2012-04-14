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

import os

def create_file(filepath, dirmode=0700, filemode=0600):
    """
    Creates a new file
    """
    if not os.path.isfile(filepath):
        # if the base dir doesn't exist we need to create it first
        basedir = os.path.dirname(filepath) 
        if not os.path.isdir(basedir):
            os.makedirs(os.path.dirname(filepath), dirmode)
        # create the file
        f = open(filepath, 'w+')
        f.write('')
        f.close()
        os.chmod(filepath, filemode)
        return True
    else:
        return False
    
