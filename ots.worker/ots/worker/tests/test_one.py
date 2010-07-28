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
Tests one process is receiving things

Need to have RabbitMQ running on the machine
"""
import unittest
from time import sleep

from ots.worker.worker import Worker
from ots.worker.client import Client
from ots.worker.tests.utils import Utils, queue_size

class TestOne(unittest.TestCase):

    def setUp(self):
        self.util = Utils()
        self.util.lazy_set()

    def testOne(self):
        worker = self.util.spawn_server(no_respond=True)
        worker._declare()
        client = self.util.spawn_client()
        conf = self.util.config #alias
        client.queue_purge(conf('queue'))
        connection = client._connection
        original_queue_size = queue_size(connection, 
                                         self.util.config('queue'))
        print "original: " + str(original_queue_size)
        # Send two messages, one of which is quit
        client.send_message(conf('services_exchange'), conf('queue'),
                            dict(command=['ls -la'],timeout=30,response_queue=''))
        client.send_message(conf('services_exchange'), conf('queue'),
                            dict(command=['quit'],timeout=30,response_queue=''))
        
        print "after: " + str(queue_size(connection,
                                         self.util.config('queue')))
        # Two messages shoved in the queue
        self.assertEqual(
            queue_size(connection, self.util.config('queue')),2 + original_queue_size,
            "Queue size increased by two"
        )
        
        worker._consume()
        worker._work_loop()
        client.connect()
        new_queue_size = queue_size(connection, self.util.config('queue'))
        # And received
        self.assertEqual(
            new_queue_size, original_queue_size,
            "Queue size restored to original: (%s, %s)" %(new_queue_size,original_queue_size)
        )
        client.queue_purge(queue=self.util.config('queue'))
        client._connection.cleanup()

if __name__ == '__main__':
    import logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)
    unittest.main()
