# -*- coding: utf-8 -*-

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

"""Parses test XML definition and constructs various test-related objects"""

import logging
import os
from xml.etree.cElementTree import parse
from xml.etree.cElementTree import fromstring
from xml.etree.cElementTree import ElementTree

from testpackagedata import TestPackageData, PreSteps, PostSteps
from minixsv import pyxsval


OTS_TESTDEFINITION = "OTS_TESTDEFINITION"
TEST_DEFINITION_XSD = "testdefinition-tm_terms.xsd"

DEFAULT_TIMEOUT = "90"  #default test case timeout

ALL_ENVIRONMENT = ['hardware']
DEFAULT_SCHEMA = "/usr/share/test-definition/testdefinition-tm_terms.xsd"

module = os.path.dirname(os.path.abspath(__file__))
TEST_XSD = os.path.join(module, "data", "testdefinition-tm_terms.xsd")

class TestDefinitionParser(object):
    """
    This class conducts all the parsing work of test definition file.

    Note: For faster XML parsing, MiniXSV web site recommends using ElementTree 
    as parser. Thus this parameter: xmlIfClass= pyxsval.XMLIF_ELEMENTTREE
    """

    #
    # Public API:
    #

    def __init__(self, input_file_path = None, input_xml = None, 
                 validate_xml = True, test_xsd = None):
        """
        There are two alternatives how to provide the input XML to be parsed:
        as a file (input_file_path) or as a string (input_xml). If both are
        given, file is used.

        test_xsd allows testing against specific XSD file. It's a relative path
        from the directory where this file is located.
        Provided for unit testing purposes only.
        """

        self.log = logging.getLogger("TestDefinitionParser")
        self.input_file_path = input_file_path #Preferred input.
        self.input_xml = input_xml             #Alternative input.
        self.xsd_file_path = ""
        self.xml_root = None
        self.validate_xml = validate_xml
        self.test_xsd = test_xsd
        self.testcase_ids = []  


    def parse_test_definition(self):
        '''
        Validates and parses the test definition file. 
        Returns a testpackagedata object holding all test information.
        '''
        self._validate_XML()

        # construct object of class TestPackageData    
        testpackagedata = self._create_testpackagedata(self.xml_root)
        for test_suite in self.xml_root.findall("suite"):
            # construct object of class Testsuite
            testsuiteobj = self._create_testsuite(testpackagedata, test_suite)
            for test_set in test_suite.findall("set"):
                # construct object of class Testset
                testsetobj = self._create_testset(testpackagedata, 
                                                  testsuiteobj, test_set)
                self._inherit_attributes_suite_to_set(testsuiteobj, testsetobj)
                for test_case in test_set.findall("case"):
                    # construct object of class TestCase
                    testcaseobj = self._create_testcase(testpackagedata, 
                                                        testsetobj, test_case)
                    self._inherit_attributes_set_to_case(testsetobj, 
                                                         testcaseobj)
        
        return testpackagedata


    #
    # Private methods:
    #        
        
    def _validate_XML(self, validate_schema = False):
        '''Validates XML against schema file'''

        self._check_input_defined()
        self._choose_schema_file()

        if validate_schema:
            self._validate_schema_file()

        if self.input_file_path:
            self._validate_and_parse_from_file()
        else:
            self._validate_and_parse_from_string()


    def _check_input_defined(self):
        if not self.input_file_path and not self.input_xml:
            raise Exception("No input XML given")

    def _choose_schema_file(self):
        """Choose schema file"""
        if self.test_xsd:
            self.xsd_file_path = os.path.join(\
                    os.path.dirname(os.path.abspath(__file__)), self.test_xsd)
        else:
            self.xsd_file_path = DEFAULT_SCHEMA

        if not os.path.isfile(self.xsd_file_path):
            env = os.environ
            if env.has_key(OTS_TESTDEFINITION):
                dirname = env[OTS_TESTDEFINITION]
                self.xsd_file_path = os.path.join(dirname, TEST_DEFINITION_XSD)

        if not os.path.isfile(self.xsd_file_path):
            raise Exception("XSD file missing: %s" % self.xsd_file_path)

    def _validate_schema_file(self):
        """Validate schema file"""
        pyxsval.parseAndValidateXmlSchema(self.xsd_file_path, 
                                    xmlIfClass= pyxsval.XMLIF_ELEMENTTREE)

    def _validate_and_parse_from_file(self):
        """Validate xml from file"""
        self.log.debug("Validating xml from file")

        # Validate
        if self.validate_xml:
            pyxsval.parseAndValidateXmlInput(self.input_file_path, 
                                    self.xsd_file_path, 
                                    xmlIfClass= pyxsval.XMLIF_ELEMENTTREE)
            self.log.info("%s is valid." % self.input_file_path)

        # Parse
        self.xml_root = parse(self.input_file_path).getroot() #default parser

    def _validate_and_parse_from_string(self):
        """Validate xml from string"""
        self.log.debug("Validating xml from string")

        # Validate
        if self.validate_xml:
            xsd_file = open(self.xsd_file_path, "r")
            xsd_text = xsd_file.read()
            xsd_file.close()
            pyxsval.parseAndValidateXmlInputString(self.input_xml, xsd_text,
                                    xmlIfClass= pyxsval.XMLIF_ELEMENTTREE)
            self.log.info("XML is valid.")

        # Parse
        self.xml_root = ElementTree(fromstring(self.input_xml)).getroot()

        
    def _find_node(self, set_node, pattern):
        '''find demanded node under set_node according to specific pattern'''
        demand_node = set_node.findall(pattern)
        demand_list = []
        for child_node in demand_node:
            for element in child_node:
                demand_list.append(element.text)
                
        return demand_list


    def _pick_description(self, node):
        """Return description from XML element. Prefer tag over attribute."""
        if node.findall("description"):
            return node.findall("description")[0].text
        else:
            return node.get('description')


    def _get_prestep(self, set_node):
        '''Returns a Prestep object'''
        prestep = PreSteps()
        
        demand_node = set_node.findall('pre_steps')
        for child_node in demand_node:
            for element in child_node:
                prestep.presteps.append(element.text)
                #Pre_step: allowed value for expected result 
                #is "integer-string" or not given at all
                expected_result = element.get('expected_result', None)
                prestep.expected_results.append(expected_result)
                                
        return prestep
        
    def _get_poststep(self, set_node):
        '''Returns a Poststep object'''
        poststep = PostSteps()
        
        demand_node = set_node.findall('post_steps')
        for child_node in demand_node:
            for element in child_node:
                poststep.poststeps.append(element.text)
                expected_result = element.get('expected_result', "0")
                poststep.expected_results.append(expected_result)
                                
        return poststep
        
    def _get_environments(self, set_node):
        """Returns list of environments defined in the set_node"""
        demand_node = set_node.findall("environments")
        
        # All environments are enabled by default.
        demand_list = ALL_ENVIRONMENT[:]

        for environment in demand_node:
            for specific_environment in environment:
                if specific_environment.text == 'false' \
                    and specific_environment.tag in demand_list:
                    demand_list.remove(specific_environment.tag)
                elif specific_environment.text == 'true' \
                    and not specific_environment.tag in demand_list:
                    demand_list.append(specific_environment.tag)
                                
        return demand_list

        
    def _create_testpackagedata(self, root):
        '''Initialize the testpackagedata object'''    
        testpackagedata = TestPackageData(root.get('version'))
        return testpackagedata
        
    def _create_testsuite(self, testpackagedata, suite_node):
        '''create testsuite object'''

        description = self._pick_description(suite_node)

        #if xml attribute is not set, each parameter will be set to None
        testsuite = testpackagedata.newTestsuiteObject(
                    name =          suite_node.get('name'), 
                    domain =        suite_node.get('domain'), 
                    type =          suite_node.get('type', 'unknown'), 
                    timeout =       suite_node.get('timeout', DEFAULT_TIMEOUT), 
                    description =   description,
                    requirement =   suite_node.get('requirement'),
                    manual =        suite_node.get('manual', 'false'),
                    level =         suite_node.get('level', 'unknown'),
                    insignificant = suite_node.get('insignificant', 'false')
                    )

        return testsuite
        
        
    def _create_testset(self, testpackagedata, testsuite, set_node):
        '''create testset object'''
                
        # To find presteps, if any, in the test set definition
        prestep = self._get_prestep(set_node)
                
        # To find poststeps, if any, in the test set definition
        poststep = self._get_poststep(set_node)
                
        # To find definition of test environments
        test_environment_list = self._get_environments(set_node)

        # To find any addtional result file 
        additional_file_list = self._find_node(set_node, "get")

        description = self._pick_description(set_node)

        #if xml attribute is not set, each parameter will be set to None
        testset = testpackagedata.newTestsetObject(
                    suiteobject         = testsuite, 
                    name                = set_node.get('name'), 
                    description         = description,
                    feature             = set_node.get('feature'), 
                    timeout             = set_node.get('timeout'), 
                    type                = set_node.get('type'), 
                    prestep             = prestep, 
                    additional_files    = additional_file_list, 
                    environments        = test_environment_list, 
                    poststep            = poststep,
                    requirement         = set_node.get('requirement'),
                    manual              = set_node.get('manual'),
                    level               = set_node.get('level'),
                    insignificant       = set_node.get('insignificant')
                    )

        return testset
        
        
    def _create_testcase(self, testpackagedata, testset, case_node):
        '''create testcase object'''

        case_steps = []
        expected_results = []

        description = self._pick_description(case_node)

        for single_step in case_node.findall("step"):
            expected_result = single_step.get('expected_result', "0")
            expected_results.append(expected_result)
            case_steps.append(single_step.text)

        #if xml attribute is not set, each parameter will be set to None
        testcase = testpackagedata.newTestcaseObject(
                    setobject           = testset, 
                    name                = case_node.get('name'), 
                    description         = description,
                    command             = case_steps, 
                    subfeature          = case_node.get('subfeature'), 
                    timeout             = case_node.get('timeout'), 
                    type                = case_node.get('type'), 
                    requirement         = case_node.get('requirement'), 
                    manual              = case_node.get('manual'), 
                    expected_results    = expected_results,
                    level               = case_node.get('level'),
                    insignificant       = case_node.get('insignificant')
                    )

        return testcase
    
    def _inherit_attributes_suite_to_set(self, testsuite, testset):
        '''attribute inheritance from testsuite to testset'''
        if not testset.getRequirement():
            testset.setRequirement(testsuite.getRequirement())
        if not testset.getType():
            testset.setType(testsuite.getType())
        if not testset.getTimeout():
            testset.setTimeout(testsuite.getTimeout())
        if not testset.getManual():
            testset.setManual(testsuite.getManual())
        if not testset.getLevel():
            testset.setLevel(testsuite.getLevel())
        if not testset.getInsignificant():
            testset.setInsignificant(testsuite.getInsignificant())
            
    def _inherit_attributes_set_to_case(self, testset, testcase):
        '''attribute inheritance from testset to testcase'''
        if not testcase.getRequirement():
            testcase.setRequirement(testset.getRequirement())
        if not testcase.getType():
            testcase.setType(testset.getType())
        if not testcase.getRequirement():
            testcase.setRequirement(testset.getRequirement())
        if not testcase.getTimeout():
            testcase.setTimeout(testset.getTimeout())
        if not testcase.getManual():
            testcase.setManual(testset.getManual())
        if not testcase.getLevel():
            testcase.setLevel(testset.getLevel())
        if not testcase.getInsignificant():
            testcase.setInsignificant(testset.getInsignificant())
