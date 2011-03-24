#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

import unittest
import os

from ots.worker.conductor.chroot import Chroot
from ots.worker.conductor.executor import TestRunData

FAKE_ROOTSTRAP_PATH = "testdata/fake-rootstrap.tar.gz"


class Options(object):
    def __init__(self):
        self.testrun_id = None #standalone
        self.image_url = "xxx/yyy.bin"
        self.content_image_url = "xxx/yyy"
        self.content_image_path = None
        self.packages = ""
        self.host = False
        self.dontflash = False
        self.filter_options = ""
        self.verbose = False
        self.otsserver = None
        self.flasher_url = None
        self.bootmode = None
        self.rootstrap_url = None
        self.chrooted = None
        self.rootstrap_path = None


class TestChroot(unittest.TestCase):

    def setUp(self):
        self.testrun = TestRunData(Options(),
                                   config = _conductor_config_simple())
        self.testrun.is_chrooted = True
        self.testrun.rootstrap_path = self._fake_rootstrap_path()
        self.chroot = Chroot(self.testrun)
        
    def _fake_rootstrap_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + \
            os.sep + FAKE_ROOTSTRAP_PATH

    def tearDown(self):
        pass

    def test_setup_and_remove_chroot(self):
        self.chroot.prepare()
        chroot_path = self.chroot.path
        self.assertTrue(os.path.isdir(chroot_path))

        hosts_file = chroot_path + os.sep + os.sep.join(['etc', 'hosts'])
        self.assertTrue(os.path.isfile(hosts_file))

        resolv_conf = chroot_path + os.sep + os.sep.join(['etc', 'resolv.conf'])
        self.assertTrue(os.path.isfile(resolv_conf))

        f = file(hosts_file, 'rb')
        hosts = f.read()
        f.close()
        self.assertTrue('testdevice' in hosts) 

        self.chroot.cleanup()
        self.assertFalse(os.path.isdir(chroot_path))

    def test_home_dir_creation(self):
        self.chroot.prepare()
        chroot_path = self.chroot.path
        home_path = os.environ['HOME']
        self.assertTrue(os.path.isdir(chroot_path + os.sep + home_path))

        self.chroot.cleanup()
        self.assertFalse(os.path.isdir(chroot_path))


def _conductor_config_simple(config_file = "", default_file = ""):
    config = dict()
    config['device_packaging'] = 'debian'
    config['pre_test_info_commands_debian'] = ['ls', 'echo "jouni"']
    config['pre_test_info_commands_rpm'] = ['ls', 'echo "jouni"']
    config['pre_test_info_commands'] = ['ls', 'echo "testing ...."', 'ls -al']
    config['files_fetched_after_testing'] = ['xxx']
    config['tmp_path'] = "/tmp/"
    return config


if __name__ == '__main__':
    unittest.main()
