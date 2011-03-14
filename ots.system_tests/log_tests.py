# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ***** END LICENCE BLOCK *****

"""
OTS log based system tests.

These tests expect that you have full ots system set up. They trigger testruns
and check http logs for expected results

Make sure there is no other activities going on in the system while running 
the tests!

Please check that system_tests.conf is up to date!

"""

import configobj
import unittest
import urllib2
from configobj import ConfigObj
from BeautifulSoup import BeautifulSoup
from ots.tools.trigger.ots_trigger import ots_trigger

CONFIGFILE = "system_tests.conf"
CONFIG = ConfigObj(CONFIGFILE).get("log_tests")

class Options(object):
    """A mock for ots_trigger options"""

    def __init__(self):


        # Default call options
        self.id = 0
        self.image = CONFIG["image_url"]
        self.testpackages = ""
        self.hosttest = ""
        self.distribution = "default"
        self.filter = ""
        self.input_plugin = ""
        self.device = ""
        self.sw_product = "ots-system-tests"
        self.email = CONFIG["email"]
        self.timeout = 30
        self.server = CONFIG["server"]

    pass

class TestSuccessfulTestruns(unittest.TestCase):

    def test_hw_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.testpackages = "test-definition-tests"
        options.sw_product = "ots-system-tests"
        options.timeout = 30

        print "****************************"
        print "Triggering a HW based test run with test-definition-tests\n"
        print "System requirements:"
        print "Image with test-definition-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check environment
        string = "Environment: Hardware"
        self.assertTrue(has_message(testrun_id, string))

        string = "Environment: Host_Hardware"
        self.assertFalse(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string))

        # Check a message from testrunner-lite
        string = """Finished running tests."""
        self.assertTrue(has_message(testrun_id, string))

    def test_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.testpackages = ""
        options.sw_product = "ots-system-tests"
        options.timeout = 30

        print "****************************"
        print "Triggering a testrun with test-definition-tests\n"
        print "System requirements:"
        print "Image with test-definition-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check environment
        string = "Environment: Hardware"
        self.assertFalse(has_message(testrun_id, string))

        string = "Environment: Host_Hardware"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string))

        # Check a message from testrunner-lite
        string = """Finished running tests."""
        self.assertTrue(has_message(testrun_id, string))

    def test_hw_and_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.testpackages = "test-definition-tests"
        options.sw_product = "ots-system-tests"
        options.timeout = 60

        print "****************************"
        print "Triggering a testrun with test-definition-tests on host and hardware\n"
        print "System requirements:"
        print "Image with test-definition-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests configured to sw_product %s." % options.sw_product

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check environment
        string = "Environment: Hardware"
        self.assertTrue(has_message(testrun_id, string))

        string = "Environment: Host_Hardware"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string))

        # Check that both environments get executed
        string = "Environment: Host_Hardware"
        self.assertTrue(has_message(testrun_id, string))

        string = "Environment: Hardware"
        self.assertTrue(has_message(testrun_id, string))

        # Check a message from testrunner-lite
        string = """Finished running tests."""
        self.assertTrue(has_message(testrun_id, string))

    def test_testrun_with_filter(self):
        options = Options()
        options.testpackages = "testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.timeout = 30
        options.filter = "testcase=trlitereg01,trlitereg02"

        print "****************************"
        print "Triggering a test run with testrunner-lite-regression-tests and"\
            " filter\n"
        print "System requirements:"
        print "Image with testrunner-lite-regression-tests available in %s"\
             % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product
        print "Test filter with two cases enabled: %s"\
            % options.filter

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check test case filtering
        # trlitereg01 should not be filtered
        string = "Test case trlitereg01 is filtered"
        self.assertFalse(has_message(testrun_id, string))
        
        # trlitereg02 should not be filtered
        string = "Test case trlitereg02 is filtered"
        self.assertFalse(has_message(testrun_id, string))
        
        # trlitereg03 should be filtered
        string = "Test case quoting_01 is filtered"
        self.assertTrue(has_message(testrun_id, string))
        
        # quoting_01 should be filtered
        string = "Test case quoting_01 is filtered"
        self.assertTrue(has_message(testrun_id, string))
        
        # two cases should be executed and passed
        string = "Executed 2 cases. Passed 2 Failed 0"
        self.assertTrue(has_message(testrun_id, string))

    def test_hw_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60

        print "****************************"
        print "Triggering two test runs with per package distribution"
        print "System requirements:"
        print "Image with test-definition-tests and testrunner-lite-" \
            "regression-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests and testrunner-lite-regression-tests configured to "\
            "sw_product %s." % options.sw_product
        print "Filter set to run only one case from both packages: %s" \
            % options.filter
        
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string, 2))

        # Check a message from testrunner-lite
        string = "Finished running tests."
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check two messages from two separate tests on HW
        string = "Testrun ID: %s  Environment: Hardware" % testrun_id
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check correct test package executions
        string = "Beginning to execute test package: test-definition-tests"
        self.assertTrue(has_message(testrun_id, string, 1))
        string = "Beginning to execute test package: testrunner-lite-regression-test"
        self.assertTrue(has_message(testrun_id, string, 1))
        
        string = "Executed 1 cases. Passed 1 Failed 0"
        self.assertTrue(has_message(testrun_id, string, 2))

    def test_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60

        print "****************************"
        print "Triggering two host based test runs with per package "\
            "distribution"
        print "System requirements:"
        print "Image with test-definition-tests and testrunner-lite-" \
            "regression-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests and testrunner-lite-regression-tests configured to "\
            "sw_product %s." % options.sw_product
        print "Filter set to run only one case from both packages: %s" \
            % options.filter
        
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string, 2))

        # Check a message from testrunner-lite
        string = "Finished running tests."
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check two messages from two separate tests on host
        string = "Testrun ID: %s  Environment: Host_Hardware" % testrun_id
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check correct test package executions
        string = "Beginning to execute test package: test-definition-tests"
        self.assertTrue(has_message(testrun_id, string, 1))
        string = "Beginning to execute test package: testrunner-lite-regression-test"
        self.assertTrue(has_message(testrun_id, string, 1))
        
        string = "Executed 1 cases. Passed 1 Failed 0"
        self.assertTrue(has_message(testrun_id, string, 2))

    def test_hw_and_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 120

        print "****************************"
        print "Triggering a test run with test-definition-tests on "\
            "host and hardware\n"
        print "System requirements:"
        print "Image with test-definition-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests configured to sw_product %s." % options.sw_product

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string, 4))

        # Check that both environments get executed, two test on host side
        # and two tests on HW side
        string = "Environment: Host_Hardware"
        self.assertTrue(has_message(testrun_id, string, 2))
        string = "Environment: Hardware"
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check that test finished four times (2 x HW and 2 x host).
        string = "Finished running tests."
        self.assertTrue(has_message(testrun_id, string, 4))

    def test_hw_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution = "default"
        options.testpackages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = "ots-system-tests"
        options.timeout = 60

        print "****************************"
        print "Triggering two HW based test runs with multiple test packages"
        print "System requirements:"
        print "Image with test-definition-tests and testrunner-lite-regression"\
            "-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests and testrunner-lite-regression-tests configured to "\
            "sw_product %s." % options.sw_product
        print "Filter set to run one case from each package: %s" \
            % options.filter
        
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string, 1))

        # Check a message from testrunner-lite
        string = "Finished running tests."
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check two messages from two separate tests on HW
        string = "Environment: Hardware"
        self.assertTrue(has_message(testrun_id, string, 1))
    
    def test_host_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution = "default"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.filter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = "ots-system-tests"
        options.timeout = 60

        print "****************************"
        print "Triggering two host based test runs with multiple test packages"
        print "System requirements:"
        print "Image with test-definition-tests and testrunner-lite-regression"\
            "-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product
        print "A fully functional worker capable of running test-definition-"\
            "tests and testrunner-lite-regression-tests configured to "\
            "sw_product %s." % options.sw_product
        print "Filter set to run one case from each package: %s" \
            % options.filter
        
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "PASS")

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertFalse(has_errors(testrun_id))

        string = "Testrun finished with result: PASS"
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string, 1))

        # Check a message from testrunner-lite
        string = "Finished running tests."
        self.assertTrue(has_message(testrun_id, string, 2))
        
        # Check two messages from two separate tests on host
        string = "Environment: Host_Hardware"
        self.assertTrue(has_message(testrun_id, string, 1))

class TestCustomDistributionModels(unittest.TestCase):

    def assert_log_contains_string(self, testrun_id, string):
        self.assertTrue(has_message(testrun_id, string),
          "'%s' not found on log for testrun_id: '%s'" % (string, testrun_id))
    
    def test_load_example_distribution_model(self):
        options = Options()
        options.distribution = "example_model"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with test package distribution schema '%s'"\
            % options.distribution
        print "This test requires that ots.plugin.example_distribution_model "\
            +"from examples/ is installed."

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = "Example distribution model not implemented."
        self.assert_log_contains_string(testrun_id, string)

class TestErrorConditions(unittest.TestCase):

    def assert_log_contains_string(self, testrun_id, string): 
        self.assertTrue(has_message(testrun_id, string), 
         "'%s' not found on log for testrun_id: '%s'" % (string, testrun_id))

    def test_bad_image_url(self):
        # Trigger a testrun with non existing image url. Check correct result
        # and error message
        options = Options()
        options.image = options.image+"asdfasdfthiswontexistasdfasdf"
        options.testpackages = "testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.timeout = 30

        print "****************************"
        print "Triggering a testrun with bad image url\n"

        result = ots_trigger(options)

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id

        # Check the return value
        self.assertEquals(result, "ERROR")

        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assertTrue(has_message(testrun_id, string))

        path = options.image.split("/")[-1]
        string = "Error: Could not download file " \
            "%s, Error code: 103" % path
        self.assertTrue(has_message(testrun_id, string))

        # Check message from conductor
        string = "Starting conductor at"
        self.assertTrue(has_message(testrun_id, string))


    def test_timeout(self):
        # Trigger long testrun with short timeout value. Make sure result is
        # fail and correct error message is generated

        options = Options()
        options.testpackages = "testrunner-lite-regression-tests"
        options.sw_product = "ots-system-tests"
        options.timeout = 1

        print "****************************"
        print "Triggering a testrun with testrunner-lite-regression-tests, 1 minute timeout\n"
        print "System requirements:"
        print "Image with testrunner-lite-regression-tests available in %s" % options.image
        print "SW Product %s defined" % options.sw_product
        print "A fully functional worker configured to %s."\
            % options.sw_product

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id

        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"


        # Check error message

        string = "Error: Timeout while executing test package testrunner-lite-regression-tests, Error code: 1091"
        self.assert_log_contains_string(testrun_id, string)

        # Check message from conductor        
        string = 'Test execution error: Timeout while executing test package testrunner-lite-regression-tests'
        self.assert_log_contains_string(testrun_id, string)



    def test_non_existing_devicegroup(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with non existing devicegroup '%s'"\
            % options.device
        print "Please make sure the system does not have that devicegroup."

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Testrun finished with result: ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = """No queue for this_should_not_exist"""
        self.assert_log_contains_string(testrun_id, string)

        string = """Incoming request: program: ots-system-tests, request: 0, notify_list: ['%s'], options: {"""  % (CONFIG["email"])
        self.assert_log_contains_string(testrun_id, string)
        string = """'image': '%s'""" % CONFIG["image_url"]
        self.assert_log_contains_string(testrun_id, string)
        string = """'distribution_model': 'default'"""
        self.assert_log_contains_string(testrun_id, string)
        string = """'timeout': 1"""
        self.assert_log_contains_string(testrun_id, string)
        string = """'device': 'devicegroup:this_should_not_exist'"""
        self.assert_log_contains_string(testrun_id, string)

    def test_non_existing_sw_product(self):
        options = Options()
        options.sw_product = "this_should_not_exist"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with non existing sw_product '%s'"\
            % options.sw_product
        print "Please make sure the system does not have that sw_product."

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))
        string = """'this_should_not_exist' not found"""
        self.assert_log_contains_string(testrun_id, string)

        string = """Incoming request: program: this_should_not_exist, request: 0, notify_list: ['%s'], options: {"""  % (CONFIG["email"])
        self.assert_log_contains_string(testrun_id, string)


        string = """'image': '%s'""" % CONFIG["image_url"]
        self.assert_log_contains_string(testrun_id, string)
        string = """'distribution_model': 'default'"""
        self.assert_log_contains_string(testrun_id, string)
        string = """'timeout': 1"""
        self.assert_log_contains_string(testrun_id, string)



    def test_bad_testpackage_names(self):
        options = Options()
        options.testpackages = "test-definition-tests thisisnotatestpackage"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with invalid test package names '%s'"\
            % options.testpackages

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = "Invalid testpackage(s): thisisnotatestpackage"
        self.assert_log_contains_string(testrun_id, string)


    def test_no_image_url(self):
        options = Options()
        options.timeout = 1
        options.image = ""
        print "****************************"
        print "Triggering a testrun with empty image url"


        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = "Missing `image` parameter"
        self.assert_log_contains_string(testrun_id, string)

    def test_bad_distribution_model(self):
        options = Options()
        options.distribution = "sendalltestrunstowastebin"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with invalid test package distribution schema '%s'"\
            % options.distribution

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = "Invalid distribution model: sendalltestrunstowastebin"
        self.assert_log_contains_string(testrun_id, string)

    def test_perpackage_distribution_no_packages(self):
        options = Options()
        options.distribution = "perpackage"
        options.timeout = 1
        print "****************************"
        print "Triggering a testrun with perpackage distribution without any testpackages defined"

        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")
        
        # Log checks:
        testrun_id = get_latest_testrun_id()
        print "testrun_id: %s" %testrun_id
        self.assertTrue(has_errors(testrun_id))

        string = "Result set to ERROR"
        self.assert_log_contains_string(testrun_id, string)

        string = "Test packages must be defined for specified distribution model 'perpackage'"
        self.assert_log_contains_string(testrun_id, string)



class TestDeviceProperties(unittest.TestCase):

    def test_multiple_devicegroups(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist_1;devicegroup:this_should_not_exist_either"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with multiple devicegroups: '%s'"\
            % options.device
        print "Please make sure the system does not have these devicegroups."
        print "Checking that a separate testrun gets created for all devicegroups."
        
        old_testrun = get_latest_testrun_id()
        print "latest testrun_id before test: %s" % old_testrun
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id()
        testrun_id2 = get_latest_testrun_id()
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2

        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(testrun_id1))
        self.assertTrue(has_errors(testrun_id2))

        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)
        string1 = """No queue for this_should_not_exist_1"""
        string2 = """No queue for this_should_not_exist_either"""
        
        if (has_message(testrun_id1, string1)):
            self.assertTrue(has_message(testrun_id2, string2))
        else:
            self.assertTrue(has_message(testrun_id2, string1))
            self.assertTrue(has_message(testrun_id1, string2))

    def test_one_devicegroup_multiple_devicenames(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:device1;devicegroup:this_should_not_exist devicename:device2"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with one devicegroup, multiple devicenames: '%s'"\
            % options.device
        print "Please make sure the system does not have the devicegroup."
        print "Checking that a separate testrun gets created for all devicenames."
        
        old_testrun = get_latest_testrun_id()
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id()        
        testrun_id2 = get_latest_testrun_id()

        print "latest testrun_id before test: %s" % old_testrun
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2

        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(testrun_id1))
        self.assertTrue(has_errors(testrun_id2))

        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)

        string1 = """No queue for this_should_not_exist.device1"""
        string2 = """No queue for this_should_not_exist.device2"""
        
        if (has_message(testrun_id1, string1)):
            self.assertTrue(has_message(testrun_id2, string2))
        else:
            self.assertTrue(has_message(testrun_id2, string1))
            self.assertTrue(has_message(testrun_id1, string2))


    def test_one_devicegroup_one_devicename_multiple_device_ids(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:device1 deviceid:id1;devicegroup:this_should_not_exist devicename:device1 deviceid:id2"
        options.timeout = 1
        print "****************************"
        print "Calling ots xmlrpc with one devicegroup, one devicename,  multiple device ids: '%s'"\
            % options.device
        print "Please make sure the system does not have the devicegroup."
        print "Checking that a separate testrun gets created for all devicenames."
        
        old_testrun = get_latest_testrun_id()
        result = ots_trigger(options)

        # Check the return value
        self.assertEquals(result, "ERROR")

        testrun_id1 = get_second_latest_testrun_id()        
        testrun_id2 = get_latest_testrun_id()

        print "latest testrun_id before test: %s" % old_testrun
        print "testrun_id1: %s" %testrun_id1
        print "testrun_id2: %s" %testrun_id2


        # Make sure we are not reading logs from previous runs
        self.assertTrue(old_testrun not in (testrun_id1, testrun_id2))

        self.assertTrue(has_errors(testrun_id1))
        self.assertTrue(has_errors(testrun_id2))
        

        # Make sure correct routing keys are used
        string1 = """No queue for this_should_not_exist.device1.id1"""
        string2 = """No queue for this_should_not_exist.device1.id2"""
        
        if (has_message(testrun_id1, string1)):
            self.assertTrue(has_message(testrun_id2, string2))
        else:
            self.assertTrue(has_message(testrun_id2, string1))
            self.assertTrue(has_message(testrun_id1, string2))


##################################
# Helper functions for log parsing
#

def get_latest_testrun_id():
    """
    Scrape the latest testrun id from the global log
    """
    file =  urllib2.urlopen(CONFIG["global_log"])
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    row1 = table.findAll("tr")[1]
    td = row1.findAll("td")[0]
    a = td.findAll("a")[0].string
    return a

def get_second_latest_testrun_id():
    """
    Scrape the second latest testrun id from the global log
    """
    latest = get_latest_testrun_id()
    file =  urllib2.urlopen(CONFIG["global_log"])
    soup = BeautifulSoup(file.read())
    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for row in rows:
        if row.findAll("td"):
            td = row.findAll("td")[0]
            a = td.findAll("a")[0].string
            if a != latest:
                return a
    return None

def has_message(testrun_id, string, times=None):
    """
    Tries to find a message in the log for the given testrun.
    Returns True if message was found.
    If times parameter given returns True if string is found as many times
    as defined by count.
    """
    ret_val = False
    count = 0
    file =  urllib2.urlopen(CONFIG["global_log"]+"testrun/%s/" % testrun_id)
    soup = BeautifulSoup(file.read(),
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            if td[5].string and td[5].string.count(string):
                if times == None:
                    ret_val = True
                    break
                else:
                    count += 1
            elif td[5].string == None: # Check also <pre> messages </pre>
                if td[5].findAll("pre")[0].string.count(string):
                    if times == None:
                        ret_val = True
                        break
                    else:
                        count += 1
    
    if times == None:
        return ret_val
    else:
        if times == count:
            return True
        else:
            return False

def has_errors(testrun_id):
    """
    Checks if testrun has any error messages
    """
    ret_val = False
    file =  urllib2.urlopen(CONFIG["global_log"]+"testrun/%s/" % testrun_id)
    soup = BeautifulSoup(file.read(), 
                         convertEntities=BeautifulSoup.ALL_ENTITIES)

    table =  soup.findAll("table")[1]
    rows = table.findAll("tr")
    for tr in rows:
        td = tr.findAll("td")
        if td:
            try:
                error = td[4].findAll("span")[0].string
                if error == "ERROR":
                    ret_val = True
                    break
            except IndexError:
                pass

    return ret_val


if __name__ == "__main__":
    unittest.main()
