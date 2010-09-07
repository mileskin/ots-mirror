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

"""This backend determines the testrun overall result"""

from ots.common.results.result_backend import ResultBackend
import re
import logging

PASS = "PASS"
FAIL = "FAIL"
NO_CASES = "NO_CASES"
ERROR = "ERROR"

class ResultJudge(ResultBackend):
    """
    This backend determines the overall result of the testrun and sets it to 
    PASS, FAIL, NO_CASES or ERROR. If result is already set to ERROR, this 
    backend should have no effect to the result - this is assured with the logic
    in testrun.set_result(). It should keep the first occurrence of ERROR. 

    Prerequirements: 
    Values dictionary must contain following attributes: result, insignificant
    """

    
    def __init__(self, testrun_object, insignificant_tests_matter = False):
        self.log = logging.getLogger(__name__)
        self.testrun = testrun_object
        self.active_package = ""
        self.testcase_results = dict() #test cases with insignificant == 'false'
        self.testcase_results_insig = dict() #insignificant == 'true'
        self.insignificant_tests_matter = insignificant_tests_matter
        self.log.info("Insignificant test cases are taken into account")

    def _overall_result(self,
                        packages_significant_results, 
                        packages_insignificant_results, 
                        results_packages, 
                        insignificant_tests_matter):
        """
        Make an overall result judgement for the given packages
        from the supplied datastructures.

        @type packages_significant_results: C{dictionary} 
                                   keys: C{string} 
                                   values: C{list} of C{strings) 
        @param packages_significant_results: significant results packages

        @type insignificant_results: C{dictionary} 
                                   keys: C{string} 
                                   values: C{list} of C{strings) 

        @param packages_significant_results: insignificant results packages

        @type packages: C{list}
        @param results_packages: The test packages 

        @type insignificant_tests_matter: C{boolean}
        @param insignificant_tests_matter: Insignificant tests are judged 
                    
        @rtype: C{string} 
        @return: pass, fail, no_cases
        """
        ret_val = NO_CASES

        #Rationalise the dicts into a list of capitalised results strings
        results =  []
        for pkg in results_packages:
            results.extend(packages_significant_results[pkg])
        if insignificant_tests_matter:
            for pkg in results_packages:
                results.extend(packages_insignificant_results[pkg])
        results = [result.upper() for result in results]
        #Make judrgement
        if results:
            self.log.debug("No of Passes: %s"%(results.count(PASS)))
            if results.count(PASS) == len(results):
                ret_val = PASS
            else:
                ret_val = FAIL
        return ret_val
            
    def name(self):
        """Returns the name of the backend"""
        return "ResultJudge"

    def pre_process_xml_file(self, result_object, testrun):
        """
        Initialize processing of test package for certain test environment.
        Call for this method means we got results for the package + environment.
        """
        self.active_package = result_object.get_testpackage()+ \
                                  "-"+result_object.get_environment().lower()
        self.testcase_results[self.active_package] = []
        self.testcase_results_insig[self.active_package] = []

    def pre_process_case(self, values):
        """Save test case result into list. Called for each test case."""
        try:
            insignificant = values["insignificant"].lower()
        except KeyError:
            insignificant = "false"

        if insignificant == 'false':
            self.testcase_results[self.active_package].append(values["result"])
        elif insignificant == 'true':
            self.testcase_results_insig[self.active_package].append( \
                                                              values["result"])
        else:
            raise Exception("insignificant attribute must be 'false' or 'true'"\
                " but it was %s" % insignificant)

    def finished_processing(self):
        """
        Sets testrun result to one of these: (PASS, FAIL, NO_CASES, ERROR).

        This method is executed only once for the whole testrun. All the test
        results (i.e. result objects, extracted from result xml files) that were
        introduced via pre_process_xml_file() method are taken into account
        here.

        Note: 
        We're dependant on the logic in testrun.set_result() in situations where
        the result is already ERROR.

        Determining the testrun result:

        - ERROR: 
           * Test results (xml file) was not received for any of the required
             test packages. 
           * Required test packages are not defined by user nor by worker.

        - NO_CASES: No test cases found in any of the received results.

        - PASS or FAIL: If any of the test cases contained in the received test 
        results has failed result is FAIL, otherwise result is PASS.
        """

        self.log.info("Checking that there are executed test packages")

        required_packages = self._get_list_of_required_packages()

        #If required packages is undefined at this point, there was a problem 
        #somewhere. This could indicate for example bad error handling in server
        #or worker code e.g. in a situation where networking had failed.
        if not required_packages:
            self.testrun.set_result(ERROR) 
            self.testrun.set_error_info("No test packages defined nor found.")
            return

        packages_with_results = self.testcase_results.keys()
        missing = packages_lacking_results(required_packages,
                                           packages_with_results)
        if missing:
            self.log.info("Did not get results for all packages")
            self.log.info("Results missing from: %s" % missing)
            self.testrun.set_result("ERROR")
            self.testrun.set_error_info("Results missing from: %s" \
                                        % ", ".join(missing))
            return

        self.log.info("Examining test results...")
        result = self._overall_result(self.testcase_results, 
                                      self.testcase_results_insig, 
                                      packages_with_results, 
                                      self.insignificant_tests_matter)
        self.log.info("Setting testrun result to %s"%(result))
        self.testrun.set_result(result)

    def _get_list_of_required_packages(self):
        """
        Generates a list of test packages defined in testrun.

        Returns:
            A list of strings in form "testpackage-environment".
        """

        def host_tests_found(pkgs):
            """Return True if pkgs dict has at least one key for a host test"""
            return any([key for key in pkgs.keys() if re.match("host.*", key)])

        all_packages = []
        executed = self.testrun.get_all_executed_packages() #provided by workers
        packages = self.testrun.get_testpackages() #user-defined. For HW and SB
        host_packages = \
            self.testrun.get_host_testpackages() #user-defined. For Host
        hw_enabled = self.testrun.hardware_testing_enabled()
        sb_enabled = self.testrun.scratchbox_testing_enabled()

        self.log.debug("User-defined test packages: %s" % packages)
        self.log.debug("User-defined host test packages: %s" % host_packages)
        self.log.debug("Executed packages returned from worker: %s" % executed)

        #Executed packages per environment are the required packages
        for environment in executed.keys():
            for package in executed[environment]:
                all_packages.append(package+"-"+environment.lower())

        #If executed list does not contain packages for all the environments
        #that were specified by user, append the package list with 
        #packages provided by user for that environment.
        #This can happen for example if a worker times out after image flashing
        #and if timeout is not detected and handled properly before this code
        #is executed.

        #Note: "host_scratchbox" is not checked below!

        if not host_tests_found(executed) and host_packages and hw_enabled:
            for package in host_packages:
                all_packages.append(package+"-host_hardware")

        if not 'hardware' in executed.keys() and packages and hw_enabled:
            for package in packages:
                all_packages.append(package+"-hardware")

        if not 'scratchbox' in executed.keys() and packages and sb_enabled:
            for package in packages:
                all_packages.append(package+"-scratchbox")

        self.log.debug("Required packages: %s" % all_packages)

        return all_packages


def packages_lacking_results(required_packages, packages_with_results):
    """Returns list of required packages that got no results"""
    packages = []
    for pkg in required_packages:
        if pkg not in packages_with_results:
            packages.append(pkg)
    return packages


