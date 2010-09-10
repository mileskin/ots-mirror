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

import re

############################
# FLAGS
############################

TRUE = "true"
FALSE = "false"
PERPACKAGE = "perpackage"
BIFH = "bifh"
ON = "on"

#################################
# PACKAGE NAMING DEFINITIONS
#################################

TESTS = "-tests"
TEST = "-test"
BENCHMARK = "-benchmark"

VALID_PKG_SUFFIXES = [TESTS, TEST, BENCHMARK]

#################################
# Options Factory
#################################

def options_factory(options_dict):
    """
    @type options_dict : C{dict}
    @param options_dict: The dictionary of options

    Adapts the options dictionary to the interface
    """
    #sanitise the options dict
    #hyphens aren't Python friendly
    options_dict = dict([(k.replace("-","_"), v) for k,v in
                         options_dict.items()])
    return Options(**options_dict)

###################################
# Options
###################################

class Options(object):
    """
    Interface for the options available to the client
    """

    def __init__(self, image,
                       packages = None, plan = None, execute = TRUE,
                       gate = None, label = None, hosttest = None,
                       device = None, emmc = None, distribution_model = None,
                       flasher = None, testfilter = None, input_plugin = None,
                       email = None, email_attachments = None, **kwargs):
        """
        @type: C{image}
        @param: The image url


        """
        self._image = image
        if packages is None:
            packages = []
        self._packages = packages
        self._plan = plan
        self._execute = execute
        self._gate = gate
        self._label = label
        if hosttest is None:
            hosttest = []
        self._hosttest = hosttest
        self._device = device
        self._emmc = emmc
        self._distribution_model = distribution_model
        self._flasher = flasher
        self._testfilter = testfilter
        self._input_plugin = input_plugin
        self._email = email
        self._email_attachments = email_attachments

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
        #TODO check definition
        return self._string_2_list(self._packages)

    @property
    def host_packages(self):
        """
        @rtype: C{list} of C{str}
        @return: Packages for host testing
        """
        #TODO check definition
        return self._string_2_list(self._hosttest)

    @property
    def testplan_id(self):
        """
        @rtype: C{str}
        @return: The Testplan id
        """
        return self._plan

    @property
    def execute(self):
        """
        @rtype: C{bool}
        @return: Execute flag
        """
        return self._execute != FALSE

    @property
    def gate(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._gate

    @property
    def label(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._label

    @property
    def device(self):
        """
        @rtype: TODO
        @return: TODO
        """
        if self._device is not None:
            return self._string_2_dict(self._device)
        else:
            return {}

    @property
    def emmc(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._emmc

    @property
    def is_package_distributed(self):
        """
        @rtype: C{bool}
        @return: Is the Testrun distributed Package by Package
        """
        return self._distribution_model == PERPACKAGE

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
        @return: TODO
        """
        if self._testfilter is not None:
            testfilter = self._testfilter.replace('"',"'")
            return "\"%s\"" % testfilter

    @property
    def is_email_on(self):
        """
        @rtype: C{bool}
        @return: Is the email switched on?
        """
        return self._email == ON

    @property
    def is_email_attachments_on(self):
        """
        @rtype: C{bool}
        @return: Is the email attachment switched on?
        """
        return self._email_attachments == "on"


    ############################
    # HELPERS
    ############################

    @staticmethod
    def _string_2_list(string):
        """
        Converts a spaced string to an array

        @param string: The string for conversion
        @type product: C{string}

        @rtype: C{list} consisting of C{string}
        @return: The converted string
        """
        if string:
            spaces = re.compile(r'\s+')
            return spaces.split(string.strip())
        else:
            return []

    @staticmethod
    def _string_2_dict(string):
        """
        Converts a spaced string of form 'foo:1 bar:2 baz:3'
        to a dictionary

        @param string: The string for conversion
        @type product: C{string}

        @rtype: C{dict} consisting of C{string}
        @return: The converted string
        """
        spaces = re.compile(r'\s+')
        return dict([ pair.split(':', 1) for pair \
                           in spaces.split(string) if ':' in pair ])

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

        @type test_packages: D{List} consiting of D{string}
        @param test_packages: List of test package names

        """
        invalid_packages = [pkg for pkg in packages
                              if not self._is_valid_suffix(pkg)]
        if invalid_packages:
            pretty_packages =  ', '.join(invalid_packages)
            error_msg = "Invalid testpackage(s): %s" % pretty_packages
            raise ValueError(error_msg)
