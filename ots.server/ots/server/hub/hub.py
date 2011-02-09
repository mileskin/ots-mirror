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
import datetime
import configobj
from traceback import format_exception

from unittest import TestCase
from unittest import TestResult
from copy import deepcopy
import pkg_resources
import ots.server

from ots.server.allocator.api import primed_taskrunner

from ots.server.version import __VERSION__
from ots.server.hub.sandbox import sandbox
from ots.server.hub.testrun import Testrun
from ots.server.hub.publishers import Publishers
from ots.server.hub.options_factory import OptionsFactory
from ots.server.server_config_filename import server_config_filename

LOG = logging.getLogger()

#TODO: move to somewhere else or implement default models as plugins
DEFAULT_DISTRIBUTION_MODELS = ["default", "perpackage"]

DEBUG = False

#####################################
# 'ESSENTIAL' PARAMETERS DEFAULTS
#####################################


#Fallback parameters required for Publishing

EXAMPLE_SW_PRODUCT = "example_sw_product"
DEFAULT_REQUEST_ID = "default_request_id"
NO_IMAGE = "no_image"

# In error cases we want to try email sending to get the error reported
DEFAULT_EXTENDED_OPTIONS_DICT = {"email": "on",
                                 "email_attachments": "off"} 

# Default log directory
LOG_DIR = "/var/log/ots/"

class HubException(Exception):
    """Error in Hub"""
    pass

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
        
        self._filehandler = None
        self._initialize_logger()

        self._publishers = Publishers(self.request_id, 
                                      self.testrun_uuid, 
                                      self.sw_product, 
                                      self.image,
                                      **self.extended_options_dict)
        sandbox_is_on = False
        LOG.debug("Publishers initilialised... sandbox switched off...")
        LOG.info("OTS Server. version '%s'" % (__VERSION__))

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
    
    def __del__(self):
        """
        Destructor
        """
        if self._filehandler is not None:
            root_logger = logging.getLogger('')
            root_logger.removeHandler(self._filehandler)

    #############################################
    # Sandboxed Properties
    #############################################

    @property
    @sandbox(EXAMPLE_SW_PRODUCT)
    def sw_product(self):
        """
        @rtype C{str}
        @rparam Name of the sw product this testrun belongs to
        """
        return str(self._sw_product).lower()
       
    @property
    @sandbox(DEFAULT_REQUEST_ID)
    def request_id(self):
        """
        @rtype C{str}
        @rparam An identifier for the request from the client
        """
        return str(self._request_id)

    @property
    @sandbox(DEFAULT_EXTENDED_OPTIONS_DICT)
    def extended_options_dict(self):
        """
        rtype : C{dict}
        rparam : Additional Options passed to OTS
        """
        return self._options_factory.extended_options_dict

    @property
    @sandbox(NO_IMAGE)
    def image(self):
        """
        rtype : C{dict}
        rparam : Additional Options passed to OTS
        """
        return self._options_factory().image


    #############################################
    # Properties
    #############################################

    @property
    def is_hw_enabled(self):
        """
        @rtype C{bool}
        @rparam Is hw testing enabled?
        """        
        hw_packages = self.options.hw_packages
        return bool(len(hw_packages))
     
    @property 
    def is_host_enabled(self):
        """
        @rtype C{bool}
        @rparam Is host testing enabled
        """
        host_packages = self.options.host_packages
        return  bool(len(host_packages))
      
    @property
    def testrun_uuid(self):
        """
        @rtype C{str}
        @rparam A globally unique identifier for the testrun
        """
        if self._testrun_uuid is None:
            self._testrun_uuid = uuid.uuid1().hex
            LOG.info("Testrun ID: '%s'"%(self._testrun_uuid))
        return self._testrun_uuid

    @property
    def options(self):
        """
        @rtype : C{ots.server.hub.options.Options
        @rparam : The Options
        """
        if self._options is None:
            self._options = self._options_factory()
        return self._options

    @property 
    def taskrunner(self):
        """
        A Taskrunner loaded with Tasks as 
        allocated by preferences

        @rtype : L{ots.server.distributor.taskrunner}
        @rparam : A Taskrunner loaded with Tasks
        """
        custom_distribution_model = None
        distribution_model = self.options.distribution_model
        
        # Search for custom package distribution models if not using default
        # models
        if distribution_model not in DEFAULT_DISTRIBUTION_MODELS:
            try:
                entry_point = pkg_resources.iter_entry_points(
                    group = "ots_distribution_model",
                    name = distribution_model).next()

                custom_distribution_model = entry_point.load()(self.options)
                LOG.info("Loaded custom distribution model '%s'"%
                         (entry_point.module_name))
            except StopIteration:
                raise ValueError("Invalid distribution model: %s"\
                                     % distribution_model)

        if self._taskrunner is None:
            self._taskrunner = primed_taskrunner(self.testrun_uuid, 
                                              self.options.timeout,
                                              self.options.distribution_model,
                                              self.options.device_properties,
                                              self.options.image,
                                              self.options.hw_packages,
                                              self.options.host_packages,
                                              self.options.emmc,
                                              self.options.testfilter,
                                              self.options.flasher,
                                              custom_distribution_model)

        return self._taskrunner

    #########################
    # HELPERS
    #########################

    def _initialize_logger(self):
        """
        initializes the logger
        """
        # This makes sure default formatters get loaded. Otherwise exc_info is
        # not processed correctly
        logging.basicConfig()
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        
        config_file = server_config_filename()
        
        try:
            config = configobj.ConfigObj(config_file).get("ots.server")
            log_dir = config.get('log_dir', LOG_DIR)
            # File handler for maintainers/developers
            log_id_string = _generate_log_id_string(self._request_id, self.testrun_uuid)
            format = '%(asctime)s  %(module)-12s %(levelname)-8s %(message)s'
            os.system("mkdir -p %s" % log_dir)
            log_file = os.path.join(log_dir, log_id_string)
            self._filehandler = logging.FileHandler(log_file)
            self._filehandler.setLevel(logging.DEBUG) # All messages to the files
            self._filehandler.setFormatter(logging.Formatter(format))
            root_logger.addHandler(self._filehandler)
        except IOError, ioerror:
            root_logger.error("IOError, no permission to write %s?" % log_dir,
                              exc_info=True)
        except:
            root_logger.error("Unexpected error while creating testrun log",
                              exc_info=True)
                
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
            type, value, traceback = sys.exc_info()
            LOG.error(str(value) or "Testrun Error", exc_info=err)
            publishers.set_exception(value)
            testrun_result.addError(TestCase, (type, value, traceback))
            if DEBUG:
                raise

        # Quick and dirty hack to make all available information published
        try:
            LOG.info("Publishing results")
            publishers.set_expected_packages(testrun.expected_packages)
            publishers.set_tested_packages(testrun.tested_packages)
            publishers.set_results(testrun.results)
            publishers.set_monitors(testrun.monitors)

        except Exception, err:
            type, value, traceback = sys.exc_info()
            testrun_result.addError(TestCase, (type, value, traceback))
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
            LOG.error("Testrun Error. Forced Initialisation", \
                          exc_info = sandbox.exc_info)
            etype, value, traceback = sandbox.exc_info
            testrun_result = TestResult() 
            testrun_result.addError(TestCase, (etype, value, traceback))
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
    """
    Convert unittest.TestResult to string
    
    @type testrun_result: C{unittest.TestResult}
    @param testrun_result: A TestResult
    
    @rtype C{str}
    @rparam Result as string
    """

    if testrun_result.wasSuccessful():
        return "PASS"
    elif testrun_result.failures:
        return "FAIL"
    else:
        return "ERROR"

def _generate_log_id_string(build_id, testrun_id):
    """
    Generates the log file name
    """
    request_id = "testrun_%s_request_%s_"% (testrun_id, build_id)
    request_id += str(datetime.datetime.now()).\
        replace(' ','_').replace(':','_').replace('.','_')
    return request_id
