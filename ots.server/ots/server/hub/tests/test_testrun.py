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

import unittest

import os

from ots.common.dto.api import Packages, Results

import ots.results
from ots.results.api import TestrunResult, PackageException

from ots.server.hub.testrun import Testrun

class TestTestrun(unittest.TestCase):

    def test_package_exception(self):
        tr = Testrun()
        tr.run_test = lambda : 1
        self.assertRaises(PackageException, tr.run)

    def test_fail(self):
        pkgs = Packages("hardware", ["pkg1", "pkg2"])
        results_dir = os.path.dirname(os.path.abspath(ots.results.__file__))
        results_fqname = os.path.join(results_dir, 
                                      "tests", "data", 
                                      "dummy_results_file.xml")
        results_xml = open(results_fqname, "r")
        results = Results("tatam_xml_testrunner_fail", results_xml.read())
        tr = Testrun()
        tr._dto_handler.expected_packages = pkgs
        tr._dto_handler.tested_packages = pkgs
        

        tr._dto_handler.results = [results]
        tr.run_test = lambda : 1
        self.assertFalse(tr.run())
      
    def test_pass(self):
        pkgs = Packages("hardware", ["pkg1", "pkg2"])
        results_dir = os.path.dirname(os.path.abspath(ots.results.__file__))
        results_fqname = os.path.join(results_dir, 
                                      "tests", "data", 
                                      "dummy_pass_file.xml")
        results_xml = open(results_fqname, "r")
        results = Results("tatam_xml_testrunner_results_for_pass", results_xml.read())

        tr = Testrun()
        tr._dto_handler.expected_packages = pkgs
        tr._dto_handler.tested_packages = pkgs
        tr._dto_handler.results = [results]
        tr.run_test = lambda : 1
        self.assertTrue(tr.run())
 
if __name__ == "__main__":
    unittest.main()
