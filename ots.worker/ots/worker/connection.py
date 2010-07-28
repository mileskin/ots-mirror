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
Shared connection object between client and worker
"""

import logging 
import re

from amqplib import client_0_8 as amqp

class NotConnectedError(Exception):
    pass


logger = logging.getLogger(__name__)

class Connection(object):
    """
    Class to encapsulate the connection and provide an api around amqplib
    """
    #FIXME: This *really* needs sorting out before Open Sourcing
    _vhost = None #:@type string @ivar amqp vhost
    _host = None #:@type string @ivar amqp host
    _port = None #:@type number @ivar amqp port
    _username = None #:@type string @ivar amqp username
    _password = None #:@type string @ivar amqp password
    _queue = None #:@type string @ivar amqp queue name
    _routing_key = None #:@type string @ivar amqp routing key
    _services_exchange = None #:@type string @ivar amqp exchange name
    _settable_keys = ['log_filename', 'vhost', 'host', 'port', 'username',
                       'password', 'queue', 'routing_key', 'services_exchange',
    ] #:@cvar
    channel = None #:@type amqplib.client_0_8.channel @ivar amqp channel
    connection = None #:@type amqplib.client_0_8.connection @ivar amqp connection
    
    def __init__(self, vhost, host, port, username, password, queue,
                       routing_key, services_exchange):
        """
        Store the variables passed to the object
        @type log_filename string
        @type vhost string
        @type host string
        @type port number
        @type username string
        @type password string
        @type queue string_
        @type routing_key string
        @type services_exchange string
        """
        l = locals()
        for k in l.keys():
            if k in self._settable_keys:
                setattr(self,'_' + k, l[k])
            else:
                del l[k]
        self.consumer_tag = ""
        
    def connect(self):
        """
        Create the connection to the rabbitMQ server
        """
        logger.debug("Connecting to RabbitMQ")
        self.connection = amqp.Connection(
            host=("%s:%s" %(self._host, self._port)),
            userid=self._username,
            password=self._password,
            virtual_host=self._vhost,
            insist=False)

        self.channel = self.connection.channel()
       
    def config(self, name):
        """
        Gets a config item by name
        """
        if name in self._settable_keys:
            return getattr(self, '_' + name)
        else:
            raise KeyError(name)

    def queue_declare(self, **kwargs):
        """
        Declares a queue
        """
        logger.debug("Declaring queue: " + self._queue)
        if self.channel is not None:
            self.channel.queue_declare(**kwargs)
        else:
            raise NotConnectedError()


    def exchange_declare(self, **kwargs):
        """
        Declares an exchange
        """
        logger.debug('Declaring services exchange: '  + kwargs['exchange'])
        if self.channel is not None:
            self.channel.exchange_declare(**kwargs)
        else:
            raise NotConnectedError()

    def queue_bind(self, **kwargs):
        """
        Binds a queue to an exchange
        """
        if self.channel is not None:
            logger.debug("Binding queue '%s' to exchange '%s' with routing key '%s'" % (self._queue, self._services_exchange, self._routing_key,))
            self.channel.queue_bind(**kwargs)
        else:
            raise NotConnectedError()

    def queue_purge(self, queue):
        """
        Empties all messages from a queue
        """
        if self.channel is not None:
            logger.debug("Purging queue '%s' of all messages" % (queue))
            self.channel.queue_purge(queue=queue, nowait=True)
        else:
            raise NotConnectedError()

    def basic_consume(self, **kwargs):
        """
        Marks this connection as having a consumer
        """
        if self.channel is not None:        
            logger.debug("Marked server as a consumer")
            self.consumer_tag = self.channel.basic_consume(**kwargs)
        else:
            raise NotConnectedError()


    def basic_cancel(self,**kwargs):
        """
        stops consuming
        """
        if self.channel is not None:
            logger.debug("Stopped consuming")
            self.channel.basic_cancel(self.consumer_tag)
        else:
            raise NotConnectedError()


    def basic_publish(self, msg, **kwargs):
        """
        Publishes a message to the response queue
        """
        self.channel.basic_publish(msg, **kwargs)
        
    def basic_qos(self, *args, **kwargs):
        """
        Sets up Quality of Service parameters
        """
        if self.channel is not None:
            self.channel.basic_qos(*args, **kwargs)
        else: 
            raise NotConnectedError()

    def does_queue_exist(self, queue):
        """
        Checks if the given queue exists
        """
        try:
            self.channel.queue_declare(queue=queue, passive=True)
        except:
            #If the queue does not exist, amqp disconnects us. unfriendly!
            self.connect()
    
    def wait(self):
        """
        Waits for a message
        """
        self.channel.wait()
       
    def cleanup(self):
        """
        Cleans up after ourselves, closing connections etc.
        """
        # Multiple try blocks to ensure everything is cleaned up properly
        try:
            self.channel.basic_cancel(self.consumer_tag)
        except:
            pass
        logger.debug('Shutting down connection to Rabbit')
        try:
            self.channel.close()
            self.connection.close()
        except:
            pass
        try:
            #Fix Memory leaks
            del self.channel.callbacks
            del self.connection.channels
            del self.connection.connection
        except:
            pass
        # Zero out
        self.channel = self.connection = None

    def basic_ack(self, **kwargs):
        """
        Acknowledges a message
        """
        logger.debug("Ack Message: %s"%(kwargs['delivery_tag']))
        self.channel.basic_ack(**kwargs)

    def basic_recover(self,**kwargs):
        """
        Delegate `basic_recover` to channel
        """
        self.channel.basic_recover(**kwargs)
