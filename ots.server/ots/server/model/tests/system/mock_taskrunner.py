import os

from ots.common.api import OTSProtocol, PROTOCOL_VERSION
from ots.common.api import ResultObject

from ots.server.distributor.api import RESULTS_SIGNAL

import ots.server.results

class MockTaskRunner(object):

    def __init__(*args, **kwargs):
        pass

    def run(self):
        results_dirname = os.path.dirname(
                          os.path.abspath((ots.server.results.__file__)))
        results_file = os.path.join(results_dirname,
                                    "tests",
                                    "data", 
                                    "dummy_results_file.xml")
        results_xml = open(results_file, "r").read()
        print results_xml
        result = ResultObject("test",
                              content = results_xml,
                              testpackage = "Unknown",
                              origin = "mock_task_runner",
                              environment = "component_test")

        message = {OTSProtocol.VERSION : PROTOCOL_VERSION,
                   OTSProtocol.RESULT : result}
        #RESULTS_SIGNAL.send(sender = "MockTaskRunner", message)
      
