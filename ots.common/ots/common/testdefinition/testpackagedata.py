#! /usr/bin/env python


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


"""Classes for representing data from test definition xml."""

from xml.etree.cElementTree import tostring
import xml.etree.cElementTree as ET

class GeneralElement(object): 
    """Common methods for TestSuite, TestSet and TestCase classes."""

    def __init__(self):
        self.name = None
        self.type = None
        self.timeout = None
        self.description = None
        self.requirement = None
        self.insignificant = None
        self.level = None
        self.manual = None

    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name

    def setType(self, type):
        self.type = type
       
    def getType(self):
        return self.type
        
    def setTimeout(self, timeout):
        self.timeout = timeout
        
    def getTimeout(self):
        return self.timeout
        
    def setDescription(self, description):
        self.description = description
        
    def getDescription(self):
        return self.description

    def setManual(self, manual):
        self.manual = manual

    def getManual(self):
        return self.manual

    def setLevel(self, level):
        self.level = level

    def getLevel(self):
        return self.level

    def setRequirement(self, requirement):
        self.requirement = requirement
        
    def getRequirement(self):
        return self.requirement

    def getRequirementList(self):
        """Returns requirements as a list

        Returns:

            Requirements as a list of strings

        Notes:

            - Whitespaces are stripped from the end and beginning of the items
        """
        requirement_list = []
        if self.requirement:
            for requirement in self.requirement.split(","):
                requirement_list.append(requirement.strip())
        return requirement_list

    def setInsignificant(self, insignificant):
        self.insignificant = insignificant

    def getInsignificant(self):
        return self.insignificant

    def _set_general_data(self, element):
        """Write general attributes into given XML element"""
        if self.getName():
            element.set("name", self.getName())
        if self.getRequirement():
            element.set("requirement", self.getRequirement())
        if self.getType():
            element.set("type", self.getType())
        if self.getTimeout():
            element.set("timeout", self.getTimeout())
        if self.getManual():
            element.set("manual", self.getManual())
        if self.getLevel():
            element.set("level", self.getLevel())
        if self.getInsignificant():
            element.set("insignificant", self.getInsignificant())

        description = ET.SubElement(element, 'description')
        description.text = self.getDescription()


class TestSuite(GeneralElement):
    '''Class to contain the attributes of test suite'''
    def __init__(self, name, domain = None, type = None, timeout = None,
                 description = None, requirement = None, manual = None,
                 level = None, insignificant = None):

        GeneralElement.__init__(self)

        # mandatory attributes
        self.name = name
        self.description = description
        self.state = True
        
        # optional attributes
        self.domain = domain
        self.type = type
        self.timeout = timeout
        self.requirement = requirement
        self.manual = manual
        self.level = level
        self.insignificant = insignificant

        # a list of TestSet objects in this suite        
        self.testsets = []

    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state
        
    def setSuiteName(self, name): #depricated
        self.name = name
    def getSuiteName(self): #depricated
        return self.name

    def setDomain(self, domain):
        self.domain = domain
        
    def getDomain(self):
        return self.domain
        
    
    def setTestsets(self, testsets):
        self.testsets = testsets
        
    def getTestsets(self):
        return self.testsets
        
    def addTestset(self, testset):
        """Add a new testset to this suite"""
        self.testsets.append(testset)
        
    def remove_testset(self, testset):
        '''remove a testset from the list'''
        if testset in self.testsets:
            self.testsets.remove(testset)
            

    def toXML(self):
        '''returns an Suite object constructed by ElementTree'''
        
        root = ET.Element("suite")

        # General attributes and tags

        self._set_general_data(root)

        # Specific content

        if self.getDomain():
            root.set("domain", self.getDomain())
        
        for testset in self.getTestsets():
            # append each set subelement to suite element
            root.append(testset.toXML())
                
        return root
        
        
        
class PreSteps(object):
    '''Class to hold pre-steps inside testset'''
    def __init__(self):
        self.presteps = []
        self.expected_results = []
        self.state = True


    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state

        
    def setPresteps(self, presteps):
        self.presteps = presteps
        
    def getPresteps(self):
        return self.presteps
        
    def setExpectedResults(self, expected_results):
        self.expected_results = expected_results
        
    def getExpectedResults(self):
        return self.expected_results
        
        
class PostSteps(object):
    '''Class to hold post-steps inside testset'''
    def __init__(self):
        self.poststeps = []
        self.expected_results = []
        self.state = True


    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state

        
    def setPoststeps(self, poststeps):
        self.poststeps = poststeps
        
    def getPoststeps(self):
        return self.poststeps
        
    def setExpectedResults(self, expected_results):
        self.expected_results = expected_results
        
    def getExpectedResults(self):
        return self.expected_results
        
                

class AdditionalFiles(object):
    '''Class to hold additional files inside testset'''
    def __init__(self):
        self.additional_files = []
        self.state = True


    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state

        
    def setAdditionalFiles(self, additional_files):
        self.additional_files = additional_files
        
    def getAdditionalFiles(self):
        return self.additional_files
    

class TestSet(GeneralElement):
    '''Class to contain the attributes of test set'''
    def __init__(self, name, description, feature = None, timeout = None,
                 type = None, requirement = None, manual = None, level = None,
                 insignificant = None):

        GeneralElement.__init__(self)

        self.name = name
        self.description = description
        self.state = True        
        self.feature = feature
        self.timeout = timeout
        self.type = type
        self.requirement = requirement
        self.manual = manual
        self.level = level
        self.insignificant = insignificant

        # initialize object presteps
        self.presteps = PreSteps()
        self.poststeps = PostSteps()
        self.environments = []
        
        # initialize object additional_files
        self.additional_files = AdditionalFiles()
        
        # a list of TestCase objects in this test set
        self.testcases = []


    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state
        

    def setSetName(self, name): #depricated
        self.name = name
    def getSetName(self): #depricated
        return self.name
       
        
    def setFeature(self, feature):
        self.feature = feature
        
    def getFeature(self):
        return self.feature
        
        
    def setPrestep(self, prestep):
        self.presteps = prestep
    
    def getPrestep(self):
        return self.presteps
        
    def setPoststep(self, poststep):
        self.poststeps = poststep
        
    def getPoststep(self):
        return self.poststeps
        
    def setEnvironments(self, environments):
        self.environments = environments
        
    def getEnvironments(self):
        return self.environments
        
    def addEnvironment(self, environment):
        """Add Environment to current set"""
        self.environments.append(environment)
        
    def setAdditionalFiles(self, additionalfiles):
        self.additional_files.setAdditionalFiles(additionalfiles)
        
    def getAdditionalFiles(self):
        return self.additional_files.getAdditionalFiles()
      
        
    def setTestcases(self, testcases):
        self.testcases = testcases
        
    def getTestcases(self):
        return self.testcases
    
        
    def addTestcase(self, testcase):
        """Add a test case to self"""
        self.testcases.append(testcase)
        
    def remove_testcase(self, testcase):
        '''remove testcase from the list'''
        if testcase in self.testcases:
            self.testcases.remove(testcase)
        

    def toXML(self): #TODO: some tags (e.g. <get>) are not implemented
        '''returns an Set object constructed by ElementTree'''
        setRoot = ET.Element("set")

        # General attributes and tags

        self._set_general_data(setRoot)

        # Specific content

        if self.getFeature():
            setRoot.set("feature", self.getFeature())

        #pre_steps tag
        if self.getPrestep().getPresteps():
            pre_steps = ET.SubElement(setRoot, 'pre_steps')
            for step_content in self.getPrestep().getPresteps():
                step = ET.SubElement(pre_steps, 'step')
                step.text = step_content

        #post_steps tag
        if self.getPoststep().getPoststeps():
            post_steps = ET.SubElement(setRoot, 'post_steps')
            for step_content in self.getPoststep().getPoststeps():
                step = ET.SubElement(post_steps, 'step')
                step.text = step_content

        #case tags
        for testcase in self.getTestcases():
            setRoot.append(testcase.toXML())
        
        #environments tag
        environments = ET.SubElement(setRoot, 'environments')
        for env in ('scratchbox', 'hardware'): #TODO: get list from
                                               #      testdefinionparser?
            env_node = ET.SubElement(environments, env)
            if env in self.getEnvironments():
                env_node.text = "true"
            else:
                env_node.text = "false"
                        
        return setRoot    


class TestCase(GeneralElement):
    '''Class to contain the attributes of test case'''
    def __init__(self, name, description, subfeature = None, timeout = None,
                 type = None, requirement = None, manual = None, level = None,
                 insignificant = None):

        GeneralElement.__init__(self)

        self.name = name
        self.description = description
        
        self.steps = []
        self.expected_results = []
        self.state = True        
        self.subfeature = subfeature
        self.timeout = timeout
        self.type = type
        self.requirement = requirement
        self.manual = manual
        self.level = level
        self.insignificant = insignificant


    def get_state(self):
        """
        Returns the state of the object. True means that object is active and 
        will be processed.

        Filters can change the state to False. Then they will not be processed. 
        """
        return self.state
        

    def set_state(self, state):
        """
        Sets the state of the object. True means that object is active and 
        will be processed.

        To filter out a suite/set/case etc, call set_state(False) 
        """
        self.state = state

    def setCaseName(self, name): #depricated
        self.name = name
    def getCaseName(self): #depricated
        return self.name
    
        
    def setSteps(self, steps):
        self.steps = steps
        
    def getSteps(self):
        return self.steps
    
    def addSteps(self, steps):
        """Add steps to this case"""
        self.steps.extend(steps)
        
    def setSubfeature(self, subfeature):
        self.subfeature = subfeature
        
    def getSubfeature(self):
        return self.subfeature
        

    def setExpectedResults(self, expected_results):
        self.expected_results = expected_results
        
    def getExpectedResults(self):
        return self.expected_results
        

    def toXML(self):
        '''returns a Case object constructed by ElementTree'''
        caseRoot = ET.Element("case")

        # General attributes and tags

        self._set_general_data(caseRoot)

        # Specific content

        if self.getSubfeature():
            caseRoot.set("subfeature", self.getSubfeature())

        for step in self.getSteps():
            stepNode = ET.SubElement(caseRoot, "step")
            stepNode.text = step
            
        return caseRoot
        


class TestPackageData(object):
    '''
    Class to contain test package data including info. of test suite, set and
    cases
    '''
    def __init__(self, version):
        self.version = version
        self.suites = []
        self.name = ""
        self.environment = ""
        
    def setXMLVersion(self, version):
        self.version = version
        
    def getXMLVersion(self):
        return self.version
        
    def setTestSuite(self, suites): #depricated
        self.suites = suites
    def getTestSuite(self):  #depricated
        return self.suites

    def setSuites(self, suites):
        self.suites = suites
    def getSuites(self):
        return self.suites
        
    def addTestSuite(self, testSuite):
        """Add a test suite to this testpackagedata"""
        self.suites.append(testSuite)
        

    def newTestsuiteObject(self,
                           name,
                           domain = None,
                           type = None,
                           timeout = None,
                           description = None,
                           requirement = None,
                           manual = None,
                           level = None,
                           insignificant = None):
        """
        Creates new TestSuite to self
        """

        suiteObject = TestSuite(name,
                                domain,
                                type,
                                timeout,
                                description,
                                requirement,
                                manual,
                                level,
                                insignificant)

        self.addTestSuite(suiteObject)
        return suiteObject
        
    def newTestsetObject(self,
                         suiteobject,
                         name, description,
                         feature = None,
                         timeout = None,
                         type = None,
                         prestep = None,
                         additional_files = None,
                         environments = None,
                         poststep = None,
                         requirement = None,
                         manual = None,
                         level = None,
                         insignificant = None):
        """
        Creates new TestSet to the suiteobject
        """

        setObject = TestSet(name,
                            description,
                            feature,
                            timeout,
                            type,
                            requirement,
                            manual,
                            level,
                            insignificant)

        if prestep:
            setObject.setPrestep(prestep)
        if poststep:
            setObject.setPoststep(poststep)
        if additional_files:
            setObject.setAdditionalFiles(additional_files)
        if environments:
            setObject.setEnvironments(environments)
        
        suiteobject.addTestset(setObject)
        return setObject
        
    def newTestcaseObject(self,
                          setobject,
                          name,
                          description,
                          command,
                          subfeature = None,
                          timeout = None,
                          type = None,
                          requirement = None,
                          manual = None,
                          expected_results = None,
                          level = None,
                          insignificant = None):
        """
        Creates new TestCase to the setobject
        """
        caseObject = TestCase(name,
                              description,
                              subfeature,
                              timeout,
                              type,
                              requirement,
                              manual,
                              level,
                              insignificant)
        caseObject.addSteps(command)
        caseObject.setExpectedResults(expected_results)
        
        setobject.addTestcase(caseObject)
        return caseObject
        
        
    def toXML(self):
        '''returns test package root object constructed by ElementTree '''
        root = ET.Element("testdefinition")
        root.set("version", self.getXMLVersion())
        
        for test_suite in self.getSuites():
            root.append(test_suite.toXML())
                
        return root
                
    def toXMLs(self):
        '''convert the entire test package into XML string representation'''
        root = self.toXML()
        indent(root)
        return tostring(root)
        
    def process_testdata(self, processor):
        '''general structure to implement test-related executions'''
        
        processor.pre_process_testpackagedata(self.getXMLVersion())

        for test_suite in self.getSuites():
            if test_suite.get_state() == False:
                continue
            processor.pre_process_suite(test_suite)
            for test_set in test_suite.getTestsets():
                if test_set.get_state() == False:
                    continue
                processor.pre_process_set(test_set)
                processor.process_presteps(test_set.getPrestep())
                for test_case in test_set.getTestcases():
                    if test_case.get_state() == False:
                        continue
                    processor.pre_process_case(test_case)
                    processor.post_process_case(test_case)
                    
                processor.post_process_set()
                processor.\
                    process_get_additional_files(test_set.getAdditionalFiles())
                processor.process_poststeps(test_set.getPoststep())
                            
            processor.post_process_suite()
            
        return processor.post_process_testpackagedata()
        
        
def indent(elem, level=0):
    """Creates an indented version of elementree xml"""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
