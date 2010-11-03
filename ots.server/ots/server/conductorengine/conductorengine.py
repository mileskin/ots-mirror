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

"""Ots TA Engine plugin"""
from ots.common.interfaces.taengine import TAEngine
from ots.common.routing.routing import get_routing_key
from ots.server.conductorengine.conductor_command import get_commands
from ots.server.distributor.api import OtsQueueDoesNotExistError, \
    OtsGlobalTimeoutError, OtsQueueTimeoutError, OtsConnectionError
from ots.server.distributor.api import taskrunner_factory
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import STATUS_SIGNAL
from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL


import logging 

class ConductorEngine(TAEngine):
    """
    TAEngine component for ots distributor.
    """

    def __init__(self, ots_config, taskrunner=None):
        self._ots_config = ots_config 
        self.log = logging.getLogger(__name__)
        self.log.debug("Initialising Ots Adapter")
        self._distribution_model = None
        self._routing_key = ""
        self._timeout = None
        self._image_url = ""
        self._emmc_flash_parameter = ""
        self._testrun_id = ""
        self._test_list = dict()
        self._storage_address = ""
        self._test_filter = ""
        self._flasher = ""
        self._taskrunner = taskrunner
    
    def _init_ots_from_testrun(self, testrun):
        """
        Hardware specific unpacking helper method
        """
        self._distribution_model = testrun.get_option('distribution_model')
        self._routing_key = get_routing_key(testrun.get_option("device"))
        self.log.info("Using routing key %s" % self._routing_key)
        self._timeout = testrun.get_timeout()*60
        self._image_url = testrun.get_image_url()
        self._emmc_flash_parameter = testrun.get_option('emmc')
        self._testrun_id = testrun.get_testrun_id()        
        self._flasher = testrun.get_option('flasher')

        # Check for device tests
        if testrun.get_testpackages():
            self.log.debug("Found device tests")
            self._test_list['device'] = ",".join(testrun.get_testpackages()) 
        # Check for host tests
        if testrun.get_host_testpackages():
            self.log.debug("Found host tests")
            self._test_list['host'] = ",".join(testrun.get_host_testpackages())


        service_host = self._ots_config['host']
        service_port = self._ots_config['port']

        self._storage_address = service_host+":"+str(service_port)
        self._test_filter = ""
        if testrun.get_option('testfilter'):
            filter_string = testrun.get_option('testfilter').replace('"',"'")
            self._test_filter =  "\"%s\"" % filter_string
            

        
    def execute(self, testrun):
        """
        Satisfies the TAEngine interface 
        """
        self._init_ots_from_testrun(testrun)

        if not self._taskrunner:
            self._taskrunner = taskrunner_factory(self._routing_key,
                                                  self._timeout,
                                                  testrun.get_testrun_id())

    # Ignoring "unused argument warning"
    # pylint: disable-msg=W0613    

        def results_callback(signal, **kwargs):
            """
            Callback for storing resultfiles
            """
            testrun.add_result_object(kwargs['result'])

        def status_callback(signal, **kwargs):
            """
            Callback for changing testrun state
            """
            testrun.set_state(kwargs['state'], kwargs['status_info'])

        def error_callback(signal, **kwargs):
            """
            Callback for testrun error
            """
            testrun.set_result("ERROR")
            testrun.set_error_info(kwargs['error_info'])
            testrun.set_error_code(kwargs['error_code'])

        def packagelist_callback(signal, **kwargs):
            """
            Callback for packagelist messages
            """

            testrun.add_executed_packages(kwargs['environment'],
                                          kwargs['packages'])

        RESULTS_SIGNAL.connect(results_callback)
        STATUS_SIGNAL.connect(status_callback)
        ERROR_SIGNAL.connect(error_callback)
        PACKAGELIST_SIGNAL.connect(packagelist_callback)

        cmds = get_commands(self._distribution_model,
                            self._image_url,
                            self._test_list,
                            self._emmc_flash_parameter,
                            self._testrun_id,
                            self._storage_address,
                            self._test_filter,
                            self._flasher)

        try:

            for cmd in cmds:
                self._taskrunner.add_task(cmd)
            self._taskrunner.run()

        except OtsQueueDoesNotExistError:
            error_info = "Queue '%s' does not exist" \
                % (self._routing_key)
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
            self.log.exception(error_info)

        except OtsGlobalTimeoutError:
            error_info = ("Server side timeout. (Worker went offline during "+\
                              "testrun or some tasks were not started in time)")
                              
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
            self.log.exception(error_info)

        except OtsConnectionError:
            error_info = "A connectivity issue was encountered"
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
            self.log.exception(error_info)

        except OtsQueueTimeoutError, exception:
            error_info = ("The job was not started within %s minutes. "+\
                "A worker in that devicegroup may be down or there may be "+\
                "exceptional demand") % str(exception.timeout_length / 60)
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
            self.log.exception(error_info)

        except Exception:
            error_info = "A miscellaneous error was encountered"
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
            self.log.exception(error_info)


    def name(self):
        """Returns the name of the engine"""
        return "ConductorEngine"
