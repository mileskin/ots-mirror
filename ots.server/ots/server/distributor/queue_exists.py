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
Determines whether a Queue exists or not
"""

import logging

from amqplib import client_0_8 as amqp
from amqplib.client_0_8.exceptions import AMQPChannelException 

LOGGER = logging.getLogger(__name__)

def queue_exists(host, user_id, password, virtual_host, queue):
    """
    @type host: C{str}
    @param host: The AMQP host name

    @type user_id: C{str} 
    @param user_id: The AMQP userid

    @type password: C{str} 
    @param password: The AMQP password

    @type virtual_host: C{str} 
    @param virtual_host: The AMQP virtual host

    @type queue : C{str} 
    @param queue: The name of queue which presence is queried

    @rtype: C{bool} 
    @return: Whether the AMQP queue exists or not 
    """
    ret_val = False
    connection = amqp.Connection(host = host, 
                                 userid = user_id,
                                 password = password,
                                 virtual_host = virtual_host, 
                                 insist = False)
    channel = connection.channel()
    try:
        channel.queue_declare(queue = queue, 
                              durable = False, 
                              exclusive = False,
                              auto_delete=True,
                              passive = True)
        ret_val = True
    except AMQPChannelException:
        LOGGER.debug("No queue for %s"%(queue))
    return ret_val 
