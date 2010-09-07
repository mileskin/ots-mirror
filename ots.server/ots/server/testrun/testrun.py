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
import logging

from collections import defaultdict

from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL

from ots.results.api import parse_results
from ots.results.api import go_nogo_gauge
from ots.results.api import TestrunResult
#FIXME
from ots.results.is_valid_run import is_valid_run
from ots.common.api import Environment

LOG = logging.getLogger(__name__)

class TestrunException(Exception):
    """
    Reraise Exceptions from Workers
    """
    pass

class Testrun(object):
    """
    Holds the metadata associated with a Testrun 
    
    Wraps the handlers and runner and hooks up the results

    Closely associated with the Taskrunner
    """
    
    def __init__(self, 
                 run_test,
                 is_hw_enabled = True,
                 is_host_enabled = False,
                 insignificant_tests_matter = True):
        """
        @type run_test: C{callable} The callable to run
        @param run_test: The callable to run
        @type is_hw_enabled: C{bool} 
        @param is_hw_enabled: Flag

        @type is_host_enabled: C{bool}
        @param is_host_enabled: Flag

        @type insignificant_tests_matter: C{bool} 
        @param insignificant_tests_matter: Flag
        """
        self._run_test = run_test
        self.is_hw_enabled = is_hw_enabled
        self.is_host_enabled = is_host_enabled
        self.insignificant_tests_matter = insignificant_tests_matter
        #
        self.results_xmls = []
        self.tested_packages_dict = defaultdict(list)
        self.expected_packages_dict = defaultdict(list)

    ###########################################
    # HANDLERS
    ###########################################

    def _results_cb(self, signal, result, sender, **kwargs):
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type result: L{ots.common.api.ResultObject}
        @param result: The Results Objects

        @type sender: C{str}
        @param sender: The name of the sender of the Signal

        Handler for results
        """
        LOG.debug("Received results: %s from %s"%(result, sender))
        #
        environment = Environment(result.environment)
        self.tested_packages_dict[environment].append(result.testpackage)
        #
        self.results_xmls.append(result.content)

    def _packagelist_cb(self, signal, environment, packages, sender, **kwargs): 
        """
        @type signal: L{django.dispatch.dispatcher.Signal}
        @param signal: The django signal

        @type environment: C{str}
        @param environment: The environment that the test was run under

        @type packages: C{list} of C{str}
        @param packages: The packages executed by the Testrun

        @type sender: C{str}
        @param sender: The name of the sender of the Signal

        Handler for package list
        """
        LOG.debug("Received packages: %s from %s"%(packages, sender))

        environment = Environment(environment)
        self.expected_packages_dict[environment].extend(packages)

    @staticmethod
    def _error_cb(signal, error_info, error_code, sender, **kwargs):
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
        LOG.debug("Received error: %s:%s from %s"%(error_info, error_code, 
                                                   sender))
        #FIXME: Use Python Exceptions
        msg = "%s: %s" % (error_info, error_code)
        raise TestrunException(msg)
   
    #############################################
    # HELPERS
    #############################################
            
    def _go_nogo(self):
        """
        @rtype: L{TestrunResult}
        @return: PASS / FAIL / NO_CASES
        """
        #FIXME this should be moved out 
        ret_val = TestrunResult.NO_CASES
        aggregated_results = []
        for results_xml in self.results_xmls:
            all_passed = parse_results(results_xml,
                                       self.insignificant_tests_matter)
            if all_passed is not None:
                aggregated_results.append(all_passed)
        if aggregated_results:
            if all(aggregated_results):
                ret_val = TestrunResult.PASS
            else:
                ret_val = TestrunResult.NO_CASES
        return ret_val


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
        is_valid_run(self.expected_packages_dict,
                     self.tested_packages_dict,
                     self.is_hw_enabled,
                     self.is_host_enabled)
        ret_val = self._go_nogo()
        return ret_val
