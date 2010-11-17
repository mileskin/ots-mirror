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

"""Unit tests for ots.worker.responseclient"""
import unittest

from pickle import dumps, loads

from ots.common.dto.environment import Environment 

from ots.worker.responseclient import ResponseClient

class ChannelStub(object):

    def __init__(self):
        self.close_called = False
        self.msg = None
        self.exchange = None
        self.routing_key = None

    def close(self):
        self.close_called = True
    def basic_publish(self,
                      msg,
                      mandatory,
                      exchange,
                      routing_key):
        self.msg = msg
        self.exchange = exchange
        self.routing_key = routing_key

    

class ConnectionStub(object):

    def __init__(self):
        self.close_called = False

    def close(self):
        self.close_called = True

class TestResponseClient(unittest.TestCase):
    """Unittests for ResponseClient class"""
    def setUp(self):
        self.testrun_id = 666
       
        self.client = ResponseClient("localhost", 666)
        self.conn = ConnectionStub()
        self.channel = ChannelStub()
        self.client.conn = self.conn
        self.client.channel = self.channel
    
    def tearDown(self):
        pass

    def test_init(self):
        self.assertEquals(self.client.testrun_id, self.testrun_id)
        
    def test_predefined_response_queue(self):
        queue = "test_queue1"
        another_client = ResponseClient("localhost", 666, queue)
        self.assertEquals(another_client.response_queue, queue)

    def test_close(self):
        del self.client
        self.assertTrue(self.conn.close_called)
        self.assertTrue(self.channel.close_called)

#     def test_set_state(self):
#         state = "FLASHING"
#         status_info = "flashing content image"
#         self.client.set_state(state, status_info)
#         msg = self.channel.msg
#         status = loads(msg.body)
#         self.assertEquals(status.state, state)
#         self.assertEquals(status.status_info, status_info)


    def test_set_error(self):
        error_info = "Flashing failed"
        error_code = "666"
        self.client.set_error(error_info, error_code)
        msg = self.channel.msg
        self.assertTrue(msg)
        exc = loads(msg.body)
        self.assertEquals(exc.strerror, error_info)
        self.assertEquals(exc.errno, error_code)


    def test_add_executed_packages(self):
        environment = "Flashing failed"
        packages = ['pkg1-tests', 'pkg2-tests']
        self.client.add_executed_packages(environment, packages)
        msg = self.channel.msg
        self.assertTrue(msg)
        executed_pkgs = loads(msg.body)
        self.assertEquals(executed_pkgs.environments[0], environment)
        self.assertEquals(executed_pkgs.packages(environment), packages)

    def test_add_result(self):
        filename = "result.xml"
        file_content = "<xm>foo</xml>"
        origin = "localhost"
        test_package = "dummy-tests"
        environment = "hardware"

        self.client.add_result(filename,
                               file_content,
                               origin, 
                               test_package,
                               environment)

        msg = self.channel.msg
        self.assertTrue(msg)
        result = loads(msg.body)
        self.assertEquals(result.results_xml.name, filename)
        self.assertEquals(result.results_xml.read(), file_content)
        self.assertEquals(result.hostname, origin)
        self.assertEquals(result.package, test_package)
        self.assertEquals(result.environment, Environment(environment))
        


if __name__ == '__main__':
    unittest.main()
    
    
