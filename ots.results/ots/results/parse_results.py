# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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

import xml.etree.cElementTree as ElementTree

from ots.results.validate_xml import validate_xml
from ots.results.visitors import ElementTreeVisitor 
from ots.results.significant_results_processor import \
                               SignificantResultsProcessor
        
def parse_results(results_xml, insignificant_tests_matter):
    """
    @type results_xml: C{string} 
    @param results_xml: The results xml

    @type insignificant_tests_matter: C{bool} 
    @param insignificant_tests_matter: Flag

    @rtype: C(list} of C{TestrunResult} 
    @param: A list of the Test results that matter

    Parse the Test results xml
    """
    validate_xml(results_xml)
    visitor = ElementTreeVisitor()
    processor = SignificantResultsProcessor(insignificant_tests_matter)
    visitor.add_processor(processor)
    root = ElementTree.fromstring(results_xml)
    visitor.visit(root)
    return processor.all_passed
