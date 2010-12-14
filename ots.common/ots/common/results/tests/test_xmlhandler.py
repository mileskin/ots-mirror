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
import os
from ots.common.results.xmlhandler import XmlHandler 
from ots.common.results.result_backend import ResultBackend 
from ots.common.resultobject import ResultObject

import logging
#logging.basicConfig(level=logging.ERROR,
#                    format='%(asctime)s  %(name)-12s %(levelname)-8s %(message)s',
#                    datefmt='%a, %d %b %Y %H:%M:%S',)

log = logging.getLogger('resultsplugin')


        
STARTTIME =  "2009-02-17 17:56:39.481646"
REQUESTID = "66666"


class testXmlHandler(unittest.TestCase):
    """unit tests for xmlhandler"""


    def setUp(self):
        self.testrun = testrunStub()
        self.plugin = XmlHandler(self.testrun, "tests.xml")
        
        
    def tearDown(self):
        pass
        
    def testName(self):
        self.assertEquals(self.plugin.name(), "XmlHandler")

        

    def testSaveRawResults(self):
        backend1 = BackendStub("stub 1")
        backend2 = BackendStub("stub 2")
        
        self.plugin.register_backend(backend1)
        self.plugin.register_backend(backend2)

        result = ResultObject("test.txt", "This is a raw result file.", "dummy-tests", "testsystem", "hardware")
        
        self.plugin.add_result_object(result)

        self.assertEquals(backend1.result, result)
        self.assertEquals(backend1.testrun, self.testrun)

        self.assertEquals(backend2.result, result)
        self.assertEquals(backend2.testrun, self.testrun)

    def testSaveXmlResults(self):
        backend1 = BackendStub("stub 1")
        
        self.plugin.register_backend(backend1)

        result = ResultObject("tests.xml", _generateXmlStringWith1Case(), "dummy-tests", "testsystem", "hardware")
        self.plugin.add_result_object(result)
        self.assertEquals(backend1.result, result) #raw file needs to be saved too 
        
        expected_sequence = ['pre_process_xml', 'pre_process_test_results',
                             'pre_process_test_suite', 'pre_process_test_set',
                             'pre_process_test_case', 'pre_process_test_step',
                             'post_process_test_step', 'post_process_test_case',
                             'post_process_test_set', 'post_process_test_suite',
                              'post_process_test_results', 'post_process_xml']

        self.assertEquals(backend1.sequence, expected_sequence)        



    def testWIthResultXmlContainingAllData(self):
        backend1 = BackendStub("stub 1")
        
        self.plugin.register_backend(backend1)
        dirname = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        result_file = os.path.join(dirname,"tests" , "result_xml_with_all_data.xml")
        result_xml = open(result_file, 'r').read()
        result = ResultObject("tests.xml",
                              result_xml,
                              "dummy-tests",
                              "testsystem",
                              "hardware")
        self.plugin.add_result_object(result)
        errors = self.plugin.save_results(self.testrun)
        expected_errors = []
        self.assertEquals(errors, expected_errors)



    def testBackendExceptionMessageHandling(self):
        backend1 = FailingBackendStub("stub 1")
        
        self.plugin.register_backend(backend1)

        result = ResultObject("tests.xml", _generateXmlStringWith1Case(), "dummy-tests", "testsystem", "hardware")
        self.plugin.add_result_object(result)
        errors = self.plugin.save_results(self.testrun)
        expected_errors = ['started_processing failed',
                           'process_raw_file failed',
                           'pre_process_xml_file failed',
                           'pre_process_test_results failed',
                           'pre_process_test_suite failed',
                           'pre_process_test_set failed',
                           'pre_process_case failed',
                           'pre_process_test_step failed',
                           'post_process_test_step failed',
                           'post_process_test_case failed',
                           'post_process_test_set failed',
                           'post_process_test_suite failed',
                           'post_process_test_results failed',
                           'post_process_xml failed',
                           'finished_processing failed']
        self.assertEquals(errors, expected_errors)



    def testSaveResults(self):
        backend1 = BackendStub("stub 1")
        self.plugin.register_backend(backend1)
        self.plugin.save_results(self.testrun)
        self.assertEquals(backend1.sequence, ['finished'])
    





class testCommentUpload(unittest.TestCase):
    """test that comment field is uploaded properly"""


    def setUp(self):
        self.testrun = testrunStub()
        self.plugin = XmlHandler(self.testrun, "tests.xml")
        
        
    def tearDown(self):
        pass

        

    def testSaveRawResults(self):
        backend1 = BackendStub("stub 1")
        
        self.plugin.register_backend(backend1)
        result = ResultObject("tests.xml",
                               _generateXmlStringWithComments(),
                               "dummy-tests",
                               "testsystem",
                               "hardware")

        
        self.plugin.add_result_object(result)

        self.assertEquals(backend1.case_comment, "kommentti")




class TestNAResults(unittest.TestCase):
    """
    No reason to think that there is anything unusual 
    about N/A but check anyway
    """

    def test_na_results(self):
        test_values = []
        backend = BackendStub("stub 1")
        def pre_process_step(values):
            test_values.append(values)
        backend.pre_process_step = pre_process_step
        testrun = testrunStub()
        plugin = XmlHandler(testrun, "tests.xml")
        plugin.register_backend(backend)
        result = ResultObject("tests.xml", 
                               NA_XML, 
                               "dummy-tests", 
                               "testsystem", 
                               "hardware")
        plugin.add_result_object(result)
        #
        v1 = test_values[0] 
        self.assertEquals('Step 1', v1['command'])
        self.assertEquals('N/A', v1['result'])
        v2 = test_values[1] 
        self.assertEquals('Step 2', v2['command'])
        self.assertEquals('N/A', v2['result'])
       
        
        

#
#
# Helpers:
#
#


class BackendStub(ResultBackend):
    """A stub representing backend plugin"""
    def __init__(self, name):
        
        self.plugin_name = name
        self.result = None
        self.testrun = None
        self.sequence = []
        self.case_comment = ""
        
    def name(self):
        """Returns the name of the backend"""
        return self.plugin_name
    
    def process_raw_file(self, result_object, testrun_object):
        """This is called when raw file is sent to results plugin"""
        self.result = result_object
        self.testrun = testrun_object

    def pre_process_xml_file(self, result_object, testrun_object):
        """This is called when starting to process new xml file"""
        self.sequence.append("pre_process_xml")
        
    def pre_process_test_results(self, values):
        """This is called when starting to process a test results"""
        self.sequence.append("pre_process_test_results")
    
    def pre_process_suite(self, values):
        """This is called when starting to process a suite"""
        if not "name" in values:
            raise Exception("bad suite data")
        self.sequence.append("pre_process_test_suite")

    def pre_process_set(self, values):
        """This is called when starting to process a set"""
        if not "name" in values:
            raise Exception("bad set data")
        self.sequence.append("pre_process_test_set")

    def pre_process_case(self, values):
        """This is called when starting to process a case"""

        if not "name" in values:
            raise Exception("bad case data")
        if "comment" in values.keys():
            self.case_comment = values["comment"]
        self.sequence.append("pre_process_test_case")

    def pre_process_step(self, values):
        """This is called when starting to process a step"""
        if not "result" in values:
            raise Exception("bad step data")
        self.sequence.append("pre_process_test_step")


    def post_process_xml_file(self):
        """This is called when finished processing new xml file"""
        self.sequence.append("post_process_xml")
        
    def post_process_test_results(self):
        """This is called when finished processing a test results"""
        self.sequence.append("post_process_test_results")
    
    def post_process_suite(self):
        """This is called when finished processing a suite"""
        self.sequence.append("post_process_test_suite")

    def post_process_set(self):
        """This is called when finished processing a set"""
        self.sequence.append("post_process_test_set")

    def post_process_case(self):
        """This is called when finished processing a case"""
        self.sequence.append("post_process_test_case")

    def post_process_step(self):
        """This is called when finished processing a step"""
        self.sequence.append("post_process_test_step")

    def finished_processing(self):
        """This is called when all files are processed"""
        self.sequence.append("finished")



class FailingBackendStub(BackendStub):
    """A stub representing backend plugin"""
    def __init__(self, name):
        
        self.plugin_name = name
        self.result = None
        self.testrun = None
        self.sequence = []
        self.case_comment = ""
        
    def name(self):
        """Returns the name of the backend"""
        return self.plugin_name


    def finished_processing(self):
        """This is called when all files are processed"""
        raise Exception("finished_processing failed")

    def started_processing(self, asdf):
        raise Exception("started_processing failed")
    
    def process_raw_file(self, result_object, testrun_object):
        """This is called when raw file is sent to results plugin"""
        raise Exception("process_raw_file failed")

    def pre_process_xml_file(self, result_object, testrun_object):
        """This is called when starting to process new xml file"""
        raise Exception("pre_process_xml_file failed")



    def pre_process_case(self, values):
        """This is called when starting to process a case"""
        raise Exception("pre_process_case failed")



        
    def pre_process_test_results(self, values):
        """This is called when starting to process a test results"""
        raise Exception("pre_process_test_results failed")
    
    def pre_process_suite(self, values):
        """This is called when starting to process a suite"""
        raise Exception("pre_process_test_suite failed")

    def pre_process_set(self, values):
        """This is called when starting to process a set"""
        raise Exception("pre_process_test_set failed")

    def pre_process_step(self, values):
        """This is called when starting to process a step"""
        raise Exception("pre_process_test_step failed")


    def post_process_xml_file(self):
        """This is called when finished processing new xml file"""
        raise Exception("post_process_xml failed")
        
    def post_process_test_results(self):
        """This is called when finished processing a test results"""
        raise Exception("post_process_test_results failed")
    
    def post_process_suite(self):
        """This is called when finished processing a suite"""
        raise Exception("post_process_test_suite failed")

    def post_process_set(self):
        """This is called when finished processing a set"""
        raise Exception("post_process_test_set failed")

    def post_process_case(self):
        """This is called when finished processing a case"""
        raise Exception("post_process_test_case failed")

    def post_process_step(self):
        """This is called when finished processing a step"""
        raise Exception("post_process_test_step failed")


class testrunStub():
    def get_request_id(self):
        return REQUESTID

    def get_start_time(self):
        return STARTTIME

    def get_image_name(self):
        return "image.img"

    def get_sw_product(self):
        return "meego"
    def getName(self):
        return "testrun name"

    def setTestCenterId(self, joo):
        pass


NA_XML = """
<testresults version="1.0" environment="hardware" hwproduct="unknown" hwbuild="unknown">

<suite name="manual-demo-tests">

<set name="testset1" description="sample_description" environment="hardware">

<case name="run" description="demo" manual="true" insignificant="false" result="N/A" comment="no can do">

<step command="Step 1" result="N/A">
<expected_result>0</expected_result>
<return_code>0</return_code>
<start>2010-05-18 14:08:23</start>
<end>2010-05-18 14:08:27</end>
</step>

<step command="Step 2" result="N/A">
<expected_result>0</expected_result>
<return_code>0</return_code>
<start>1970-01-01 02:00:00</start>
<end>1970-01-01 02:00:00</end>
</step>
</case>

<case name="manual_test_2" description="second manual test" manual="true" insignificant="false" result="PASS" comment="dad">

<step command="Open a calculator. Expected result: the calculator is opened." result="PASS">
<expected_result>0</expected_result>
<return_code>0</return_code>
<start>2010-05-18 14:08:30</start>
<end>2010-05-18 14:08:32</end>
</step>
</case>

<case name="serm006" description="automatic test 2" manual="false" insignificant="false" result="PASS">

<step command="pwd" result="PASS">
<expected_result>0</expected_result>
<return_code>0</return_code>
<start>2010-05-18 14:08:34</start>
<end>2010-05-18 14:08:34</end>
<stdout>/home/user
</stdout>
<stderr/>
</step>
</case>
</set>
</suite>
</testresults>
"""

def _generateXmlStringWith1Case():
    xml_string = """<?xml version="1.0" encoding="ISO-8859-1"?>
    <testresults version="0.1">
    <suite name="examplebinary-tests">
        <set name="testset1" description="Terminal tests" environment="hardware">
            <case name="term002" result="PASS" description="testi1" requirement="1">
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

def _generateXmlStringWith2Cases():
    xml_string = """<?xml version="1.0" encoding="ISO-8859-1"?>
<testresults version="0.1">
    <suite name="examplebinary2-tests">
        <set name="terminaltestset" description="Terminal tests" environment="hardware">
            <case name="term002" result="PASS" description="" requirement="">
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
            <case name="term003" result="FAIL" description="testi2" requirement="2">
                <step command="ls -la ~" result="FAIL">
                    <expected_result>0</expected_result>
                    <return_code>0</return_code>

                    <start>2009-2-27 01:00:00</start>
                    <end>2009-2-27 01:00:02</end>

                    <stdout>output</stdout>
                    <stderr>error</stderr>
                </step>
            </case>        
            <case name="term005" result="PASS" description="testi5" requirement="33">
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


def _generateXmlStringWithComments():
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<testresults environment="hardware" version="0.1">
  <suite domain="sample_suite_domain" name="examplebinary-tests">
    <set description="test set description" environment="hardware" feature="feature2" name="testset2">
      <case description="automatic test 1" insignificant="false" level="unknown" manual="false" name="serm005" result="PASS" type="unknown">
        <step command="uname" result="PASS">
          <expected_result>0</expected_result>
          <return_code>0</return_code>
          <start>2010-04-12 10:16:47</start>
          <end>2010-04-12 10:16:47</end>
          <stdout>Linux
</stdout>
          <stderr/>
        </step>
      </case>
      <case description="first manual test" insignificant="false" level="unknown" manual="true" name="manual_test_1" requirement="8000, 8001" result="PASS" type="unknown">
        <step description="first step" result="PASS">
          <start>2010-04-12 10:16:47</start>
          <end>2010-04-12 10:16:50</end>
        </step>
        <step description="second step" result="PASS">
          <start>2010-04-12 10:16:50</start>
          <end>2010-04-12 10:16:52</end>
        </step>
        <comment>kommentti</comment>
      </case>
    </set>
  </suite>
</testresults>

"""
    return xml_string




if __name__ == '__main__':
    unittest.main()
