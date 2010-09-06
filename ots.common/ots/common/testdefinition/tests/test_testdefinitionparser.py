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

from xml.etree import ElementTree as ET

from ots.common.testdefinition.testdefinitionparser import TestDefinitionParser
from ots.common.testdefinition.testdefinitionparser import DEFAULT_TIMEOUT
from ots.common.testdefinition.testdefinitionparser import PostSteps
from ots.common.testdefinition.testpackagedata import TestPackageData

module = os.path.dirname(os.path.abspath(__file__))
TEST_XSD = os.path.join(module, "data", "testdefinition-tm_terms.xsd")


class TestTestDefinitionParser(unittest.TestCase):
    '''unit test for testdefinitionparser'''
    def setUp(self):
        #In most tests below we don't really use this test definition file.
        #It is just needed to initialise the parser --> must be valid to schema!
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "sample_input_file.xml")
        self.test_parser = TestDefinitionParser(fqname, test_xsd = TEST_XSD)

    #
    # Helper methods:
    #
    def _generateSuiteXML(self): 
        #NOTE: Below XML should have: 
        #1) all possible data fields set 
        #2) each "inheritable" data field containing a unique, different value
        #   (e.g. timeout value in test case is different to timeout in test set).
        xml = "<suite name='sample_suite' domain='sample_domain' type='Performance' description='suite_description' timeout='111' level='suitelevel' insignificant='true' manual='false' requirement='suitereq'>\
<description>Preferred suite description.</description>\
<set name='sample_set' description='set_description' timeout='20' type='Security' feature='yyy' level='setlevel' insignificant='false' manual='true' requirement='setreq'>\
<pre_steps><step>ls</step></pre_steps>\
<post_steps><step>pwd</step></post_steps>\
<case name='sample_case' description='case_description' type='Functional' timeout='10' subfeature='xxx' level='caselevel' insignificant='true' manual='false' requirement='casereq'>\
<description>Preferred case description.</description>\
<step>sample step</step></case><environments><scratchbox>false</scratchbox><hardware>true</hardware></environments><get><file>/tmp/*.xml</file></get>\
</set></suite>"
        return xml

    def _generateSuiteXML_minimum_data(self): 
        #Below XML should have all possible data fields NOT set!
        xml = "<suite name='sample_suite'>\
<set name='sample_set'><case name='sample_case'>\
<step>sample step</step></case></set></suite>"
        return xml

    def _assert_default_general_values(self, node):
        self.assertEquals(node.getType(), 'unknown')
        self.assertEquals(node.getTimeout(), DEFAULT_TIMEOUT)
        self.assertEquals(node.getDescription(), None)
        self.assertEquals(node.getRequirement(), None)
        self.assertEquals(node.getManual(), 'false')
        self.assertEquals(node.getLevel(), 'unknown')
        self.assertEquals(node.getInsignificant(), 'false')


    #
    # Tests:
    #

    def testDefaultTimeoutIsString(self):
        self.assert_(type(DEFAULT_TIMEOUT) == type(""))
    
    def test_validate_XML(self):
        """test for private _validate_XML() method"""
        self.test_parser._validate_XML()
        self.assertEquals('0.1', self.test_parser.xml_root.get('version'))
    
    def test_parse_XML_without_validation(self):
        """test that xml validation can be disabled without breaking anything"""
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "sample_input_file.xml")
        parser = TestDefinitionParser(fqname, validate_xml = False, test_xsd = TEST_XSD)
        parser._validate_XML()
        self.assertEquals('0.1', parser.xml_root.get('version'))
    
    def test_create_testpackagedata(self):
        """test for private _create_testpackagedata() method"""
        self.test_parser._validate_XML()
        testpackagedata = self.test_parser._create_testpackagedata(self.test_parser.xml_root)
        self.assertEquals('0.1', testpackagedata.getXMLVersion())
        
    def test_create_testsuite(self):
        """test for private _create_testsuite() method"""
        testpackagedata = TestPackageData('0.1')
        suite_node = ET.XML(self._generateSuiteXML())
        node = self.test_parser._create_testsuite(testpackagedata, suite_node)
        self.assertEquals(node.getName(), 'sample_suite')
        self.assertEquals(node.getType(), 'Performance')
        self.assertEquals(node.getTimeout(), '111')
        self.assertEquals(node.getDescription(), 'Preferred suite description.')
        self.assertEquals(node.getRequirement(), 'suitereq')
        self.assertEquals(node.getManual(), 'false')
        self.assertEquals(node.getLevel(), 'suitelevel')
        self.assertEquals(node.getInsignificant(), 'true')

        self.assertEquals(node.getDomain(), 'sample_domain')

    def test_create_testset(self):
        """test for private _create_testset() method"""
        testpackagedata = TestPackageData('0.1')
        suite_node = ET.XML(self._generateSuiteXML())
        testsuite = self.test_parser._create_testsuite(testpackagedata, suite_node)
        
        for set_node in suite_node:
            if set_node.tag == 'set':
                node = self.test_parser._create_testset(testpackagedata, testsuite, set_node)
                self.assertEquals(node.getName(), 'sample_set')
                self.assertEquals(node.getType(), 'Security')
                self.assertEquals(node.getTimeout(), '20')
                self.assertEquals(node.getDescription(), 'set_description')
                self.assertEquals(node.getRequirement(), 'setreq')
                self.assertEquals(node.getManual(), 'true')
                self.assertEquals(node.getLevel(), 'setlevel')
                self.assertEquals(node.getInsignificant(), 'false')

                self.assertEquals(node.getFeature(), 'yyy')

    def test_create_testcase(self):
        """test for private _create_testcase() method"""
        testpackagedata = TestPackageData('0.1')
        suite_node = ET.XML(self._generateSuiteXML())
        testsuite = self.test_parser._create_testsuite(testpackagedata, suite_node)
        
        for set_node in suite_node.findall('set'):
            testset = self.test_parser._create_testset(testpackagedata, testsuite, set_node)
            for case_node in set_node.findall('case'):
                node = self.test_parser._create_testcase(testpackagedata, testset, case_node)
                self.assertEquals(node.getName(), 'sample_case')
                self.assertEquals(node.getType(), 'Functional')
                self.assertEquals(node.getTimeout(), '10')
                self.assertEquals(node.getDescription(), 'Preferred case description.')
                self.assertEquals(node.getRequirement(), 'casereq')
                self.assertEquals(node.getManual(), 'false')
                self.assertEquals(node.getLevel(), 'caselevel')
                self.assertEquals(node.getInsignificant(), 'true')

                self.assertEquals(node.getSubfeature(), 'xxx')


    def test_testsuite_default_values(self):
        """Test testsuite default values"""
        testpackagedata = TestPackageData('0.1')
        suite_node = ET.XML(self._generateSuiteXML_minimum_data())
        node = self.test_parser._create_testsuite(testpackagedata, suite_node) #assumes there's only one suite

        self._assert_default_general_values(node)

        self.assertEquals(node.getDomain(), None)


    def test_default_values_inheritance(self):
        """Test inheritance of default values all the way from suite to case"""
        testpackagedata = TestPackageData('0.1')
        suite_node = ET.XML(self._generateSuiteXML_minimum_data())
        testsuite = self.test_parser._create_testsuite(testpackagedata, suite_node) #assumes there's only one suite

        for set_node in suite_node:
            if set_node.tag == 'set':
                testset = self.test_parser._create_testset(testpackagedata, testsuite, set_node)

                self.test_parser._inherit_attributes_suite_to_set(testsuite, testset)

                self._assert_default_general_values(testset)

                self.assertEquals(testset.getFeature(), None)

                for case_node in set_node.findall('case'):
                    testcase = self.test_parser._create_testcase(testpackagedata, testset, case_node)

                    self.test_parser._inherit_attributes_set_to_case(testset, testcase)

                    self._assert_default_general_values(testcase)

                    self.assertEquals(testcase.getSubfeature(), None)


    def testFindNode(self):
        """test _find_node function"""
        suite_node = ET.XML(self._generateSuiteXML())
        presteps = []
        get_files = []
        
        for set_node in suite_node:
            presteps = self.test_parser._find_node(set_node, "pre_steps")
            get_files = self.test_parser._find_node(set_node, "get")
        
        self.assertEquals(['ls'], presteps)
        self.assertEquals(['/tmp/*.xml'], get_files)
        
    def testGetEnvironments(self):
        """test _get_environments function"""
        suite_node = ET.XML(self._generateSuiteXML())
        environments = []
        
        for set_node in suite_node:
            environments = self.test_parser._get_environments(set_node)
            
        self.assertEquals(['hardware'], environments)
    
    def testGetPoststep(self):
        """test get_poststep function"""
        suite_node = ET.XML(self._generateSuiteXML())
        poststep = PostSteps()
        
        for set_node in suite_node:
            poststep = self.test_parser._get_poststep(set_node)
        
        self.assertEquals(['pwd'], poststep.getPoststeps())




class TestTestDefinitionParser2(unittest.TestCase):
    '''more unit tests for testdefinitionparser'''
    def setUp(self):
        #Note: These tests are really using the below file as input!
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "sample_input_file.xml")
        self.test_parser = TestDefinitionParser(fqname, test_xsd = TEST_XSD) 

    def testParseTestDefinition(self):
        """test parse_test_definition function"""
        testpackagedata = self.test_parser.parse_test_definition()
        
        self.assertEquals('examplebinary-tests', testpackagedata.suites[0].getName())
        self.assertEquals('testset1', testpackagedata.suites[0].testsets[0].getName())
        self.assertEquals('serm003', testpackagedata.suites[0].testsets[0].testcases[1].getName())
        self.assertEquals('pwd', testpackagedata.suites[0].testsets[0].testcases[0].getSteps()[1])
        

    def test_data_inheritance_suite_to_set(self):
        """test data inheritance from suite to set"""
        testpackagedata = self.test_parser.parse_test_definition()
        
        self.assertEquals('unknown', testpackagedata.suites[0].testsets[0].getType())
        self.assertEquals('15',      testpackagedata.suites[0].testsets[0].getTimeout())
        self.assertEquals('12345',   testpackagedata.suites[0].testsets[0].getRequirement())

        self.assertEquals('unknown', testpackagedata.suites[0].testsets[1].getType())
        self.assertEquals('10',      testpackagedata.suites[0].testsets[1].getTimeout())

        #assert inheritance should not overwrite existing attribute
        self.assertEquals('715517',   testpackagedata.suites[0].testsets[1].getRequirement()) 
        
    def test_data_inheritance_set_to_case(self):
        """test data inheritance from set to case"""
        testpackagedata = self.test_parser.parse_test_definition()
        
        self.assertEquals('unknown', testpackagedata.suites[0].testsets[0].testcases[0].getType())
        self.assertEquals('15',      testpackagedata.suites[0].testsets[0].testcases[1].getTimeout())
        self.assertEquals('715517',      testpackagedata.suites[0].testsets[1].testcases[2].getRequirement())

        self.assertEquals('unknown', testpackagedata.suites[0].testsets[1].testcases[0].getType())
        self.assertEquals('10',      testpackagedata.suites[0].testsets[1].testcases[3].getTimeout())

        #assert inheritance should not overwrite existing attribute
        self.assertEquals('33333',   testpackagedata.suites[0].testsets[1].testcases[0].getRequirement()) 

if __name__ == "__main__":
    unittest.main()
