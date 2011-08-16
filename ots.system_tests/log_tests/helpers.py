from configobj import ConfigObj
from log_scraper import has_message

common_cfg = ConfigObj("log_tests.conf")
# This file optional and not in version control. Put your local changes there!
local_cfg = ConfigObj("log_tests.local.conf")
common_cfg.merge(local_cfg)
CONFIG = common_cfg.get("log_tests")

def base_url():
    return "http://" + CONFIG["server"]

def assert_has_messages(test, testrun_id, messages):
    for message in messages:
        assert_has_message(test, testrun_id, message)

def assert_has_message(test, testrun_id, string):
    test.assertTrue(has_message(CONFIG["global_log"], testrun_id, string),
        "Missing text: " + string)

