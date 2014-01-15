#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2014 Vítor Brandão <vitor@noiselabs.org>
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

import abc
import platform
import subprocess

def get_pms():
    """In here we try to determine the Linux distro we are currently running and
    then return the Package Management System commonly associated with that
    distro."""
    if platform.system() != 'Linux': return False

    (distname,version,id) = platform.linux_distribution(full_distribution_name=False)
    if distname == 'gentoo':
        from noiselabs.box.pms.portage import Portage
        return Portage()
    elif distname in ['debian', 'ubuntu']:
        from noiselabs.box.pms.apt import APT
        return APT()
    elif distname in ['SuSE', 'fedora', 'redhat', 'centos', 'yellowdog', 'UnitedLinux', 'turbolinux']:
        from noiselabs.box.pms.yum import YUM
        return YUM()
    elif distname == 'slackware':
        from noiselabs.box.pms.slackpkg import Slackpkg
        return Slackpkg()
    elif distname == 'archlinux':
        from noiselabs.box.pms.pacman import Pacman
        return Pacman()
    else:
        return False

class BasePMS(object):
    """An abstract base class to be inherited by every PMS implementation."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def search(self, pkg):
        """Retrieve as a string the command used to search for a given package"""
        return        
        
    @abc.abstractmethod
    def install(self, pkg):
        """Retrieve as a string the command required to install the package"""
        return
        
    @abc.abstractmethod
    def remove(self, pkg):
        """Retrieve as a string the command required to remove the package"""
        return
        
    def run(self, cmd):
        """Executes the command"""
        return subprocess.call(cmd, shell=True)