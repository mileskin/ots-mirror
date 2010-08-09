import unittest

import os

from ots.server.hub.results_visitor import visit_results, ResultsVisitor

class TestResultsVisitor(unittest.TestCase):

    def test_results_visitor(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        f = open(results_file, "r")
        visit_results(f.read())

if __name__ == "__main__":
    unittest.main()
