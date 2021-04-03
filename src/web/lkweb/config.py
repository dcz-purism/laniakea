# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2019 Matthias Klumpp <matthias@tenstral.net>
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

# Instance folder path
INSTANCE_FOLDER_PATH = '/var/lib/laniakea-web/'


class BaseConfig:

    PROJECT = 'Laniakea Web'
    BUG_REPORT_URL = 'https://github.com/lkorigin/laniakea/issues'

    LOG_STORAGE_URL = '/raw/logs'  # web URL where raw logs are stored by Rubicon

    #
    # Caching behavior
    #
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Get app root path, also can use flask.root_path.
    # ../../config.py
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'

    LOG_FOLDER = os.path.join(INSTANCE_FOLDER_PATH, 'logs')

    THEME = 'default'


class DefaultConfig(BaseConfig):

    DEBUG = False
    CACHE_TYPE = 'simple'


class DebugConfig(BaseConfig):

    DEBUG = True
    CACHE_TYPE = 'null'
