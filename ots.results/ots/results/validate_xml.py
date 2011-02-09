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
Validate the testresults using the schema defined here:

http://gitorious.org/qa-tools/test-definition/
"""

from minixsv import pyxsval as xsv

from ots.results.results_schema import SCHEMA_FILENAME 

def validate_xml(results_xml):
    """
    @type results_xml: C{string} 
    @param results_xml: The results xml 

    Postprocess the element
    """

    results_xsd = open(SCHEMA_FILENAME).read()
    etw = xsv.parseAndValidateXmlInputString(results_xml, 
                                     xsdText = results_xsd)
   
    etw.getTree()
