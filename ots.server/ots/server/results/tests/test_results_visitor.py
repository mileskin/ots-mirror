import unittest

import os

from ots.server.results.results_visitor import visit_results, ResultsVisitor
from ots.server.results.results_visitor import validate_xml

class TestResultsVisitor(unittest.TestCase):

    def test_results_visitor(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        f = open(results_file, "r")
        visit_results(f.read())

    def test_validate_xml(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        validate_xml(results_xml)
        

if __name__ == "__main__":
    unittest.main()
