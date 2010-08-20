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

from ots.results.package_results_processor import PackageResultsProcessor

class TestPackageResultsProcessor(unittest.TestCase):

    def test_is_significant(self):
        package_results_processor = PackageResultsProcessor("testpackage", 
                                                            "environment")
        #
        class NoInsigTagElementStub:
            def items(self):
                return [("foo", 1)]
        self.assertTrue(package_results_processor._is_significant(
                                  NoInsigTagElementStub()))
            
        #
        class InsigFalseElementStub:
            def items(self):
                return [("insignificant", "false")]
        self.assertTrue(package_results_processor._is_significant(
                                  InsigFalseElementStub()))
            
        #
        class InsigTrueElementStub:
            def items(self):
                return [("insignificant", "true")]
        self.assertFalse(package_results_processor._is_significant(
                                  InsigTrueElementStub()))
            
    def test_pre_process_case(self):
        package_results_processor = PackageResultsProcessor("testpackage", 
                                                            "environment")
        class ElementSignificant:
            def items(self):
                return [("insignificant", "false"), ("result", "pass")]
        package_results_processor._preproc_case(ElementSignificant())
        
        class ElementInsignificant:
            def items(self):
                return [("insignificant", "true"), ("result", "fail")]
        package_results_processor._preproc_case(ElementInsignificant())

        pkg_results = package_results_processor.package_results
        self.assertEquals(["pass"], pkg_results.significant_results)
        self.assertEquals(["fail"], pkg_results.insignificant_results)



if __name__ == "__main__":
    unittest.main()
