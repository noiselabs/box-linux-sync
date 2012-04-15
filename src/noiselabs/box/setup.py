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

from __future__ import print_function

import grp
import os
import shutil
import subprocess
import ConfigParser

from noiselabs.box.config import BoxConfig, BASEDIR
from noiselabs.box.utils import get_username

class BoxSetup(object):
    """
    Box setup helper.
    """
    def __init__(self, box_console):
        self.config = BoxConfig(box_console)
        self.out = box_console
    
    def check(self):
        self.check_config()
        self.check_deps()

    def check_config(self):
        self.config.check_file()
        self.config.check_config()

    def check_deps(self):
        self.check_dep_davfs()

    def check_dep_davfs(self):
        self.out.info("* Checking davfs installation...")
        if not os.path.isfile("/etc/davfs2/davfs2.conf"):
            self.out.error("* Davfs is not installed in your system. Please install it and re-run this application.")
            self.out.error("  Gentoo:         emerge davfs2")
            self.out.error("  Debian, Ubuntu: apt-get install davfs2")
            self.out.error("  Red Hat:        yum install davfs2")
            return False
        else:
            self.out.info("  Davfs install is OK.")
        """
        * Quick setup:
        *    (as root)
        *    # gpasswd -a ${your_user} davfs2
        *    # echo 'http://path/to/dav /home/${your_user}/dav davfs rw,user,noauto  0  0' >> /etc/fstab
        *    (as user)
        *    # mkdir -p ~/dav
        *    $ mount ~/dav
        """

    def setup_davfs(self):
        self.out.info("* Setting up davfs...")
        box_dir = self.get_box_dir()
        if not os.path.isdir(box_dir):
            os.makedirs(box_dir, 0775)
            self.out.info("  Created sync directory at '%s'" % box_dir)
        else:
            self.out.info("  Found sync directory at '%s'" % box_dir)

        user = get_username()
        if not user in grp.getgrnam("davfs2").gr_mem:
            self.out.warning("Adding yourself to davfs2 group (requires sudo)")
            cmd = "sudo gpasswd -a %s davfs2" % user
            if subprocess.call(cmd, shell=True) is not 0:
                self.out.error("Failed to add yourself to the davfs2 group")
                return False

        print()
        self.out.warning("The remaining procedures require a human intervention.")
        self.out.warning("Please follow them carefully. Thanks for your patience!")
        print()

        self.out.info("* 1. Add this line to your /etc/fstab (if not done already):")
        print("  $ sudo echo \"https://www.box.com/dav %s davfs rw,user,noauto 0 0\" >> /etc/fstab" % box_dir)
        print()

        self.out.info("* 2. Add this line to the bottom of the /etc/davfs2/secrets file (replace with your email address and password):")
        print("  $ sudo echo \"https://www.box.net/dav EMAIL PASSWORD\" >> /etc/davfs2/secrets")
        print()

        self.out.info("* 3. Make sure 'use_locks 0' is set in /etc/davfs2/davfs2.conf")
        editor = os.getenv('EDITOR')
        print("  $ sudo %s /etc/davfs2/davfs2.conf" % editor)
        print()

    def wizard(self):
        self.setup_davfs()

    def get_box_dir(self):
        try:
            box_dir = self.config.cfgparser.get("main", "box_dir")
        except ConfigParser.NoSectionError:
            self.check_config()
        box_dir = self.config.cfgparser.get("main", "box_dir")
        if not os.path.isabs(box_dir):
            box_dir = os.path.join(os.path.expanduser('~'), box_dir)
        return box_dir

    def uninstall(self):
        if not os.path.isdir(BASEDIR):
            self.out.info("Directory %s was already removed." % BASEDIR)
            return False

        self.out.countdown()
        try:
            shutil.rmtree(BASEDIR)
            self.out.info("Removed directory %s." % BASEDIR)
        except OSError:
            self.out.error("Error removing directory %s" % BASEDIR)
    