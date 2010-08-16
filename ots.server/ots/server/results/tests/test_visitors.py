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

import xml.etree.cElementTree as ElementTree

from ots.server.results.visitors import ElementTreeVisitor, ResultsVisitor
from ots.server.results.results_processor_base import ResultsProcessorBase

class DispatcherStub(object):

    tags = []
    
    def dispatch_element(self, element):
        self.tags.append(element.tag)

class TestElementTreeVisitor(unittest.TestCase):

    def test_visit(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        root = ElementTree.fromstring(results_xml)
        visitor = ElementTreeVisitor()
        dispatcher = DispatcherStub()
        visitor.add_dispatcher(dispatcher)
        visitor.visit(root)
        expected = ["testresults", "suite", "set",
        "case", "step", "expected_result", "return_code", "start", "end", 
        "case", "step", "expected_result", "return_code", "start", "end", 
        "case", "step", "expected_result", "return_code", "start", "end"]
        self.assertEquals(expected, dispatcher.tags)
        

class ProcessorStub(ResultsProcessorBase):

    cases = []

    def _preproc_case(self, element):
        self.cases.append(element.tag)

    def _postproc_case(self):
        self.cases.append("postproc")

class TestResultsVisitor(unittest.TestCase):

    def test_visit(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        root = ElementTree.fromstring(results_xml)
        visitor = ResultsVisitor()
        processor = ProcessorStub()
        visitor.add_processor(processor)
        visitor.visit(root)
        self.assertEqual(['case', 'postproc']*3, processor.cases)

if __name__ == "__main__":
    unittest.main()
