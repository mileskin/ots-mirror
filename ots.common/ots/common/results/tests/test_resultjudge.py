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
from ots.common.resultobject import ResultObject
from ots.common.results.resultjudge import ResultJudge, PASS, FAIL, NO_CASES

from xml.etree import ElementTree as ET

import logging
logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s  %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',)

log = logging.getLogger('resultsplugin')

STARTTIME =  "2009-02-17 17:56:39.481646"
REQUESTID = "66666"

def _generateXmlString():
    xml_string = """<?xml version="1.0" encoding="ISO-8859-1"?>
    <testresults version="0.1">
    <suite name="examplebinary-tests">
        <set name="testset1" description="Terminal tests" environment="hardware">
            <case name="term002" result="PASS" insignificant="false">
                <step command="ls -la ~" result="PASS">
                    <expected_result>0</expected_result>
                    <return_code>0</return_code>

                    <start>2009-2-27 01:00:00</start>
                    <end>2009-2-27 01:00:02</end>

                    <stdout>output</stdout>
                    <stderr>error</stderr>
                </step>
            </case>        
        </set>
    </suite>
</testresults>

        """
    return xml_string

def _generateXmlStringWithMultipleCases():
    xml_string = """<?xml version="1.0" encoding="ISO-8859-1"?>
<testresults version="0.1">
    <suite name="examplebinary2-tests">
        <set name="terminaltestset" description="Terminal tests" environment="hardware">
            <case name="term002" result="PASS" insignificant="false">
                <step command="ls -la ~" result="PASS">
                    <expected_result>0</expected_result>
                    <return_code>0</return_code>

                    <start>2009-2-27 01:00:00</start>
                    <end>2009-2-27 01:00:02</end>

                    <stdout>"output2"</stdout>
                    <stderr>"error2"</stderr>
                </step>
            </case>
        </set>        
        <set name="terminaltestset2" description="Terminal tests" environment="hardware">
            <case name="term003" result="FAIL" insignificant="false">
                <step command="ls -la ~" result="FAIL">
                    <expected_result>0</expected_result>
                    <return_code>0</return_code>

                    <start>2009-2-27 01:00:00</start>
                    <end>2009-2-27 01:00:02</end>

                    <stdout>output</stdout>
                    <stderr>error</stderr>
                </step>
            </case>        
            <case name="term005" result="PASS" insignificant="false">
                <step command="ls -la ~" result="FAIL">
                    <expected_result>0</expected_result>
                    <return_code>0</return_code>

                    <start>2009-2-27 01:00:00</start>
                    <end>2009-2-27 01:00:02</end>

                    <stdout>output</stdout>
                    <stderr>error</stderr>
                </step>
            </case>        

        </set>
    </suite>
</testresults>
"""
    return xml_string


def _generateXmlStringWithNoCases():
    xml_string = """<?xml version="1.0" encoding="ISO-8859-1"?>
    <testresults version="0.1"></testresults>"""
    return xml_string


class testrun_stub():
    def __init__(self, packages = None, hostpackages = None):
        self.packages = []
        self.hostpackages = []
        self.executed_packages = dict()
        if packages:
            self.packages = packages
        if hostpackages:
            self.hostpackages = hostpackages

        self.result = "NOT_READY"
        self.sb_enabled = False
        self.hw_enabled = True
        
    def set_error_info(self, info):
        pass
    
    def get_request_id(self):
        return REQUESTID
    def get_start_time(self):
        return STARTTIME
    def get_image_name(self):
        return "image.img"
    def get_sw_product(self):
        return "dummy_sw_product"
    def getName(self):
        return "testrun name"
    def get_testpackages(self):
        return self.packages
    def get_host_testpackages(self):
        return self.hostpackages

    def get_all_executed_packages(self):
        return self.executed_packages

    def get_result(self):
        return self.result
    def set_result(self, result):
        if self.result in ("NOT_READY"):
            self.result = result
            log.debug("Result set to %s" % result)
        else:
            log.debug("Denied setting of result. Result is already ERROR")
    
    def scratchbox_testing_enabled(self):
        return self.sb_enabled

    def hardware_testing_enabled(self):
        return self.hw_enabled

        
class TestResultJudge(unittest.TestCase):
    """Unit tests for ResultJudge"""

    def setUp(self):
        """Setup"""
        self.pkg1 = "package1-tests"
        self.pkg2 = "package2-tests"
        self.backend = None

        #hardware
        self.result_object1 = ResultObject("tatam_xml_testrunner_results.xml", 
                                        _generateXmlString(), 
                                        self.pkg1, "", "hardware")
        self.result_object2 = ResultObject("tatam_xml_testrunner_results.xml",
                                        _generateXmlStringWithMultipleCases(),
                                        self.pkg2, "", "hardware")

        #scratchbox
        self.result_object1_sb = ResultObject("tatam_xml_testrunner_results.xml", 
                                        _generateXmlString(), 
                                        self.pkg1, "", "scratchbox")
        self.result_object2_sb = ResultObject("tatam_xml_testrunner_results.xml",
                                        _generateXmlStringWithMultipleCases(),
                                        self.pkg2, "", "scratchbox")

        #host
        self.result_object1_host = ResultObject("tatam_xml_testrunner_results.xml", 
                                        _generateXmlString(), 
                                        self.pkg1, "", "host_hardware")
        self.result_object2_host = ResultObject("tatam_xml_testrunner_results.xml",
                                        _generateXmlStringWithMultipleCases(),
                                        self.pkg2, "", "host_hardware")

        #hardware with no cases
        self.result_object_no_cases = ResultObject("tatam_xml_testrunner_results.xml", 
                                        _generateXmlStringWithNoCases(), 
                                        self.pkg1, "", "hardware")

    def test_init(self):
        """Test __init__"""
        self.testrun = testrun_stub()
        self.backend = ResultJudge(self.testrun)
        self.assertTrue(self.backend.testrun == self.testrun)
        self.assertTrue(self.backend.testcase_results == dict())
        self.assertTrue(self.backend.testcase_results_insig == dict())

    def test_pre_process_xml_file(self):
        """Test pre_process_test_results"""
        self.testrun = testrun_stub()
        self.backend = ResultJudge(self.testrun)
        self.backend.pre_process_xml_file(self.result_object1, self.testrun)
        identifier = self.result_object1.get_testpackage()+"-"+self.result_object1.get_environment()
        self.assertTrue(self.backend.active_package == identifier)
        self.assertTrue(self.backend.testcase_results[identifier] == [])
        self.assertTrue(self.backend.testcase_results_insig[identifier] == [])
             
    def test_pre_process_case(self):
        """Test pre_process_case"""
        self.testrun = testrun_stub([self.pkg1])
        self.backend = ResultJudge(self.testrun)
        self.backend.pre_process_xml_file(self.result_object1, self.testrun)
        values = dict()
        values["result"] = "PASS"
        values["insignificant"] = "false"
        self.backend.pre_process_case(values)
        identifier = self.result_object1.get_testpackage()+"-"+self.result_object1.get_environment()
        self.assertEquals(self.backend.testcase_results[identifier], ["PASS"])
    
    def test_finished_processing_1(self):
        """Test finished_processing for 2 test packages, each with 2 cases"""
        self.testrun = testrun_stub([self.pkg1, self.pkg2])
        self.backend = ResultJudge(self.testrun)
        self.backend.testcase_results = dict()
        self.backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        self.backend.testcase_results[self.pkg2+"-hardware"] = ["FAIL", "PASS"]
        self.backend.finished_processing()
        self.assertEquals(self.testrun.get_result(), "FAIL")

    def test_finished_processing_2(self):
        """Test finished_processing for no test packages (no results)"""
        self.testrun = testrun_stub([self.pkg1, self.pkg2])
        self.backend = ResultJudge(self.testrun)
        self.backend.testcase_results = dict()
        self.backend.finished_processing()
        self.assertEquals(self.testrun.get_result(), "ERROR")

    def test_finished_processing_3(self):
        """Test finished_processing for 1 test package without any cases"""
        self.testrun = testrun_stub([self.pkg1])
        self.backend = ResultJudge(self.testrun)
        self.backend.testcase_results = dict()
        self.backend.testcase_results[self.pkg1+"-hardware"] = []
        self.backend.finished_processing()
        self.assertEquals(self.testrun.get_result(), "NO_CASES")

    def test_finished_processing_4(self):
        """Test finished_processing for 2 test packages, 1 without cases."""
        self.testrun = testrun_stub([self.pkg1, self.pkg2])
        self.backend = ResultJudge(self.testrun)
        self.backend.testcase_results = dict()
        self.backend.testcase_results[self.pkg1+"-hardware"] = []
        self.backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        self.backend.finished_processing()
        self.assertEquals(self.testrun.get_result(), "PASS")


    def test_same_package_from_multiple_environments(self):
        """
        Test finished_processing() with two packages with same name.
        (This situation occurs when same testpackage has been executed in 
        multiple environments.)
        """
        testrun = testrun_stub([self.pkg1])
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        backend = ResultJudge(testrun)
        backend.pre_process_xml_file(self.result_object1, testrun)
        values = dict()
        values["result"] = "FAIL"
        values["insignificant"] = "false"
        backend.pre_process_case(values)

        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        values = dict()
        values["result"] = "PASS"
        values["insignificant"] = "false"
        backend.pre_process_case(values)

        backend.finished_processing()
        self.assertEquals(testrun.result, "FAIL")

    def test_check_results_from_all_packages_1(self):
        """HW only, two packages. Results missing for one package."""
        testrun = testrun_stub([self.pkg1, self.pkg2])
        testrun.hw_enabled = True
        backend = ResultJudge(testrun)
        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_results_from_all_packages_2(self):
        """HW only, two packages. Results received for all packages."""
        testrun = testrun_stub([self.pkg1, self.pkg2])
        testrun.hw_enabled = True
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_results_from_all_packages_3(self):
        """Host_HW only, two packages. Results missing for one package."""
        testrun = testrun_stub(None, [self.pkg1, self.pkg2]) #host_packages only
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_results_from_all_packages_4(self):
        """Host_HW only, two packages. Results received for both packages."""
        testrun = testrun_stub(None, [self.pkg1, self.pkg2]) #host_packages only
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_results_from_all_packages_multiple_environments_1(self):
        """HW + SB, two packages. Results missing for one package for both environments."""
        testrun = testrun_stub([self.pkg1, self.pkg2])
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_results_from_all_packages_multiple_environments_2(self):
        """HW + SB, two packages. Results received for all packages in both environments."""
        testrun = testrun_stub([self.pkg1, self.pkg2])
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_results_from_all_packages_multiple_environments_3(self):
        """HW + SB + Host, two packages. Results missing for one packages in one environment."""
        testrun = testrun_stub([self.pkg1, self.pkg2], [self.pkg1, self.pkg2]) #hw & sb + host
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.pre_process_xml_file(self.result_object1_host, testrun)
        #backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        #backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_results_from_all_packages_multiple_environments_4(self):
        """HW + SB + Host, two packages. Results received for all packages in all environments."""
        testrun = testrun_stub([self.pkg1, self.pkg2], [self.pkg1, self.pkg2]) #hw & sb + host
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")


    # Tests for testruns that received executed_packages from worker:


    def test_check_all_packages_with_executed_pkgs_1(self):
        """
        HW, two packages. Package list is specified and got executed packages. 
        Results received for all packages.
        """
        testrun = testrun_stub([self.pkg1, self.pkg2])
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        executed = dict()
        executed['Hardware'] = [self.pkg1, self.pkg2]
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_2(self):
        """
        HW, two packages. No package list specified but got executed packages. 
        Results received for all packages.
        """
        testrun = testrun_stub([])
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        executed = dict()
        executed['Hardware'] = [self.pkg1, self.pkg2]
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_3(self):
        """
        HW, two packages. No package list specified. No executed packages. 
        No results received.
        """
        testrun = testrun_stub([])
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        backend = ResultJudge(testrun)

        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_all_packages_with_executed_pkgs_4(self):
        """
        HW, two packages. No package list specified and no executed packages. 
        Results received for all packages. 
        This situation could indicate bad error handling somewhere in OTS code.
        """
        testrun = testrun_stub([])
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        executed = dict()
        executed['Hardware'] = [self.pkg1, self.pkg2]
        #testrun.executed_packages = executed #this was not received from worker
        backend = ResultJudge(testrun)
        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "ERROR")

    def test_check_all_packages_with_executed_pkgs_5(self):
        """
        HW, two packages. No used-defined package list. Got executed packages. 
        One package is missing from executed packages list but all results were 
        received. Note: in practise, this kinda situation is nearly impossible!
        """
        testrun = testrun_stub() # no user-defined packages
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        executed = dict()
        executed['Hardware'] = [self.pkg1]  #self.pkg2 is missing here
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"] #but results were received
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_multiple_environments_1(self):
        """
        HW + SB + Host, two packages. 
        Results received for all packages in all environments. 
        Got executed packages list for all environments.
        """
        pkgs = [self.pkg1, self.pkg2]
        testrun = testrun_stub(pkgs, pkgs) #hw & sb + host
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        executed = dict()
        executed['Hardware'] = pkgs
        executed['Scratchbox'] = pkgs
        executed['Host_Hardware'] = pkgs
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_multiple_environments_2(self):
        """
        HW + SB + Host, two packages. 
        Results received for all packages in all environments. 
        Executed packages list missing for one environment. 
        User-defined list should compliment the missing executed packages.
        """
        pkgs = [self.pkg1, self.pkg2]
        testrun = testrun_stub(pkgs, pkgs) #hw & sb + host
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        executed = dict()
        executed['Hardware'] = pkgs
        executed['Scratchbox'] = pkgs
        #executed['host_hardware'] = pkgs #this is now missing
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_multiple_environments_3(self):
        """
        HW + SB, two packages. 
        Results received for all packages in all environments. 
        Executed packages list missing for SB. User-defined package list should 
        compliment the missing executed packages and no missing pkgs reported.
        """
        pkgs = [self.pkg1, self.pkg2]
        testrun = testrun_stub(pkgs) #hw & sb
        testrun.hw_enabled = True
        testrun.sb_enabled = True
        executed = dict()
        executed['Hardware'] = pkgs
        #executed['Scratchbox'] = pkgs  #this information is missing
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_sb, testrun)
        backend.pre_process_xml_file(self.result_object2_sb, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-scratchbox"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-scratchbox"] = ["PASS", "PASS"]
        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")

    def test_check_all_packages_with_executed_pkgs_multiple_environments_4(self):
        """
        HW + Host, two packages. 
        Results received for all packages in all environments. 
        Executed packages list missing for HW. User-defined package list should 
        compliment the missing executed packages and no missing pkgs reported.
        """
        pkgs = [self.pkg1, self.pkg2]
        testrun = testrun_stub(pkgs, pkgs) #hw & sb + host
        testrun.hw_enabled = True
        testrun.sb_enabled = False
        executed = dict()
        #executed['Hardware'] = pkgs #this information is missing
        executed['Host_Hardware'] = pkgs
        testrun.executed_packages = executed
        backend = ResultJudge(testrun)

        backend.pre_process_xml_file(self.result_object1, testrun)
        backend.pre_process_xml_file(self.result_object2, testrun)
        backend.pre_process_xml_file(self.result_object1_host, testrun)
        backend.pre_process_xml_file(self.result_object2_host, testrun)
        backend.testcase_results[self.pkg1+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg1+"-host_hardware"] = ["PASS", "PASS"]
        backend.testcase_results[self.pkg2+"-host_hardware"] = ["PASS", "PASS"]

        backend.finished_processing()
        self.assertEquals(testrun.get_result(), "PASS")


class TestResultJudge_insignificant_tests(unittest.TestCase):
    """
    More unit tests for ResultJudge.

    Test with one test defined as insignificant and ResultJudge initialised 
    to take also insignificant tests into account when determining testrun 
    result.
    """

    def setUp(self):
        """Setup"""
        self.pkg1 = "package1-tests"

        self.testrun = testrun_stub([self.pkg1])
        self.backend = ResultJudge(self.testrun, insignificant_tests_matter = True)
        self.result_object1 = ResultObject("tatam_xml_testrunner_results.xml", 
                                        _generateXmlString(), 
                                        self.pkg1, "", "hardware")

    def test_insignificant_tests_matter_1(self):
        """Test with insignificant test case result PASS"""
        self.backend.pre_process_xml_file(self.result_object1, self.testrun)
        values = dict()
        values["result"] = "PASS"
        values["insignificant"] = "true"
        self.backend.pre_process_case(values)
        self.backend.finished_processing()

        self.assertEquals(self.testrun.result, "PASS")

    def test_insignificant_tests_matter_2(self):
        """Test with insignificant test case result FAIL"""
        self.backend.pre_process_xml_file(self.result_object1, self.testrun)
        values = dict()
        values["result"] = "FAIL"
        values["insignificant"] = "true"
        self.backend.pre_process_case(values)
        self.backend.finished_processing()

        self.assertEquals(self.testrun.result, "FAIL")

class TestOverallResult(unittest.TestCase):

    def test_significant_pass(self):
        rj = ResultJudge(None)
        pkgs =  {'pkg_1': [PASS], 
                 'pkg_2': ['FAIL']}
        result = rj._overall_result(pkgs, pkgs, ['pkg_1'], False)
        self.assertEquals(PASS, result)

    def test_significant_fail(self):
        rj = ResultJudge(None)
        pkgs =  {'pkg_1': [PASS], 
                 'pkg_2': ['FAIL']}
        result = rj._overall_result(pkgs, pkgs, ['pkg_1', 'pkg_2'], False)
        self.assertEquals(FAIL, result) 

    def test_significant_na(self):
        rj = ResultJudge(None)
        pkgs =  {'pkg_1': [PASS], 
                 'pkg_2': ['N/A']}
        result = rj._overall_result(pkgs, pkgs, ['pkg_1', 'pkg_2'], False)
        self.assertEquals(FAIL, result) 

    def test_insignificant_pass(self):
        rj = ResultJudge(None)
        pkgs =  {'pkg_1': [PASS], 
                 'pkg_2': ['FAIL']}
        result = rj._overall_result(pkgs, pkgs, ['pkg_1'], True)
        self.assertEquals(PASS, result)

    def test_insignificant_fail(self):
        rj = ResultJudge(None)
        pkgs_sig =  {'pkg_1': [PASS], 
                 'pkg_2': [PASS]}
        pkgs_insig =  {'pkg_1': [PASS], 
                 'pkg_2': ['FAIL']}
        result = rj._overall_result(pkgs_sig, 
                                    pkgs_insig, 
                                    ['pkg_1', 'pkg_2'], 
                                    True)
        self.assertEquals(FAIL, result) 

    def test_insignificant_na(self):
        rj = ResultJudge(None)
        pkgs_sig =  {'pkg_1': [PASS], 
                 'pkg_2': [PASS]}
        pkgs_insig =  {'pkg_1': [PASS], 
                 'pkg_2': ['N/A']}
        result = rj._overall_result(pkgs_sig, 
                                    pkgs_insig, 
                                    ['pkg_1', 'pkg_2'], 
                                    True)
        self.assertEquals(FAIL, result) 

    def test_lower_case(self):
        rj = ResultJudge(None)
        pkgs_sig =  {'pkg_1': ['pass'], 
                     'pkg_2': [PASS]}
        pkgs_insig =  {'pkg_1': [PASS], 
                       'pkg_2': ['pass']}
        result = rj._overall_result(pkgs_sig, 
                                    pkgs_insig, 
                                    ['pkg_1', 'pkg_2'], 
                                    True)
        self.assertEquals(PASS, result) 



if __name__ == '__main__':
    unittest.main()

