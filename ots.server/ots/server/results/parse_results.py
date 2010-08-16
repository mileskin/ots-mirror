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
Parses Test Results XML as defined by

http://gitorious.org/qa-tools/test-definition

Implemented using Visitor Pattern to maintain backward compatibility
"""

import os

import xml.etree.cElementTree as ElementTree

from ots.server.results.validate_xml import validate_xml
from ots.server.results.visitors import ResultsVisitor 
from ots.server.results.package_results_processor import PackageResultsProcessor
        
def parse_results(results_xml, test_package, environment):
    """
    @type results_xml: C{string} 
    @param results_xml: The results xml

    @type results_xml: C{string} 
    @param results_xml: The name of the test package 

    @type results_xml: C{string} 
    @param results_xml: The enviroment

    @rtype: L{ots.common.api.PackageResults}
    @return: A populated PackageResults

    Parse the Test results xml
    """
    validate_xml(results_xml)
    visitor = ResultsVisitor()
    results_judge_processor = PackageResultsProcessor(test_package, environment)
    visitor.add_processor(results_judge_processor)
    root = ElementTree.fromstring(results_xml)
    visitor.visit(root)
    return results_judge_processor.package_results
