#!/usr/bin/python -tt

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

import unittest
from ots.common.routing.routing import get_queues, get_routing_key

class TestRouting(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass    

    def test_get_queues_device_group_only(self):

        properties = dict()
        properties["devicegroup"] = "test"
        queues = get_queues(properties)
        self.assertEquals(queues, ["test"])
        
    def test_get_queues_device_group_and_name(self):
        properties = dict()
        properties["devicegroup"] = "test"
        properties["devicename"] = "testname"
        queues = get_queues(properties)
        self.assertEquals(queues, ["test.testname", "test"])
        
    def test_get_queues_device_group_name_and_id(self):
        properties = dict()
        properties["devicegroup"] = "test"
        properties["devicename"] = "testname"
        properties["deviceid"] = "hw1"
        queues = get_queues(properties)
        self.assertEquals(queues, [ "test.testname.hw1", "test.testname", "test"])
        

    def test_get_routing_key_device_group_only(self):

        properties = dict()
        properties["devicegroup"] = "test"
        routing_key = get_routing_key(properties)
        self.assertEquals(routing_key, "test")
        
    def test_get_routing_key_device_group_and_name(self):
        properties = dict()
        properties["devicegroup"] = "test"
        properties["devicename"] = "testname"
        routing_key = get_routing_key(properties)
        self.assertEquals(routing_key, "test.testname")
        
    def test_get_routing_key_device_group_name_and_id(self):
        properties = dict()
        properties["devicegroup"] = "test"
        properties["devicename"] = "testname"
        properties["deviceid"] = "hw1"
        routing_key = get_routing_key(properties)
        self.assertEquals(routing_key, "test.testname.hw1")
        
    def test_get_routing_key_no_properties(self):
        properties = dict()
        self.assertRaises(Exception, get_routing_key, properties)



        
            

if __name__ == '__main__':
    unittest.main()
