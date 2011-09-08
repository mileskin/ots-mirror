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

from amqplib import client_0_8 as amqp

port = 5672
userid = "guest"
password = "guest"
virtual_host = "/"

class QueueProcessor:
    def __init__(self, host, queue_name):
        self.process_queue(host, queue_name)

    def process_queue(self, host, queue_name):
        print "Processing queue '%s' on host '%s'..." % (queue_name, host)
        connection = amqp.Connection(
            host = ("%s:%s" %(host,port)),
            userid = userid,
            password = password,
            virtual_host = virtual_host,
            insist = False)
        self.process_channel(connection.channel(), queue_name)
        print "Done."

class EmptyQueue(QueueProcessor):
    def process_channel(self, channel, queue_name):
        channel.queue_purge(queue = queue_name, nowait=True)

class DeleteQueue(QueueProcessor):
    def process_channel(self, channel, queue_name):
        channel.queue_delete(queue = queue_name, nowait=True)

