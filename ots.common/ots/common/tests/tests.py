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

"""Tests for ots.common"""

import unittest
from ots.common import testrun

import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',)

log = logging.getLogger("testrun")

class TestTestrun(unittest.TestCase):
    """Tests for Testrun class"""
    
    def setUp(self):
        
        self.testrun = testrun.Testrun()


    def test_update_device_properties(self):
        default_options = dict()
        default_options["device"] = {"devicegroup":"default"}
        default_options["email"] = "off" # To make sure other options handled ok

        user_options = dict()
        user_options["device"] = {"devicename":"name"}

        self.testrun.set_options(default_options)
        self.assertEquals(self.testrun.get_option("device"),
                                                  default_options["device"])

        self.assertEquals(self.testrun.get_option("email"),
                                                  default_options["email"])

        self.testrun.set_options(user_options)

        expected_device = {"devicegroup":"default",
                           "devicename":"name"}


        self.assertEquals(self.testrun.get_option("device"),
                                                  expected_device)

        self.assertEquals(self.testrun.get_option("email"),
                                                  default_options["email"])

        

    def test_target_packages(self):
        pkgs = ["pkg1", "pkg2"]
        self.testrun.set_target_packages(pkgs)
        self.assertEquals(self.testrun.get_target_packages(), pkgs)

    def test_get_devicegroup(self):
        group = "jeejee"
        self.testrun.options["device"] = dict()
        self.testrun.options["device"]["devicegroup"] = group
        self.assertEquals(self.testrun.get_device_group(), group)

    def test_executed_packages(self):
        self.assertEquals(self.testrun.get_all_executed_packages(), dict())
        pkgs = dict()
        pkgs['hardware'] = ["pkg1-tests", "pkg2-tests"]
        self.testrun.set_all_executed_packages( pkgs.copy() )
        packages = self.testrun.get_all_executed_packages()
        #simple comparison of dictionaries only compares dictionary lenghts!
        #so, trying to test dicts a bit more thoroughly here
        for env in packages.keys():
            self.assertEquals(packages[env], pkgs[env])

    def test_add_executed_packages(self):
        self.testrun.add_executed_packages('hardware', ["pkg1-tests"])
        packages = self.testrun.get_all_executed_packages()
        self.assertEquals(packages['hardware'], ["pkg1-tests"])
        self.testrun.add_executed_packages('hardware', ["pkg2-tests"])
        packages = self.testrun.get_all_executed_packages()
        self.assertEquals(packages['hardware'], ["pkg1-tests", "pkg2-tests"])
        self.testrun.add_executed_packages('host_hardware', ["my-tests"])
        packages = self.testrun.get_all_executed_packages()
        self.assertEquals(packages['hardware'], ["pkg1-tests", "pkg2-tests"])
        self.assertEquals(packages['host_hardware'], ["my-tests"])

    def test_set_executed_packages_from_lists(self):
        pkgs = dict()
        pkg_list = ["pkg1-tests", "pkg2-tests", "sb-tests"]
        env_list = ['hardware', 'hardware', 'scratchbox']
        self.testrun.set_executed_pkgs_from_lists( pkg_list, env_list )
        packages = self.testrun.get_all_executed_packages()
        pkgs['hardware'] = ["pkg1-tests", "pkg2-tests"]
        pkgs['scratchbox'] = ['sb-tests']
        self.assertEquals(packages['hardware'], pkgs['hardware'])
        self.assertEquals(packages['scratchbox'], pkgs['scratchbox'])
    
    def testGetOptionsList(self):
        options = dict()
        options['hosttest'] = ['asdf-tests','asdfasdf-tests','asdfasdfasdf-benchmark']
        self.testrun.set_options(options)
        expected = ['asdf-tests','asdfasdf-tests','asdfasdfasdf-benchmark']
        self.assertEquals(expected, self.testrun.get_option('hosttest'))

    def testGetSingleOption(self):
        options = dict()
        options['scratchbox'] = 'false'
        self.testrun.set_options(options)
        expected = "false"
        self.assertEquals(expected, self.testrun.get_option('scratchbox'))

    def testGetValuelessOption(self):
        options = dict()
        options['nowait'] = ""
        self.testrun.set_options(options)
        expected = ""
        self.assertEquals(expected, self.testrun.get_option('nowait'))

    def testGetMissingOption(self):
        options = dict()
        options['nowait'] = []
        options['hosttest'] = ['asdf-tests','asdfasdf-tests','asdfasdfasdf-benchmark']
        self.testrun.set_options(options)
        expected = ""
        self.assertEquals(expected, self.testrun.get_option('scratchbox'))



    def testGetAllTestPackageData(self):
        
        package_data1 = TestPackageDataStub()
        package_data2 = TestPackageDataStub()
        self.testrun.add_testpackage_data(package_data1)
        self.testrun.add_testpackage_data(package_data2)
        stored_data = self.testrun.get_all_testpackage_data()
        self.assertTrue(package_data1 in stored_data)
        self.assertTrue(package_data2 in stored_data)


    def test_result_default_value(self):
        self.assertEquals(self.testrun.get_result(), "NOT_READY")

    def test_result_changeable_values(self):
        self.testrun.set_result("NOT_READY")
        self.assertEquals(self.testrun.get_result(), "NOT_READY")
        self.testrun.set_result("PASS")
        self.assertEquals(self.testrun.get_result(), "PASS")

    def test_result_pass_can_be_changed_to_error(self):
        self.testrun.set_result("PASS")
        self.assertEquals(self.testrun.get_result(), "PASS")
        self.testrun.set_result("ERROR")
        self.assertEquals(self.testrun.get_result(), "ERROR")

    def test_result_fail_can_be_changed_to_error(self):
        self.testrun.set_result("FAIL")
        self.assertEquals(self.testrun.get_result(), "FAIL")
        self.testrun.set_result("ERROR")
        self.assertEquals(self.testrun.get_result(), "ERROR")

    def test_result_error_cannot_be_changed(self):
        self.testrun.set_result("ERROR")
        self.assertEquals(self.testrun.get_result(), "ERROR")
        self.testrun.set_result("PASS")
        self.assertEquals(self.testrun.get_result(), "ERROR")

    def test_result_no_cases_cannot_be_changed(self):
        self.testrun.set_result("NO_CASES")
        self.assertEquals(self.testrun.get_result(), "NO_CASES")
        self.testrun.set_result("PASS")
        self.assertEquals(self.testrun.get_result(), "NO_CASES")

    def test_error_info(self):
        self.assertEquals(self.testrun.get_error_info(), "")
        info = "My error info."
        self.testrun.set_error_info(info)
        self.assertEquals(self.testrun.get_error_info(), info)

    def test_error_code(self):
        self.assertEquals(self.testrun.get_error_code(), "")
        code = "2"
        self.testrun.set_error_code(code)
        self.assertEquals(self.testrun.get_error_code(), code)


class TestPackageDataStub(object):
    def __init__(self):
        self.name = "joo"
    



if __name__ == '__main__':
    unittest.main()

