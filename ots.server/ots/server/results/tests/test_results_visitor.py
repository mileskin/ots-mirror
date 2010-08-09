import unittest

import os

from ots.server.results.results_visitor import visit_results, ResultsVisitor

class TestResultsVisitor(unittest.TestCase):

    def test_results_visitor(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        package_results =  visit_results(results_xml, "foo", "bar")
        print "sig", package_results.significant_results
        print "insig", package_results.insignificant_results

if __name__ == "__main__":
    unittest.main()
