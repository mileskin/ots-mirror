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
Handler to put LogRecords on an AMQP Queue
"""

import logging

from amqplib.client_0_8 import AMQPChannelException

from ots.common.amqp.api import pack_message


class AMQPLogHandler(logging.Handler):
    """
    CustomHandler for AMQP
    """
    
    exchange = None
    queue = None
    channel = None

    def __init__(self):
        logging.Handler.__init__(self)
       
    def emit(self, record):
        """
        @type record : C{logging.LogRecord}
        @param record : The Log Record
        """
        if self.channel is not None \
                and self.queue is not None \
                and self.exchange is not None:
            #FIXME: This rudely ignores the exc_info
            #as Python can't pickle the traceback
            record.exc_info = None
            #
            message = pack_message(record)
            try:
                self.channel.basic_publish(message,
                                           mandatory = True,
                                           exchange = self.exchange,
                                           routing_key = self.queue)
            except AMQPChannelException:
                print "Can't log to %s" % (self.queue)
