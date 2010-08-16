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
Runs an OTS Testrun 
"""

from ots.common.api import OTSProtocol
from ots.common.api import ExecutedPackage

from ots.server.distributor.api import taskrunner_factory
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import STATUS_SIGNAL
from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL

from ots.server.distributor.api import OtsQueueDoesNotExistError
from ots.server.distributor.api import OtsGlobalTimeoutError
from ots.server.distributor.api import OtsQueueTimeoutError
from ots.server.distributor.api import OtsConnectionError

from ots.server.results.api import parse_results, PackageException
from ots.server.results.api import go_nogo_gauge
from ots.server.results.api import TestrunResult


class TestrunException(Exception):
    pass

class Testrun(object):
    """
    Holds the metadata associated with a Testrun 
    
    Wraps the handlers and runner and hooks up the results

    Closely associated with the Taskrunner
    """
    
    def __init__(self, 
                 run_test,
                 hardware_packages = None,
                 host_packages = None,
                 is_hw_testing_enabled = True,
                 insignificant_tests_matter = True):
        """
        @type run_test: C{callable} The callable to run
        @param run_test: The callable to run

        @type hardware_packages: C{List} 
        @param hardware_packages: Names of the packages to be run on the device

        @type host_packages: C{List} 
        @param host_packages: Names of the packages to be run as host tests

        @type is_hw_testing_enabled: C{bool} 
        @param is_hw_testing_enabled: Flag

        @type insignificant_tests_matter: C{bool} 
        @param insignificant_tests_matter: Flag
        """
        self._run_test = run_test
        self.is_hw_testing_enabled = is_hw_testing_enabled
        if hardware_packages is None:
            self.hardware_packages = []
        if host_packages is None:
            self.host_packages = []
        self.insignificant_tests_matter = insignificant_tests_matter
        #
        self.results = [] #Results from the testrun
        self.executed_packages = {} #All packages executed by the testrun
        self.environment = None       

    ###########################################
    # HANDLERS
    ###########################################

    def _results_cb(self, signal, result, sender):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type result: L{ots.common.api.ResultObject}
        @param result: The Results Objects

        @type sender: C{str}
        @param sender: The name of the sender of the Signal

        Handler for results
        """
        self.results.append(result)

    def _packagelist_cb(self, signal, packages, sender): 
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type packages: C{list} of C{ots.common.api.ExecutedPackage}
        @param packages: The packages executed by the Testrun

        @type sender: C{str}
        @param sender: The name of the sender of the Signal

        Handler for package list
        """
        self.executed_packages = packages


    def _error_cb(self, signal, error_info, error_code, sender):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type error_info: C{str}
        @param error_info: Error Message

        @type error_code: C{int}
        @param error_code: Error Code

        @type sender: C{str}
        @param sender: The name of the sender of the Signal

        Handler for errors
        """
        #FIXME: Use Python Exceptions
        msg = "%s: %s"%(error_info, error_code)
        raise TestrunException(msg)
   
    #############################################
    # HELPERS
    #############################################

    def _package_results_iter(self):
        """
        @yield: C{List} of C{ots.common.api.PackageResults}
        
        Generator for PackageResults received in 
        course of running the test
        """
        for result in self.results:
            yield parse_results(result.content, 
                                result.testpackage, 
                                result.environment)

    def _go_nogo(self):
        """
        @rtype: L{TestrunResult}
        @return: PASS / FAIL / NO_CASES

        Helper that delegates the members accumulated in
        the testrun to the go_nogo gauge
        """
        package_results_list = list(self._package_results_iter())    
        return go_nogo_gauge(self.executed_packages,
                             self.hardware_packages,
                             self.host_packages,
                             self.is_hw_testing_enabled,
                             package_results_list,
                             self.insignificant_tests_matter)

    ####################################################
    # PUBLIC METHOD
    ####################################################

    def run(self):
        """
        @rtype: L{TestrunResult}
        @return: PASS / FAIL / NO_CASES
        
        Run...
        """

        ret_val = TestrunResult.FAIL
        RESULTS_SIGNAL.connect(self._results_cb)
        ERROR_SIGNAL.connect(self._error_cb)
        PACKAGELIST_SIGNAL.connect(self._packagelist_cb)

        self._run_test()
        ret_val = self._go_nogo()
        return ret_val
