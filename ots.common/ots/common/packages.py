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
Containers for the Packages from the run 

The Package can be executed under the following Environments:

 - Hardware 
 - Host 

"""

import re

class PackagesBase(object):
    """
    Base class associates a list of
    packages with a given Environment
    """

    HOST_TEST_PATTERN = "host.*"
    HARDWARE = "hardware"

    def __init__(self, environment, packages):
        """
        @type environment: C{string}
        @param: environment: The test environment
        
        @type packages: C{list} of C{string}
        @param: packages: The Packages 
        """
        #FIXME. Backend interface currently string based  
        self.environment = environment
        self.packages = packages

    @property    
    def is_host_tested(self):
        """Was the Package run as a host test"""
        match = re.match(self.HOST_TEST_PATTERN, self.environment)
        return match is not None

    @property 
    def is_hw_tested(self):
        """Was the Package run as a hardware test"""
        match = self.HARDWARE in self.environment
        return match is not None

    def __eq__(self, other):
        """Do the containers contain the same package information"""
        return ((self.environment == other.environment) and 
                (self.packages.sort() == other.packages.sort()))

class ExpectedPackages(PackagesBase):
    """
    Container for all the Packages 
    that *should* have been executed in the Testrun
    for the given environment 
    """ 

    def __init__(self, environment, packages):
        PackagesBase.__init__(self, environment, packages)

class TestedPackages(PackagesBase):
    """
    Container for all the Packages 
    that *have* been executed on the Testrun
    for the given environment
    """

    def __init__(self, environment, packages):
        PackagesBase.__init__(self, environment, packages)
        self.significant_results = []
        self.insignificant_results = []
