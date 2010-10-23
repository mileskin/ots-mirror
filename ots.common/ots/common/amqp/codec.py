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
The Methods for packing and unpacking the amqp messages
"""

from pickle import dumps, loads

from amqplib import client_0_8 as amqp

import ots.common

DELIVERY_MODE = 2

#########################
# PACK / UNPACK
#########################

def unpack_message(message):
    """
    Unpack the message with Pickle

    @type message: amqplib.client_0_8.basic_message.Message
    @param message: A pickled message in AMQP message format

    @rtype message: L{ots.common.message_io.Message} 
    @rparam mesage: The Message 
    """
    body = loads(message.body)
    return body

def pack_message(message):
    """
    Packs the message for sending as AMQP with Pickle

    @type message: L{ots.common.message_io.Message} 
    @param mesage: The AMQP message 

    @rtype message: amqplib.client_0_8.basic_message.Message
    @return message: A pickled message in AMQP message format
    """
    message = dumps(message, True)
    amqp_message = amqp.Message(message)
    amqp_message.properties['delivery_mode'] = DELIVERY_MODE
    return amqp_message
