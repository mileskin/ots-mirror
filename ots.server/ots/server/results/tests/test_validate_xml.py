import unittest

import os

from ots.server.results.validate_xml import validate_xml

class TestValidateXML(unittest.TestCase):

    def test_validate_xml(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        results_file = os.path.join(dirname, "data", "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        validate_xml(results_xml)
        
if __name__ == "__main__":
    unittest.main()
