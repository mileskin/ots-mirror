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
Tests process timeout is effective
"""
import unittest
import time

from ots.worker.worker import Worker
from ots.worker.client import Client
from ots.worker.tests.utils import Utils, queue_size

class TestTimeout(unittest.TestCase):

    def setUp(self):
        self.util = Utils()
        self.util.lazy_set()

    def testTimeout(self):
        worker = self.util.spawn_server(no_respond=True)
        client = self.util.spawn_client()
        connection = client._connection
        pre_queue_size = queue_size(connection,
                                    self.util.config('queue'))

        start_time = time.clock()
        # Send two messages, one of which is quit
        conf = self.util.config #alias
        client.send_message(conf('services_exchange'), conf('queue'),
                   dict(command=['sleep 3'],timeout=1,response_queue=''))
        client.send_message(conf('services_exchange'), conf('queue'),
                   dict(command=['quit'],timeout=1,response_queue=''))
        post_client_queue_size = queue_size(connection,
                                            self.util.config('queue'))
        print "before: " + str(pre_queue_size)
        print "after: " + str(post_client_queue_size)

        # Sanity check
        self.assertEqual(
            post_client_queue_size,
            2 + pre_queue_size,
            "Queue size increased by two"
        )
        worker.start()
        # Take the time
        end_time = time.clock()
        #Get the queue size again
        client.connect()
        post_worker_queue_size = queue_size(connection,
                                            self.util.config('queue'))
        # Sanity check
        self.assertEqual(
            pre_queue_size, post_worker_queue_size,
            "queue size restored to original: (%s,%s)" % ( pre_queue_size, post_worker_queue_size)
        )
        # Check it didn't wait the whole time
        self.assertTrue((end_time - start_time) < 3,
            "Process was killed before finishing")
        #Empty it
        client.queue_purge(self.util.config('queue'))
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
