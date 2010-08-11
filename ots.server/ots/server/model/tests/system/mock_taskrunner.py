import os
import time

from ots.common.api import OTSProtocol, PROTOCOL_VERSION
from ots.common.api import ResultObject

from ots.server.distributor.api import RESULTS_SIGNAL

import ots.server.results

class MockTaskRunnerResults(object):

    @property
    def results_xml(self):
        results_dirname = os.path.dirname(
                          os.path.abspath((ots.server.results.__file__)))
        results_file = os.path.join(results_dirname,
                                    "tests",
                                    "data", 
                                    "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()


    def run(self):
        time.sleep(1)
        self._send_result(self.results_xml, "test_1")
        time.sleep(1)
        self._send_result(self.results_xml, "test_2")

    @staticmethod
    def _send_result(results_xml, name):
        result = ResultObject(name,
                              content = results_xml,
                              testpackage = "Unknown",
                              origin = "mock_task_runner",
                              environment = "component_test")

        message = {OTSProtocol.RESULT : result}
        RESULTS_SIGNAL.send(sender = "MockTaskRunner", **message)

class MockTaskRunnerTimeout(object):

    def run(self):
        pass
