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
The rules for checking 
whether all the Packages in the run  
meet a global pass / fail criteria
""" 

from copy import copy

from ots.results.testrun_result import TestrunResult

class PackageException(Exception):
    """Problem with the Package"""
    pass

def _check_host_testing(is_host_enabled, expected_packages_list):
    """
    @type is_host_enabled: C{bool}
    @param is_host_enabled: Is host testing enabled
    
    @type expected_packages: C{list} of 
                                L{ots.common.api.EnvironmentPackages}  
    @param expected_packages: packages requested for execution in the run
    
    If host testing specified are there host packages?
    """
    if is_host_enabled:
        if not any([package.is_host_tested 
                 for package in expected_packages_list]):
            msg = "Host testing enabled but no host packages found "
            raise PackageException(msg)
    

def _check_hw_testing(is_hw_enabled, expected_packages_list):
    """
    @type is_hw_testing_enabled: C{bool}
    @param is_hw_testing_enabled: Is hardware testing enabled
    
    @type expected_packages: C{list} of 
                                L{ots.common.api.EnvironmentPackages}  
    @param expected_packages: packages requested for execution in the run
    
    If hardware testing specified are there hardware test packages?
    """
    if is_hw_enabled:
        if not any([package.is_hw_tested 
                for package in expected_packages_list]):
            msg = "Hardware testing enabled but no hardware packages found" 
            raise PackageException(msg)


def _check_all_results(expected_packages_list, 
                       tested_packages_list):
    """
    @type expected_packages_list: C{list} of 
                                L{ots.common.api.EnvironmentPackages}  
    @param expected_packages_list: packages requested for execution in the run

    @type tested_packages_list: C{list} consisting of L{PackageResults}
    @param tested_packages_list: The packages that have been executed 
                             *and* have results

    Are there Tested Packages for all the Expected Packages?
    """
    not_run_packages_list = copy(expected_packages_list)
    for expected_pkg in expected_packages_list:
        for tested_pkg in tested_packages_list:
            if expected_pkg == tested_pkg:
                not_run_packages_list.remove(expected_pkg)
    if not_run_packages_list:
        pretty_list = ','.join(["%s:%s"%(pkg.environment, pkg.packages) 
                                for pkg in not_run_packages_list])
        msg = "Missing packages: %s"%(pretty_list)
        raise PackageException(msg)

def _check_run_validity(expected_packages_list,
                        results_packages_list,
                        is_hw_enabled,
                        is_host_enabled):
    """
    @type expected_packages: C{list} of 
                                L{ots.common.api.EnvironmentPackages}  
    @param expected_packages: packages requested for execution in the run

    @type results_package_list: C{list} consisting of L{PackageResults}
    @param results_package_list: The packages that have been executed 
                             *and* have results

    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: Is hardware testing enabled

    @type is_host_enabled: C{bool}
    @param is_host_enabled: Is host testing enabled
    """
    #Have any packages been found at all?
    if not expected_packages_list:
        raise PackageException("No packages found")
    #
    _check_hw_testing(is_hw_enabled, 
                      expected_packages_list)
    _check_host_testing(is_host_enabled, 
                        expected_packages_list)
    _check_all_results(expected_packages_list, results_packages_list)
        
def _reduce_results_package(results_packages_list,
                            insignificant_tests_matter):

    """
    @type results_package_list: C{list} of L{ots.common.api.PackageResults}
    @param: results_packages_list: A list of the packages with results

    @rtype: L{TestrunResult}
    @return: PASS / FAIL / NO_CASES

    Reduces a list of package results to a single Pass / Fail
    """

    ret_val = TestrunResult.NO_CASES
    results = []
    for package_results in results_packages_list:
        results.extend(package_results.significant_results)
        if insignificant_tests_matter:
            results.extend(package_results.insignificant_results)
    if results:
        if results.count(TestrunResult.PASS) == len(results):
            ret_val = TestrunResult.PASS
        else:
            ret_val = TestrunResult.FAIL
    return ret_val


def go_nogo_gauge(expected_packages_list,
                  results_packages_list, 
                  is_hw_enabled,
                  is_host_enabled,
                  insignificant_tests_matter):
    """
    @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @type results_packages_list: C{list} of L{ots.common.api.PackageResults}
    @param: results_packages_list: A list of the packages with results

    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: 

    @type is_host_enabled: C{bool}
    @param is_host_enabled:

    @type insignificant_tests_enabled: C{bool}
    @param insignificant_tests_matter: 

    @rtype: L{TestrunResult}
    @return: PASS / FAIL / NO_CASES

    Determines Pass / Fail for the Testrun
    """
    #_check_run_validity(expected_packages_list,
    #                    results_packages_list,
    #                    is_hw_enabled,
    #                    is_host_enabled)
    #return _reduce_results_package(results_packages_list,
    #                               insignificant_tests_matter)
