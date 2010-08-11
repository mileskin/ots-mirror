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

class Testrun(object):

    results = []
    error_code = None
    error_info = None
    executed_packages = []

    def __init__(self, device_group, timeout, testrun_id):
        self._taskrunner = taskrunner_factory(device_group,
                                              timeout,
                                              testrun_id)

    def _results_cb(self, signal, **kwargs):
        results.append(kwargs['result'])

    def _status_cb(self, signal, **kwargs):
        testrun.set_state(kwargs['state'], kwargs['status_info'])

    def _error_cb(signal, **kwargs):
        testrun.set_result = "ERROR" #FIXME
        testrun.error_info = kwargs['error_info']
        testrun.error_code = kwargs['error_code']

    def _packagelist_cb(signal, **kwargs):
        self.executed_packages.append(kwargs['environment'],
                                      kwargs['packages'])

       
    def run(self, cmds):
        RESULTS_SIGNAL.connect(self._results_cb)
        STATUS_SIGNAL.connect(self._status_cb)
        ERROR_SIGNAL.connect(self._error_cb)
        PACKAGELIST_SIGNAL.connect(self._packagelist_cb)

        try:
            for cmd in cmds:
                self._taskrunner.add_task(cmd)
            self._taskrunner.run()

        except OtsQueueDoesNotExistError:
            error_info = "Device group '%s' does not exist" \
                % (self._device_group)
            self.error_info(error_info)
            self.result = "ERROR" #FIXME
            self.log.exception(error_info)

        except OtsGlobalTimeoutError:
            testrun.set_error_info(error_info)
            testrun.set_result("ERROR")
        
    def go_nogo(self):
        #Some kind of status check here
        all_packages = []
        for result in self.results:            
            all_packages.append(visit_results(result.content, 
                                              result.testpackage, 
                                              result.environment))
        return go_no_go_gauge()#FIXME
