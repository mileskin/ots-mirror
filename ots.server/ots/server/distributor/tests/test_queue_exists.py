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

"""
Prerequisits: RabbitMQ on localhost with a `foo` queue
"""

import unittest

from amqplib import client_0_8 as amqp

from ots.server.distributor.queue_exists import queue_exists 

class TestQueueExists(unittest.TestCase):

    def setUp(self):
        self.host = "localhost"
        self.port = 5672
        self.user_id = "guest"
        self.password = "guest"
        self.virtual_host = "/"
        self.connection = amqp.Connection(
                                     host = ("%s:%s" %(self.host, self.port)),
                                     userid = self.user_id,
                                     password = self.password,
                                     virtual_host = self.virtual_host,
                                     insist = False)
        self.channel = self.connection.channel()
        self.channel.queue_declare("foo")
        
    def tearDown(self):
        self.channel.queue_delete(queue = "nokia", nowait=True)

    def test_queue_exists_positive(self):
        exists = queue_exists(self.host, self.user_id, self.password, 
                              self.virtual_host, "foo")
        self.assertTrue(exists)

    def test_queue_exists_negative(self):
        exists = queue_exists(self.host, self.user_id, self.password, 
                              self.virtual_host, "nokia")
        self.assertFalse(exists) 

if __name__ == "__main__":
    unittest.main() 
