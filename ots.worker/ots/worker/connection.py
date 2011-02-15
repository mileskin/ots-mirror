# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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
The AMQP Connection 

Caches connection parameters to allow reconnection.

FIXME: retries need adding to this class
"""

import logging 


from amqplib import client_0_8 as amqp

LOGGER = logging.getLogger(__name__)

class Connection(object):
    """
    Connection
    """
    #@ivar connection: amqp connection (amqplib.client_0_8.connection)
    #@ivar channel: amqp connection (amqplib.client_0_8.channel)

    connection = None
    
    def __init__(self, vhost, host, port, username, password):
        """
        @type vhost: C{string}
        @param vhost: amqp vhost

        @type host: C{string}
        @param host: amqp host

        @type port: C{integer}
        @param port: amqp port

        @type username: C{string}
        @param username: amqp username

        @type password: C{string}
        @param password: amqp password
        """
        self._vhost = vhost
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.channel = None
        self.connect()

    def connect(self):
        """
        Create the connection to the rabbitMQ server
        """
        LOGGER.debug("Connecting to RabbitMQ")
        self.connection = amqp.Connection(
                            host = ("%s:%s" % (self._host, self._port)),
                            userid = self._username,
                            password = self._password,
                            virtual_host = self._vhost,
                            insist = False)
        self.channel = self.connection.channel()
          
    def clean_up(self):
        """
        Cleans up after ourselves, closing connections etc.
        """
        LOGGER.debug('Shutting down connection to Rabbit')
        try:
            self.channel.close()
            try:
                self.connection.close()
            except AttributeError:
                LOGGER.debug("Connection already lost")
        except:
            LOGGER.exception("clean_up() failed")
        #Fix Memory leaks
        if hasattr(self.channel, "callbacks"):
            del self.channel.callbacks
        if hasattr(self.connection, "channels"):
            del self.connection.channels
        if hasattr(self.connection, "connection"):
            del self.connection.connection
