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
#
# Code in this module adapted from:
# - nautilus-dropbox-1.6.0/dropbox-cli (Copyright Dropbox, Inc.)

import optparse
import os
import socket
import subprocess
import sys
import threading
import time
from contextlib import closing

from .syncd.config import BoxSyncConfig
from .syncd.daemon import SyncDaemon
from .defaults import *
from .logger import Console
from .util import *
from tornado.ioloop import IOLoop

console = Console(ENCODING)

def is_boxsync_running():
    pidfile = os.path.join(DEFAULT_BOXSYNC_DATA_PATH, 'boxsyncd.pid')

    try:
        with open(pidfile, "r") as f:
            pid = int(f.read())
        with open("/proc/%d/cmdline" % pid, "r") as f:
            cmdline = f.read().lower()
    except:
        cmdline = ""

    return "boxsyncd" in cmdline

class CommandTicker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        ticks = ['[.  ]', '[.. ]', '[...]', '[ ..]', '[  .]', '[   ]']
        i = 0
        first = True
        while True:
            self.stop_event.wait(0.25)
            if self.stop_event.isSet(): break
            if i == len(ticks):
                first = False
                i = 0
            if not first:
                sys.stderr.write("\r%s\r" % ticks[i])
                sys.stderr.flush()
            i += 1
        sys.stderr.flush()

class BoxSyncCommand(object):
    class CouldntConnectError(Exception): pass
    class BadConnectionError(Exception): pass
    class EOFError(Exception): pass
    class CommandError(Exception): pass

    def __init__(self, timeout=5):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
        try:
            self.s.connect(os.path.join(DEFAULT_BOXSYNC_DATA_PATH, 'command_socket'))
        except socket.error, e:
            raise BoxSyncCommand.CouldntConnectError()
        self.f = self.s.makefile("r+", 4096)

    def close(self):
        self.f.close()
        self.s.close()

    def __readline(self):
        try:
            toret = self.f.readline().decode('utf8').rstrip(u"\n")
        except socket.error, e:
            raise BoxSyncCommand.BadConnectionError()
        if toret == '':
            raise BoxSyncCommand.EOFError()
        else:
            return toret

    # atttribute doesn't exist, i know what you want
    def send_command(self, name, args):
        self.f.write(name.encode('utf8'))
        self.f.write(u"\n".encode('utf8'))
        self.f.writelines((u"\t".join([k] + (list(v)
                                             if hasattr(v, '__iter__') else
                                             [v])) + u"\n").encode('utf8')
                          for k,v in args.iteritems())
        self.f.write(u"done\n".encode('utf8'))

        self.f.flush()

        # Start a ticker
        ticker_thread = CommandTicker()
        ticker_thread.start()

        # This is the potentially long-running call.
        try:
            ok = self.__readline() == u"ok"
        except KeyboardInterrupt:
            raise BoxSyncCommand.BadConnectionError("Keyboard interruption detected")
        finally:
            # Tell the ticker to stop.
            ticker_thread.stop()
            ticker_thread.join()

        if ok:
            toret = {}
            for i in range(21):
                if i == 20:
                    raise Exception(u"close this connection!")

                line = self.__readline()
                if line == u"done":
                    break

                argval = line.split(u"\t")
                toret[argval[0]] = argval[1:]

            return toret
        else:
            problems = []
            for i in range(21):
                if i == 20:
                    raise Exception(u"close this connection!")

                line = self.__readline()
                if line == u"done":
                    break

                problems.append(line)

            raise BoxSyncCommand.CommandError(u"\n".join(problems))

    # this is the hotness, auto marshalling
    def __getattr__(self, name):
        try:
            return super(BoxSyncCommand, self).__getattr__(name)
        except:
            def __spec_command(**kw):
                return self.send_command(unicode(name), kw)
            self.__setattr__(name, __spec_command)
            return __spec_command

commands = {}
aliases = {}

def command(meth):
    global commands, aliases
    assert meth.__doc__, "All commands need properly formatted docstrings (even %r!!)" % meth
    if hasattr(meth, 'im_func'): # bound method, if we ever have one
        meth = meth.im_func
    commands[meth.func_name] = meth
    meth_aliases = [unicode(alias) for alias in aliases.iterkeys() if aliases[alias].func_name == meth.func_name]
    if meth_aliases:
        meth.__doc__ += u"\nAliases: %s" % ",".join(meth_aliases)
    return meth

def alias(name):
    def decorator(meth):
        global commands, aliases
        assert name not in commands, "This alias is the name of a command."
        aliases[name] = meth
        return meth
    return decorator

def requires_boxsync_running(meth):
    def newmeth(*n, **kw):
        if is_boxsync_running():
            return meth(*n, **kw)
        else:
            console.write(u"BoxSync isn't running!")
    newmeth.func_name = meth.func_name
    newmeth.__doc__ = meth.__doc__
    return newmeth

def get_boxsyncd_path():
    bs_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'boxsyncd')
    if not os.path.exists(bs_path):
        # which('boxsyncd')
        for path in os.environ['PATH'].split(os.pathsep):
            bs_path = os.path.join(path, 'boxsyncd')
            if os.path.isfile(bs_path):
                break
            else:
                bs_path = None

    return bs_path

def start_boxsync():
    bs_path = get_boxsyncd_path()
    if os.access(bs_path, os.X_OK):
        f = open("/dev/null", "w")
        from .boxsyncd import main
        main()
        return True
        # we don't reap the child because we're gonna die anyway, let init do it
        a = subprocess.Popen([bs_path], preexec_fn=os.setsid, cwd=os.path.expanduser("~"),
                             stderr=sys.stderr, stdout=f, close_fds=True)

    # in seconds
    interval = 0.5
    wait_for = 60
    for i in xrange(int(wait_for / interval)):
        if is_boxsync_running():
            return True
        # back off from connect for a while
        time.sleep(interval)

        return False

def start_boxsync_debug():
    ioloop = IOLoop.instance()
    cfg = BoxSyncConfig()
    syncd = SyncDaemon(ioloop, cfg)

    #client = BoxClient(ioloop, cfg, bc)
    #client.authenticate()

    syncd.run()


# Extracted and modified from os.cmd.Cmd
def columnize(list, display_list=None, display_width=None):
    if not list:
        console.write(u"<empty>")
        return

    non_unicode = [i for i in range(len(list)) if not (isinstance(list[i], unicode))]
    if non_unicode:
        raise TypeError, ("list[i] not a string for i in %s" %
                          ", ".join(map(unicode, non_unicode)))

    if not display_width:
        d = os.popen('stty size', 'r').read().split()
        if d:
            display_width = int(d[1])
        else:
            for item in list:
                console.write(item)
            return

    if not display_list:
        display_list = list

    size = len(list)
    if size == 1:
        console.write(display_list[0])
        return

    for nrows in range(1, len(list)):
        ncols = (size+nrows-1) // nrows
        colwidths = []
        totwidth = -2
        for col in range(ncols):
            colwidth = 0
            for row in range(nrows):
                i = row + nrows*col
                if i >= size:
                    break
                x = list[i]
                colwidth = max(colwidth, len(x))
            colwidths.append(colwidth)
            totwidth += colwidth + 2
            if totwidth > display_width:
                break
        if totwidth <= display_width:
            break
    else:
        nrows = len(list)
        ncols = 1
        colwidths = [0]
    lines = []
    for row in range(nrows):
        texts = []
        display_texts = []
        for col in range(ncols):
            i = row + nrows*col
            if i >= size:
                x = ""
                y = ""
            else:
                x = list[i]
                y = display_list[i]
            texts.append(x)
            display_texts.append(y)
        while texts and not texts[-1]:
            del texts[-1]
        original_texts = texts[:]
        for col in range(len(texts)):
            texts[col] = texts[col].ljust(colwidths[col])
            texts[col].replace(original_texts[col], display_texts[col])
        line = u"  ".join(texts)
        lines.append(line)
    for line in lines:
        console.write(line)


@command
@requires_boxsync_running
@alias('stat')
def filestatus(args):
    u"""get current sync status of one or more files
boxsync filestatus [-l] [-a] [FILE]...

Prints the current status of each FILE.

options:
  -l --list  prints out information in a format similar to ls. works best when your console supports color :)
  -a --all   do not ignore entries starting with .
"""
    global ENCODING

    oparser = optparse.OptionParser()
    oparser.add_option("-l", "--list", action="store_true", dest="list")
    oparser.add_option("-a", "--all", action="store_true", dest="all")
    (options, args) = oparser.parse_args(args)

    try:
        with closing(BoxSyncCommand()) as dc:
            if options.list:
                # Listing.

                # Separate directories from files.
                if len(args) == 0:
                    dirs, nondirs = [u"."], []
                else:
                    dirs, nondirs = [], []

                    for a in args:
                        try:
                            (dirs if os.path.isdir(a) else nondirs).append(a.decode(ENCODING))
                        except UnicodeDecodeError:
                            continue

                    if len(dirs) == 0 and len(nondirs) == 0:
                        #TODO: why?
                        exit(1)

                dirs.sort(key=methodcaller('lower'))
                nondirs.sort(key=methodcaller('lower'))

                # Gets a string representation for a path.
                def path_to_string(file_path):
                    if not os.path.exists(file_path):
                        path = u"%s (File doesn't exist!)" % os.path.basename(file_path)
                        return (path, path)
                    try:
                        status = dc.icon_overlay_file_status(path=file_path).get(u'status', [None])[0]
                    except BoxSyncCommand.CommandError, e:
                        path =  u"%s (%s)" % (os.path.basename(file_path), e)
                        return (path, path)

                    env_term = os.environ.get('TERM','')
                    supports_color = (sys.stderr.isatty() and (
                                        env_term.startswith('vt') or
                                        env_term.startswith('linux') or
                                        'xterm' in env_term or
                                        'color' in env_term
                                        )
                                     )

                    # TODO: Test when you don't support color.
                    if not supports_color:
                        path = os.path.basename(file_path)
                        return (path, path)

                    if status == u"up to date":
                        init, cleanup = "\x1b[32;1m", "\x1b[0m"
                    elif status == u"syncing":
                        init, cleanup = "\x1b[36;1m", "\x1b[0m"
                    elif status == u"unsyncable":
                        init, cleanup = "\x1b[41;1m", "\x1b[0m"
                    elif status == u"selsync":
                        init, cleanup = "\x1b[37;1m", "\x1b[0m"
                    else:
                        init, cleanup = '', ''

                    path = os.path.basename(file_path)
                    return (path, u"%s%s%s" % (init, path, cleanup))

                # Prints a directory.
                def print_directory(name):
                    clean_paths = []
                    formatted_paths = []
                    for subname in sorted(os.listdir(name), key=methodcaller('lower')):
                        if type(subname) != unicode:
                            continue

                        if not options.all and subname[0] == u'.':
                            continue

                        try:
                            clean, formatted = path_to_string(unicode_abspath(os.path.join(name, subname)))
                            clean_paths.append(clean)
                            formatted_paths.append(formatted)
                        except (UnicodeEncodeError, UnicodeDecodeError), e:
                            continue

                    columnize(clean_paths, formatted_paths)

                try:
                    if len(dirs) == 1 and len(nondirs) == 0:
                        print_directory(dirs[0])
                    else:
                        nondir_formatted_paths = []
                        nondir_clean_paths = []
                        for name in nondirs:
                            try:
                                clean, formatted = path_to_string(unicode_abspath(name))
                                nondir_clean_paths.append(clean)
                                nondir_formatted_paths.append(formatted)
                            except (UnicodeEncodeError, UnicodeDecodeError), e:
                                continue

                        if nondir_clean_paths:
                            columnize(nondir_clean_paths, nondir_formatted_paths)

                        if len(nondirs) == 0:
                            console.write(dirs[0] + u":")
                            print_directory(dirs[0])
                            dirs = dirs[1:]

                        for name in dirs:
                            console.write()
                            console.write(name + u":")
                            print_directory(name)

                except BoxSyncCommand.EOFError:
                    console.write(u"BoxSync daemon stopped.")
                except BoxSyncCommand.BadConnectionError, e:
                    console.write(u"BoxSync isn't responding!")
            else:
                if len(args) == 0:
                    args = [name for name in sorted(os.listdir(u"."), key=methodcaller('lower')) if type(name) == unicode]
                if len(args) == 0:
                    # Bail early if there's nothing to list to avoid crashing on indent below
                    console.write(u"<empty>")
                    return
                indent = max(len(st)+1 for st in args)
                for file in args:

                    try:
                        if type(file) is not unicode:
                            file = file.decode(ENCODING)
                        fp = unicode_abspath(file)
                    except (UnicodeEncodeError, UnicodeDecodeError), e:
                        continue
                    if not os.path.exists(fp):
                        console.write(u"%-*s %s" % \
                                          (indent, file+':', "File doesn't exist"))
                        continue

                    try:
                        status = dc.icon_overlay_file_status(path=fp).get(u'status', [u'unknown'])[0]
                        console.write(u"%-*s %s" % (indent, file+':', status))
                    except BoxSyncCommand.CommandError, e:
                        console.write(u"%-*s %s" % (indent, file+':', e))
    except BoxSyncCommand.CouldntConnectError, e:
        console.write(u"BoxSync isn't running!")

@command
@requires_boxsync_running
def ls(args):
    u"""list directory contents with current sync status
boxsync ls [FILE]...

This is an alias for filestatus -l
"""
    return filestatus(["-l"] + args)

@command
@requires_boxsync_running
def status(args):
    u"""get current status of the boxsyncd
boxsync status

Prints out the current status of the BoxSync daemon.
"""
    if len(args) != 0:
        console.write(status.__doc__,linebreak=False)
        return

    try:
        with closing(BoxSyncCommand()) as dc:
            try:
                lines = dc.get_boxsync_status()[u'status']
                if len(lines) == 0:
                    console.write(u'Idle')
                else:
                    for line in lines:
                        console.write(line)
            except KeyError:
                console.write(u"Couldn't get status: daemon isn't responding")
            except BoxSyncCommand.CommandError, e:
                console.write(u"Couldn't get status: " + str(e))
            except BoxSyncCommand.BadConnectionError, e:
                console.write(u"BoxSync isn't responding!")
            except BoxSyncCommand.EOFError:
                console.write(u"BoxSync daemon stopped.")
    except BoxSyncCommand.CouldntConnectError, e:
        console.write(u"BoxSync isn't running!")

@command
def running(argv):
    u"""return whether boxsync is running
boxsync running

Returns 1 if running 0 if not running.
"""
    return int(is_boxsync_running())

@command
@requires_boxsync_running
def stop(args):
    u"""stop boxsyncd
boxsync stop

Stops the boxsync daemon.
"""
    try:
        with closing(BoxSyncCommand()) as bsc:
            try:
                bsc.tray_action_hard_exit()
            except BoxSyncCommand.BadConnectionError, e:
                console.write(u"BoxSync isn't responding!")
            except BoxSyncCommand.EOFError:
                console.write(u"BoxSync daemon stopped.")
    except BoxSyncCommand.CouldntConnectError, e:
        if is_boxsync_running():
            SyncDaemon(IOLoop.instance(), BoxSyncConfig()).stop()
            console.write(u"BoxSync daemon stopped.")
        else:
            console.write(u"BoxSync isn't running!")

#returns true if link is necessary
def grab_link_url_if_necessary():
    try:
        with closing(BoxSyncCommand()) as bsc:
            try:
                link_url = bsc.needs_link().get(u"link_url", None)
                if link_url is not None:
                    console.write(u"To link this computer to a Box account, visit the following url:\n%s" % link_url[0])
                    return True
                else:
                    return False
            except BoxSyncCommand.CommandError, e:
                pass
            except BoxSyncCommand.BadConnectionError, e:
                console.write(u"BoxSync isn't responding!")
            except BoxSyncCommand.EOFError:
                console.write(u"BoxSync daemon stopped.")
    except BoxSyncCommand.CouldntConnectError, e:
        console.write(u"BoxSync isn't running!")

@command
@requires_boxsync_running
def exclude(args):
    u"""ignores/excludes a directory from syncing
boxsync exclude [list]
boxsync exclude add [DIRECTORY] [DIRECTORY] ...
boxsync exclude remove [DIRECTORY] [DIRECTORY] ...

"list" prints a list of directories currently excluded from syncing.
"add" adds one or more directories to the exclusion list, then resynchronizes BoxSync.
"remove" removes one or more directories from the exclusion list, then resynchronizes BoxSync.
With no arguments, executes "list".
Any specified path must be within BoxSync.
"""
    if len(args) == 0:
        try:
            with closing(BoxSyncCommand()) as bsc:
                try:
                    lines = [relpath(path) for path in bsc.get_ignore_set()[u'ignore_set']]
                    lines.sort()
                    if len(lines) == 0:
                        console.write(u'No directories are being ignored.')
                    else:
                        console.write(u'Excluded: ')
                        for line in lines:
                            console.write(unicode(line))
                except KeyError:
                    console.write(u"Couldn't get ignore set: daemon isn't responding")
                except BoxSyncCommand.CommandError, e:
                    if e.args[0].startswith(u"No command exists by that name"):
                        console.write(u"This version of the client does not support this command.")
                    else:
                        console.write(u"Couldn't get ignore set: " + str(e))
                except BoxSyncCommand.BadConnectionError, e:
                    console.write(u"BoxSync isn't responding!")
                except BoxSyncCommand.EOFError:
                    console.write(u"BoxSync daemon stopped.")
        except BoxSyncCommand.CouldntConnectError, e:
            console.write(u"BoxSync isn't running!")
    elif len(args) == 1 and args[0] == u"list":
        exclude([])
    elif len(args) >= 2:
        sub_command = args[0]
        paths = args[1:]
        absolute_paths = [unicode_abspath(path.decode(sys.getfilesystemencoding())) for path in paths]
        if sub_command == u"add":
            try:
                with closing(BoxSyncCommand(timeout=None)) as bsc:
                    try:
                        result = bsc.ignore_set_add(paths=absolute_paths)
                        if result[u"ignored"]:
                            console.write(u"Excluded: ")
                            lines = [relpath(path) for path in result[u"ignored"]]
                            for line in lines:
                                console.write(unicode(line))
                    except KeyError:
                        console.write(u"Couldn't add ignore path: daemon isn't responding")
                    except BoxSyncCommand.CommandError, e:
                        if e.args[0].startswith(u"No command exists by that name"):
                            console.write(u"This version of the client does not support this command.")
                        else:
                            console.write(u"Couldn't get ignore set: " + str(e))
                    except BoxSyncCommand.BadConnectionError, e:
                        console.write(u"BoxSync isn't responding! [%s]" % e)
                    except BoxSyncCommand.EOFError:
                        console.write(u"BoxSync daemon stopped.")
            except BoxSyncCommand.CouldntConnectError, e:
                console.write(u"BoxSync isn't running!")
        elif sub_command == u"remove":
            try:
                with closing(BoxSyncCommand(timeout=None)) as bsc:
                    try:
                        result = bsc.ignore_set_remove(paths=absolute_paths)
                        if result[u"removed"]:
                            console.write(u"No longer excluded: ")
                            lines = [relpath(path) for path in result[u"removed"]]
                            for line in lines:
                                console.write(unicode(line))
                    except KeyError:
                        console.write(u"Couldn't remove ignore path: daemon isn't responding")
                    except BoxSyncCommand.CommandError, e:
                        if e.args[0].startswith(u"No command exists by that name"):
                            console.write(u"This version of the client does not support this command.")
                        else:
                            console.write(u"Couldn't get ignore set: " + str(e))
                    except BoxSyncCommand.BadConnectionError, e:
                        console.write(u"BoxSync isn't responding! [%s]" % e)
                    except BoxSyncCommand.EOFError:
                        console.write(u"BoxSync daemon stopped.")
            except BoxSyncCommand.CouldntConnectError, e:
                console.write(u"BoxSync isn't running!")
        else:
            console.write(exclude.__doc__, linebreak=False)
            return
    else:
        console.write(exclude.__doc__, linebreak=False)
        return

@command
def start(argv):
    u"""start boxsyncd
boxsync start

Starts the boxsync daemon, boxsyncd. If boxsyncd is already running, this will do nothing.
"""

    # first check if boxsync is already running
    if is_boxsync_running():
        if not grab_link_url_if_necessary():
            console.write(u"BoxSync is already running!")
        return

    console.write(u"Starting BoxSync...", linebreak=False)
    console.flush()
    if not start_boxsync():
        console.write()
        console.write(u"No good, boxsyncd failed to start.")
        return
    else:
        if not grab_link_url_if_necessary():
            console.write(u"Done!")

@command
def debug(argv):
    u"""run boxsyncd in debug mode
boxsync debug

Starts the boxsync daemon in debug mode. Useful for troubleshooting and people with too much free time.
"""

    # first check if boxsync is already running
    if is_boxsync_running():
        if not grab_link_url_if_necessary():
            console.write(u"BoxSync is already running!")
        return

    console.write(u"Starting BoxSync...", linebreak=False)
    console.flush()
    if not start_boxsync_debug():
        console.write()
        console.write(u"The BoxSync daemon is not installed!")
        console.write(u"Please install it using your favorite package manager")
        return
    else:
        if not grab_link_url_if_necessary():
            console.write(u"Done!")

@command
def help(argv):
    u"""provide help
boxsync help [COMMAND]

With no arguments, print a list of commands and a short description of each. With a command, print descriptive help on how to use the command.
"""
    if not argv:
        return usage(argv)
    for command in commands:
        if command == argv[0]:
            console.write(commands[command].__doc__.split('\n', 1)[1].decode('ascii'))
            return
    for alias in aliases:
        if alias == argv[0]:
            console.write(aliases[alias].__doc__.split('\n', 1)[1].decode('ascii'))
            return
    console.write(u"unknown command '%s'" % argv[0], f=sys.stderr)

def usage(argv):
    console.write(u"BoxSync command-line interface\n")
    console.write(u"commands:\n")
    console.write(u"Note: use boxsync help <command> to view usage for a specific command.\n")
    out = []
    for command in commands:
        out.append((command, commands[command].__doc__.splitlines()[0]))
    spacing = max(len(o[0])+3 for o in out)
    for o in out:
        console.write(" %-*s%s" % (spacing, o[0], o[1]))
    console.write()


def boxsync_main(argv):
    """
    @param argv: command arguments
    @type argv: list
    """

    global commands

    # now we need to find out if one of the commands are in the
    # argv list, and if so split the list at the point to
    # separate the argv list at that point
    cut = None
    for i in range(len(argv)):
        if argv[i] in commands or argv[i] in aliases:
            cut = i
            break

    if cut is None:
        usage(argv)
        os._exit(0)
        return

    # lol no options for now
    globaloptionparser = optparse.OptionParser()
    globaloptionparser.parse_args(argv[0:i])

    # now dispatch and run
    result = None
    if argv[i] in commands:
        result = commands[argv[i]](argv[i+1:])
    elif argv[i] in aliases:
        result = aliases[argv[i]](argv[i+1:])

    # flush, in case output is rerouted to a file.
    console.flush()

    # done
    return result
