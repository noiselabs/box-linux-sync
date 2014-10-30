#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2014 Vítor Brandão <vitor@noiselabs.org>
#
# box-linux-sync is free software; you can redistribute it  and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# box-linux-sync is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with box-linux-sync; if not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import pyinotify
import re


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

    def handle_read_callback(self, notifier):
        pass

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


class FilesystemWatcher(object):
    """
    The Almighty Filesystem Watcher. Sometimes it works.
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

    def __init__(self, ioloop, box_path):
        """
        Constructor.

        @param cfg:
        @return:
        """
        self.ioloop = ioloop
        self.async = True # AsyncNotifier or ThreadedNotifier
        self.boxdir = box_path
        self.notifier = None

        #self.exclude_list_relative = self.cfg.get_exclude_list()
        #self.exclude_list_absolute = [os.path.join(self.boxdir, r) for r in
        #  self.exclude_list_relative]
        self.exclude_list_relative = []
        self.exclude_list_absolute = []

    def start(self):
        """

        @return:
        """
        self.index()

        wm = pyinotify.WatchManager()
        handler = EventHandler(self, "", self.boxdir)
        self.notifier = pyinotify.TornadoAsyncNotifier(wm, self.ioloop,
                                                   callback=handler.handle_read_callback, default_proc_fun=handler)

        # Adding exclusion list
        exclude_filter = pyinotify.ExcludeFilter(self.exclude_list_absolute)
        # Start watching a path
        wm.add_watch(self.boxdir, self.mask, rec=True, auto_add=True, exclude_filter=exclude_filter)

        print("[%s] Monitoring started (type Ctrl^C to exit)" % datetime.datetime.now())

    def stop(self):
        if self.notifier:
            self.notifier.stop()
        pass

    def index(self):
        print('[%s] Indexing "%s" ...' % (datetime.datetime.now(), self.boxdir))
        prefix_len = len(self.boxdir)
        for root, dirnames, filenames in os.walk(self.boxdir):
            root = root[prefix_len:].lstrip('/')
            if root in self.exclude_list_relative:
                print('[%s] -  Skipped "%s" (selective sync)' % (datetime.datetime.now(), root))
                continue
            else:
                for d in dirnames:
                    dir = os.path.join(root, d)
                    if dir not in self.exclude_list_relative:
                        print('[%s] d  %s' % (datetime.datetime.now(), dir))
                for file in filenames:
                    print('[%s] f  %s' % (datetime.datetime.now(), os.path.join(root, file)))
