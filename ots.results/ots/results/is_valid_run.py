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
Checks whether the testrun is valid.

Verifies that all the Packages have been run  
""" 

class PackageException(Exception):
    """Problem with the Package"""
    pass

def _check_packages(expected_packages_dict):
    """
    @type expected_packages_dict: C{dict} 
                            - keys C{ots.common.Environment}
                            - values C{list} of C{string}
    @param expected_packages_dict: Is hardware testing enabled
  
    Have any packages been found at all?
    """
    if expected_packages_dict is not None:
        packages = [pkg for pkgs in expected_packages_dict.values() 
                    for pkg in pkgs]
    if expected_packages_dict is None or not packages:
        raise PackageException("No packages found")

def _check_hw_testing(is_hw_enabled, expected_packages_dict):
    """
    @type is_hw_testing_enabled: C{bool}
    @param is_hw_testing_enabled: Is hardware testing enabled
    
    @type expected_packages_dict: C{dict} 
                            - keys C{ots.common.Environment}
                            - values C{list} of C{string}
    @param expected_packages_dict:  The packages that should have been tested

    If hardware testing specified are there hardware test packages?
    """
    if is_hw_enabled:
        if not any([env.is_hw for env in expected_packages_dict.keys()]):
            msg = "Hardware testing enabled but no hardware packages found"
            raise PackageException(msg)

def _check_host_testing(is_host_enabled, expected_packages_dict):
    """
    @type is_host_enabled: C{bool}
    @param is_host_enabled: Is host testing enabled
    
    @type expected_packages_dict: C{dict} 
                            - keys C{ots.common.Environment}
                            - values C{list} of C{string}
    @param expected_packages_dict:  The packages that should have been tested

    If host testing specified are there host packages?
    """
    if is_host_enabled:
        if not any([env.is_host for env in expected_packages_dict.keys()]):
            msg = "Host testing enabled but no host packages found "
            raise PackageException(msg)
    
def _check_complete(expected_packages_dict,
                    tested_packages_dict):

    """
    @type expected_packages_dict: C{dict} 
                            - keys C{ots.common.Environment}
                            - values C{list} of C{string}
    @param expected_packages_dict: The packages that should have been tested

    @type tested_packages_dict: C{dict} 
                            - keys C{ots.common.Environment}
                            - values C{list} of C{string}
    @param tested_packages_dict: The packages that were actually tested
    """
    missing_packages = []
    #Find missing environments
    for env in set(expected_packages_dict.keys()).difference(
                                      set(tested_packages_dict.keys())):
        missing_packages.extend(expected_packages_dict[env])
    #Check the tested environments contain all packages
    for env in tested_packages_dict.keys():
        pkgs = set(expected_packages_dict[env]).difference(
                                      set(tested_packages_dict[env]))
        missing_packages.extend(pkgs)
    #Format Exception
    if missing_packages:
        pretty_list = ', '.join(missing_packages)
        msg = "Missing packages: %s" % (pretty_list)
        raise PackageException(msg)
    
def is_valid_run(expected_packages_dict,
                 tested_packages_dict,
                 is_hw_enabled,
                 is_host_enabled):
    """
    @type is_hw_enabled: C{bool}
    @param is_hw_enabled: Is hardware testing enabled

    @type is_host_enabled: C{bool}
    @param is_host_enabled: Is host testing enabled
    """
    _check_packages(expected_packages_dict)
    _check_hw_testing(is_hw_enabled, 
                      expected_packages_dict)
    _check_host_testing(is_host_enabled, 
                        expected_packages_dict)
    _check_complete(expected_packages_dict,
                    tested_packages_dict)
