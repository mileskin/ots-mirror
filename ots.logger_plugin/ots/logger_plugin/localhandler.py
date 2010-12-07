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
A Custom handler for sending local log messages to http logger directly without
apache or http.
"""

import logging
from django.http import HttpRequest
from ots.logger_plugin.django_logger.views import create_message
from socket import gethostname

class LocalHttpHandler(logging.Handler):
    """
    A Custom handler for sending local log messages to http logger directly
    without apache or http.
    """
    
    def __init__(self, testrun_id):
        """
        Create new LocalHttpHandler
        
        @type testrun_id: C{int}
        @param testrun_id: Testrun id this logger is logging into
        """
        logging.Handler.__init__(self)
        self.testrun_id = testrun_id
	    
    def emit(self, record):
        """
        Stores the message in db by calling create_message() directly

        @type record: L{logging.LogRecord}
        @param arg1: LogRecord object from pythons logging module

        """
        meta_data = {
            'REMOTE_ADDR'   : '127.0.0.1',
            'REMOTE_HOST'   : gethostname(),
            }

        request = HttpRequest()
        request.method = 'POST'
        request.POST = record.__dict__
        request.META = meta_data
        try:
            create_message(request, servicename = "ots",
                           run_id=self.testrun_id)

        except Exception, e:
            print("error in LocalHttpHandler, testrun %s" % self.testrun_id)
            print e
