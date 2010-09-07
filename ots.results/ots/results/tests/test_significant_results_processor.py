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

from ots.results.significant_results_processor import \
                     SignificantResultsProcessor

class TestSignificantResultsProcessor(unittest.TestCase):

    def test_is_insignificant(self):
        significant_results_processor = SignificantResultsProcessor(True)
        #
        class NoInsigTagElementStub:
            def items(self):
                return [("foo", 1)]
        self.assertFalse(significant_results_processor._is_insignificant(
                                  NoInsigTagElementStub()))
            
        #
        class InsigFalseElementStub:
            def items(self):
                return [("insignificant", "false")]
        self.assertFalse(significant_results_processor._is_insignificant(
                                  InsigFalseElementStub()))
            
        #
        class InsigTrueElementStub:
            def items(self):
                return [("insignificant", "true")]
        self.assertTrue(significant_results_processor._is_insignificant(
                                  InsigTrueElementStub()))
            
    def test_pre_process_case(self):
        significant_results_processor = SignificantResultsProcessor(True)
        class ElementSignificant:
            def items(self):
                return [("insignificant", "false"), ("result", "pass")]
        result = significant_results_processor._case(ElementSignificant())
        self.assertEquals("PASS", result)


        class ElementInsignificant:
            def items(self):
                return [("insignificant", "true"), ("result", "fail")]
        result = significant_results_processor._case(ElementInsignificant())
        self.assertEquals("FAIL" ,result)

if __name__ == "__main__":
    unittest.main()
