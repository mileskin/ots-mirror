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

import re

"""
Provides a container for the Meta Data for a Package that has 
been executed by a Testrun
"""


class RequestedPackage(object):
    """
    Container for *all* the Packages executed in the Testrun
    """

    HOST_TEST_PATTERN = "host.*"
    HARDWARE = "hardware"

    def __init__(self, environment, packages):
        self.environment = environment
        self.packages = packages

    @property    
    def is_host_test(self):
        """Was the Package run as a host test"""
        return re.match(self.HOST_TEST_PATTERN, self.environment)

    @property 
    def is_hardware(self):
        """Was the Package run as a hardware test"""
        return self.HARDWARE in self.environment
