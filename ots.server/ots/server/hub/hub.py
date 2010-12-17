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
The Hub provides a focal point for inter-component 
data-flow in the OTS system.

Hence OTS suggests a centralised topology 
with the Hub as it's central component.

The role of the Hub is the high level management of a single Testrun.

Specifically:

 - Receive test request from third-party client
 - Allocate Tasks 
 - Dispatch Testrun
 - Receives results
 - Publish results

"""

import sys
import os
import logging
import logging.config
import configobj
import traceback

from unittest import TestCase
from unittest import TestResult

from ots.server.allocator.api import primed_taskrunner

from ots.server.hub.sandbox import Sandbox
from ots.server.hub.testrun import Testrun
from ots.server.hub.application_id import get_application_id
from ots.server.hub.publishers import Publishers

LOG = logging.getLogger(__name__)


DEBUG = False
 
class Hub(object):

    """
    The Hub is the Keystone of the OTS system
    """

    def __init__(self, sw_product, request_id, **kwargs):
        """
        The kwargs are the dictionary of arguments provided by the 
        request.
        Note. That these must contain an 'image'

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type request_id: C{str}
        @param request_id: An identifier for the request from the client
        """
        self._sandbox = Sandbox(sw_product, request_id, **kwargs)
        self._publishers = Publishers(self._sandbox.request_id, 
                                      self._sandbox.testrun_uuid, 
                                      self._sandbox.sw_product, 
                                      self._sandbox.options.image,
                                      **self._sandbox._extended_options_dict)
        self._taskrunner = None
        self._init_logging()

    #############################################
    # Properties
    #############################################

    @property 
    def taskrunner(self):
        """
        A Taskrunner loaded with Tasks as 
        allocated by preferences

        rtype : L{ots.server.distributor.taskrunner}
        rparam : A Taskrunner loaded with Tasks
        """
        if self._taskrunner is None:
            self._taskrunner = primed_taskrunner(
                                    self._sandbox.testrun_uuid, 
                                    self._sandbox.options.timeout,
                                    self._sandbox.options.priority,
                                    self._sandbox.options.device_properties,
                                    self._sandbox.options.image,
                                    self._sandbox.options.hw_packages,
                                    self._sandbox.options.host_packages,
                                    self._sandbox.options.emmc,
                                    self._sandbox.options.testfilter,
                                    self._sandbox.options.flasher,
                                    self._publishers)
        return self._taskrunner

    #########################
    # HELPERS
    #########################

    @staticmethod
    def _init_logging():
        """
        Initialise the logging from the configuration file
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        conf = os.path.join(dirname, "logging.conf")
        if os.path.isfile(conf):
            logging.config.fileConfig(conf)

    def _publish(self, testrun_result):
        """
        Publish the testrun

        @type : C{unittest.TestResult}
        @param : A TestResult 
        """
        try:
            self._publishers.set_testrun_result(testrun_result)
            self._publishers.publish()
        except Exception, err:
            LOG.debug("Error setting testrun_result '%s'"%(err))
            if DEBUG:
                raise

    def _testrun(self):
        """
        Start a Testrun and populate the Publishers

        @rtype : C{unittest.TestResult}
        @rparam : A TestResult 
        """    
        testrun_result = TestResult()
        try:
            publishers = self._publishers
            testrun = Testrun(self._sandbox.is_hw_enabled,
                              self._sandbox.is_host_enabled)
            taskrunner = self.taskrunner

            #FIXME: Cheap hack to make testable
            testrun.run_test = taskrunner.run

            testrun_result.addSuccess(TestCase)if testrun.run() else \
                  testrun_result.addFailure(TestCase, (None, None, None))
            
            publishers.set_expected_packages(testrun.expected_packages)
            publishers.set_tested_packages(testrun.tested_packages)
            publishers.set_results(testrun.results)
            publishers.set_monitors(testrun.monitors)
           
        except Exception, err:
            LOG.debug("Testrun Exception: %s"%(err))
            LOG.debug(traceback.format_exc())
            type, value, tb = sys.exc_info()
            publishers.set_exception(value)
            testrun_result.addError(TestCase, (type, value, tb))
            if DEBUG:
                raise
        return testrun_result

    ################################
    # RUN
    ################################

    def run(self):
        """
        Start a Testrun and publish the data

        @rtype : C{unittest.TestResult}
        @rparam : A TestResult 
        """    
        if self._sandbox.exc_info() is not None:
            LOG.debug("Publishers not initialised")
            self._publishers.set_exception(self._sandbox.exc_info()[1])
            testrun_result = TestResult()
            testrun_result.addError(TestCase, testrun_factory.exc_info)
            if DEBUG:
                raise self._sandbox.exc_info[0] 
        else:
            testrun_result = self._testrun()
        self._publish(testrun_result)
        return testrun_result
