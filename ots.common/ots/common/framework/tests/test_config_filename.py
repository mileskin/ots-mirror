# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
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

import os

import unittest

from ots.common.framework.config_filename import config_filename

class TestConfigFilename(unittest.TestCase):

    def test_config_filename_1(self):
        self.assertEquals(['ots.common', 'ots', 'common', 'config.ini'],
                          config_filename().split("/")[-4:])

    def test_config_filename_2(self):
        dirname = os.path.split(os.path.split(
                os.path.dirname(os.path.abspath(__file__)))[0])[0]
        self.assertEquals(['ots.common', 'ots', 'common', 'config.ini'],
                        config_filename("config", dirname).split("/")[-4:])

if __name__ == "__main__":
    unittest.main()
