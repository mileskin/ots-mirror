
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import STATUS_SIGNAL
from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL

class MockTaskrunner(object):

    def __init__(*args, **kwargs):
        pass

    def run(self):
        RESULTS_SIGNAL.send(sender = "TaskRunner", **kwargs)
        STATUS_SIGNAL.send(sender = "TaskRunner", **kwargs)
        ERROR_SIGNAL.send(sender = "TaskRunner", **kwargs)
        PACKAGELIST_SIGNAL.send(sender = "TaskRunner", **kwargs)
