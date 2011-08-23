from log_scraper import has_message
from configuration import CONFIG

def testrun_log_urls(testrun_ids):
    return map(testrun_log_url, testrun_ids)

def testrun_log_url(testrun_id):
    return "%s/logger/view/testrun/%s/" % (base_url(), testrun_id)

def base_url():
    return "http://" + CONFIG["server"]

def assert_has_messages(test, testrun_id, messages):
    for message in messages:
        assert_has_message(test, testrun_id, message)

def assert_has_not_messages(test, testrun_id, messages):
    for message in messages:
        assert_has_not_message(test, testrun_id, message)

def assert_has_message(test, testrun_id, string):
    test.assertTrue(has_message(testrun_id, string),
        "Missing text '%s' in testrun '%s'." %
        (string, testrun_log_url(testrun_id)))

def assert_has_not_message(test, testrun_id, string):
    test.assertFalse(has_message(testrun_id, string),
        "Found text '%s' in testrun '%s'." %
        (string, testrun_log_url(testrun_id)))

