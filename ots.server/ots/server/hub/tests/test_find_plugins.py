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

$sudo python setup.py bdist_egg
"""

import os

import unittest

from pkg_resources import working_set

from ots.server.hub.find_plugins import _find_plugins, activate_plugins

class TestFindPlugins(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = os.path.join(dirname, "test_plugin",
                                  "ots.test_plugin", "dist")

    def test_find_plugins(self):
        plugins = _find_plugins(self.plugin_dir)
        self.assertEquals(1, len(plugins))
        self.assertTrue(plugins[0].egg_name().startswith("ots.test_plugin"))

    def test_activate_plugins(self):
        activate_plugins(self.plugin_dir)
        module = __import__("ots.test_plugin")
        foo = list(working_set.iter_entry_points('foo'))[0].load()
        self.assertEquals(111, foo(111))

if __name__ == "__main__":
    unittest.main()
