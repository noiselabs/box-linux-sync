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

from __future__ import print_function

import datetime
import grp
import os
import shutil
import subprocess
import ConfigParser

from noiselabs.box import __prog__, __version__
from noiselabs.box.config import BoxConfig, BASEDIR
from noiselabs.box.configparser import WhitespaceDelimitedConfigParser
from noiselabs.box.pms.pms import get_pms
from noiselabs.box.utils import get_username

class BoxSetup(object):
    """
    Box setup helper.
    """
    def __init__(self, box_console):
        self.config = BoxConfig(box_console)
        self.out = box_console
        self.home_dir = os.path.expanduser('~')
    
    def check(self):
        self.check_config()
        self.check_deps()

    def check_config(self):
        self.config.check_file()
        self.config.check_config()

    def check_deps(self):
        self.check_dep_davfs()

    def check_dep_davfs(self):
        """Check for the existence of files installed by davfs2 package.
        If they are not found create a PMS instance and ask it what's the
        command used to install the package."""
        self.out.info("* Checking davfs installation...")
        for davfs_file in ['/usr/sbin/mount.davfs', '/sbin/umount.davfs', '/etc/davfs2/davfs2.conf']:
            if not os.path.isfile(davfs_file):
                self.out.error("! Davfs is not installed in your system. Please install it and re-run this application.")
                pms = get_pms()
                if pms == False: return False
                suggestion = pms.install('davfs2')
                if suggestion != False:
                    self.out.info("  You may install it using: $ sudo " + suggestion)
                return False

        self.out.info("* Congratulations. Your Davfs install is OK ;)")
        return True
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
            self.out.info("* Created sync directory at '%s'" % box_dir)
        else:
            self.out.debug("* Found sync directory at '%s'." % box_dir)

        # Add the user to the davfs2 group
        user = get_username()
        if not user in grp.getgrnam("davfs2").gr_mem:
            self.out.warning("* Adding yourself to davfs2 group (requires sudo)")
            cmd = "sudo gpasswd -a %s davfs2" % user
            if subprocess.call(cmd, shell=True) != 0:
                self.out.error("! Failed to add yourself to the davfs2 group")
                return False

        # Create ~/.davfs2 directory if needed
        home_davfs_dir = os.path.join(self.home_dir, '.davfs2')
        if not os.path.isdir(home_davfs_dir):
            os.makedirs(home_davfs_dir, 0700)
            self.out.info("*  Created a personal davfs2 directory at '%s'" % home_davfs_dir)
        else:
            self.out.debug("* Found personal davfs2 directory at '%s'." % home_davfs_dir)

        # Create ~/.davfs2/cache directory if needed
        davfs_cache_dir = os.path.join(home_davfs_dir, 'cache')
        if not os.path.isdir(davfs_cache_dir):
            os.makedirs(davfs_cache_dir, 0700)
            self.out.info("*  Created a personal cache directory at '%s'" % davfs_cache_dir)
        else:
            self.out.debug("* Found personal cache directory at '%s'." % davfs_cache_dir)
            if (os.stat(davfs_cache_dir).st_mode & 0777) != 0700:
                os.chmod(davfs_cache_dir, 0700)
                self.out.info("*  Fixed '%s' permissions" % davfs_cache_dir)

        # Check for a .davfs2 secrets file in the home dir
        secrets_file = os.path.join(home_davfs_dir, 'secrets')
        try:
            with open(secrets_file, 'r') as f: pass
            self.out.debug("* Found personal secrets file in '%s'" % secrets_file)
        except IOError as e:
            # Create a secrets file if needed
            with open(secrets_file, 'wb') as f:
                f.write("# davfs2 secrets file\n"+
                "# version 4\n"+
                "# Created by %s-%s in %s" % (__prog__, __version__, str(datetime.date.today())+"\n"+
                "\n"+
                "# https://www.box.com/dav me@example.com mypassword\n"))
                os.chmod(secrets_file, 0600)
            self.out.info("* Created a new secrets file in '%s'" % secrets_file)

        # Check for a davfs2.conf file in the home dir
        davfs_conf_file = os.path.join(home_davfs_dir, 'davfs2.conf')
        try:
            with open(davfs_conf_file, 'r') as f: pass
            self.out.debug("* Found personal config file in '%s'" % secrets_file)
        except IOError as e:
            # Create a davfs.conf file if needed
            with open(davfs_conf_file, 'wb') as f:
                f.write("# davfs2 configuration file\n"+
                "# version 9\n"+
                "# Created by %s-%s in %s" % (__prog__, __version__, str(datetime.date.today())+"\n"+
                "\n"+
                "use_locks 0\n"))
            os.chmod(davfs_conf_file, 0600)
            self.out.info("* Installed a new davfs config file in '%s'" % davfs_conf_file)

        cp = WhitespaceDelimitedConfigParser()

        #print()
        #self.out.warning("The remaining procedures may require human intervention.")
        #self.out.warning("Please follow them carefully. Thanks for your patience!")
        #print()

        cp.read(secrets_file)
        line = cp.get_option('https://www.box.com/dav')
        if line:
            self.out.info("* '%s' looks good ;)" % secrets_file)
            line[2] = '<HIDDEN>'
            self.out.debug('  Read: "' + ' '.join(line) + '"')
        else:
            self.out.warning("* Credentials are missing from %s. Please add them:" % secrets_file)
            print("  $ echo \"https://www.box.com/dav MYEMAIL MYPASSWORD\" >> %s" % secrets_file)
            print()
        cp.close()

        fstab_file = '/etc/fstab'
        cp.read(fstab_file)
        line = cp.get_option('https://www.box.com/dav')
        if line:
            self.out.info("* '%s' looks good ;)" % fstab_file)
            self.out.debug('  Read: "' + ' '.join(line) + '"')
        else:
            self.out.warning("* Box mount point is missing. Please add this line to your /etc/fstab:")
            print("  $ sudo sh -c 'echo \"https://www.box.com/dav %s davfs rw,user,noauto 0 0\" >> /etc/fstab'" % box_dir)
            print()
        cp.close()

        cp.read(davfs_conf_file)
        line = cp.get_option('use_locks')
        if line and line[1] == '0':
            self.out.info("* '%s' looks good ;)" % davfs_conf_file)
            self.out.debug('  Read: "' + ' '.join(line) + '"')
        else:
            self.out.warning("* Please set 'use_locks 0' in /etc/davfs2/davfs2.conf")
            editor = os.getenv('EDITOR')
            print("  $ sudo %s /etc/davfs2/davfs2.conf" % editor)
            print()
        cp.close()

    def wizard(self):
        self.setup_davfs()

    def get_box_dir(self):
        try:
            box_dir = self.config.cfgparser.get("main", "box_dir")
        except ConfigParser.NoSectionError:
            self.check_config()
        box_dir = self.config.cfgparser.get("main", "box_dir")
        if not os.path.isabs(box_dir):
            box_dir = os.path.join(self.home_dir, box_dir)
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
    
