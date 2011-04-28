# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

"""Conductor plug-in unit tests"""

import unittest

from ots.worker.conductor.conductor_plugins import ConductorPlugins
from ots.worker.conductor.executor import TestRunData
from ots.worker.conductor.tests.test_conductor import Options


class TestConductorPlugins(unittest.TestCase):
    """Tests for ConductorPlugins class"""
    def test_delegators_iter_setter(self):
        class ConductorPluginStub:
            called = False
            def set_result_dir(self, target):
                self.called = True

        tr_data = TestRunData(Options(), {})
        plugins = ConductorPlugins(tr_data)
        stub_1 = ConductorPluginStub()
        stub_2 = ConductorPluginStub()
        plugins._plugins = [stub_1, stub_2]
        self.assertFalse(stub_1.called)
        self.assertFalse(stub_2.called)
        plugins.set_result_dir("/foo/bar")
        self.assertTrue(stub_1.called)
        self.assertTrue(stub_2.called)
        
    def test_delegator_iter_getter(self):
        class ConductorPluginStub1:
            def get_result_files(self):
                return ['/foo/file1']
        class ConductorPluginStub2:
            def get_result_files(self):
                return ['/foo/file2', '/bar/file3']

        tr_data = TestRunData(Options(), {})
        plugins = ConductorPlugins(tr_data)
        stub_1 = ConductorPluginStub1()
        stub_2 = ConductorPluginStub2()
        plugins._plugins = [stub_1, stub_2]
        expected = ['/foo/file1', '/foo/file2', '/bar/file3']
        self.assertEquals(expected, plugins.get_result_files())

    def test_exception_policy(self):
        class MyException(Exception):
            pass
        class ConductorPluginStub:
            def set_result_dir(self, *args):
                raise MyException

        tr_data = TestRunData(Options(), {})
        plugins = ConductorPlugins(tr_data)
        plugins._plugins = [ConductorPluginStub()]
        plugins.set_result_dir(None)
        plugins.SWALLOW_EXCEPTIONS = False
        self.assertRaises(MyException, plugins.set_result_dir, None)


if __name__ == "__main__":
    unittest.main()
