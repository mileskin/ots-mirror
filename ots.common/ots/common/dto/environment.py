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
The Environment under which the tests occurred

Currently:

 - hardware (the device)
 - host (the worker)
"""

import re

class Environment(object):
    """
    The Environment Datatype
    """

    HOST_TEST_PATTERN = "host.*"
    HARDWARE = "hardware"

    def __init__(self, environment):
        """
        @type environment: C{string}
        @param: environment: The test environment
        """
        self.environment = environment

    @property    
    def is_host(self):
        """Is this a host environment?"""
        match = re.match(self.HOST_TEST_PATTERN, self.environment)
        return match is not None

    @property 
    def is_hw(self):
        """Is this a hardware environment?"""
        match = self.HARDWARE in self.environment
        return match 

    def __eq__(self, other):
        return self.environment == other.environment
               
    def __hash__(self):
        return hash(self.environment)

    def __str__(self):
        return "<%s.Environment (%s) at %s>"%(__name__, 
                                              self.environment, 
                                              hex(id(self)))

