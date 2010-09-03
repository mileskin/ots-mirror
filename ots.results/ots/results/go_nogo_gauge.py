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

HARDWARE = "hardware"
HOST_HARDWARE = "host_hardware"

class PackageException(Exception):
    """Problem with the Package"""
    pass

def _check_run_validity(expected_packages_list,
                        is_hw_enabled,
                        is_host_testing_enabled,
                        results_packages_list):
    """
    @type expected_packages: C{list} of 
                                L{ots.common.api.EnvironmentPackages}  
    @param expected_packages: packages requested for execution in the run

    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: Is hardware testing enabled

    @type is_host_testing_enabled: C{bool}
    @param is_host_testing_enabled: Is host testing enabled

    @type package_results_list: C{list} consisting of L{PackageResults}
    @param package_results_list: The packages that have been executed 
                             *and* have results
    """
    #Have any packages been found at all?
    if not expected_packages_list:
        raise PackageException("No packages found")
    
    #If host testing specified are there host packages?
    if is_host_testing_enabled:
        if not any([package.is_host_tested 
                 for package in expected_packages_list]):
            msg = "Host testing enabled but no host packages found "
            raise PackageException(msg)
    
    #If hardware testing specified are there hardware test packages?
    if is_hw_enabled:
        if not any([package.is_hw_tested 
                for package in expected_packages_list]):
            msg = "Hardware testing enabled but no hardware packages found" 
            raise PackageException(msg)

    #Have we got all the results for the packages found?
    #This algorithm sucks 
    not_run_packages_list = copy(expected_packages_list)
    for expected_pkg in expected_packages_list:    
        for results_pkg in results_packages_list:
            if expected_pkg == results_pkg:
                not_run_packages_list.remove(expected_pkg)
    if not_run_packages_list:
        pretty_list = ','.join([str(pkg) for pkg in not_run_packages_list])
        msg = "Missing packages %s"%(pretty_list)
        raise PackageException(msg)
        
def _reduce_package_results(package_results_list,
                            insignificant_tests_matter):

    """
    @type package_results_list: C{list} of L{ots.common.api.PackageResults}
    @param: package_results_list: A list of the packages with results

    @rtype: L{TestrunResult}
    @return: PASS / FAIL / NO_CASES

    Reduces a list of package results to a single Pass / Fail
    """

    ret_val = TestrunResult.NO_CASES
    results = []
    for package_results in package_results_list:
        results.extend(package_results.significant_results)
        if insignificant_tests_matter:
            results.extend(package_results.insignificant_results)
    if results:
        if results.count(TestrunResult.PASS) == len(results):
            ret_val = TestrunResult.PASS
        else:
            ret_val = TestrunResult.FAIL
    return ret_val


def go_nogo_gauge(executed_packages, 
                  hardware_packages, 
                  host_packages, 
                  is_hw_testing_enabled,
                  package_results_list,
                  insignificant_tests_matter):
    """
    @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @type hardware_packages: C{list}
    @param hardware_packages: Hardware test packages

    @type host_packages: C{list}
    @param host_packages: Host test packages

    @type is_hardware_testing_enabled:
    @param is_hardware_testing_enabled:

    @type package_results_list: C{list} of L{ots.common.api.PackageResults}
    @param: package_results_list: A list of the packages with results

    @rtype: L{TestrunResult}
    @return: PASS / FAIL / NO_CASES

    Determines Pass / Fail for the Testrun
    """

    results_packages = [package.testpackage 
                        for package in package_results_list]

    _check_run_validity(executed_packages, 
                        hardware_packages, 
                        host_packages, 
                        is_hw_testing_enabled,
                        results_packages)
    return _reduce_package_results(package_results_list,
                                   insignificant_tests_matter)
