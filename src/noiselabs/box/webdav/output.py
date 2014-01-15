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

from __future__ import print_function

import curses
import logging
import os
import time
import sys
import types

from noiselabs.box.webdav.config import BASEDIR
from noiselabs.box.webdav.utils import create_file
from noiselabs.box.webdav.ansistrm import ColorizingStreamHandler

################################################################################
##
## Color codes (taken from Portage)
##
################################################################################

_styles = {}
"""Maps style class to tuple of attribute names."""

codes = {}
"""Maps attribute name to ansi code."""

esc_seq = "\x1b["

codes["normal"]         = esc_seq + "0m"
codes['reset']          = esc_seq + "39;49;00m"

codes["bold"]         =  esc_seq + "01m"
codes["faint"]        =  esc_seq + "02m"
codes["standout"]     =  esc_seq + "03m"
codes["underline"]    =  esc_seq + "04m"
codes["blink"]        =  esc_seq + "05m"
codes["overline"]     =  esc_seq + "06m"
codes["reverse"]      =  esc_seq + "07m"
codes["invisible"]    =  esc_seq + "08m"

codes["no-attr"]      = esc_seq + "22m"
codes["no-standout"]  = esc_seq + "23m"
codes["no-underline"] = esc_seq + "24m"
codes["no-blink"]     = esc_seq + "25m"
codes["no-overline"]  = esc_seq + "26m"
codes["no-reverse"]   = esc_seq + "27m"

codes["bg_black"]      = esc_seq + "40m"
codes["bg_darkred"]    = esc_seq + "41m"
codes["bg_darkgreen"]  = esc_seq + "42m"
codes["bg_brown"]      = esc_seq + "43m"
codes["bg_darkblue"]   = esc_seq + "44m"
codes["bg_purple"]     = esc_seq + "45m"
codes["bg_teal"]       = esc_seq + "46m"
codes["bg_lightgray"]  = esc_seq + "47m"
codes["bg_default"]    = esc_seq + "49m"
codes["bg_darkyellow"] = codes["bg_brown"]

def color(fg, bg="default", attr=["normal"]):
    mystr = codes[fg]
    for x in [bg]+attr:
        mystr += codes[x]
    return mystr

ansi_codes = []
for x in range(30, 38):
    ansi_codes.append("%im" % x)
    ansi_codes.append("%i;01m" % x)

rgb_ansi_colors = ['0x000000', '0x555555', '0xAA0000', '0xFF5555', '0x00AA00',
    '0x55FF55', '0xAA5500', '0xFFFF55', '0x0000AA', '0x5555FF', '0xAA00AA',
    '0xFF55FF', '0x00AAAA', '0x55FFFF', '0xAAAAAA', '0xFFFFFF']

for x in range(len(rgb_ansi_colors)):
    codes[rgb_ansi_colors[x]] = esc_seq + ansi_codes[x]
del x

codes["black"]     = codes["0x000000"]
codes["darkgray"]  = codes["0x555555"]

codes["red"]       = codes["0xFF5555"]
codes["darkred"]   = codes["0xAA0000"]

codes["green"]     = codes["0x55FF55"]
codes["darkgreen"] = codes["0x00AA00"]

codes["yellow"]    = codes["0xFFFF55"]
codes["brown"]     = codes["0xAA5500"]

codes["blue"]      = codes["0x5555FF"]
codes["darkblue"]  = codes["0x0000AA"]

codes["fuchsia"]   = codes["0xFF55FF"]
codes["purple"]    = codes["0xAA00AA"]

codes["turquoise"] = codes["0x55FFFF"]
codes["teal"]      = codes["0x00AAAA"]

codes["white"]     = codes["0xFFFFFF"]
codes["lightgray"] = codes["0xAAAAAA"]

codes["darkteal"]   = codes["turquoise"]
# Some terminals have darkyellow instead of brown.
codes["0xAAAA00"]   = codes["brown"]
codes["darkyellow"] = codes["0xAAAA00"]

# Colors from /etc/init.d/functions.sh
_styles["NORMAL"]     = ( "normal", )
_styles["GOOD"]       = ( "green", )
_styles["WARN"]       = ( "yellow", )
_styles["BAD"]        = ( "red", )
_styles["HILITE"]     = ( "teal", )
_styles["BRACKET"]    = ( "blue", )

def style_to_ansi_code(style):
    """
    @param style: A style name
    @type style: String
    @rtype: String
    @return: A string containing one or more ansi escape codes that are
        used to render the given style.
    """
    ret = ""
    for attr_name in _styles[style]:
        # allow stuff that has found it's way through ansi_code_pattern
        ret += codes.get(attr_name, attr_name)
    return ret

def colorize(color_key, text):
    if color_key in codes:
        return codes[color_key] + text + codes["reset"]
    elif color_key in _styles:
        return style_to_ansi_code(color_key) + text + codes["reset"]
    else:
        return text

class BoxConsole():
    """
    A class that performs fancy terminal formatting for status and informational
    messages built upon the logging module.
    """
    def __init__(self, opts, name):
        self.name = name
        self.opts = opts
        self.logger = logging.getLogger(name)

        self.level = logging.DEBUG if self.opts.verbose else logging.INFO
        self.logger.setLevel(self.level)

        # create console handler
        ch = ColorizingStreamHandler()
        ch.setLevel(self.level)
        # create formatter and add it to the handlers
        #ch.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(ch)

        # create file handler
        if self.opts.log:
            logfile = os.path.join(BASEDIR, 'box-sync.log')
            create_file(logfile)
            fh = logging.FileHandler(logfile)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'))
            self.logger.addHandler(fh)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, lvl, msg):
        self.logger.log(lvl, msg)

    def countdown(self, secs=5, doing="Starting"):
        """ This method is based on Portage's _emerge.countdown
        Copyright 1999-2009 Gentoo Foundation"""
        if secs:
            print("Waiting",secs,"seconds before starting (Control-C to abort)...")
            print(doing+" in: ", end=' ')
            ticks=list(range(secs))
            ticks.reverse()
            for sec in ticks:
                sys.stdout.write(colorize("red", str(sec+1)+" "))
                sys.stdout.flush()
                time.sleep(1)
            print()
