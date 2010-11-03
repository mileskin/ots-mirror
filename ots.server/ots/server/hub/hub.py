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
The Hub provides a focal point for inter-component data-flow.

Hence OTS suggests a centralised topology with the Hub as it's
central component.

The role of the Hub is the high level management of a single Testrun.
Specifically:

 - Receive test request from third-party client
 - Allocate Tasks 
 - Dispatch Testrun
 - Receives results
 - Publish results
 - Persist monitoring data

"""

import sys
import os
import logging
import logging.config
import uuid
import ConfigParser
import traceback
from socket import gethostname

from ots.common.framework.config_filename import config_filename


from ots.server.allocator.api import primed_taskrunner

from ots.server.hub.testrun import Testrun
from ots.server.hub.options_factory import options_factory
from ots.server.hub.application_id import get_application_id
from ots.server.hub.publishers import Publishers

LOG = logging.getLogger(__name__)

def _init_logging():
    """
    Initialise the logging from the configuration file
    """
    #FIXME
    dirname = os.path.dirname(os.path.abspath(__file__))
    conf = os.path.join(dirname, "logging.conf")
    logging.config.fileConfig(conf)


########################
# Configuration stuff
########################

def _timeout():
    """
    rtype: C{int}
    rparam: The timeout in minutes
    """
    server_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    app_id = get_application_id() 
    conf = config_filename(app_id, server_path)
    config = ConfigParser.ConfigParser()
    config.read(conf)       
    return int(config.get('ots.server.hub', 'timeout'))

def _run(sw_product, request_id, testrun_uuid, 
        notify_list, run_test, options, **kwargs):
    """
    The keystone function in the running of the tests.
    Start a Testrun and publish the data 

    @type sw_product: C{str}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{str}
    @param request_id: An identifier for the request from the client

    @type testrun_uuid: C{str}
    @param: The unique identifier for the testrun

    @type notify_list: C{list}
    @param notify_list: Email addresses for notifications
   
    @type run_test: C{callable}
    @param run_test: The run test callable

    @type options : L{Options}
    @param options: The Options for the testrun
    """    
   
    LOG.debug("Initialising Testrun")
    publishers = Publishers(request_id, 
                            testrun_uuid, 
                            sw_product, 
                            options.image,
                            **kwargs)

    try:
        is_hw_enabled = bool(len(options.hw_packages))
        is_host_enabled = bool(len(options.host_packages))
        testrun = Testrun(is_hw_enabled = is_hw_enabled, 
                          is_host_enabled = is_host_enabled)
        testrun.run_test = run_test
        testrun_result = testrun.run()
        LOG.debug("Testrun finished with result: %s"%(testrun_result))
        
        publishers.set_testrun_result(testrun_result)
        publishers.set_expected_packages(testrun.expected_packages)
        publishers.set_tested_packages(testrun.tested_packages)
        publishers.set_results(testrun.results)
            
    except Exception, err:
        LOG.debug("Testrun Exception: %s"%(err))
        LOG.debug(traceback.format_exc())
        publishers.set_exception(sys.exc_info()[1])

    publishers.publish() 


#########################################
# PUBLIC
#########################################

def run(sw_product, request_id, notify_list, options_dict):
    """
    The interface for the hub.
    Processes the raw parameters and fires a testrun

    @type sw_product: C{str}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{str}
    @param request_id: An identifier for the request from the client

    @type notify_list: C{list}
    @param notify_list: Email addresses for notifications

    #FIXME legacy interface 
    @type options_dict: C{dict}
    @param options_dict: A dictionary of options
    """
    sw_product = sw_product.lower()
    options = options_factory(sw_product, options_dict)
    taskrunner = primed_taskrunner(testrun_uuid, 
                                    _timeout(),
                                   options.priority,
                                   options.device,
                                   options.image,
                                   options.hw_packages,
                                   options.host_packages,
                                   options.emmc,
                                   options.testfilter,
                                   options.flasher)
    testrun_uuid = uuid.uuid1().hex
    _run(sw_product, request_id, testrun_uuid, notify_list, 
         taskrunner.run, options)
