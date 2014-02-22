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

import logging.config
import os
import sys
from .defaults import DEFAULT_LOG_PATH, ENCODING

__all__ = ('Console', 'GlobalLogger')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(module)s.%(levelname)s: %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s] %(name)s.%(levelname)s: %(message)s'
        },
        'debug': {
            'format': '[%(asctime)s] %(module)s.%(levelname)s [%(process)d.%(thread)d]: %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'logging.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DEFAULT_LOG_PATH,
            'maxBytes': '5242880', # 5 megabytes
            'backupCount': '4',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'boxsync': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'boxsyncd': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'peewee': {
            'handlers':['console', 'file'],
            'propagate': True,
            'level':'ERROR',
        },
    }
}


class Console(object):
    def __init__(self, enc=None):
        self.enc = ENCODING if enc is None else enc

    def write(self, st=u"", f=sys.stdout, linebreak=True):
        assert type(st) is unicode
        f.write(st.encode(self.enc))
        if linebreak: f.write(os.linesep)

    def flush(self, f=sys.stdout):
        f.flush()


class GlobalLogger(object):
    def __init__(self, verbose=False, debug=False):
        self.config = LOGGING_CONFIG
        loggers = self.config['loggers'].keys()
        if debug:
            for l in loggers:
                self.config['loggers'][l]['level'] = 'DEBUG'
            self.config['handlers']['file']['formatter'] = 'debug'
        elif verbose:
            for l in loggers:
                self.config['loggers'][l]['level'] = 'INFO'

        self.setup(self.config)
        logging.captureWarnings(True)

    def setup(self, config):
        logging.config.dictConfig(config)

    def getLogger(self, name='boxsyncd'):
        return logging.getLogger(name)

    def setLevel(self, level, name=None):
        if name is None:
            for k in self.config['loggers'].keys():
                self.config['loggers'][k]['level'] = level
                logging.getLogger(k).setLevel(level)
        else:
            self.config['loggers'][name]['level'] = level
            logging.getLogger(name).setLevel(level)
