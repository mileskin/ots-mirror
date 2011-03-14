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

from ots.server.hub.publishers import Publishers

class TestPublishers(unittest.TestCase):

    def test_delegators_iter_setter(self):
        publishers = Publishers(111, 222, "sw_product" , "image")
        class PublisherStub:
            called = False
            def set_expected_packages(self, packages):
                self.called = True
        stub_1 = PublisherStub()
        stub_2 = PublisherStub()
        publishers._publishers = [stub_1, stub_2]
        self.assertFalse(stub_1.called)
        self.assertFalse(stub_2.called)
        publishers.set_expected_packages("foo")
        self.assertTrue(stub_1.called)
        self.assertTrue(stub_2.called)
        
    def test_delegator_iter_getter(self):
        publishers = Publishers(111, 222, "sw_product" , "image")
        class PublisherStub1:
            def get_uris(self):
                return {"Parrot" : "Norwegian Blue", "Cheese" : "Wensleydale"}
        stub_1 = PublisherStub1()
        class PublisherStub2:
            def get_uris(self):
                return {"Song" : "Lumberjack", "Walk" : "Funny"}
        stub_2 = PublisherStub2()
        publishers._publishers = [stub_1, stub_2]
        expected = {'Cheese': 'Wensleydale', 
                    'Song': 'Lumberjack', 
                    'Parrot': 'Norwegian Blue', 
                    'Walk': 'Funny'}
        self.assertEquals(expected, publishers.get_uris())
       
    def test_exception_policy(self):
        publishers = Publishers(111, 222, "sw_product" , "image")
        class MyException(Exception):
            pass
        class PublisherStub:
            def set_expected_packages(self, *args):
                raise MyException
        publishers._publishers = [PublisherStub()]
        publishers.set_expected_packages(None)
        publishers.SWALLOW_EXCEPTIONS = False
        self.assertRaises(MyException, publishers.set_expected_packages, None)
        

if __name__ == "__main__":
    unittest.main()
