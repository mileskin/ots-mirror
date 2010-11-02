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
Runs an OTS Testrun 
"""

#FIXME: A Placeholder module while the surrounding interfaces are defined

from ots.results.api import TestrunResult
from ots.results.api import is_valid_run
from ots.results.api import go_nogo_gauge

from ots.server.hub.dto_handler import DTOHandler

class Testrun(object):
    

    def __init__(self, is_hw_enabled = True,
                       is_host_enabled = False,
                       insignificant_tests_matter = True):
        """"
        @type is_hw_enabled: C{bool} 
        @param is_hw_enabled: Flag

        @type is_host_enabled: C{bool}
        @param is_host_enabled: Flag

        @type insignificant_tests_matter: C{bool} 
        @param insignificant_tests_matter: Flag
        """
       
        self._dto_handler = DTOHandler()
        self.expected_packages = None
        self.tested_packages = None
        self.run_test = None
        self.is_hw_enabled = is_hw_enabled
        self.is_host_enabled = is_host_enabled
        self.insignificant_tests_matter = insignificant_tests_matter
        
    def run(self):
        #blocking call returns when test completed   
        ret_val = TestrunResult.FAIL
        self.run_test()
        self.expected_packages = self._dto_handler.expected_packages
        self.tested_packages = self._dto_handler.tested_packages
        is_valid_run(self.expected_packages,
                     self.tested_packages,
                     self.is_hw_enabled,
                     self.is_host_enabled)
        self.results = self._dto_handler.results_xmls
        ret_val = go_nogo_gauge(self._dto_handler.results_xmls,
                                self.insignificant_tests_matter)
        return ret_val

                      
