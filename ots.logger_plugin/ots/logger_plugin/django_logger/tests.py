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

from BeautifulSoup import BeautifulSoup

from django.http import HttpRequest
from django.test.client import Client

from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerResultsFail
from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerTimeout
from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerError
from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerResultsPass
from ots.server.hub.api import Hub

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


################################################
# TestView Helpers 
################################################

#TODO: Remove Duplication.. Pretty well lifted verbatim from the ots.system

def get_latest_testrun_id(content):
    """
    Scrape the latest testrun id from the global log
    """
    soup = BeautifulSoup(content)
    table =  soup.findAll("table")[1]
    row1 = table.findAll("tr")[1]
    td = row1.findAll("td")[0]
    a = td.findAll("a")[0].string
    return a

def has_message(content, testrun_id, string):
    """
    Tries to find a message in the log for the given testrun
    Returns True if message was found
    """
    ret_val = False
    soup = BeautifulSoup(content, 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            if td[5].string and td[5].string.count(string):
                ret_val = True
                break
            elif td[5].string == None: # Check also <pre> messages </pre>
                if td[5].findAll("pre")[0].string.count(string):
                    ret_val = True
                    break
    return ret_val

def has_errors(content, testrun_id):
    """
    Checks if testrun has any error messages
    """
    ret_val = False
    soup = BeautifulSoup(content, 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            try:
                error = td[4].findAll("span")[0].string
                if error == "ERROR":
                    ret_val = True
                    break
            except IndexError:
                pass

    return ret_val


###################################################
# Test View
###################################################

class TestView(unittest.TestCase):

    def assert_log_contains_string(self, content, testrun_id, string): 
        self.assertTrue(has_message(content, testrun_id, string), 
         "'%s' not found on log for testrun_id: '%s'" % (string, testrun_id))

    def assert_has_latest(self, testrun_id):
        client = Client()
        response = client.get('/logger/view', follow = True)
        content = response.content
        latest_testrun_uuid = get_latest_testrun_id(content)
        self.assertEquals(testrun_id, latest_testrun_uuid)

    def get_log_content(self, testrun_id):
        client = Client()
        response = client.get('/logger/view/testrun/%s'%(testrun_id),
                               follow = True)
        content = response.content
        return content

    def test_passing_run(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        string = "Testrun finished with result: PASS"
        self.assert_log_contains_string(content, testrun_id, string)

    def test_error_run(self):
        mock_taskrunner = MockTaskRunnerError()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        self.assertTrue(has_errors(content, testrun_id))
        string = "Result set to ERROR"
        self.assert_log_contains_string(content, testrun_id, string)
        
    def test_fail_run(self):
        mock_taskrunner = MockTaskRunnerResultsFail()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        string = "Testrun finished with result: FAIL"
        self.assert_log_contains_string(content, testrun_id, string)

    def test_timeout(self):
        mock_taskrunner = MockTaskRunnerTimeout()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        self.assertTrue(has_errors(content, testrun_id))
        string = "Result set to ERROR"
        self.assertTrue(has_message(content, testrun_id, string))
        
    def test_non_existent_sw_product(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub("None", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        string = "not found in sw products"
        self.assert_log_contains_string(content, testrun_id, string)
        
    def test_no_image(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub("example_sw_product", 111)
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        testrun_id =  hub.testrun_uuid
        self.assert_has_latest(testrun_id)
        content = self.get_log_content(testrun_id)
        string = "Missing `image` parameter"
        self.assert_log_contains_string(content, testrun_id, string)
