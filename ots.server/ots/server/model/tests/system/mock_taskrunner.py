import os
import time

from ots.common.api import OTSProtocol, PROTOCOL_VERSION
from ots.common.api import ResultObject

from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL
from ots.server.distributor.api import OtsGlobalTimeoutError

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
        return open(results_file, "r").read()

    def run(self):
        self._send_testpackages()
        time.sleep(0.5)
        self._send_result(self.results_xml, "test_1")
        time.sleep(0.5)
        self._send_result(self.results_xml, "test_2")

    @staticmethod
    def _send_result(results_xml, name):
        result = ResultObject(name,
                              content = results_xml,
                              testpackage = "Unknown",
                              origin = "mock_task_runner",
                              environment = "component_test")

        kwargs = {OTSProtocol.RESULT : result}
        RESULTS_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

    @staticmethod
    def _send_testpackages():
        packages = {"component_test" : ["package_1", "package_2"]}
        kwargs = {OTSProtocol.PACKAGES : packages}
        PACKAGELIST_SIGNAL.send(sender = "MockTaskRunner", **kwargs)


class MockTaskRunnerTimeout(object):

    def run(self):
        raise OtsGlobalTimeoutError("Mock")

class MockTaskRunnerError(object):

    def run(self):
        kwargs = {OTSProtocol.ERROR_CODE : 6310,
                  OTSProtocol.ERROR_INFO : "mock task runner"}
        ERROR_SIGNAL.send(sender = "MockTaskRunner", **kwargs)
