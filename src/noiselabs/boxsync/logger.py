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
from .defaults import DEFAULT_LOG_PATH

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'debug': {
            'format': '[%(asctime)s] %(module)s.%(levelname)s [%(process)d.%(thread)d]: %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s] %(name)s.%(levelname)s: %(message)s'
        },
        'simple': {
            'format': '%(module)s.%(levelname)s: %(message)s'
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
            'maxBytes': '4096',
            'backupCount': '5',
            'formatter': 'debug'
        }
    },
    'loggers': {
        'peewee': {
            'handlers':['console', 'file'],
            'propagate': True,
            'level':'ERROR',
        },
        'boxsyncd': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

def start_logger():
    logging.config.dictConfig(LOGGING_CONFIG)