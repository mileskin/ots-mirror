from ots.common.protocol import OTSProtocol

from ots.server.distributor.api import taskrunner_factory
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import STATUS_SIGNAL
from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL

from ots.server.distributor.api import OtsQueueDoesNotExistError
from ots.server.distributor.api import OtsGlobalTimeoutError
from ots.server.distributor.api import OtsQueueTimeoutError
from ots.server.distributor.api import OtsConnectionError

from ots.server.results.api import visit_results, PackageException
from ots.server.results.api import go_nogo_gauge
from ots.server.results.api import TestrunResult

class Testrun(object):

    results = []
    environment = None
    executed_packages = {}
    
    def __init__(self, 
                 run_test,
                 host_packages = None,
                 is_hw_testing_enabled = True,
                 insignificant_tests_matter = True):
        self._run_test = run_test
        self.is_hw_testing_enabled = is_hw_testing_enabled
        if host_packages is None:
            self.host_packages = []
        self.insignificant_tests_matter = insignificant_tests_matter

    def _results_cb(self, signal, result, sender):
        self.results.append(result)

    def _status_cb(self, signal, **kwargs):
        testrun.set_state(kwargs[OTSProtocol.STATE], 
                          kwargs[OTSProtocol.STATUS_INFO])

    def _error_cb(self, signal, **kwargs):
        testrun.set_result = "ERROR" #FIXME
        testrun.error_info = kwargs[OTSProtocol.ERROR_INFO]
        testrun.error_code = kwargs[OTSProtocol.ERROR_CODE]

    def _packagelist_cb(self, signal, packages, sender): 
        self.executed_packages = packages

    def run(self):
        ret_val = TestrunResult.FAIL

        RESULTS_SIGNAL.connect(self._results_cb)
        STATUS_SIGNAL.connect(self._status_cb)
        ERROR_SIGNAL.connect(self._error_cb)
        PACKAGELIST_SIGNAL.connect(self._packagelist_cb)

        try:
            self._run_test()
            ret_val = self._go_nogo()

        except OtsQueueDoesNotExistError:
            pass
            #error_info = "Device group '%s' does not exist" \
            #    % (self._device_group)
            #self.error_info(error_info)
            #self.result = "ERROR" #FIXME
            #self.log.exception(error_info)

        except OtsGlobalTimeoutError:
            pass
            #testrun.set_error_info(error_info)
            #testrun.set_result("ERROR")

        return ret_val
   
    def _package_results_iter(self):
        for result in self.results:
            yield visit_results(result.content, 
                                result.testpackage, 
                                result.environment)

    def _go_nogo(self):
        package_results_list = list(self._package_results_iter())    
        wtf_packages = []
        return go_nogo_gauge(self.executed_packages,
                             wtf_packages,
                             self.host_packages,
                             self.is_hw_testing_enabled,
                             package_results_list,
                             self.insignificant_tests_matter)
