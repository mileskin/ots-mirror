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

from ots.server.hub.sandbox import sandbox

class Stub(object):

    @sandbox(7)
    def my_func(self, *args):
        return 4

    @sandbox(8)
    def exception_func(self):
        raise ValueError


class TestSandbox(unittest.TestCase):

    def setUp(self):
        self.stub = Stub()

    def test_non_invasive(self):
        self.assertEquals(4, self.stub.my_func(4,5))

    def test_exception_is_on(self):
        sandbox.is_on = True
        self.assertEquals(8, self.stub.exception_func())
        
    #FIXME unexpected behaviour for class scope variables
    #under nose these tests work in the CL

        #self.assertTrue(isinstance(sandbox.exc_info[1], ValueError))

    #def test_exception_is_off(self):
    #    sandbox.is_on = False
    #    self.assertRaises(ValueError, self.stub.exception_func)

if __name__ == "__main__":
    unittest.main()
