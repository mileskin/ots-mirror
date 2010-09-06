#!/usr/bin/env python
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
ResultObject encapsulates a raw result file. It includes file content and 
additional metadata about the file.
"""
import time

class ResultObject(object):
    """
    ResultObject encapsulates a raw result file. It includes file content and 
    additional metadata about the file.

    """
    
    def __init__(self,
                 name,
                 content,
                 testpackage="Unknown",
                 origin="",
                 environment=""):
        
        self.content = content
        self.filename = name
        self.testpackage = testpackage
        self.origin = origin
        self.environment = environment
        self.timestamp = time.time()

    def name(self):
        """Outputs the name of the result file as a string"""
        return self.filename

    def get_testpackage(self):
        """
        Returns the name of the testpackage this resultfile belongs to.
        None if result file is not related to testpackages.
        """
        return self.testpackage
        
    def get_origin(self):
        """Returns the hostname of the machine this result file is originated"""
        return self.origin
    
    def get_environment(self):
        """
        Returns the environment (HW/SB/host) this result file originates from
        """
        return self.environment

    def get_timestamp(self):
        """returns creation time of the results object. (epoch)"""
        return self.timestamp

    def get_content(self):
        """Outputs results as raw string."""
        return self.content
    
    def __unicode__(self):
        return self.filename + ": " + self.content
