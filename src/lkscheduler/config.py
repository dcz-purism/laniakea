# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 Matthias Klumpp <matthias@tenstral.net>
#
# SPDX-License-Identifier: LGPL-3.0+

import os
import shutil

import tomlkit

import laniakea.typing as T
from laniakea.localconfig import get_config_file


class SchedulerConfig:
    """Configuration for the maintenance scheduler daemon."""

    instance = None

    class __SchedulerConfig:
        def __init__(self, fname=None):
            if not fname:
                fname = get_config_file('scheduler.toml')
            self.fname = fname

            cdata = {}
            if fname and os.path.isfile(fname):
                with open(fname) as toml_file:
                    cdata = tomlkit.load(toml_file)

            cintervals = cdata.get('Intervals', {})
            self._intervals_min = {}

            # run Rubicon every 15min by default
            self._intervals_min['rubicon'] = cintervals.get('rubicon', 15)

            # publish repos all 4h by default
            self._intervals_min['publish-repos'] = cintervals.get('publish-repos', 4 * 60)

            # find executables
            my_dir = os.path.dirname(os.path.realpath(__file__))
            self._lk_archive_exe = os.path.normpath(os.path.join(my_dir, '..', 'lkarchive', 'lk-archive.py'))
            if not os.path.isfile(self._lk_archive_exe):
                self._lk_archive_exe = shutil.which('lk-archive')
            if not self._lk_archive_exe:
                raise ValueError('Unable to find `lk-archive` binary. Check your Laniakea installation!')

            self._rubicon_exe = os.path.normpath(os.path.join(my_dir, '..', 'rubicon', 'rubicon'))
            if not os.path.isfile(self._rubicon_exe):
                self._rubicon_exe = shutil.which('rubicon')
            if not self._rubicon_exe:
                raise ValueError('Unable to find `rubicon` binary. Check your Laniakea installation!')

        @property
        def lk_archive_exe(self) -> T.PathUnion:
            """Executable path for lk-archive"""
            return self._lk_archive_exe

        @property
        def rubicon_exe(self) -> T.PathUnion:
            """Executable path for rubicon"""
            return self._rubicon_exe

        @property
        def intervals_min(self) -> T.Dict[str, T.Optional[int]]:
            """Defined intervals to run the respective jobs at"""
            return self._intervals_min

    def __init__(self, fname=None):
        if not SchedulerConfig.instance:
            SchedulerConfig.instance = SchedulerConfig.__SchedulerConfig(fname)

    def __getattr__(self, name):
        return getattr(self.instance, name)
