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

    def test_result(self):
        sig_results_proc = SignificantResultsProcessor(True)
        class PassElementStub:
            def items(self):
                return [("result", "PASS")]
        self.assertTrue(sig_results_proc._result(PassElementStub()))
        #
        class FailElementStub:
            def items(self):
                return [("result", "FAIL")]
        self.assertFalse(sig_results_proc._result(FailElementStub()))
        #
        class NAElementStub:
            def items(self):
                return [("result", "N/A")]
        self.assertFalse(sig_results_proc._result(NAElementStub()))

    def test_is_counted(self):
        sig_results_proc_true = SignificantResultsProcessor(True)
        sig_results_proc_false = SignificantResultsProcessor(False)

        class InsigTrueElementStub:
            def items(self):
                return [("insignificant", "true")]
        self.assertTrue(sig_results_proc_true._is_processed(
                                  InsigTrueElementStub()))

        class InsigFalseElementStub:
            def items(self):
                return [("insignificant", "false")]

        self.assertTrue(sig_results_proc_true._is_processed(
                                  InsigTrueElementStub()))

        self.assertTrue(sig_results_proc_true._is_processed(
                                  InsigFalseElementStub()))

        self.assertFalse(sig_results_proc_false._is_processed(
                                  InsigTrueElementStub()))

        self.assertTrue(sig_results_proc_true._is_processed(
                                  InsigFalseElementStub()))

    def _test_case(self):
        sig_results_proc = SignificantResultsProcessor(True)

        class ElementPass:
            def items(self):
                return [("result", "pass")]
        result = sig_results_proc._case(ElementSignificant())
        self.assertEquals("PASS", result)

        class ElementFail:
            def items(self):
                return [("result", "fail")]

        sig_results_proc._case(ElementPass())
        self.assertEquals(True, sig_results_proc.all_passed)
        sig_results_proc._case(ElementPass())
        self.assertEquals(True, sig_results_proc.all_passed)
        sig_results_proc._case(ElementFail())
        self.assertEquals(Fail, sig_results_proc.all_passed)

if __name__ == "__main__":
    unittest.main()
