import os

import xml.etree.cElementTree as ET
from minixsv import pyxsval as xsv


from ots.server.results.results_judge_processor import ResultsJudgeProcessor

def validate_xml(results_xml):
    dirname = os.path.dirname(os.path.abspath(__file__))
    testdefinition_xsd = os.path.join(dirname,
                                      "testdefinition-results.xsd")
    results_xsd = open(testdefinition_xsd).read()
    etw = xsv.parseAndValidateXmlInputString(results_xml, 
                                     xsdText = results_xsd)
   
    tree = etw.getTree()
        
def visit_results(results_xml):
    visitor = ResultsVisitor()
    results_judge_processor = ResultsJudgeProcessor()
    #FIXME: Where are the active packages set from
    results_judge_processor.set_active_package("foo", "bar")
    visitor.add_processor(results_judge_processor)
    root = ET.fromstring(results_xml)
    visitor.visit(root)

class ResultsVisitor(object):
    """
    Extrinsic Visitor 
    """

    _processors = []

    def add_processor(self, processor):
        self._processors.append(processor)

    def visit(self, node):
        for processor in self._processors:
            processor.pre_process(node)
        for child_node in node.getchildren():
            self.visit(child_node)
        for processor in self._processors:
            processor.post_process(node)
