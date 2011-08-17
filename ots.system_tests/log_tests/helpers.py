from log_scraper import has_message
from configuration import CONFIG

def base_url():
    return "http://" + CONFIG["server"]

def assert_has_messages(test, testrun_id, messages):
    for message in messages:
        assert_has_message(test, testrun_id, message)

def assert_has_message(test, testrun_id, string):
    test.assertTrue(has_message(testrun_id, string), "Missing text: " + string)

