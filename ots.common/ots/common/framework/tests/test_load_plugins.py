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

"""
For this test you need to build the egg
in the subdirectory test_plugin

{{{
$sudo python setup.py bdist_egg
}}}
"""

import os

import unittest

from pkg_resources import working_set

from ots.common.framework.load_plugins import plugins_iter 

class TestFindPlugins(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = os.path.join(dirname, "test_plugin",
                                  "ots.test_plugin", "dist")
    def test_plugins_iter(self):
        test_plugins = list(plugins_iter(self.plugin_dir, "TestPlugin"))
        self.assertEquals(1, len(test_plugins))
        self.assertEquals("ots.test_plugin.test_plugin", 
                          test_plugins[0].__name__)
        

if __name__ == "__main__":
    unittest.main()
