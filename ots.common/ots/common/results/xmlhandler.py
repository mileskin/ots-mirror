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
This file contains the xml handler plugin. It parses xml files and
calls registered backend objects to do the real work with the parsed data.
"""
import xml.etree.cElementTree as ET
from ots.common.interfaces.resultfilehandler import ResultFileHandler
import logging

XML_PATTERN = "tatam_xml_testrunner"

class XmlHandler(ResultFileHandler):
    """plugin class for parsing xml result format"""

        
    # Disabling pylint warning about not specified exception types.
    # We want to make sure that problems in a backend cannot crash the whole
    # parsing process so we want to catch everything.
    # pylint: disable-msg=W0702
    # pylint: disable-msg=W0703


    
    def __init__(self, testrun, xml_file_name_pattern=XML_PATTERN):
        self.log = logging.getLogger(__name__)
        self.backends = []
        self.testrun = testrun
        self.xml_filename_pattern = xml_file_name_pattern
        self.processing_started = False
        self.error_messages = []

    def register_backend(self, backend):
        """
        Register new backend into plugin. Backend is used for saving
        results into for example database, testcenter etc.
        """
        self.backends.append(backend)
        self.log.debug("registered backend %s into xml handler" \
                           % backend.name())
        
    def name(self):
        """Returns name of the results plugin"""
        return "XmlHandler"
        
    def save_results(self, testrun_object):
        """
        Store testrun results with all backends

        @type testrun_object: C{testrun}
        @param testrun_object: Testrun object

        @rtype: C{list}
        @return: List of error message strings if backends raised exceptions

        """
        
        # Invalid name is part of the interface
        # pylint: disable-msg=C0103
        
        # testrun_object is part of the interface so it's an argument
        # even though it is not needed here
        # pylint: disable-msg=W0613
               
        
        for plugin in self.backends:
            try:
                plugin.finished_processing()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

        return self.error_messages

    
    def add_result_object(self, result_object):
        """Processes a new result object"""

        # Invalid name is part of the interface
        # pylint: disable-msg=C0103
        
        if not self.processing_started:
            self._processing_started(self.testrun)
        
        self._process_raw_file(result_object)
       
        if result_object.name().find(self.xml_filename_pattern) != -1:
            self._process_xml_file(result_object)

    def _process_raw_file(self, result_object):
        """Processes a raw result file with every backend plugin"""
        for plugin in self.backends:
            self.log.debug("Processing raw file %s with %s" %
                           (result_object.name(), plugin.name()))
            try:
                plugin.process_raw_file(result_object, self.testrun)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _process_xml_file(self, result_object):
        """Processes an xml file with every backend plugin"""

        self._pre_process_xml_file(result_object)
        root = ET.fromstring(result_object.get_content())
        values = self._xml_element_get_items(root)

        self._pre_process_test_results(values)
        for suite in root.findall("suite"):
            values = self._xml_element_get_items(suite)
            self._pre_process_suite(values)
            for testset in suite.findall("set"):
                values = self._xml_element_get_items(testset)
                self._pre_process_set(values)
                for case in testset.findall("case"):
                    case_values = self._xml_element_get_items(case)

                    for child in case.getchildren(): # process element values
                        if child.tag != "step":      # (for example "comment")
                            case_values[child.tag] = child.text
                        
                    self._pre_process_case(case_values)
                    for child in case.findall("step"): # process steps
                        step_values = self._xml_element_get_items(child)
                        for element in child.getchildren():
                            step_values[element.tag] = element.text
                        self._pre_process_step(step_values)
                        self._post_process_step()
                        
                    self._post_process_case()
                self._post_process_set()
            self._post_process_suite()
        self._post_process_test_results()
        self._post_process_xml_file()

    def _pre_process_xml_file(self, result_object):
        """Calls pre_process_xml_file() in every backend plugin"""
        for plugin in self.backends:
            self.log.debug("Processing xml result file %s with %s" %
                           (result_object.name(), plugin.name()))

            try:
                plugin.pre_process_xml_file(result_object, self.testrun)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _pre_process_test_results(self, values):
        """Calls pre_process_test_results() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.pre_process_test_results(values)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _pre_process_suite(self, values):
        """Calls pre_process_suite() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.pre_process_suite(values)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _pre_process_set(self, values):
        """Calls pre_process_set() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.pre_process_set(values)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _pre_process_case(self, values):
        """Calls pre_process_case() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.pre_process_case(values)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _pre_process_step(self, values):
        """Calls pre_process_step() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.pre_process_step(values)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_xml_file(self):
        """Calls post_process_xml_file() in every backend plugin"""
        for plugin in self.backends:
            try:        
                plugin.post_process_xml_file()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_test_results(self):
        """Calls post_process_test_results() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.post_process_test_results()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_suite(self):
        """Calls post_process_suite() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.post_process_suite()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_set(self):
        """Calls post_process_set() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.post_process_set()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_case(self):
        """Calls post_process_case() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.post_process_case()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _post_process_step(self):
        """Calls post_process_step() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.post_process_step()
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")

    def _processing_started(self, testrun_object):
        """Calls started_processing() in every backend plugin""" 
        for plugin in self.backends:
            try:
                plugin.started_processing(testrun_object)
            except Exception, error_message:
                self.error_messages.append(str(error_message))
                self.log.exception("Something went wrong in backend")


    def _xml_element_get_items(self, element):
        """returns xml element items as a dictionary"""
        values = element.items()
        items = {}
        for key, value in values:
            items[key] = value

        return items


