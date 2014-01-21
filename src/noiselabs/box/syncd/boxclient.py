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

import time
import webbrowser

from box import start_authenticate_v2, finish_authenticate_v2
from tornado.httpserver import HTTPServer


class AuthServer(object):
    """

    """
    def __init__(self, ioloop):
        self.http_server = HTTPServer(self.handle_request)
        self.ioloop = ioloop

    def handle_request(self, request):
        if 'state' in request.query_arguments and request.query_arguments['state'] == 'granted' \
            and 'code' in request.query_arguments:
            code = request.query_arguments['code']
            print(code)
        else:
            print('Code not provided')


        message = "You requested %s\n" % request.uri
        request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s" % (
                     len(message), message))
        request.finish()

    def start(self):
        self.http_server.listen(8888)

    def stop(self):
        self.http_server.stop()

class BoxClient(object):
    """

    """

    def __init__(self, ioloop, cfg, bc):
        self.ioloop = ioloop
        self.cfg = cfg
        self.bc = bc

        auth_server = AuthServer(ioloop)
        auth_server.start()

    def authenticate(self):
        if not self.cfg.get('authorization_code'):
            self.bc.info('Authenticating with Box.com, please wait...')
            url = start_authenticate_v2(self.cfg.get('api_key'), state='granted', redirect_uri=self.cfg.get('redirect_uri'))
            self.bc.info('We are opening a new browser tab to complete the authentication process, please follow the steps as shown.')
            time.sleep(2)
            webbrowser.open_new_tab(url)
