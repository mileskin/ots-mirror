import os

from minixsv import pyxsval as xsv

def validate_xml(results_xml):
    dirname = os.path.dirname(os.path.abspath(__file__))
    testdefinition_xsd = os.path.join(dirname,
                                      "testdefinition-results.xsd")
    results_xsd = open(testdefinition_xsd).read()
    etw = xsv.parseAndValidateXmlInputString(results_xml, 
                                     xsdText = results_xsd)
   
    tree = etw.getTree()
