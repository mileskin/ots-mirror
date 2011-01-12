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
 - Get the Options
 - Allocate Tasks 
 - Dispatch Testrun
 - Receives results
 - Publish results

Construction of the Options is quite involved 
To allow the best possible chance of Publishing any 
ValueErrors in the input parameters. 

The execution of the code for the generation of Parameters 
essential for the intialisation of the Publishers is controlled
by the `sandbox` if exceptions are raised they are cached and 
a default value is returned
"""

import sys
import os
import logging
import logging.config
import uuid
from traceback import format_exception

from unittest import TestCase
from unittest import TestResult
from copy import deepcopy
import ots.server

from ots.server.allocator.api import primed_taskrunner

from ots.server.hub.sandbox import sandbox
from ots.server.hub.testrun import Testrun
from ots.server.hub.publishers import Publishers
from ots.server.hub.options_factory import OptionsFactory

LOG = logging.getLogger()


DEBUG = False

#####################################
# 'ESSENTIAL' PARAMETERS DEFAULTS
#####################################


#Fallback parameters required for Publishing

EXAMPLE_SW_PRODUCT = "example_sw_product"
DEFAULT_REQUEST_ID = "default_request_id"
NO_IMAGE = "no_image"
DEFAULT_EXTENDED_OPTIONS_DICT = {} 


######################################
# HUB
######################################


class Hub(object):
    """
    The Hub is the Keystone of the OTS system.
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
        sandbox.is_on = True
        self._sw_product = sw_product
        self._request_id = request_id
        self._testrun_uuid = None

        self._options_factory = OptionsFactory(self.sw_product, kwargs)
        self._taskrunner = None

        self._options = None

        # Dont enable before logging is configured properly!
        # - If disabled all messages are visible in http logger.
        # - if enabled, we don't get any logging from server.
#        self._init_logging()

        self._publishers = Publishers(self.request_id, 
                                      self.testrun_uuid, 
                                      self.sw_product, 
                                      self.image,
                                      **self.extended_options_dict)
        sandbox_is_on = False
        LOG.debug("Publishers initilialised... sandbox switched off...")
        LOG.info("OTS Server. version '%s'" % (ots.server.__VERSION__))

        # Log incoming options to help testrun debugging.
        # These need to match the xmlrpc interface options!
        try:
            incoming_options = deepcopy(kwargs)
            notify_list = ""
            if "notify_list" in incoming_options.keys():
                notify_list = incoming_options["notify_list"]
                del incoming_options["notify_list"]
            LOG.info(("Incoming request: program: %s, request: %s, " \
                          "notify_list: %s, options: %s")\
                         % (sw_product,
                            request_id,
                            notify_list,
                            incoming_options))
        except ValueError:
            pass

    #############################################
    # Sandboxed Properties
    #############################################

    @property
    @sandbox(EXAMPLE_SW_PRODUCT)
    def sw_product(self):
        """
        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to
        """
        return str(self._sw_product).lower()
       
    @property
    @sandbox(DEFAULT_REQUEST_ID)
    def request_id(self):
        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client
        """
        return str(self._request_id)

    @property
    @sandbox(DEFAULT_EXTENDED_OPTIONS_DICT)
    def extended_options_dict(self):
        return self._options_factory.extended_options_dict

    @property
    @sandbox(NO_IMAGE)
    def image(self):
        return self._options_factory().image


    #############################################
    # Properties
    #############################################

    @property
    def is_hw_enabled(self):
        """
        @type is_hw_enabled: C{bool}
        @param is_hw_enabled: Is hw testing enabled?
        """        
        hw_packages = self.options.hw_packages
        return bool(len(hw_packages))
     
    @property 
    def is_host_enabled(self):
        """
        @type is_host_enabled: C{bool}
        @param is_host_enabled: Is host testing enabled
        """
        host_packages = self.options.host_packages
        return  bool(len(host_packages))
      
    @property
    def testrun_uuid(self):
        """
        @type testrun_uuid: C{str}
        @param testrun_uuid: A globally unique identifier for the testrun
        """
        if self._testrun_uuid is None:
            LOG.info("Testrun ID: '%s'"%(self._testrun_uuid))
            self._testrun_uuid = uuid.uuid1().hex
        return self._testrun_uuid

    @property
    def options(self):
        if self._options is None:
            self._options = self._options_factory()
        return self._options

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
                                    self.testrun_uuid, 
                                    self.options.timeout,
                                    self.options.priority,
                                    self.options.device_properties,
                                    self.options.image,
                                    self.options.hw_packages,
                                    self.options.host_packages,
                                    self.options.emmc,
                                    self.options.testfilter,
                                    self.options.flasher,
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
                
    def _testrun(self):
        """
        Start a Testrun and populate the Publishers

        @rtype : C{unittest.TestResult}
        @rparam : A TestResult 
        """    
        testrun_result = TestResult()
        try:
            publishers = self._publishers
            testrun = Testrun(self.is_hw_enabled,
                              self.is_host_enabled)
            taskrunner = self.taskrunner

            #FIXME: Cheap hack to make testable
            testrun.run_test = taskrunner.run
            testrun_result.addSuccess(TestCase)if testrun.run() else \
                  testrun_result.addFailure(TestCase, (None, None, None))
        except Exception, err:
            LOG.error("Testrun error", exc_info=err)
            type, value, tb = sys.exc_info()
            publishers.set_exception(value)
            testrun_result.addError(TestCase, (type, value, tb))
            if DEBUG:
                raise
        # Quick and dirty hack to make all available information published
        try:
            LOG.info("Publishing results")
            publishers.set_expected_packages(testrun.expected_packages)
            publishers.set_tested_packages(testrun.tested_packages)
            publishers.set_results(testrun.results)
            publishers.set_monitors(testrun.monitors)
            if testrun.exceptions:
                LOG.debug("Publishing errors")
                # TODO: we should publish all exceptions, or just start
                #       using TestrunResult for error reporting
                publishers.set_exception(testrun.exceptions[0])
                for error in testrun.exceptions:
                    LOG.info("error_info set to '%s'"%(error.strerror))
                    testrun_result.addError(TestCase,
                                            (error, error.strerror, None))
        except Exception, err:
            type, value, tb = sys.exc_info()
            testrun_result.addError(TestCase, (type, value, tb))
            LOG.debug("publishing failed", exc_info=True)
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
        if sandbox.exc_info != (None, None, None): 
            LOG.error("Sandbox Error. Forced Initialisation")
            etype, value, tb = sandbox.exc_info
            str_tb = ''.join(format_exception(etype, value, tb, 50))
            LOG.error(str_tb)
            testrun_result = TestResult() 
            LOG.info("error_info set to '%s'" %(str(value)))
            testrun_result.addError(TestCase, (etype, value, tb))
            self._publishers.set_exception(value)
            sandbox.exc_info = (None, None, None)
        else:
            testrun_result = self._testrun()
        result_string = result_to_string(testrun_result)
        # TODO: Whats the result format in publisher interface???????
        LOG.info("Result set to %s"%(result_string))
        self._publishers.set_testrun_result(result_string)
        self._publishers.publish()
        LOG.info("Testrun finished with result: %s" % result_string)
        return testrun_result

# TODO: Move to more suitable place? This same value should be reported in email
# etc.
def result_to_string(testrun_result):
    if testrun_result.wasSuccessful():
        return "PASS"
    elif testrun_result.failures:
        return "FAIL"
    else:
        #LOG.debug("Testrun failure %s" % testrun_result.errors)
        return "ERROR"
