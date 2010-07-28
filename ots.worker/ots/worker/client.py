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
This is the server for the worker itself.
It sets up a queue and waits for jobs to process
"""

import sys
from os import kill, setpgrp
import logging 
from subprocess import Popen, PIPE
import signal
from pickle import dumps
from time import sleep

from amqplib import client_0_8 as amqp
from amqplib.client_0_8.exceptions import AMQPChannelException

logger = logging.getLogger(__name__)

class Alarm(Exception):
    """
    Basic exception class to handle timeouts
    """
    pass

def alarm_handler(signum, frame):
    """
    Utility function to raise Alarm()
    """
    raise Alarm

#Use ots.worker.base.Base to setup logging
class Client(object):
    """
    Simple client that posts messages back to the OTS distributor through amqp
    """
    
    _connection = None #: @ivar ots.worker.connection.Connection
    
    def __init__(self, connection):
        """
        Store the variables passed to the object
        @type connection ots.worker.connection.Connection
        """
        self._connection = connection

    def send_message(self,exchange,routing_key,message):
        """
        Sends the message itself
        """
        logger.debug("sending message: '%s' to queue '%s'" % (message,routing_key))
        msg = amqp.Message(dumps(message))
        msg.properties['delivery_mode'] = 2
        try:
            self._connection.basic_publish(msg,
                                           mandatory = True,
                                           exchange=exchange,
                                           routing_key=routing_key)
        except AMQPChannelException,e:
            self.connect()
            raise e

    def queue_purge(self,queue):
        """
        Empties a queue of messages
        """
        return self._connection.queue_purge(queue)

    def connect(self):
        """
        Manual reconnect. Useful for tests
        """
        self._connection.connect()
