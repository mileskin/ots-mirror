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
Client that sends response messages back to server over amqp
"""
import logging

from amqplib import client_0_8 as amqp

from ots.common.testrun_queue_name import testrun_queue_name
from ots.common.protocol import OTSMessageIO

LOGGER = logging.getLogger(__file__)

class ResponseClient(object):
    """
    Client that sends response messages back to server over amqp
    """

    def __init__(self, server_host, testrun_id, response_queue = None):

        self.log = logging.getLogger(__file__)
        self.host = server_host
        self.testrun_id = testrun_id
        self.conn = None
        self.channel = None

        if response_queue:
            self.response_queue = response_queue
        else:
            self.response_queue = testrun_queue_name(testrun_id)
        
    def __del__(self):
        """Close amqp connection if they are still open"""
        
        try:
            self.channel.close()
            self.conn.close()

        except:
            pass



#
# Public methods:
#



    def connect(self):
        """Set up connection to amqp server"""

        self.conn = amqp.Connection(host=self.host+":5672",
                                    userid="guest",
                                    password="guest",
                                    virtual_host="/",
                                    insist=False)
        self.channel = self.conn.channel()



    def add_result(self, filename, content, origin="Unknown", 
                         test_package="Unknown", environment="Unknown"):
        """Calls OTSMessageIO to create result object message"""
        
        self._send_message(OTSMessageIO.pack_result_message(filename, content,
                           origin, test_package, environment))

    def set_state(self, state, status_info):
        """Calls OTSMessageIO to create testrun state change message"""

        if state not in ("NOT_STARTED", "QUEUED", "TESTING", "FLASHING", \
                             "STORING_RESULTS", "FINISHED"):
            LOGGER.warning("Unknown testrun state %s given, skipping "\
                                 "setting state" % state)
            return

        self._send_message(OTSMessageIO.pack_testrun_status_message(state,
                           status_info))


    def set_error(self, error_info, error_code):
        """Calls OTSMessageIO to cerate testrun error message"""

        self._send_message(OTSMessageIO.pack_testrun_error_message(error_info,
                           error_code))

    def add_executed_packages(self, environment, packages):
        """Calls OTSMessageIO to create test package list"""
        self._send_message(
            OTSMessageIO.pack_testpackage_list_message(environment,
                                                       packages))
 

#
# Private methods:
#


    def _send_message(self, msg):
        """
        Sends a message to server
        """
        self.channel.basic_publish(msg,
                                   mandatory = True,
                                   exchange = self.response_queue,
                                   routing_key = self.response_queue)
        


