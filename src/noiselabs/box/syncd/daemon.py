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

import fnmatch, os, time, atexit
from signal import SIGTERM
import pyinotify
import datetime
import re
from types import *


class Daemon(object):
    """
    A generic daemon class

    Usage: subclass the Daemon class and override the run method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        """

        @param pidfile:
        @param stdin:
        @param stdout:
        @param stderr:
        @return:
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced Programming in the
        UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                #exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("Fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("Fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Write pid file
        atexit.register(self.remove_pidfile)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def remove_pidfile(self):
        """
        Remove the pidfile.
        """
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon.
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
        # Get the pid from the pidfile
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
        raise NotImplementedError('Please override run() in your Daemon subclass')


class EventHandler(pyinotify.ProcessEvent):
    """
    Process events objects.
    """
    def __init__(self, parent, prefix, root):
        pyinotify.ProcessEvent.__init__(self)
        self.parent = parent       #should be calling instance of WatcherDaemon
        self.prefix = prefix       #prefix to handle recursively watching new dirs
        self.root = root           #root of watch (actually used to calculate subdirs)
        self.move_map = {}

    def run_command(self, event, ignore_cookie=True):
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

        # Run substitutions on the command
        print("[%s] watched:'%s' filename:'%s' dest_file:'%s' tflags:'%s' nflags:'%s' src_path:'%s' src_rel_path:'%s'" %(
                datetime.datetime.now(), event.path,  event.pathname, dfile, event.maskname, event.mask, src_path, src_rel_path))



    def process_IN_ACCESS(self, event):
        self.run_command(event)

    def process_IN_ATTRIB(self, event):
        self.run_command(event)

    def process_IN_CLOSE_WRITE(self, event):
        self.run_command(event)

    def process_IN_CLOSE_NOWRITE(self, event):
        self.run_command(event)

    def process_IN_CREATE(self, event):
        self.run_command(event)

    def process_IN_DELETE(self, event):
        self.run_command(event)

    def process_IN_MODIFY(self, event):
        self.run_command(event)

    def process_IN_MOVE_SELF(self, event):
        self.run_command(event)

    def process_IN_MOVED_FROM(self, event):
        self.move_map[event.cookie] = event.pathname
        self.run_command(event)

    def process_IN_MOVED_TO(self, event):
        self.run_command(event, False)

    def process_IN_OPEN(self, event):
        self.run_command(event)


class SyncDaemon(Daemon):
    """
    The Almighty BoxSync daemon. Sometimes it works.
    """

    # List of events:
    #  IN_ACCESS: File was accessed.
    #  IN_MODIFY: File was modified.
    #  IN_ATTRIB: Metadata changed.
    #  IN_CLOSE_WRITE: Writtable file was closed.
    #  IN_CLOSE_NOWRITE: Unwrittable file closed.
    #  IN_OPEN: File was opened.
    #  IN_MOVED_FROM: File was moved from X.
    #  IN_MOVED_TO: File was moved to Y.
    #  IN_CREATE: Subfile was created.
    #  IN_DELETE: Subfile was deleted.
    #  IN_DELETE_SELF: Self (watched item itself) was deleted.
    #  IN_MOVE_SELF: Self (watched item itself) was moved.
    #  IN_UNMOUNT: Backing fs was unmounted.
    #  IN_Q_OVERFLOW: Event queued overflowed.
    #  IN_IGNORED: File was ignored.
    #  IN_ONLYDIR: Only watch the path if it is a directory (new
    #              in kernel 2.6.15).
    #  IN_DONT_FOLLOW: Don't follow a symlink (new in kernel 2.6.15).
    #                  IN_ONLYDIR we can make sure that we don't watch
    #                  the target of symlinks.
    #  IN_EXCL_UNLINK: Events are not generated for children after they
    #                  have been unlinked from the watched directory.
    #                  (new in kernel 2.6.36).
    #  IN_MASK_ADD: add to the mask of an already existing watch (new
    #               in kernel 2.6.14).
    #  IN_ISDIR: Event occurred against dir.
    #  IN_ONESHOT: Only send event once.
    #  ALL_EVENTS: Alias for considering all of the events.
    mask = pyinotify.IN_MODIFY | pyinotify.IN_ATTRIB | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO \
    | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_UNMOUNT | pyinotify.IN_ONLYDIR | pyinotify.IN_EXCL_UNLINK

    def __init__(self, cfg, bc):
        """
        Constructor.

        @param cfg:
        @param bc:
        @return:
        """
        self.cfg = cfg
        self.bc = bc
        self.async = True # AsyncNotifier or ThreadedNotifier
        self.boxdir = self.cfg.get_box_location()
        super(SyncDaemon,self).__init__(os.path.join(self.cfg.get_data_dir(), 'boxsyncd.pid'))

        self.exclude_list_relative = self.cfg.get_exclude_list()
        self.exclude_list_absolute = [os.path.join(self.boxdir, r) for r in self.exclude_list_relative]

    def run(self):
        """

        @return:
        """
        self.bc.debug("[%s] Daemon started" % datetime.datetime.now())
        if self.bc.opts.verbose:
            self.bc.debug('[%s] Exclude list: "%s"' %(datetime.datetime.now(), '", "'.join(self.exclude_list_relative)))
        self.index()

        wm = pyinotify.WatchManager()
        handler = EventHandler(self, "", self.boxdir)

        if self.async:
            notifier = pyinotify.AsyncNotifier(wm, handler)
            self.bc.debug("[%s] pyinotify: using AsyncNotifier" % datetime.datetime.now())
        else:
            # Start the notifier from a new thread, without doing anything as no directory or file are currently
            # monitored yet.
            notifier = pyinotify.ThreadedNotifier(wm, handler)
            self.bc.debug("[%s] pyinotify: using ThreadedNotifier" % datetime.datetime.now())

        # Adding exclusion list
        exclude_filter = pyinotify.ExcludeFilter(self.exclude_list_absolute)
        # Start watching a path
        wm.add_watch(self.boxdir, self.mask, rec=True, auto_add=True, exclude_filter=exclude_filter)

        self.bc.info("[%s] Monitoring started (type Ctrl^C to exit)" % datetime.datetime.now())
        if self.async:
            import asyncore
            asyncore.loop()
        else:
            notifier.loop()

    def index(self):
        self.bc.info('[%s] Indexing "%s" ...' % (datetime.datetime.now(), self.boxdir))
        prefix_len = len(self.boxdir)
        for root, dirnames, filenames in os.walk(self.boxdir):
            root = root[prefix_len:].lstrip('/')
            if root in self.exclude_list_relative:
                self.bc.debug('[%s] -  Skipped "%s" (selective sync)' % (datetime.datetime.now(), root))
                continue
            else:
                for d in dirnames:
                    dir = os.path.join(root, d)
                    if dir not in self.exclude_list_relative:
                        self.bc.debug('[%s] d  %s' % (datetime.datetime.now(), dir))
                for file in filenames:
                    self.bc.debug('[%s] f  %s' % (datetime.datetime.now(), os.path.join(root, file)))

