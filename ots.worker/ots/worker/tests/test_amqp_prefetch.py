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
Effectively unittesting pyamqplib
A port of the txamqp prefetch test that is absent in pyamqplib
Note that a similar test also exists in the qpid source code 
"""

import unittest 
import signal

from amqplib.client_0_8 import Connection
from amqplib.client_0_8 import Message

from ots.worker.tests.utils import Utils

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

class TestPrefetch(unittest.TestCase):

    PREFETCH = 5

    def setUp(self):
        self.util = Utils()

        connect_args = {'ssl': False, 
                        'host': 'localhost', 
                        'password': 'guest', 
                        'userid': 'guest'}
        self.conn = Connection(**connect_args)
        self.ch = self.conn.channel()
        self._messages = []

    def _tearDown(self):
        self.ch.close()
        self.conn.close()
#         self.util.stop_rabbitmq()

    def _pull_messages(self, qname, channel):
        for i in range(self.PREFETCH):
            print "waiting..."    
            channel.wait()
        try:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(2)
            channel.wait()
            #should not get here!
            self.assertTrue(False)
        except Alarm:
            print "Timed out waiting for message"
        finally:
            channel.basic_ack(delivery_tag = self._messages[self.PREFETCH-1].delivery_tag, 
                              multiple = True)
                   
    def _message_handler(self, message):
        self._messages.append(message)
        
    def test_qos(self):
        channel = self.ch
        qname, junk, junk = channel.queue_declare(queue="test-prefetch-count",
                                                  exclusive = True)
       
        channel.basic_consume(queue = qname, 
                              callback = self._message_handler)

        channel.basic_qos(prefetch_size = 0,
                          prefetch_count = self.PREFETCH,
                          a_global = False)

        for i in range(1, self.PREFETCH*2+1):
            msg = Message("Message %d" % i,
                          content_type='text/plain',
                          application_headers={'foo': 7, 
                                               'bar': 'baz'})
            channel.basic_publish(msg,
                                  routing_key="test-prefetch-count")
                    
        self._pull_messages(qname, channel)
        self._pull_messages(qname, channel)
        messages = [m.body for m in self._messages]
        expected = ["Message %d"%i for i in range(1, self.PREFETCH*2+1)]
        self.assertEquals(set(expected), set(messages))

if __name__ == "__main__":
    unittest.main()
