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
Tests queue and message durability
"""
import unittest
from time import sleep

from ots.worker.tests.utils import Utils, queue_size

class TestDurability(unittest.TestCase):

    def setUp(self):
        self.util = Utils()
        self.util.lazy_set()

    def testDurability(self):
        worker = self.util.spawn_server(no_respond=True)
        worker._declare()
        client = self.util.spawn_client()
        # Send two messages, one of which is quit
        conf = self.util.config #alias
        client.queue_purge(conf('queue'))
        client.send_message(conf('services_exchange'), conf('queue'),
                            dict(command='ls -la',timeout=30,response_queue=''))
        client.send_message(conf('services_exchange'), conf('queue'),
                            dict(command='quit',timeout=30,response_queue=''))
        # Two messages shoved in the queue
        connection = client._connection
        pre_queue_size = queue_size(connection, self.util.config('queue'))
        print 'pre_queue_size: ' + str(pre_queue_size)
        #Stop and restart rabbitMQ
        self.util.stop_rabbitmq()
        self.util.start_rabbitmq()
        client.connect()
        worker._declare()
        post_queue_size = queue_size(connection, self.util.config('queue'))
        print "post_queue_size: " + str(post_queue_size)
        # Check the queue. This verifies durability of queue AND messages
        self.assertEqual(
            pre_queue_size, post_queue_size,
            "Queue size remains the same: (%s,%s)" % ( pre_queue_size, post_queue_size),
        )
        #Empty it
        client.queue_purge(self.util.config('queue'))
        worker.stop()
        client._connection.cleanup()

if __name__ == '__main__':
     unittest.main()
