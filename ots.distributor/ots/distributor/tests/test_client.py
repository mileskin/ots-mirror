# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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
import time 
import unittest 

from ots.distributor.client import Client, client_factory, WAITING_END, \
    OtsGlobalTimeoutError

class ChannelStub(object):
   
    def __init__(self,client):
        self.client = client
        self.timesrun = 0

    def wait(self):
        print "sleep 2"
        time.sleep(2)
        print "Calling back on_message"
        self.client._on_message(None)

class TestClient(unittest.TestCase):

    def test_config(self):
        dirname = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        config_file = os.path.join(dirname, "config.ini")
        client = client_factory("foo", 1, config_file, "")
        self.assertEquals('guest', client._username) 
        self.assertEquals('foo', client._services_exchange) 
        self.assertEquals('foo', client._routing_key) 
        self.assertEquals('/', client._vhost)
        self.assertEquals('localhost', client._host) 
        self.assertEquals(1, client._timeout) 
        self.assertEquals('guest', client._password) 
        self.assertEquals(5672, client._port)

    #FIXME: Testing whether the process timesout or not
    #
    #The following unittests were written to mitigate the risk of  
    #adding functionality to an overdue release. 
    #Proper unittesting of `Client` is tricky (Stateful + Asynchronous)  
    #    
    #The following tests are poor in that the methods that they 
    #claim to test are not strictly tested as an independent unit of code
   
    def test_start_does_timeout(self):
        client = Client("username", "password", "host", "vhost", 
                        "services_exchange", "port", "routing_key", 
                         1, "testrun_id")
        
        client._channel = ChannelStub(client)
        client._bulk_out_timeout = lambda: client._timeout
        self.assertRaises(OtsGlobalTimeoutError, client._start)

    def test_start_doesnt_timeout(self):
        client = Client("username", "password", "host", "vhost", 
                        "services_exchange", "port", "routing_key", 
                         3, "testrun_id")
        client._channel = ChannelStub(client)
        client._bulk_out_timeout = lambda: client._timeout
        self.assertTrue(client._start())


if __name__ == "__main__":
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    unittest.main() 
