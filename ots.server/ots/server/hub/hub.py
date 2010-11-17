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
import uuid
import configobj
import traceback

from ots.common.framework.api import config_filename

from ots.server.allocator.api import primed_taskrunner

from ots.server.hub.testrun import Testrun
from ots.server.hub.options_factory import OptionsFactory
from ots.server.hub.application_id import get_application_id
from ots.server.hub.publishers import Publishers

LOG = logging.getLogger(__name__)

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
        self.sw_product = sw_product.lower()
        self.request_id = request_id
        LOG.debug("Initialising options with: '%s'"%(kwargs))
        options_factory = OptionsFactory(sw_product, kwargs)
        self.options = options_factory()
        self.testrun_uuid = uuid.uuid1().hex 
        self.publishers = Publishers(request_id, 
                                     self.testrun_uuid, 
                                     sw_product, 
                                     self.options.image,
                                     **options_factory.extended_options_dict)
        self._taskrunner = None

    #########################
    # HELPERS
    #########################

    @staticmethod
    def _init_logging():
        """
        Initialise the logging from the configuration file
        """
        #FIXME
        dirname = os.path.dirname(os.path.abspath(__file__))
        conf = os.path.join(dirname, "logging.conf")
        logging.config.fileConfig(conf)

    @property
    def _timeout(self):
        """
        rtype: C{int}
        rparam: The timeout in minutes
        """
        return 30 # TODO: SHOULD BE READ FROM self.options!!!!!!!!
    
    ###############################
    # TASKRUNNER
    ##############################

    @property 
    def taskrunner(self):
        """
        A Taskrunner loaded with Tasks as 
        allocated by preferences

        rtype : L{ots.server.distributor.taskrunner}
        rparam : A Taskrunner loaded with Tasks
        """
        if self._taskrunner is None:
            self._taskrunner = primed_taskrunner(self.testrun_uuid, 
                                                 self._timeout,
                                                 self.options.priority,
                                                 self.options.device,
                                                 self.options.image,
                                                 self.options.hw_packages,
                                                 self.options.host_packages,
                                                 self.options.emmc,
                                                 self.options.testfilter,
                                                 self.options.flasher,
                                                 self.publishers)

        return self._taskrunner

    ################################
    # RUN
    ################################

    def run(self):
        """
        Start a Testrun and publish the data

        @rtype : C{bool}
        @rparam : True if the Testrun passes otherwise False
        """    
        testrun_result = None
        ret_val = False
        LOG.debug("Initialising Testrun")
        try:
            is_hw_enabled = bool(len(self.options.hw_packages))
            is_host_enabled = bool(len(self.options.host_packages))
            testrun = Testrun(is_hw_enabled = is_hw_enabled, 
                              is_host_enabled = is_host_enabled)
            #FIXME: Cheap hack to make testable
            testrun.run_test = self.taskrunner.run
            testrun_result = testrun.run()
            LOG.debug("Testrun finished with result: %s"%(testrun_result))
            self.publishers.set_testrun_result(testrun_result)
            self.publishers.set_expected_packages(testrun.expected_packages)
            self.publishers.set_tested_packages(testrun.tested_packages)
            self.publishers.set_results(testrun.results)
            self.publishers.set_monitors(testrun.monitors)

        except Exception, err:
            LOG.debug("Testrun Exception: %s"%(err))
            LOG.debug(traceback.format_exc())
            self.publishers.set_exception(sys.exc_info()[1])

        self.publishers.publish() 
        if testrun_result:
            ret_val = True
        return ret_val
