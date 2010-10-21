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
Delete the queue of messages 
"""

from amqplib import client_0_8 as amqp

def delete_queue(host, queue_name):
    """Delete a queue from AMQP server"""
    port = 5672
    userid = "guest"
    password = "guest"
    virtual_host = "/"
    connection = amqp.Connection(host = ("%s:%s" %(host, port)),
                                 userid = userid,
                                 password = password,
                                 virtual_host = virtual_host,
                                 insist = False)
    channel = connection.channel()
    channel.queue_delete(queue = queue_name, nowait=True)

def main():
    """Main function"""
    import sys  
    if len(sys.argv) != 3:
        print "Usage python delete_queue host queue_name"
        sys.exit()
    host = sys.argv[1]
    queue_name = sys.argv[2]
    print host, queue_name
    delete_queue(host, queue_name)

   
if __name__ == "__main__":
    main()
