from log_scraper import testrun_log_url, log_page_contains_message

def assert_log_page_contains_messages(test, testrun_id, messages):
    for message in messages:
        assert_log_page_contains_message(test, testrun_id, message)

def assert_log_page_does_not_contain_messages(test, testrun_id, messages):
    for message in messages:
        assert_log_page_does_not_contain_message(test, testrun_id, message)

def assert_log_page_contains_message(test, testrun_id, string):
    test.assertTrue(log_page_contains_message(testrun_id, string),
        "Missing text '%s' in testrun '%s'." %
        (string, testrun_log_url(testrun_id)))

def assert_log_page_does_not_contain_message(test, testrun_id, string):
    test.assertFalse(log_page_contains_message(testrun_id, string),
        "Found text '%s' in testrun '%s'." %
        (string, testrun_log_url(testrun_id)))

def assert_log_page_contains_regexp_patterns(test, testrun_id, patterns):
    for pattern in patterns:
        assert_log_page_contains_regexp_pattern(test, testrun_id, pattern)

def assert_log_page_does_not_contain_regexp_patterns(test, testrun_id, patterns):
    for pattern in patterns:
        assert_log_page_does_not_contain_regexp_pattern(test, testrun_id, pattern)

def assert_log_page_contains_regexp_pattern(test, testrun_id, pattern):
    test.assertTrue(log_page_contains_regexp_pattern(testrun_id, pattern),
        "Missing pattern '%s' in testrun '%s'." %
        (pattern, testrun_log_url(testrun_id)))

def assert_log_page_does_not_contain_regexp_pattern(test, testrun_id, pattern):
    test.assertFalse(log_page_contains_regexp_pattern(testrun_id, pattern),
        "Found pattern '%s' in testrun '%s'." %
        (pattern, testrun_log_url(testrun_id)))
