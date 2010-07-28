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
Delete the queue of messages 
"""

from amqplib import client_0_8 as amqp

def main(host, queue_name):
    port = 5672
    userid = "guest"
    password = "guest"
    virtual_host = "/"
    connection = amqp.Connection(host = ("%s:%s" %(host,port)),
                                 userid = userid,
                                 password = password,
                                 virtual_host = virtual_host,
                                 insist = False)
    channel = connection.channel()
    channel.queue_delete(queue = queue_name, nowait=True)
   
if __name__ == "__main__":
    import sys  
    if len(sys.argv) != 3:
        print "Usage python delete_queues host queue_name"
        sys.exit()
    host = sys.argv[1]
    queue_name = sys.argv[2]
    print host, queue_name
    main(host, queue_name)
