# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 Matthias Klumpp <matthias@tenstral.net>
#
# Licensed under the GNU Lesser General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the license, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os
import toml
from typing import Any
from laniakea import get_config_file


class MirkConfig():
    '''
    Local configuration for mIrk.
    '''

    host = None
    username = None
    password = None
    rooms: dict[str, dict[str, Any]] = {}

    def __init__(self):
        self._loaded = False

        # try to load default configuration
        self.load()

    def load_from_file(self, fname):

        cdata = {}
        if os.path.isfile(fname):
            with open(fname) as toml_file:
                cdata = toml.load(toml_file)

        self.host = cdata.get('Host', None)
        if not self.host:
            raise Exception('No "Host" entry in mIrk configuration: We need to know a Matrix server to connect to.')

        self.username = cdata.get('Username', None)
        if not self.username:
            raise Exception('No "Username" entry in mIrk configuration: We need to know a Matrix username to connect as.')

        self.password = cdata.get('Password', None)
        if not self.password:
            raise Exception('No "Password" entry in mIrk configuration: We need to know a password to log into Matrix.')

        self.rooms = cdata.get('Rooms', {})
        if not self.rooms:
            raise Exception('No "Rooms" entry in mIrk configuration: We need at least one registered room.')
        if type(self.rooms) is not dict:
            raise Exception('"Rooms" entry in mIrk configuration is no mapping: Needs to be a mapping of room names to settings.')

        self.allow_unsigned = cdata.get('AllowUnsigned', False)

        self.webview_url = cdata.get('WebViewUrl', '#')
        self.webswview_url = cdata.get('WebSWViewUrl', '#')

        self._loaded = True

    def load(self):
        fname = get_config_file('mirk.toml')
        if fname:
            self.load_from_file(fname)
        else:
            raise Exception('Unable to find Mirk configuration (usually in `/etc/laniakea/mirk.toml`')
