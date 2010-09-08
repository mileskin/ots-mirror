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

###########################
# Keys
###########################

IMAGE = "image"
ROOTSTRAP = "rootstrap"
PACKAGES = "packages"
PLAN = "plan"
EXECUTE = "execute"
GATE = "gate"
LABEL = "label"
HOSTTEST = "hosttest"
ENGINE = "engine"
DEVICE = "device"
EMMC = "emmc"
EMMCURL = "emmcurl"
DISTRIBUTION = "distribution_model"
FLASHER = "flasher"
TESTFILTER = "testfilter"
INPUT = "input_plugin"

############################
# VALUES
############################

FALSE = "false"
PERPACKAGE = "perpackage"
BIFH = "bifh"

############################
# HELPERS
############################

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


#################################
# Options
#################################

class Options(object):
    """
    Adapts a dictionary of options for the Testrun
    to a defined interface specification
    """

    def __init__(self, options_dict):
        """
        @type: C{dict}
        @param: The parameters for the testrun
        """
        self._options_dict = options_dict

    @property
    def image_url(self):
        """
        @rtype: C{str}
        @return: The URL of the image
        """
        return self._options_dict.get(IMAGE, '')

    @property
    def rootstrap(self):
        """
        @rtype: C{str}
        @return: TODO
        """
        return self._options_dict.get(ROOTSTRAP, '')

    @property
    def hw_packages(self):
        """
        @rtype: C{list} of C{str}
        @return: Packages for hardware testing
        """
        #TODO check definition
        return _string_2_list(self._options_dict.get(PACKAGES,''))

    @property
    def hosttest_packages(self):
        """
        @rtype: C{list} of C{str}
        @return: Packages for host testing
        """
        #TODO check definition
        return _string_2_list(self._options_dict.get(HOSTTEST,''))

    @property
    def testplan_id(self):
        """
        @rtype: C{str}
        @return: The Testplan id
        """
        return self._options_dict.get(PLAN, None)

    @property
    def execute(self):
        """
        @rtype: C{bool}
        @return: Execute flag
        """
        return self._options_dict.get(EXECUTE, False) != FALSE

    @property
    def gate(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._options_dict.get(GATE, None)

    @property
    def label(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._options_dict.get(LABEL, None)

    @property
    def device(self):
        """
        @rtype: TODO
        @return: TODO
        """
        if DEVICE in self._options_dict:
            return _string_2_dict(self._options_dict.get(DEVICE))

    @property
    def emmc(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self._options_dict.get(EMMC, None)

    @property
    def emmcurl(self):
        """
        @rtype: TODO
        @return: TODO
        """
        return self.emmc

    @property
    def is_package_distributed(self):
        """
        @rtype: C{bool}
        @return: Is the Testrun distributed Package by Package
        """
        #TODO: Is there any reason why all distributions can't
        #happen perpackage?
        return self._options_dict.get(DISTRIBUTION, False) == PERPACKAGE

    @property
    def flasher(self):
        """
        @rtype: C{str}
        @return: The URL of the flasher
        """
        return self._options_dict.get(FLASHER, None)

    @property
    def testfilter(self):
        """
        @rtype: C{str}
        @return: TODO
        """
        if self._options_dict.has_key(TESTFILTER):
            testfilter = self._options_dict[TESTFILTER]
            testfilter = testfilter.replace('"',"'")
            return "\"%s\"" % testfilter

    @property
    def is_client_bifh(self):
        """
        @rtype: C{bool}
        @return: Was BIFH the client
        """
        return self._options_dict.get(INPUT, "") == BIFH

