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
Defines the interface for the
Testrun options
as provided by OTS clients.
"""

from ots.server.hub.parameters_parser import string_2_list, string_2_dict

from ots.server.allocator.api import PERPACKAGE

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

    def __init__(self, image, packages = None, plan = None,hosttest = None,
                 device = {}, emmc = None, distribution_model = None,
                 flasher = None, testfilter = None, timeout = None,
                 input_plugin = None):
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
        self._hosttest = hosttest
        self._device = device#string_2_dict(device)
        self._emmc = emmc
        self._distribution_model = distribution_model
        self._flasher = flasher
        self._testfilter = testfilter
        self.input_plugin = input_plugin # Deprecated
        self._timeout = timeout
        self._validate_packages(self.hw_packages)

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
