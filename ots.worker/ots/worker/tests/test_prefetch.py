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

"""
Tests client only fetches one item from the queue at a time
"""
import unittest
import time

from ots.worker.worker import Worker
from ots.worker.client import Client
from ots.worker.tests.utils import Utils, queue_size

class TestPrefetch(unittest.TestCase):

    def setUp(self):
        self.util = Utils()
        self.util.lazy_set()
        self.server = self.util.spawn_server(no_respond=True)
        self.server._setup()
        self.client = self.util.spawn_client()
        self.client.queue_purge(self.util.config('queue'))

    def test_prefetch(self):
        conf = self.util.config #alias
        connection = self.client._connection     

        def check_queue_size(*args,**kwargs):
            _queue_size = queue_size(connection, conf('queue'))
            print "Queue size:", _queue_size 
            self.assertEquals(self.expected_size, _queue_size)
        
        self.server._start_process = check_queue_size

    
        pre_queue_size = queue_size(connection ,
                                    conf('queue'))
       
        self.client.send_message(conf('services_exchange'), 
                                 conf('queue'),
                                 dict(command=['foo'],
                                      timeout=1,
                                      response_queue=''))
        self.client.send_message(conf('services_exchange'), 
                                 conf('queue'),
                                 dict(command=['bar'],
                                      timeout=1,
                                      response_queue=''))
        post_client_queue_size = queue_size(connection,
                                            self.util.config('queue'))
       
        self.assertEqual(2 + pre_queue_size, post_client_queue_size)
        
        self.expected_size = 1
        self.server._connection.wait()
        self.expected_size = 0
        self.server._connection.wait()
        self.client.queue_purge(self.util.config('queue'))
        self.assertEquals(0, queue_size(connection, self.util.config('queue')))
        self.server.stop()

if __name__ == '__main__':
    unittest.main()
