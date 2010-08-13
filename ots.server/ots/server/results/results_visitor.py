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
Visitor for the Test Results XML as defined by

http://gitorious.org/qa-tools/test-definition

Pattern used to maintain backward compatibility
"""

import os

import xml.etree.cElementTree as ET

from ots.server.results.package_results_processor import PackageResultsProcessor
        
def visit_results(results_xml, test_package, environment):
    """
    @type results_xml: C{string} 
    @param results_xml: The results xml

    @type results_xml: C{string} 
    @param results_xml: The name of the test package 

    @type results_xml: C{string} 
    @param results_xml: The enviroment

    @rtype: L{ots.common.api.PackageResults}
    @return: A populated PackageResults
    """

    visitor = ResultsVisitor()
    results_judge_processor = PackageResultsProcessor(test_package, environment)
    visitor.add_processor(results_judge_processor)
    root = ET.fromstring(results_xml)
    visitor.visit(root)
    return results_judge_processor.package_results

class ResultsVisitor(object):
    """
    Extrinsic Visitor for the Test Results XML
    """

    _processors = []

    def add_processor(self, processor):
        """
        @type element: L{ots.server.results.ResultsProcessorBase} 
        @param element: A results processor

        Add a processor to accept nodes in tree traversal
        """
       
        self._processors.append(processor)

    def visit(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Elemment 

        Preorder Tree Traversal doing the 
        'Pre' and 'Post' processing for the processors 
        """
        for processor in self._processors:
            processor.pre_process(element)
        for child_node in element.getchildren():
            self.visit(child_node)
        for processor in self._processors:
            processor.post_process(element)
