import inspect
import uuid
import threading
import xmlrpclib
import time
from ots.tools.trigger.ots_trigger import ots_trigger, _parameter_validator
from configuration import CONFIG
from helpers import base_url, assert_has_messages
from log_scraper import has_errors
from logging_conf import log

COMMON_SUCCESS_MESSAGES = [
    "Finished running tests.",
    "All Tasks completed",
    "Publishing results",
    "Email sent",
    "Testrun finished with result: PASS"]

class Result:
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

class SystemTest(object):
    def __init__(self, test):
        self.test = test
        self.testrun_ids = []

    def run(self, options):
        testname = inspect.stack()[1][3]
        log.info("Starting system test '%s' against server %s..." % (testname,
            CONFIG['server']))
        cookie = str(uuid.uuid4())
        options.system_test_cookie = cookie
        fetch_testrun_id_thread = threading.Thread(
            target=self._fetch_testrun_ids,
            args=(testname, options.server, cookie, self.testrun_ids, log))
        fetch_testrun_id_thread.start()
        parameters = _parameter_validator({}, options.__dict__)
        result = ots_trigger(parameters)
        # Wait for the thread to get testrun id
        fetch_testrun_id_thread.join()
        self.testrun_ids.sort()
        self.result = result
        return self

    def verify(self, expected_result):
        if expected_result == Result.ERROR:
            self.test.assertEquals(self.result, Result.ERROR)
        elif expected_result == Result.FAIL:
            self.test.assertEquals(self.result, Result.FAIL)
        elif expected_result == Result.PASS:
            self.test.assertEquals(self.result, Result.PASS,
                "Result should be '%s', was '%s'." % (Result.PASS, self.result))
            id = self.id()
            assert_has_messages(self.test, id, COMMON_SUCCESS_MESSAGES)
            self.test.assertFalse(has_errors(id), "Found errors in log %s" % id)
        else:
            raise Exception('Unknown expected result \'%s\'. Actual result: %s'
                            % (expected_result, self.result))
        return self

    def id(self):
        self.test.assertTrue(self.testrun_ids, "testrun id not known")
        self.test.assertEquals(len(self.testrun_ids), 1, "system test had more than one testrun")
        return self.testrun_ids[0]

    def _fetch_testrun_ids(self, testname, server, cookie, ids, log1):
        rpc = xmlrpclib.Server("http://%s/" % server)
        max_num_retries = 3
        interval = 5
        for i in range(max_num_retries):
            time.sleep(interval)
            try:
                logs = rpc.latest_logs(interval+11)
            except xmlrpclib.ProtocolError:
                continue
            for id in [log[0] for log in logs if log[4].find(cookie) >= 0]:
                if id not in ids:
                    ids.append(id)
            if ids:
                break
        if not ids:
            log1.error("New test run not found on server after %d " \
                "seconds, server: %s, cookie: %s" % \
                (max_num_retries * interval, CONFIG['server'], cookie))
        for id in ids:
            log1.info("Testrun: %s" % {
                "id": id,
                "name": testname,
                "url": "%s/logger/view/testrun/%s/" % (base_url(), id)})

