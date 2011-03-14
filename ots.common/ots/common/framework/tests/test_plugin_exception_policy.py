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

from __future__ import with_statement
import unittest
from ots.common.framework.plugin_exception_policy import plugin_exception_policy

class TestPluginExceptionPolicy(unittest.TestCase):

    def test_plugin_exception_policy_swallows(self):
        with plugin_exception_policy(True):
            raise Exception

    def test_plugin_exception_policy_raises(self):
        class MyException(Exception):
            pass
        def raises():
            with plugin_exception_policy(False):
                raise MyException
        self.assertRaises(MyException, raises)

if __name__ == "__main__":
    unittest.main()
