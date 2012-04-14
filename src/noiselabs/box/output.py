#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of box-linux-sync.
#
# Copyright (C) 2012 Vítor Brandão <noisebleed@noiselabs.org>
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

import curses
import os
import time
import sys
import types
from os.path import basename

################################################################################
##
## Color codes (taken from Portage)
##
################################################################################

codes = {}
"""Maps attribute name to ansi code."""

esc_seq = '\x1b['

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

# Available colours
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


class CommandLineInterface():
    """ 
    Performs fancy terminal formatting for status and informational messages.
    """ 
    
    def __init__(self, colours=True):
        self.use_colour = colours
        self.cols = 0
        self.rows, self.cols = self.get_console_size()

    def _write(self, message='', endl=False, rewrite=False, subl=0, bullet=True, bullet_symbol='*', bullet_color=False, text_color=False):
        if rewrite:
            sys.stdout.write("\r")
        indentation = ' ' * 2 * subl
        if type(message) not in types.StringTypes:
            message = str(message)
        for i in message.split('\n'):
            if bullet:
                if bullet_color:
                    sys.stdout.write(indentation + self.colourize("%s " % bullet_symbol, bullet_color))
                else:
                    sys.stdout.write(indentation + bullet_symbol + ' ')
            if text_color:
                sys.stdout.write(self.colourize(i, text_color))
            else:
                sys.stdout.write(i)
            if endl:
                sys.stdout.write("\n")
            sys.stdout.flush()

    def clear_line(self):
        sys.stdout.write("\r" + ' '*self.cols + "\r")
        sys.stdout.flush()
   
    # Helper functions
    def colourize(self, text, colour):
        if self.use_colour:
            return codes[colour] + text + codes['reset']
        return text
   
    def noColour(self):
        "Turn off colourization"
        self.use_colours = False
   
    # Output functions 
    def notice(self, message):
        print message
    
    def info(self, message, subl=0, bullet_symbol="*", color="green", rewrite=False):
        if rewrite:
            sys.stdout.write("\r")
        indentation = " " * 2 * subl
        if type(message) not in types.StringTypes:
            message = str(message)
            
        for i in message.split('\n'):
            if not color: 
                print indentation + bullet_symbol + " " + message
            else:
                print indentation + self.colourize('%s ' % bullet_symbol, color) + i
    
    def status(self, message, bullet=True, endl=True, subl=0, bullet_symbol="*", rewrite=False):
        if rewrite:
            sys.stdout.write("\r")
        indentation = " " * 2 * subl
        if type(message) not in types.StringTypes:
            message = str(message)
        for i in message.split('\n'):
            if bullet:
                sys.stdout.write(indentation + self.colourize("%s " % bullet_symbol, "green"))
            sys.stdout.write(i)
            if endl:
                sys.stdout.write("\n")
            sys.stdout.flush()
    
    def item(self, message='', endl=True, rewrite=False, subl=1, bullet=True,
             bullet_symbol='-', bullet_color=False, text_color=False):
        return self._write(message=message, endl=endl, rewrite=rewrite,
                           subl=subl, bullet=bullet, bullet_symbol=bullet_symbol,
                           bullet_color=bullet_color, text_color=text_color)
    
    def warn(self, message, endl=True, rewrite=False):
        if rewrite:
            sys.stdout.write("\r")
        if type(message) not in types.StringTypes:
            message = str(message)
        for i in message.split('\n'):
            sys.stdout.write(self.colourize('* ', "yellow") + i)
            if endl:
                sys.stdout.write("\n")
            sys.stdout.flush()
    
    def error(self, message, endl=True, die=False, subl=0, rewrite=False):
        if rewrite:
            sys.stdout.write("\r")
        indentation = " " * 2 * subl
        if type(message) not in types.StringTypes:
            message = str(message)
        for i in message.split('\n'):
            sys.stdout.write(indentation + self.colourize('* ', "red") + i)
            if endl:
                sys.stdout.write("\n")
        if die:
            print indentation + self.colourize('* ', "red") + "/me quits."
            sys.exit(0)
    
    def die(self, message=False, subl=0, rewrite=False):
        if rewrite:
            sys.stdout.write("\r")
        indentation = " " * 2 * subl
        if message != False:
            if type(message) not in types.StringTypes:
                message = str(message)
            for i in message.split('\n'):
                print indentation + self.colourize('* ', "red") + i
        print indentation + self.colourize('* ', "red") + "/me dies."
        sys.exit(1)
        
    def cmd(self, cmd, lf=False):
        if lf:
            print ""
        print ""
        print ">>> @ "+os.getcwd()
        print ">>> Executing "+self.colourize(cmd, 'turquoise')
        print ""
    
    def kvp(self, key, value, endl=True, rewrite=False):
        ''' Key-Value-Pair '''
        if rewrite:
            sys.stdout.write("\r")
            sys.stdout.flush()
        if type(key) not in types.StringTypes:
            key = str(key)
        if type(value) not in types.StringTypes:
            value = str(value)
        sys.stdout.write("  - " + self.colourize(key, "teal") + ": " + value)
        if endl:
            sys.stdout.write("\n")

    def ask(self, message, options=False):
        options = ' ['+','.join(options)+']' if options else ''
        return raw_input(self.colourize('* ', "darkyellow") + message + options+": ")
    
    def debug(self, message):
        print message      
    
    def countdown(self, message, seconds=5):
        CLI.warn(message)
        CLI.warn("Giving you %d seconds to cancel this: " % seconds, endl=False)
        i = seconds
        for j in range(0, i): 
            sys.stdout.write("%d.. " % (i-j))
            sys.stdout.flush() 
            time.sleep(1)
        print "Go.."
        
    def get_console_size(self, use_curses=False):
        if use_curses:
            rows, cols =  curses.initscr().getmaxyx()
            curses.endwin()
        else:
            rows, cols = os.popen('stty size', 'r').read().split()
        return int(rows), int(cols)
 