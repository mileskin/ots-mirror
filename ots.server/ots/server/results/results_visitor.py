import os

import xml.etree.cElementTree as ET

from ots.server.results.package_results_processor import PackageResultsProcessor
        
def visit_results(results_xml, test_package, environment):
    visitor = ResultsVisitor()
    results_judge_processor = PackageResultsProcessor(test_package, environment)
    visitor.add_processor(results_judge_processor)
    root = ET.fromstring(results_xml)
    visitor.visit(root)
    return results_judge_processor.package_results

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
