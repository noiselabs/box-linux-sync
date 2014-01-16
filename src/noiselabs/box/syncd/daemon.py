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
#
# Class Daemon adapted from:
#   - http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#   - https://github.com/serverdensity/python-daemon/blob/master/daemon.py
#   - https://github.com/gregghz/Watcher/blob/master/watcher.py
# Credits goes to their respective project authors/contributors.

from __future__ import print_function

import sys, os, time, atexit
from signal import SIGTERM
import pyinotify
import sys, os
import datetime
import subprocess
import shlex
import re
from types import *
from string import Template

class Daemon(object):
    """
    A generic daemon class

    Usage: subclass the Daemon class and override the run method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced Programming in the
        UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                #exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        #redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        #write pid file
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exists. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the Daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, command, recursive, exclude, mask, parent, prefix, root):
        pyinotify.ProcessEvent.__init__(self)
        self.command = command     #the command to be run
        self.recursive = recursive #watch recursively?
        self.exclude = exclude      #path to exclude
        self.mask = mask           #the watch mask
        self.parent = parent       #should be calling instance of WatcherDaemon
        self.prefix = prefix       #prefix to handle recursively watching new dirs
        self.root = root           #root of watch (actually used to calculate subdirs)
        self.move_map = {}

    def runCommand(self, event, ignore_cookie=True):
        t = Template(self.command)
        sub_regex = self.root

        #build the dest_file
        dfile = event.name
        if self.prefix != "":
            dfile = self.prefix + '/' + dfile
        elif self.root != "":
            if event.path != self.root:
                sub_regex = self.root+os.sep
            dfile = re.sub('^'+re.escape(sub_regex),'',event.path) + os.sep + dfile

        #find the src_path if it exists
        src_path = ''
        src_rel_path = ''
        if not ignore_cookie and hasattr(event, 'cookie') and event.cookie in self.move_map:
            src_path = self.move_map[event.cookie]
            if self.root != "":
                src_rel_path = re.sub('^'+re.escape(sub_regex), '', src_path)
            del self.move_map[event.cookie]

        #run substitutions on the command
        command = t.safe_substitute({
                'watched': event.path,
                'filename': event.pathname,
                'dest_file': dfile,
                'tflags': event.maskname,
                'nflags': event.mask,
                'src_path': src_path,
                'src_rel_path': src_rel_path,
                'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        #try the command
        try:
            subprocess.call(shlex.split(command))
        except OSError, err:
            print("Failed to run command '%s' %s" % (command, str(err)))

        #handle recursive watching of directories
        if self.recursive and os.path.isdir(event.pathname):

            prefix = event.name
            if self.prefix != "":
                prefix = self.prefix + '/' + prefix
            self.parent.addWatch(self.mask,
                                 event.pathname,
                                 self.exclude,
                                 True,
                                 self.command,
                                 prefix)

    def process_IN_ACCESS(self, event):
        print("Access: ", event.pathname)
        self.runCommand(event)

    def process_IN_ATTRIB(self, event):
        print("Attrib: ", event.pathname)
        self.runCommand(event)

    def process_IN_CLOSE_WRITE(self, event):
        print("Close write: ", event.pathname)
        self.runCommand(event)

    def process_IN_CLOSE_NOWRITE(self, event):
        print("Close nowrite: ", event.pathname)
        self.runCommand(event)

    def process_IN_CREATE(self, event):
        print("Creating: ", event.pathname)
        self.runCommand(event)

    def process_IN_DELETE(self, event):
        print("Deleteing: ", event.pathname)
        self.runCommand(event)

    def process_IN_MODIFY(self, event):
        print("Modify: ", event.pathname)
        self.runCommand(event)

    def process_IN_MOVE_SELF(self, event):
        print("Move self: ", event.pathname)
        self.runCommand(event)

    def process_IN_MOVED_FROM(self, event):
        print("Moved from: ", event.pathname)
        self.move_map[event.cookie] = event.pathname
        self.runCommand(event)

    def process_IN_MOVED_TO(self, event):
        print("Moved to: ", event.pathname)
        self.runCommand(event, False)

    def process_IN_OPEN(self, event):
        print("Opened: ", event.pathname)
        self.runCommand(event)

class SyncDaemon(Daemon):
    """
    The Almighty BoxSync daemon. Sometimes it works.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        super(SyncDaemon,self).__init__(os.path.join(self.cfg.basedir, 'boxsyncd.pid'))

    def run(self):
        print("Daemon started at %s" % datetime.datetime.today())
        boxdir = self.cfg.get_boxdir()
        print("Box directory: " + boxdir)
        self.wdds = []
        self.notifiers = []

        # List of events to watch for: https://github.com/gregghz/Watcher/blob/master/jobs.yml#L40
        mask = self._parseMask(['create', 'move_from', 'move_to', 'delete', 'modify'])
        folder = boxdir
        exclude = []
        recursive = True
        command = "echo $datetime $filename $tflags"

        self.addWatch(mask, folder, exclude, recursive, command)

    def addWatch(self, mask, folder, exclude, recursive, command, prefix=""):
        wm = pyinotify.WatchManager()
        handler = EventHandler(command, recursive, exclude, mask, self, prefix, folder)

        # adding exclusion list
        excl_lst = exclude
        excl = pyinotify.ExcludeFilter(excl_lst)

        self.wdds.append(wm.add_watch(folder, mask, rec=recursive, exclude_filter=excl))
        # BUT we need a new ThreadNotifier so I can specify a different
        # EventHandler instance for each job
        # this means that each job has its own thread as well (I think)
        n = pyinotify.ThreadedNotifier(wm, handler)
        self.notifiers.append(pyinotify.ThreadedNotifier(wm, handler))
        n.start()

    def _parseMask(self, masks):
        ret = False;

        for mask in masks:
            if 'access' == mask:
                ret = self._addMask(pyinotify.IN_ACCESS, ret)
            elif 'atrribute_change' == mask:
                ret = self._addMask(pyinotify.IN_ATTRIB, ret)
            elif 'write_close' == mask:
                ret = self._addMask(pyinotify.IN_CLOSE_WRITE, ret)
            elif 'nowrite_close' == mask:
                ret = self._addMask(pyinotify.IN_CLOSE_NOWRITE, ret)
            elif 'create' == mask:
                ret = self._addMask(pyinotify.IN_CREATE, ret)
            elif 'delete' == mask:
                ret = self._addMask(pyinotify.IN_DELETE, ret)
            elif 'self_delete' == mask:
                ret = self._addMask(pyinotify.IN_DELETE_SELF, ret)
            elif 'modify' == mask:
                ret = self._addMask(pyinotify.IN_MODIFY, ret)
            elif 'self_move' == mask:
                ret = self._addMask(pyinotify.IN_MOVE_SELF, ret)
            elif 'move_from' == mask:
                ret = self._addMask(pyinotify.IN_MOVED_FROM, ret)
            elif 'move_to' == mask:
                ret = self._addMask(pyinotify.IN_MOVED_TO, ret)
            elif 'open' == mask:
                ret = self._addMask(pyinotify.IN_OPEN, ret)
            elif 'all' == mask:
                m = pyinotify.IN_ACCESS | pyinotify.IN_ATTRIB | pyinotify.IN_CLOSE_WRITE | \
                    pyinotify.IN_CLOSE_NOWRITE | pyinotify.IN_CREATE | pyinotify.IN_DELETE | \
                    pyinotify.IN_DELETE_SELF | pyinotify.IN_MODIFY | pyinotify.IN_MOVE_SELF | \
                    pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO | pyinotify.IN_OPEN
                ret = self._addMask(m, ret)
            elif 'move' == mask:
                ret = self._addMask(pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO, ret)
            elif 'close' == mask:
                ret = self._addMask(pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CLOSE_NOWRITE, ret)

        return ret

    def _addMask(self, new_option, current_options):
        if not current_options:
            return new_option
        else:
            return current_options | new_option
