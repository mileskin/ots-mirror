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

#FIXME: A WIP

"""
The rules for checking the aggregate packages 
meet the global pass / fail criteria
""" 

from ots.results.testrun_result import TestrunResult

HARDWARE = "hardware"
HOST_HARDWARE = "host_hardware"

class PackageException(Exception):
    """Problem with the Package"""
    pass

def _has_host_tested(executed_packages):
    """
    @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @rtype: C{bool}
    @return: Has one of the executed packages contain a host tested
    """
    return any([exec_pkg.is_host_test 
                for exec_pkg in executed_packages])


def _has_hardware_tested(executed_packages):
    """
    @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @rtype: C{bool}
    @return: Has one of the executed packages hardware tested
    """
    return any([exec_pkg.is_hardware 
                for exec_pkg in executed_packages])


def _required_packages(executed_packages, 
                       hardware_packages, 
                       host_packages, 
                       is_hw_enabled):
    """
   @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @type hardware_packages: C{list}
    @param hardware_packages: Hardware test packages

    @type host_packages: C{list}
    @param host_packages: Host test packages

    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: Is hardware testing enabled

    #FIXME Change this datastructure once the intent is established
    #Not sure why whis isn't just a list of packages

    @rtype: C{List} of C{Tuple} consisting of C{string}, C{string}
    @return: A list of testpackages,environment  ??? 
    """
    #FIXME: The logic and intent in the original code is not at all
    #clear. This mimics the original code as much as possible
    #but it either needs input from the authors
    #or (better?) analysis of what is really wanted

    all_packages = []

    #FIXME Why this repacking?
    for executed_package in executed_packages:
        environment = executed_package.environment
        for package in executed_package.packages:
            all_packages.append((package, environment))

    if (not _has_host_tested(executed_packages) 
                          and host_packages 
                          and is_hw_enabled):
        for package in host_packages:
            all_packages.append((package, HOST_HARDWARE))

    if (not _has_hardware_tested(executed_packages) 
                     and hardware_packages 
                     and is_hw_enabled):
        for hardware_package in hardware_packages:
            all_packages.append((hardware_package , HARDWARE))
    return all_packages

def _check_run_validity(executed_packages, 
                        hardware_packages, 
                        host_packages, 
                        is_hw_enabled,
                        results_packages):
    """
    @type executed_packages: C{list} of L{ots.common.api.ExecutedPackage}  
    @param executed_package: packages executed on the Testrun 

    @type hardware_packages: C{list}
    @param hardware_packages: Hardware test packages

    @type host_packages: C{list}
    @param host_packages: Host test packages

    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: Is hardware testing enabled

    @type results_packages: C{list} consisting of C{string}
    @param results_packages: The names of the packages that have results

    #FIXME Check this
    Verifies what was actually run on the testrun with what should
    have been run 
    """
    required_packages = _required_packages(executed_packages, 
                                           hardware_packages, 
                                           host_packages, 
                                           is_hw_enabled)
    if not required_packages:
        raise PackageException("No test packages defined nor found.")
    
    required_packages_set = set([pkg for pkg, env in required_packages])
    missing = required_packages_set.difference(results_packages)
    if missing: 
        missing = ", ".join(missing)
        raise PackageException("Missing results in: %s"%(missing)) 


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
