# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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
Defines the interface for the
Testrun options
as provided by OTS clients.
"""

from ots.server.hub.parameters_parser import string_2_list, string_2_dict
from StringIO import StringIO

############################
# FLAGS
############################

TRUE = "true"
FALSE = "false"
ON = "on"

#################################
# PACKAGE NAMING DEFINITIONS
#################################

TESTS = "-tests"
TEST = "-test"
BENCHMARK = "-benchmark"

VALID_PKG_SUFFIXES = [TESTS, TEST, BENCHMARK]

###################################
# Options
###################################

class Options(object):
    """
    Interface for the options available to the client
    """

    def __init__(self, image, packages = None, plan = None, hosttest = None,
                 device = {}, emmc = None, distribution_model = None,
                 flasher = None, testfilter = None, hw_testplans = None,
                 host_testplan = None, timeout = None):
        """
        @type: C{image}
        @param: The image url


        """
        self._image = image
        if packages is None:
            packages = []
        self._packages = packages
        self._plan = plan
        if hosttest is None:
            hosttest = []
        if hw_testplans is None:
            hw_testplans = []
        self._hw_testplans = hw_testplans
        if host_testplan is None:
            host_testplan = []
        self._host_testplan = host_testplan
        self._hosttest = hosttest
        self._device = device#string_2_dict(device)
        self._emmc = emmc
        self._distribution_model = distribution_model
        self._flasher = flasher
        self._testfilter = testfilter
        self._timeout = timeout
        self._validate_packages(self.hw_packages)
        self._validate_distribution_models(distribution_model,
                                           self.hw_packages \
                                               + self.host_packages)


    ##################################
    # PROPERTIES
    ##################################

    @property
    def image(self):
        """
        @rtype: C{str}
        @return: The URL of the image
        """
        return self._image

    @property
    def hw_packages(self):
        """
        @rtype: C{list} of C{str}
        @return: Packages for hardware testing
        """
        return string_2_list(self._packages)

    @property
    def host_packages(self):
        """
        @rtype: C{list} of C{str}
        @return: Packages for host testing
        """
        return string_2_list(self._hosttest)
    
    @property
    def hw_testplans(self):
        """
        @rtype: C{list} of C{str}
        @return: Test plans for hardware testing
        """
        if len(self._hw_testplans) > 0:
            if not isinstance(self._hw_testplans[0], StringIO):
                self._hw_testplans = self._convert_testplans(self._hw_testplans)
        return self._hw_testplans

    @property
    def host_testplans(self):
        """
        @rtype: C{list} of C{str}
        @return: Test plans for host testing
        """
        if len(self._host_testplan) > 0:
            if not isinstance(self._host_testplan[0], StringIO):
                self._host_testplan = self._convert_testplans(self._host_testplan)
        return self._host_testplan

    @property
    def testplan_id(self):
        """
        @rtype: C{str}
        @return: The Testplan id
        """
        return self._plan

    @property
    def device_properties(self):
        """
        @rtype: C{dict}
        @return: A dictionary of device properties this testrun requires
        """
        ret_val = {}
        if self._device is not None:
            if isinstance(self._device, dict):
                ret_val = self._device
            else:
                ret_val = string_2_dict(self._device)
        return ret_val 

    @property
    def emmc(self):
        """
        @rtype: C{str}
        @return: Url to the additional content image (memory card image)
        """
        return self._emmc

    @property
    def distribution_model(self):
        """
        @rtype: C{str}
        @return: The name of the Distribution Model
        """
        return self._distribution_model 

    @property
    def flasher(self):
        """
        @rtype: C{str}
        @return: The URL of the flasher
        """
        return self._flasher

    @property
    def testfilter(self):
        """
        @rtype: C{str}
        @return: The test filter string for testrunner-lite
        """
        if self._testfilter is not None:
            testfilter = self._testfilter.replace('"',"'")
            return "\"%s\"" % testfilter

    @property
    def timeout(self):
        """
        @rtype: C{int}
        @return: Test execution timeout in minutes
        """
        if self._timeout is None:
            self._timeout = 0
        return int(self._timeout)

    ############################
    # HELPERS
    ############################

    @staticmethod
    def _is_valid_suffix(package):
        """
        @type package: C{str}
        @param package: The package name
        """
        return any(map(package.endswith, VALID_PKG_SUFFIXES))

    @staticmethod
    def _validate_distribution_models(distribution_model, packages):
        """
        checks that all required options for given distribution model are
        defined. Raises ValueError if something is missing.

        @type distribution_model: C{str}
        @param distribution_model: Name of the distribution model

        @type packages: C{str}
        @param packages: Testpackage names separated by comma

        """
        # Check that packages are defined if "perpackage" distribution is used
        if distribution_model == 'perpackage' and len(packages) == 0:
            error_msg = "Test packages must be defined for specified "\
                +"distribution model '%s'" % distribution_model
            raise ValueError(error_msg)


    def _validate_packages(self, packages):
        """
        checks that given testpackages match our naming definitions

        Raises ValueError if invalid packages given

        @type test_packages: D{List} consiting of D{str}
        @param test_packages: List of test package names

        """
        invalid_packages = [pkg for pkg in packages
                              if not self._is_valid_suffix(pkg)]
        if invalid_packages:
            pretty_packages =  ', '.join(invalid_packages)
            error_msg = "Invalid testpackage(s): %s" % pretty_packages
            raise ValueError(error_msg)
    
    def _convert_testplans(self, test_plans):
        """
        Converts list of test plans to StringIO.
        
        @type test_plans: D{list} of D{tuple}
        @param test_plans: List of test plans
        
        @rtype : D{List} of D{StringIO}
        @return: List of test plans as StringIO
        
        """
        ret_list = []
        for (plan_name, plan_data) in test_plans:
            data = StringIO(plan_data)
            data.name = plan_name
            ret_list.append(data)
        return ret_list
