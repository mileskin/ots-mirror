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

import unittest
import os
import configobj

from log_scraper import log_page_contains_message, log_page_contains_errors
from base import SystemTest, Result
from configuration import CONFIG
from assertions import assert_log_page_contains_message, assert_log_page_contains_messages, \
         assert_log_page_does_not_contain_messages, assert_log_page_contains_regexp_pattern

############################################
# DEFAULT OPTIONS
############################################

class Options(object):
    """
    A mock for ots_trigger options
    """

    def __init__(self):
        self.build_id = CONFIG["build_id"]
        self.sw_product = CONFIG["sw_product"]
        self.image = CONFIG["image_url"]
        self.packages = "test-definition-tests"
        self.hosttest = ""
        self.hw_testplans = ""
        self.host_testplans = ""
        self.rootstrap = ""
        self.chroottest = ""
        self.distribution_model = "default"
        self.testfilter = ""
        self.input_plugin = ""
        self.device = CONFIG["device"]
        self.email = CONFIG["email"]
        self.timeout = 30
        self.server = CONFIG["server"] + "/xmlrpc"
        self.flasher_options = ""
        self.use_libssh2 = False
        self.resume = False

############################################
# TestHWBasedSuccessfulTestruns
############################################

class TestHWBasedSuccessfulTestruns(unittest.TestCase):

    def test_hw_based_testrun_with_test_definition_tests(self):
        options = Options()
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Testing in Hardware done. No errors."])

    def test_hw_based_testrun_with_test_definition_tests_using_libssh2(self):
        options = Options()
        options.use_libssh2 = True
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Starting conductor at",
            "-t %s -m 1800 --libssh2" % options.packages])

    def test_hw_based_testrun_with_flasher_options(self):
        options = Options()
        options.flasher_options = "just:testing"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_regexp_pattern(self, tid,
            "^Incoming command line parameters\:.+\-\-flasher_options\=just\:testing")

    def test_hw_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution_model = "perpackage"
        options.packages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Testrun ID: __TESTRUN_ID__  Environment: Hardware",
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-test",
            "Executed 1 cases. Passed 1 Failed 0"])

    def test_hw_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution_model = "default"
        options.packages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware"])

    def test_hw_based_testrun_with_testplan(self):
        options = Options()
        options.distribution_model = "default"
        options.hw_testplans = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Beginning to execute test package: echo_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0"])

    def test_hw_based_testrun_with_multiple_testplan(self):
        options = Options()
        options.distribution_model = "default"
        options.hw_testplans = ["data/echo_system_tests.xml",
                              "data/ls_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Beginning to execute test package: echo_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0",
            "Beginning to execute test package: ls_system_tests.xml"])

############################################
# TestHostBasedSuccessfulTestruns
############################################

class TestHostBasedSuccessfulTestruns(unittest.TestCase):

    def test_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.packages = ""
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_does_not_contain_messages(self, tid, [
            "Environment: Hardware"])

    def test_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution_model = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Testrun ID: __TESTRUN_ID__  Environment: Host_Hardware",
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-test",
            "Executed 1 cases. Passed 1 Failed 0"])

    def test_host_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution_model = "default"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware"])

    def test_host_based_testrun_with_testplan(self):
        options = Options()
        options.distribution_model = "default"
        options.host_testplans = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Beginning to execute test package: echo_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0"])

    def test_host_based_testrun_with_multiple_testplan(self):
        options = Options()
        options.distribution_model = "default"
        options.host_testplans = ["data/echo_system_tests.xml",
                              "data/ls_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Beginning to execute test package: echo_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0",
            "Beginning to execute test package: ls_system_tests.xml"])

############################################
# TestChrootBasedSuccessfulTestruns
############################################

class TestChrootBasedSuccessfulTestruns(unittest.TestCase):

    def test_chroot_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = "test-definition-tests"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: chroot",
            "Testing in chroot done. No errors."])

    def test_chroot_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution_model = "perpackage"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = \
            "test-definition-tests testrunner-lite-regression-tests"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Testrun ID: __TESTRUN_ID__  Environment: chroot",
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-test",
            "Executed 1 cases. Passed 1 Failed 0",
            "Testing in chroot done. No errors."])

    def test_chroot_based_testrun_with_multiple_tests(self):
        options = Options()
        options.distribution_model = "default"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 60
        options.rootstrap = CONFIG["rootstrap_url"]
        options.chroottest = \
            "test-definition-tests testrunner-lite-regression-tests"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: chroot",
            "Testing in chroot done. No errors."])

############################################
# TestMixedSuccessfulTestruns
############################################

class TestMixedSuccessfulTestruns(unittest.TestCase):

    def test_hw_and_host_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Environment: Host_Hardware"])

    def test_hw_and_host_based_testrun_split_into_multiple_tasks(self):
        options = Options()
        options.distribution_model = "perpackage"
        options.hosttest = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.packages = \
            "test-definition-tests testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.timeout = 120
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Environment: Hardware"])

    def test_hw_and_host_based_testplans(self):
        options = Options()
        options.distribution_model = "default"
        options.hw_testplans = ["data/ls_system_tests.xml"]
        options.host_testplans = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Environment: Hardware",
            "Beginning to execute test package: echo_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0",
            "Beginning to execute test package: ls_system_tests.xml"])

    def test_hw_test_package_and_test_plan(self):
        options = Options()
        options.distribution_model = "default"
        options.hw_testplans = ["data/ls_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Beginning to execute test package: ls_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0",
            "Beginning to execute test package: test-definition-tests"])

    def test_host_test_package_and_test_plan(self):
        options = Options()
        options.distribution_model = "default"
        options.host_testplans = ["data/ls_system_tests.xml"]
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Beginning to execute test package: ls_system_tests.xml",
            "Executed 1 cases. Passed 1 Failed 0",
            "Beginning to execute test package: test-definition-tests"])

    def test_host_and_hw_test_package_and_test_plan(self):
        options = Options()
        options.distribution_model = "default"
        options.hw_testplans = ["data/echo_system_tests.xml"]
        options.host_testplans = ["data/ls_system_tests.xml"]
        options.hosttest = "testrunner-lite-regression-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Host_Hardware",
            "Environment: Hardware",
            "Beginning to execute test package: ls_system_tests.xml",
            "Beginning to execute test package: echo_system_tests.xml",
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-tests"])

    def test_hw_host_chroot_based_testrun_with_test_definition_tests(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.chroottest = "test-definition-tests"
        options.rootstrap = CONFIG["rootstrap_url"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Environment: Hardware",
            "Environment: Host_Hardware",
            "Environment: chroot"])

############################################
# TestMiscSuccessfulTestruns
############################################

class TestMiscSuccessfulTestruns(unittest.TestCase):

    def test_testrun_with_filter(self):
        options = Options()
        options.packages = "testrunner-lite-regression-tests"
        options.testfilter = "testcase=trlitereg01,trlitereg02"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Test case quoting_01 is filtered",
            "Test case quoting_01 is filtered",
            "Executed 2 cases. Passed 2 Failed 0"])
        assert_log_page_does_not_contain_messages(self, tid, [
            "Test case trlitereg01 is filtered",
            "Test case trlitereg02 is filtered"])

    def test_hw_based_testrun_with_resume_continue(self):
        options = Options()
        options.distribution = "default"
        options.hw_testplans = ["data/shutdown_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.resume = True
        tid = SystemTest(self).run(options).verify(Result.FAIL).id()
        assert_log_page_contains_messages(self, tid, [
            "--resume=continue",
            "Environment: Hardware",
            "Beginning to execute test package: shutdown_system_tests.xml",
            "Executed 4 cases. Passed 2 Failed 2",
            "Finished test case echo-before-shutdown Result: PASS",
            "Finished test case shutdown Result: FAIL",
            "Finished test case echo-after-shutdown Result: FAIL",
            "Finished test case echo1 Result: PASS"])


############################################
# TestCustomDistributionModels
############################################

class TestCustomDistributionModels(unittest.TestCase):

    def test_load_example_distribution_model(self):
        """
        test_load_example_distribution_model

        To make this case pass example distribution model needs to be
        installed. It can be found from examples directory.
        """
        options = Options()
        options.distribution_model = "example_model"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Example distribution model not implemented"])

    def test_load_invalid_distribution_model(self):
        options = Options()
        options.distribution_model = "invalid_distribution_model"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "ValueError: Invalid distribution model"])

    def test_load_optimized_distribution_model_for_host_packages(self):
        options = Options()
        options.hosttest = "test-definition-tests testrunner-lite-regression-tests"
        options.distribution_model = "optimized"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-tests",
            "Loaded custom distribution model 'ots.plugin.history.distribution_model'",
            "Environment: Host_Hardware"])

    def test_load_optimized_distribution_model_for_hw_packages(self):
        options = Options()
        options.packages = "test-definition-tests testrunner-lite-regression-tests"
        options.distribution_model = "optimized"
        options.testfilter = "testcase=trlitereg01,Check-basic-schema"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Beginning to execute test package: test-definition-tests",
            "Beginning to execute test package: testrunner-lite-regression-tests",
            "Loaded custom distribution model 'ots.plugin.history.distribution_model'",
            "Environment: Hardware"])

    def test_optimized_without_packages(self):
        options = Options()
        options.packages = ""
        options.distribution_model = "optimized"
        options.hw_testplans = ["data/echo_system_tests.xml"]
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 10
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "No commands created"])


##########################################
# TestErrorConditions
##########################################

class TestErrorConditions(unittest.TestCase):

    def test_bad_image_url(self):
        options = Options()
        options.image = options.image+"asdfasdfthiswontexistasdfasdf"
        options.packages = "testrunner-lite-regression-tests"
        path = os.path.basename(options.image)
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Error: Could not download file %s, Error code: 103" % path,
            "Starting conductor at"])

    def test_timeout(self):
        options = Options()
        options.packages = "testrunner-lite-regression-tests"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Error: Timeout while executing test package " \
            "testrunner-lite-regression-tests, Error code: 1091",
            "Test execution error: Timeout while executing test " \
            "package testrunner-lite-regression-tests"])

    def test_non_existing_devicegroup(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "No queue for this_should_not_exist",
            "Incoming request: program: %s, request: %s, " \
            "notify_list: ['%s'], options: {" \
                % (CONFIG["sw_product"], CONFIG["build_id"], CONFIG["email"]),
            "'image': '%s'" % (CONFIG["image_url"]),
            "'distribution_model': 'default'",
            "'timeout': 1",
            "'device': 'devicegroup:this_should_not_exist'"])

    def test_non_existing_sw_product(self):
        options = Options()
        options.sw_product = "this_should_not_exist"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "'this_should_not_exist' not found",
            "Incoming request: program: this_should_not_exist, request: %s, " \
            "notify_list: ['%s'], options: {"  % (CONFIG["build_id"],
                                                  CONFIG["email"]),
            "'image': '%s'" % (CONFIG["image_url"]),
            "'distribution_model': 'default'",
            "'timeout': 1"])

    def test_bad_testpackage_names(self):
        options = Options()
        options.packages = "test-definition-tests thisisnotatestpackage"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Invalid testpackage(s): thisisnotatestpackage"])

    def test_no_image_url(self):
        options = Options()
        options.timeout = 1
        options.image = ""
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Missing `image` parameter"])

    def test_bad_distribution_model(self):
        options = Options()
        options.distribution_model = "sendalltestrunstowastebin"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Invalid distribution model: sendalltestrunstowastebin"])

    def test_perpackage_distribution_no_packages(self):
        options = Options()
        options.packages = ""
        options.distribution_model = "perpackage"
        options.timeout = 1
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Test packages must be defined for specified " \
            "distribution model 'perpackage'"])

########################################
# TestDeviceProperties
########################################

class TestDeviceProperties(unittest.TestCase):

    def test_multiple_devicegroups(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist_1;devicegroup:" \
            "this_should_not_exist_either"
        options.timeout = 1
        test = SystemTest(self).run(options).verify(Result.ERROR)
        testrun_id1 = test.testrun_ids[0]
        testrun_id2 = test.testrun_ids[1]
        self.assertTrue(log_page_contains_errors(testrun_id1))
        self.assertTrue(log_page_contains_errors(testrun_id2))
        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)
        string1 = """No queue for this_should_not_exist_1"""
        string2 = """No queue for this_should_not_exist_either"""
        if (log_page_contains_message(testrun_id1, string1)):
            assert_log_page_contains_message(self, testrun_id2, string2)
        else:
            assert_log_page_contains_message(self, testrun_id2, string1)
            assert_log_page_contains_message(self, testrun_id1, string2)

    def test_one_devicegroup_multiple_devicenames(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:" \
            "device1;devicegroup:this_should_not_exist devicename:device2"
        options.timeout = 1
        test = SystemTest(self).run(options).verify(Result.ERROR)
        testrun_id1 = test.testrun_ids[0]
        testrun_id2 = test.testrun_ids[1]
        self.assertTrue(log_page_contains_errors(testrun_id1))
        self.assertTrue(log_page_contains_errors(testrun_id2))
        # Make sure correct routing keys are used (We don't know the order so
        # we need to do check both ways)
        string1 = """No queue for this_should_not_exist.device1"""
        string2 = """No queue for this_should_not_exist.device2"""
        if (log_page_contains_message(testrun_id1, string1)):
            assert_log_page_contains_message(self, testrun_id2, string2)
        else:
            assert_log_page_contains_message(self, testrun_id2, string1)
            assert_log_page_contains_message(self, testrun_id1, string2)


    def test_one_devicegroup_one_devicename_multiple_device_ids(self):
        options = Options()
        options.device = "devicegroup:this_should_not_exist devicename:" \
            "device1 deviceid:id1;devicegroup:this_should_not_exist " \
            "devicename:device1 deviceid:id2"
        options.timeout = 1
        test = SystemTest(self).run(options).verify(Result.ERROR)
        testrun_id1 = test.testrun_ids[0]
        testrun_id2 = test.testrun_ids[1]
        self.assertTrue(log_page_contains_errors(testrun_id1))
        self.assertTrue(log_page_contains_errors(testrun_id2))
        # Make sure correct routing keys are used
        string1 = """No queue for this_should_not_exist.device1.id1"""
        string2 = """No queue for this_should_not_exist.device1.id2"""
        if (log_page_contains_message(testrun_id1, string1)):
            assert_log_page_contains_message(self, testrun_id2, string2)
        else:
            assert_log_page_contains_message(self, testrun_id2, string1)
            assert_log_page_contains_message(self, testrun_id1, string2)

########################################
# TestPlugins
########################################

class TestPlugins(unittest.TestCase):

    def test_plugins_loaded(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.testfilter = "testcase=Check-basic-schema"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Plugin: ots.plugin.conductor.richcore loaded",
            "history data saved",
            "Using smtp server",
            "Email sent"])

    def test_email_invalid_address(self):
        options = Options()
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 1
        options.image = ""
        options.email = "invalid_email_address"
        tid = SystemTest(self).run(options).verify(Result.ERROR).id()
        assert_log_page_contains_messages(self, tid, [
            "Missing `image` parameter",
            "Error in sending mail to following addresses: ['invalid_email_address']"])


class TestMultiDevice(unittest.TestCase):
    #
    # These tests are requiring that one ots-worker
    # is started as number 1 and uses meego-ai-flasher-n900
    # flasher.
    #

    def test_load_flasher_plugin(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.testfilter = "testcase=Check-basic-schema"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "Loaded flasher 'meego-ai-flasher-n900'"])

    def test_load_separated_settings(self):
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.testfilter = "testcase=Check-basic-schema"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "using config file /etc/ots/conductor_"])

class TestConductorPlugin(unittest.TestCase):
    """Tests for conductor plug-ins"""

    def test_example_conductor_plugin(self):
        """
        Example conductor plugin from examples directory needs to be installed!
        """
        options = Options()
        options.hosttest = "test-definition-tests"
        options.sw_product = CONFIG["sw_product"]
        options.timeout = 60
        options.testfilter = "testcase=Check-basic-schema"
        tid = SystemTest(self).run(options).verify(Result.PASS).id()
        assert_log_page_contains_messages(self, tid, [
            "ExampleConductorPlugin before_testrun method called.",
            "ExampleConductorPlugin after_testrun method called.",
            "ExampleConductorPlugin set_target method called.",
            "ExampleConductorPlugin set_result_dir method called.",
            "ExampleConductorPlugin get_result_files method called."])


if __name__ == "__main__":
    unittest.main()
