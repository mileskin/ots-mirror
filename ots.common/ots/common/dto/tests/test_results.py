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

from ots.common.dto.results import Results

class TestResults(unittest.TestCase):

    def test_results(self):
        results = Results("foo", "<result>pass</result>",
                          package = "pkg1", 
                          hostname = "unittest", 
                          environment = "meego")
        self.assertEquals("foo", results.data.name)
        self.assertEquals("<result>pass</result>",
                          results.data.read())

    def test_is_test_definition_true(self):
        results = Results("test_definition_for_asdf.xml",
                          "<result>pass</result>",
                          package = "pkg1", 
                          hostname = "unittest", 
                          environment = "meego")
        self.assertTrue(results.is_definition_xml)

    def test_is_test_definition_false(self):
        results = Results("thisisnotatest_definition_for_asdf.xml",
                          "<result>pass</result>",
                          package = "pkg1", 
                          hostname = "unittest", 
                          environment = "meego")
        self.assertFalse(results.is_definition_xml)


    def test_is_result_xml_true(self):
        results = Results("tatam_xml_testrunner_results_for_asdf.xml",
                          "<result>pass</result>",
                          package = "pkg1", 
                          hostname = "unittest", 
                          environment = "meego")
        self.assertTrue(results.is_result_xml)

    def test_is_result_xml_false(self):
        results = Results("thisisnotatatam_xml_testrunner_results_for_asdf.xml",
                          "<result>pass</result>",
                          package = "pkg1", 
                          hostname = "unittest", 
                          environment = "meego")
        self.assertFalse(results.is_result_xml)


        
if __name__ == "__main__":
    unittest.main()
