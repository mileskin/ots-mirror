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
from ots.common.routing.routing import get_queues

class TestRouting(unittest.TestCase):
    
    def setUp(self):
#        self.key_format = ["group","type", "build", "network"]
#        self.routing = routing.Routing(self.key_format)
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
        



        
    def _test_get_routing_key_with_valid_values(self):
        values = {}
        values["group"] = "group1"
        values["type"] = "type1"
        values["build"] = "build1"
        values["network"] = "true"
        
        expected_key = "%s.%s.%s.%s" % (values["group"], values["type"], values["build"], values["network"])
        
        key = self.routing.get_routing_key(values)
        self.assertEquals(key, expected_key)
        
        
    def _test_get_routing_key_with_no_values(self):
        values = {}
        
        expected_key = "dontcare.dontcare.dontcare.dontcare"
        
        key = self.routing.get_routing_key(values)
        self.assertEquals(key, expected_key)

    def _test_get_routing_key_with_some_values(self):
        values = {}
        values["group"] = "group1"
        values["network"] = "true"
        
        expected_key = "group1.dontcare.dontcare.true"
        
        key = self.routing.get_routing_key(values)
        self.assertEquals(key, expected_key)

    def _test_get_routing_key_with_some_values2(self):
        values = {}
        values["network"] = "true"
        
        expected_key = "dontcare.dontcare.dontcare.true"
        
        key = self.routing.get_routing_key(values)
        self.assertEquals(key, expected_key)
    
    def _test_get_routing_key_with_extra_values(self):
        values = {}
        values["group"] = "group1"
        values["asdfasdf"] = "asdfasdfasdf"
        values["type"] = "type1"
        values["build"] = "build1"
        values["network"] = "true"
        
        expected_key = "%s.%s.%s.%s" % (values["group"], values["type"], values["build"], values["network"])
        
        key = self.routing.get_routing_key(values)
        self.assertEquals(key, expected_key)
    

    def _test_get_list_of_queues_with_valid_values(self):
        values = {}
        values["group"] = "group1"
        values["type"] = "type1"
        values["build"] = "build1"
        values["network"] = "true"
        
        expected_queues = ["group1.type1.build1.true",
                           "group1.type1.build1.dontcare",
                           "group1.type1.dontcare.true",
                           "group1.type1.dontcare.dontcare",

                           "group1.dontcare.build1.true",
                           "group1.dontcare.build1.dontcare",
                           "group1.dontcare.dontcare.true",
                           "group1.dontcare.dontcare.dontcare",

                           "dontcare.type1.build1.true",
                           "dontcare.type1.build1.dontcare",
                           "dontcare.type1.dontcare.true",
                           "dontcare.type1.dontcare.dontcare",

                           "dontcare.dontcare.build1.true",
                           "dontcare.dontcare.build1.dontcare",
                           "dontcare.dontcare.dontcare.true",
                           "dontcare.dontcare.dontcare.dontcare",
                           ]
        
        queues = self.routing.get_list_of_queues(values)
        self._assert_exactly_same_values(expected_queues, queues)
        


    def _test_get_list_of_queues_with_extra_values(self):
        values = {}
        values["group"] = "group1"
        values["type"] = "type1"
        values["asdfasdf"] = "asdfasdf"
        values["build"] = "build1"
        values["network"] = "true"
        
        expected_queues = ["group1.type1.build1.true",
                           "group1.type1.build1.dontcare",
                           "group1.type1.dontcare.true",
                           "group1.type1.dontcare.dontcare",

                           "group1.dontcare.build1.true",
                           "group1.dontcare.build1.dontcare",
                           "group1.dontcare.dontcare.true",
                           "group1.dontcare.dontcare.dontcare",

                           "dontcare.type1.build1.true",
                           "dontcare.type1.build1.dontcare",
                           "dontcare.type1.dontcare.true",
                           "dontcare.type1.dontcare.dontcare",

                           "dontcare.dontcare.build1.true",
                           "dontcare.dontcare.build1.dontcare",
                           "dontcare.dontcare.dontcare.true",
                           "dontcare.dontcare.dontcare.dontcare",
                           ]
        
        queues = self.routing.get_list_of_queues(values)
        self._assert_exactly_same_values(expected_queues, queues)
        


    def _test_get_list_of_queues_with_missing_values(self):
        values = {}
        values["group"] = "group1"
        values["type"] = "type1"
        values["build"] = "build1"
        

        self.assertRaises(KeyError, self.routing.get_list_of_queues, values)

        

    def _assert_exactly_same_values(self, expected_queues, queues):
        """
        Checks that both lists have exactly same values. Order does
        not matter.
        """
        self.assertEquals(len(queues), len(expected_queues))        
        for queue in expected_queues:
            self.assertTrue(queue in queues, "queue %s not generated" % queue)
            

            

if __name__ == '__main__':
    unittest.main()
