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

import errno
import fcntl
import os
import signal

from .defaults import *
from .logger import get_logger

__all__ = [
    'kill_process_by_pid', 'there_can_be_only_one'
]


def kill_process_by_pid(pid):
    """
    Send signal sig to the process pid.
    """
    os.kill(pid, signal.SIGKILL)


def there_can_be_only_one(data_path, x):
    """
    In the End, There Can Be Only One.

    And if we are not The One this returns False.
    """
    logger = get_logger(BOXSYNCD_BIN)
    pidfile = os.path.join(data_path, '%s.pid' % BOXSYNCD_BIN)

    def get_out():
        try:
            logger.info(
                'Another instance of %s (%s) is running!' % (BOXSYNC, pid))
        except Exception:
            pass
        finally:
            return False

    logger.debug('Checking if there are other instances of %s running...' %
                 BOXSYNCD_BIN)
    logger.debug('We are running with pid %s' % os.getpid())

    try:
        with open(pidfile, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                s = f.read()
                if s:
                    try:
                        pid = int(s)
                    except Exception:
                        logger.warning(
                            'Pidfile content is unreadable. Overriding'
                            ' contents: %r' % s)
                    else:
                        if pid == os.getpid():
                            logger.debug(
                                'Good, we are the only instance running; carry'
                                ' on')
                            return
                        try:
                            yes = os.readlink('/proc/%d/exe' % pid)\
                                .endswith('/%s' % BOXSYNCD_BIN)
                        except OSError as e:
                            if e.errno != errno.ENOENT:
                                pass
                            yes = False

                        if not (yes):
                            try:
                                with open('/proc/%d/cmdline' % pid) as f2:
                                    foo = f2.read()
                                    yes = os.path.join('bin', BOXSYNCD_BIN) \
                                        in foo and 'python' in foo
                            except IOError as e:
                                if e.errno != errno.ENOENT:
                                    pass

                        if yes:
                            get_out()
                f.seek(0)
                f.truncate()
                f.write('%d' % os.getpid())
                logger.debug(
                    'Updated pidfile, we are the only instance running; carry'
                    ' on')
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    except Exception:
        pass
