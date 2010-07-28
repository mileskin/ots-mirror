# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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
import info
import logging

from ots.distributor.testrundata import TestrunData

class TestInfoService(unittest.TestCase):
    
    def setUp(self):
        self.config = dict()
        self.config['cleanup_period'] = 1
        self.host = "testhost"
        self.port = 666
        self.info = info.InfoService(self.config, self.host, self.port)
    
    def tearDown(self):
        pass
        
    def testInfo(self):
        output = self.info.info()
        expected_output = 'Info Service running at testhost'
        self.assertEquals(output, expected_output)
        
    def testAddTestrun(self):
        original_testrun = self._generateTestrunData()
        self.info.add_testrun(original_testrun)
        stored_testrun = self.info.get_testrun(original_testrun.get_testrun_id())
        self.assertEquals(stored_testrun.get_build_id(), original_testrun.get_build_id())

        
    def testRemoveTestrun(self):
        original_testrun = self._generateTestrunData()
        self.info.add_testrun(original_testrun)
        self.info.remove_testrun(original_testrun.get_testrun_id())
        stored_testrun = self.info.get_testrun(original_testrun.get_testrun_id())
        self.assertEquals(stored_testrun, None)

        
    def testCleanup(self):
        original_testrun = self._generateTestrunData()
        original_testrun.created = 1.0
        self.info.add_testrun(original_testrun)
        self.info._cleanup()
        stored_testrun = self.info.get_testrun(original_testrun.get_testrun_id())
        self.assertEquals(stored_testrun, None)



    def testAddTestrunWithNoId(self):
        testrun = TestrunData()
        self.failUnlessRaises(ValueError, self.info.add_testrun, testrun)

    def testGetAndSetState(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()

        self.assertEquals(self.info.get_state(testrun_id), None)

        self.info.add_testrun(original_testrun)
        self.assertEquals(self.info.get_state(testrun_id), ("NOT_STARTED", ""))
        
        self.info.set_state(testrun_id, "QUEUED", "testrun inserted into queue")
        self.assertEquals(self.info.get_state(testrun_id), ("QUEUED","testrun inserted into queue"))

    def testSetStateWithInvalidState(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()
        self.info.add_testrun(original_testrun)
        self.failUnlessRaises(ValueError, self.info.set_state, testrun_id, "asdf", "asdf")

    def testSetStateWithInvalidTestrunId(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()
        self.info.add_testrun(original_testrun)
        self.failUnlessRaises(KeyError, self.info.set_state, 234234, "QUEUED", "testrun inserted into queue")

    def testGetAndSetResult(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()

        self.assertEquals(self.info.get_result(testrun_id), None)

        self.info.add_testrun(original_testrun)
        self.assertEquals(self.info.get_result(testrun_id), "NOT_READY")
        
        self.info.set_result(testrun_id, "FAIL")
        self.assertEquals(self.info.get_result(testrun_id), "FAIL")

    def test_set_result_to_error(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()

        self.assertEquals(self.info.get_result(testrun_id), None)

        self.info.add_testrun(original_testrun)
        self.assertEquals(self.info.get_result(testrun_id), "NOT_READY")
        self.assertEquals(self.info.get_error_info(testrun_id), "")
        self.assertEquals(self.info.get_error_code(testrun_id), "")
        
        error_code = "654"
        error_info = "my error info string"
        self.info.set_result_to_error(testrun_id, error_code, error_info)
        self.assertEquals(self.info.get_result(testrun_id), "ERROR")
        self.assertEquals(self.info.get_error_info(testrun_id), error_info)
        self.assertEquals(self.info.get_error_code(testrun_id), error_code)

        #assure first error cannot be overwritten
        self.info.set_result_to_error(testrun_id, "999", "new error info")
        self.assertEquals(self.info.get_result(testrun_id), "ERROR")
        self.assertEquals(self.info.get_error_info(testrun_id), error_info)
        self.assertEquals(self.info.get_error_code(testrun_id), error_code)

    def test_add_executed_packages(self):
        original_testrun = self._generateTestrunData()
        testrun_id = original_testrun.get_testrun_id()
        self.info.add_testrun(original_testrun)

        all_pkgs = dict()
        self.assertEquals(len(self.info.get_all_executed_packages(testrun_id).keys()), 0)
        self.assertEquals(self.info.get_all_executed_packages(testrun_id), all_pkgs)
        env1 = "hardware"
        pkgs1 = ["my-package1-tests","my-package2-tests"]
        all_pkgs[env1] = pkgs1
        self.info.add_executed_packages(testrun_id, env1, pkgs1)

        packages = self.info.get_all_executed_packages(testrun_id)
        self._assert_equals_executed_packages(packages, all_pkgs)

        env2 = "scratchbox"
        pkgs2 = ["her-package1-tests","her-package2-tests"]
        all_pkgs[env2] = pkgs2
        self.info.add_executed_packages(testrun_id, env2, pkgs2)

        packages = self.info.get_all_executed_packages(testrun_id)
        self._assert_equals_executed_packages(packages, all_pkgs)

        self.assertEquals(len(self.info.get_all_executed_packages(testrun_id).keys()), 2)


# Utility methods

    def _assert_equals_executed_packages(self, dict1, dict2):
        #simple comparison between dicts would only compare dictionary lenghts!
        for env in dict1.keys():
            self.assertEquals(dict1[env], dict2[env])
        
    def _generateTestrunData(self):
        testrun = TestrunData()
        testrun.set_build_id(666)
        testrun.set_testrun_id(555)
        return testrun
        
        
if __name__ == '__main__':
    unittest.main()
