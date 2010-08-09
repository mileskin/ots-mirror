
import xml.etree.cElementTree as ET

from ots.server.results.results_judge_processor import ResultsJudgeProcessor


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
