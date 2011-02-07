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

import unittest
from unittest import TestResult, TestCase

from ots.server.xmlrpc.request_handler import _check_testruns_result_values

class TestRequestHandlerFunctions(unittest.TestCase):
    
    def test_check_testruns_result_values_empty(self):
        result_values, result = self._init_result_values()
        
        # empty result list
        self.assertEquals('ERROR', _check_testruns_result_values(result_values))
    
    def test_check_testruns_result_values_passed(self):
        result_values, result = self._init_result_values()
        
        # one case passed
        result.addSuccess(TestCase)
        result_values.append(result)
        self.assertEquals('PASS', _check_testruns_result_values(result_values))
        
        # two cases passed
        result.addSuccess(TestCase)
        result_values.append(result)
        self.assertTrue(len(result_values) == 2)
        self.assertEquals('PASS', _check_testruns_result_values(result_values))
        
    def test_check_testruns_result_values_failed(self):
        result_values, result = self._init_result_values()
        
        # one case failed
        result.addFailure(TestCase, (None, None, None))
        result_values.append(result)
        self.assertEquals('FAIL', _check_testruns_result_values(result_values))
        
        # two cases failed
        result_values.append(result)
        self.assertTrue(len(result_values) == 2)
        self.assertEquals('FAIL', _check_testruns_result_values(result_values))
        
    def test_check_testruns_result_values_error(self):
        result_values, result = self._init_result_values()
        
        # one case failed
        result.addError(TestCase, (None, None, None))
        result_values.append(result)
        self.assertEquals('ERROR', _check_testruns_result_values(result_values))
        
        # two cases failed
        result_values.append(result)
        self.assertTrue(len(result_values) == 2)
        self.assertEquals('ERROR', _check_testruns_result_values(result_values))
        
    def test_check_testruns_result_values_mixed(self):
        # two cases failed + error case
        result_values, result1 = self._init_result_values()
        
        result1.addFailure(TestCase, (None, None, None))
        result1.addFailure(TestCase, (None, None, None))
        result_values.append(result1)
        result1.addError(TestCase, (None, None, None))
        result_values.append(result1)
        self.assertTrue(len(result_values) == 2)
        self.assertEquals('ERROR', _check_testruns_result_values(result_values))
        
        # one case failed + one passed case
        result_values2, result2 = self._init_result_values()
        result2.addFailure(TestCase, (None, None, None))
        result2.addSuccess(TestCase)
        result_values2.append(result2)
        self.assertEquals('FAIL', _check_testruns_result_values(result_values2))
        

    def _init_result_values(self):
        return [], unittest.TestResult()


###############################################################################

if __name__ == "__main__":
    unittest.main()

