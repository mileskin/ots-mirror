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

from ots.server.results.results_visitor import visit_results, ResultsVisitor

class TestVisitResults(unittest.TestCase):

    def test_visit_results(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        package_results =  visit_results(results_xml, "foo", "bar")
        print "sig", package_results.significant_results
        print "insig", package_results.insignificant_results

class TestResultsVisitor(self):

    def test_add_processor(self):
        pass

    def test_visit(self):
        pass

if __name__ == "__main__":
    unittest.main()
