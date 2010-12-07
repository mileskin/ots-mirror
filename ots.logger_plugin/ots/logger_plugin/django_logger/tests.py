# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Ville Ilvonen <ville.p.ilvonen@nokia.com>
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
Django unit tests
"""

# Ignoring no objects member error
# pylint: disable=E1101
# Ignoring invalid method naming
# pylint: disable=C0103
# Ignoring docstring
# pylint: disable=C0111

import unittest
import logging
import uuid
from django.http import HttpRequest

from ots.logger_plugin.localhandler import LocalHttpHandler

from ots.logger_plugin.django_logger.models import LogMessage
from ots.logger_plugin.django_logger.views import create_message

SERVICENAME = 'logmessage'
RUN_ID      = uuid.uuid1().hex

class TestLogger(unittest.TestCase):
    """
    Unit tests for logger
    """

    def setUp(self):
        """
        Unit test setup
        """
        LogMessage.objects.all().delete()
        self.post_data = {
            'levelno'           : '10',             # integer NOT NULL
            'levelname'         : 'DEBUG',          # varchar(255) NOT NULL
            'name'              : 'logger name',    # varchar(255) NOT NULL
            'module'            : 'unit test',      # varchar(255) NOT NULL
            'filename'          : 'tests.py',       # varchar(255) NOT NULL
            'pathname'          : 'plugins/logger', # varchar(255) NOT NULL
            'funcName'          : 'setUp',          # varchar(255) NOT NULL
            'lineno'            : '25',             # integer NOT NULL
            'msg'               : 'debug message',  # longtext NOT NULL
            'exc_info'          : 'None',           # longtext NULL
            'exc_text'          : 'None',           # longtext NULL
            'args'              : '()',             # longtext NULL
            'threadName'        : 'ThreadName',     # varchar(255) NOT NULL
            'thread'            : '987.65',     # double precision NOT NULL
            'created'           : '432.10',     # double precision NOT NULL,
            'process'           : '24680',      # integer NOT NULL
            'relativeCreated'   : '135.79',     # double precision NOT NULL
            'msecs'             : '123.456',    # double precision NOT NULL
            }
        self.meta_data = {
            'REMOTE_ADDR'   : '127.0.0.1',
            'REMOTE_HOST'   : 'localhost',
            }

        request = HttpRequest()
        request.method = 'POST'
        request.POST = self.post_data
        request.META = self.meta_data
        create_message(request, SERVICENAME, RUN_ID)

    def tearDown(self):
        """
        Unit test tear down
        """
        # Deleting all messages
        LogMessage.objects.all().delete()

    def testMessageCount(self):
        self.assertEquals(LogMessage.objects.all().count(), 1)

    def testDebugMessageCount(self):
        self.assertEquals(
            LogMessage.objects.filter(levelname='DEBUG').count(), 1)

    def testServiceName(self):
        self.assertEquals(LogMessage.objects.all()[0].service, SERVICENAME)

    def testRunId(self):
        self.assertEquals(LogMessage.objects.all()[0].run_id, str(RUN_ID))

    def testLevelNumber(self):
        self.assertEquals(
            LogMessage.objects.all()[0].levelno,
            int(self.post_data['levelno']))

    def testLevelName(self):
        self.assertEquals(
            LogMessage.objects.all()[0].levelname, self.post_data['levelname'])

    def testLoggerName(self):
        self.assertEquals(
            LogMessage.objects.all()[0].name, self.post_data['name'])

    def testModule(self):
        self.assertEquals(
            LogMessage.objects.all()[0].module, self.post_data['module'])

    def testFilename(self):
        self.assertEquals(
            LogMessage.objects.all()[0].filename, self.post_data['filename'])

    def testPathname(self):
        self.assertEquals(
            LogMessage.objects.all()[0].pathname, self.post_data['pathname'])

    def testFuncname(self):
        self.assertEquals(
            LogMessage.objects.all()[0].funcName, self.post_data['funcName'])

    def testLinenumber(self):
        self.assertEquals(
            LogMessage.objects.all()[0].lineno, int(self.post_data['lineno']))

    def testMessage(self):
        self.assertEquals(
            LogMessage.objects.all()[0].msg, self.post_data['msg'])

    def testExecinfo(self):
        self.assertEquals(
            LogMessage.objects.all()[0].exc_info,
            eval(self.post_data['exc_info']))

    def testExectext(self):
        self.assertEquals(
            LogMessage.objects.all()[0].exc_text,
            eval(self.post_data['exc_text']))

    def testArgs(self):
        self.assertEquals(
            LogMessage.objects.all()[0].args, self.post_data['args'])

    def testThreadname(self):
        self.assertEquals(
            LogMessage.objects.all()[0].threadName,
            self.post_data['threadName'])

    def testThread(self):
        self.assertEquals(
            LogMessage.objects.all()[0].thread, 
            float(self.post_data['thread']))

    def testCreated(self):
        self.assertEquals(
            LogMessage.objects.all()[0].created, 
            float(self.post_data['created']))

    def testProcess(self):
        self.assertEquals(
            LogMessage.objects.all()[0].process, 
            int(self.post_data['process']))

    def testRelativecreated(self):
        self.assertEquals(
            LogMessage.objects.all()[0].relativeCreated,
            float(self.post_data['relativeCreated']))

    def testMsecs(self):
        self.assertEquals(
            LogMessage.objects.all()[0].msecs, float(self.post_data['msecs']))

    def testRemoteaddress(self):
        self.assertEquals(
            LogMessage.objects.all()[0].remote_ip,
            self.meta_data['REMOTE_ADDR'])

    def testRemotehost(self):
        self.assertEquals(
            LogMessage.objects.all()[0].remote_host,
            self.meta_data['REMOTE_HOST'])

class TestLocalHttpHandler(unittest.TestCase):
    """
    Unit tests for logger handler
    """
    
    def setUp(self):
        """
        Unit test setup
        """
        LogMessage.objects.all().delete()
        self.log = logging.getLogger("testlogger")
        self.log.setLevel(logging.INFO)

        httphandler = LocalHttpHandler(RUN_ID)
        httphandler.setLevel(logging.INFO)
        self.log.addHandler(httphandler)

    def tearDown(self):
        """
        Unit test tear down
        """
        LogMessage.objects.all().delete()

    def testMessageCount(self):
        self.log.error("asdf")
        self.assertEquals(LogMessage.objects.all().count(), 1)

    def testMessageData(self):
        msg_string = "asdf"
        self.log.error(msg_string)
        msg = LogMessage.objects.all()[0]

        self.assertEquals(msg.run_id, RUN_ID)
        self.assertEquals(msg.levelname.lower(), "error")
        self.assertEquals(msg.module, "tests")
        self.assertEquals(msg.filename, "tests.py")
        self.assertEquals(msg.msg, msg_string)
