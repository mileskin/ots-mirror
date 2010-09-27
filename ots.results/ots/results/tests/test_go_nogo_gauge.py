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

from ots.results.testrun_result import TestrunResult
from ots.results.go_nogo_gauge import go_nogo_gauge

class TestGoNoGoGauge(unittest.TestCase):

    def test_no_cases(self):
        self.assertEquals(TestrunResult.NO_CASES, go_nogo_gauge([]))

    def test_fail(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "dummy_results_file.xml")
        f1 = open(fqname, "r")
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "dummy_pass_file.xml")
        f2 = open(fqname, "r")
        self.assertFalse(go_nogo_gauge([f1, f2]))

    def test_pass(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "dummy_pass_file.xml")
        f1 = open(fqname, "r")
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(dirname, "data", "dummy_pass_file.xml")
        f2 = open(fqname, "r")
        self.assertTrue(go_nogo_gauge([f1, f2]))

if __name__ == "__main__":
    unittest.main()
