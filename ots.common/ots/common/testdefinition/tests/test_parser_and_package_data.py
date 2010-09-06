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


import unittest 

import os

from ots.common.testdefinition.testdefinitionparser import TestDefinitionParser

module = os.path.dirname(os.path.abspath(__file__))
TEST_XSD = os.path.join(module,
                        "data", 
                        "testdefinition-tm_terms.xsd")

class Test_Parser_With_PackageData(unittest.TestCase):
    """
    Test testpackagedata together with testdefinitionparser
    """

    def test_toXMLs(self):
        """
        Test that XML parsing and XML regeneration using toXMLs() do not leave
        any data out.
        Testpackagedata parsed from original XML and testpackagedata parsed from
        regenerated XML are verified to contain same data.

        TODO: <get> tag is not yet implemented!
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "sample_input_file.xml")

        parser1 = TestDefinitionParser(fqname, test_xsd = TEST_XSD)
        data1 = parser1.parse_test_definition()
        new_xml = data1.toXMLs()

        #print "new_xml = %s" % new_xml

        #parse regenerated xml string
        parser2 = TestDefinitionParser(input_xml = new_xml, test_xsd = TEST_XSD)
        data2 = parser2.parse_test_definition()

        def assure_general_attributes(node1, node2):
            self.assertEquals(node1.getName()          , node2.getName())
            self.assertEquals(node1.getDescription()   , node2.getDescription())
            self.assertEquals(node1.getType()          , node2.getType())
            self.assertEquals(node1.getTimeout()       , node2.getTimeout())
            self.assertEquals(node1.getRequirement()   , node2.getRequirement())
            self.assertEquals(node1.getManual()        , node2.getManual())
            self.assertEquals(node1.getLevel()         , node2.getLevel())
            self.assertEquals(node1.getInsignificant() , node2.getInsignificant())

        def assure_suite_data(node1, node2):
            assure_general_attributes(node1, node2)
            self.assertEquals(node1.getDomain()   , node2.getDomain())

        def assure_set_data(node1, node2):
            assure_general_attributes(node1, node2)
            self.assertEquals(node1.getFeature(),                node2.getFeature())
            self.assertEquals(node1.getEnvironments(),           node2.getEnvironments())
            self.assertEquals(node1.getPrestep().getPresteps(),  node2.getPrestep().getPresteps())
            self.assertEquals(node1.getPoststep().getPoststeps(),node2.getPoststep().getPoststeps())
            #self.assertEquals(node1.getGetFiles()              ,node2.getGetFiles()) #not yet implemented

        def assure_case_data(node1, node2):
            assure_general_attributes(node1, node2)
            self.assertEquals(node1.getSubfeature()   , node2.getSubfeature())

        #assure original data (data1) matches to regenerated data (data2)
        for suite1, suite2 in zip(data1.getTestSuite(), data2.getTestSuite()):
            assure_suite_data(suite1, suite2)
            for set1, set2 in zip(suite1.getTestsets(), suite2.getTestsets()):
                assure_set_data(set1, set2)
                for case1, case2 in zip(set1.getTestcases(), set2.getTestcases()):
                    assure_case_data(case1, case2)


if __name__ == "__main__":
    unittest.main()
