#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import unittest
import sys
import os
import subprocess
import tempfile
import logging
import traceback
import time

from socket import gethostname
from ots.worker.command import Command
from ots.worker.command import SoftTimeoutException
from ots.worker.command import HardTimeoutException
from ots.worker.command import FailedAfterRetries
from ots.worker.command import CommandFailed
from ots.worker.api import ResponseClient
from ots.worker.conductor.chroot import Chroot, RPMChroot

# Send log messages to stdout (by default)
logging.basicConfig(stream = sys.stdout, level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s')

from ots.worker.conductor.conductorerror import ConductorError

##############################################################################
# Constants
##############################################################################

THIS_FILE = os.path.dirname(os.path.abspath(__file__))
PATH_TO_TEST_CONF_FILE = os.path.join(THIS_FILE, "testdata/test_flash_config.conf")
EMPTY_FILE = os.path.join(THIS_FILE, "testdata/empty_file")
MD5_FOR_EMPTY_STRING = os.path.join(THIS_FILE, "testdata/md5_for_empty_string")
NON_EXISTING_FILE = "/non/existing/file"

##############################################################################
# Stubs
##############################################################################

from ots.worker.conductor.executor import TestRunData as TRD
from ots.worker.conductor.executor import Executor as TE
from ots.worker.conductor.hardware import Hardware as HW


class Mock_Hardware(HW):
    """
    Stubs out methods that make calls to file system or to internet.
    Stubs out use of flasher.
    """
    def _urlretrieve(self, url, path):
        pass
    def _read_file(self, path):
        return ""
    def _delete_file(self, path):
        pass
    def _add_execute_privileges(self, path):
        return 0
    def _flash(self):
        # Added this because real Flasher now reads it's config files
        # itself (without conductor)
        pass
    def _fetch_flasher(self):
        # Before separating Flasher configuration reading from Conductor this
        # method just returned from real Hardware class when checking
        # primary_flasher, because now obsoleted flasher was empty dict
        return 0

class Stub_Hardware(object):
    """All public methods stubbed out. Option to inject exit_code coming from shell"""
    def __init__(self, exit_code = 0):
        self.exit_code = exit_code
    def __str__(self):
        return "Hardware"
    def prepare(self):
        pass
    def cleanup(self):
        pass
    def get_command_to_copy_file(self, src_path, dest_path):
        return self._test_cmd() #HW_COMMAND_TO_COPY_FILE % (src_path, dest_path)
    def get_commands_to_show_test_environment(self):
        return [("","")] #zip(commands, plain_cmds)
    def get_command_to_copy_testdef(self):
        return self._test_cmd()
    def get_command_to_copy_results(self):
        return self._test_cmd()
    def get_command_to_find_test_packages(self):
        return ""
    def parse_packages_with_file(self, lines):
        return ["mypackage-test"]
    def get_command_to_list_installed_packages(self):
        return ""
    def parse_installed_packages(self, lines):
        return ["mypackage-test"]

    def _test_cmd(self):
        return "sh -c 'exit %s'" % self.exit_code


class Options(object):
    def __init__(self):
        self.testrun_id = None #standalone
        self.image_url = "xxx/yyy.bin"
        self.image_path = None
        self.content_image_url = "xxx/yyy"
        self.content_image_path = None
        self.packages = ""
        self.host = False
        self.dontflash = False
        self.filter_options = ""
        self.verbose = False
        self.otsserver = None
        self.flasher_url = None
        self.bootmode = None
        self.testplan = None
        self.rootstrap_url = None
        self.chrooted = None
        self.rootstrap_path = None
        self.device_n = 0

class Stub_Executor(object):
    def __init__(self, testrun, stand_alone, responseclient = None,
                 hostname = "unknown"):
        self.env = ""
        self.stand_alone = stand_alone
    def set_target(self, target):
        pass
    def execute_tests(self):
        return 0

class Mock_Executor(TE):
    def __init__(self, testrun, stand_alone, responseclient = None,
                 hostname = "unknown", testrun_timeout = 0):
        super(Mock_Executor, self).__init__(testrun, stand_alone, responseclient,
              hostname, testrun_timeout)
    def _test_execution_error_handler(self, error_info, error_code):#, test_package):
        #We're expecting ConductorError exception here
        raise Exception("%s: %s: %s" % (error_info, error_code))#(test_package, error_info, error_code))
    def _store_test_definition(self, path, test_package):
        pass
    def _get_command_for_testrunner(self):
        return "" #TODO: self.testrunner_command

class Mock_Executor_with_cmd(Mock_Executor):
    def __init__(self, testrun, stand_alone, responseclient = None,
                 hostname = "unknown", testrun_timeout = 0):
        super(Mock_Executor, self).__init__(testrun, stand_alone, responseclient,
              hostname, testrun_timeout)
    def _get_command_for_testrunner(self):
        return "sleep 2"

def _conductor_config_simple(config_file = "", default_file = ""):
    config = dict()
    config['device_packaging'] = 'debian'
    config['pre_test_info_commands_debian'] = ['ls', 'echo "jouni"']
    config['pre_test_info_commands_rpm'] = ['ls', 'echo "jouni"']
    config['pre_test_info_commands'] = ['ls', 'echo "testing ...."', 'ls -al']
    config['files_fetched_after_testing'] = ['xxx']
    config['tmp_path'] = "/tmp/"
    return config

class Stub_Command(object):
    def __init__(self, command, return_value = None):
        self.command = command
        self.return_value = return_value

class Stub_ResponseClient(object):
    def __init__(self, server_host, server_port, testrun_id):
        self.log = logging.getLogger("responseclient")
        self.host = server_host
        self.port = server_port
        self.testrun_id = testrun_id
        self.log.debug("ResponseClient initialized")

    def add_package_data(self, test_package, data):
        pass
    def add_result(self, filename, content, origin="Unknown",
                         test_package="Unknown", environment="Unknown"):
        pass
    def set_state(self, state, status_info):
        pass
    def set_error(self, error_info, error_code):
        pass
    def add_executed_packages(self, environment, packages):
        pass

##############################################################################
# Tests
##############################################################################

class TestConductorInternalConstants(unittest.TestCase):
    def test_mandatory_constants_defined(self):
        """Check that required constants exist and are defined as expected"""
        import ots.worker.conductor.conductor_config as c
        c.DEBUG_LOG_FILE
        c.TEST_DEFINITION_FILE_NAME
        c.TESTRUN_LOG_FILE
        c.TESTRUN_LOG_CLEANER
        c.CONDUCTOR_WORKDIR
        c.TESTRUNNER_WORKDIR
        c.CMD_TESTRUNNER   % (1,2,3,4,5,6)
        c.TESTRUNNER_SSH_OPTION
        c.TESTRUNNER_LOGGER_OPTION % 1
        c.TESTRUNNER_FILTER_OPTION   % "xxx"
        c.HTTP_LOGGER_PATH % 1
        c.HW_COMMAND % ("xxx", "bar")
        c.HW_COMMAND_TO_COPY_FILE    % ("xxx", 1,2)
        c.LOCAL_COMMAND_TO_COPY_FILE % (1,2)
        c.SSH_CONNECTION_RETRIES
        c.SSH_RETRY_INTERVAL
        c.TESTRUNNER_SUCCESFUL
        c.TESTRUNNER_INVALID_ARGS
        c.TESTRUNNER_SSH_FAILS
        c.TESTRUNNER_PARSING_FAILS
        c.TESTRUNNER_VALIDATION_FAILS
        c.TESTRUNNER_RESULT_FOLDER_FAILS
        c.TESTRUNNER_XML_READER_FAILS
        c.TESTRUNNER_RESULT_LOGGING_FAILS


class TestConductorConf(unittest.TestCase):
    def test_read_conductor_config(self):
        from ots.worker.conductor import conductor
        conf_file = os.path.join(os.path.dirname(__file__), "conductor.conf")
        conf = conductor._read_configuration_files(conf_file, 0)
        self.assertTrue(type(conf) == type(dict()))
        self.assertTrue(conf['device_packaging'] != "")
        self.assertTrue(conf['pre_test_info_commands_debian'] != "")
        self.assertTrue(conf['pre_test_info_commands_rpm'] != "")
        self.assertTrue(conf['pre_test_info_commands'] != "")
        self.assertTrue(conf['files_fetched_after_testing'] != "")
        self.assertTrue(conf['tmp_path'] != "")
        
    def test_read_conductor_config_instance_2(self):
        from ots.worker.conductor import conductor
        conf_file = os.path.join(os.path.dirname(__file__), "conductor_2.conf")
        conf = conductor._read_configuration_files(conf_file, 2)
        self.assertTrue(type(conf) == type(dict()))
        self.assertTrue(conf['device_packaging'] != "")
        self.assertTrue(conf['pre_test_info_commands_debian'] != "")
        self.assertTrue(conf['pre_test_info_commands_rpm'] != "")
        self.assertTrue(conf['pre_test_info_commands'] != "")
        self.assertTrue(conf['files_fetched_after_testing'] != "")
        self.assertTrue(conf['tmp_path'] != "")

    def test_read_conductor_config_with_optional_configs(self):
        from ots.worker.conductor import conductor
        optional_value = "ps aux"
        conf_file = os.path.join(os.path.dirname(__file__), "conductor.conf")
        conf = conductor._read_configuration_files(conf_file,0 )
        self.assertTrue(type(conf) == type(dict()))
        self.assertTrue(conf['device_packaging'] != "")
        self.assertTrue(conf['pre_test_info_commands_debian'] != "")
        self.assertTrue(conf['pre_test_info_commands_rpm'] != "")
        self.assertTrue(conf['pre_test_info_commands'] != "")
        self.assertTrue(conf['files_fetched_after_testing'] != "")
        self.assertTrue(conf['tmp_path'] != "")

        # Check that we do not have value in pre_test_info_commands that we will
        # insert from optional configuration file
        self.assertFalse(optional_value in conf['pre_test_info_commands'])

        temp_folder = tempfile.mkdtemp("_optional_confs")
        temp_config = tempfile.mktemp(suffix='.conf', dir=temp_folder)
        fp = open(temp_config, 'w')
        fp.write('[conductor]\npre_test_info_commands: "%s"\n' % \
                 optional_value)
        fp.close()

        conf['custom_config_folder'] = temp_folder
        conf = conductor._read_optional_config_files(temp_folder, conf)
        self.assertTrue(optional_value in conf['pre_test_info_commands'])

        os.unlink(temp_config)
        os.rmdir(temp_folder)


class TestConductor(unittest.TestCase):
    def _test_main(self):
        #TODO: Refactor code so that main can be tested
        #import ots.worker.conductor
        #main()
        pass

    def test_check_command_line_options(self):
        from ots.worker.conductor.conductor import _check_command_line_options

        options = Options()
        self.assertTrue(_check_command_line_options(options))

        options = Options()
        options.testrun_id = "1"
        options.otsserver = "server:80"
        self.assertTrue(_check_command_line_options(options))
        options.otsserver = "server:"
        self.assertFalse(_check_command_line_options(options))
        options.otsserver = ":80"
        self.assertFalse(_check_command_line_options(options))
        options.otsserver = "missing_colon"
        self.assertFalse(_check_command_line_options(options))

        options = Options()
        options.image_url = None
        self.assertFalse(_check_command_line_options(options))

        options = Options()
        options.host = True
        self.assertFalse(_check_command_line_options(options))

        options = Options()
        options.testrun_id = "1"
        self.assertFalse(_check_command_line_options(options))

        options = Options()
        options.otsserver = "server:80"
        self.assertFalse(_check_command_line_options(options))

    def test_parse_command_line(self):
        """Test default values from OptionParser"""
        from ots.worker.conductor.conductor import _parse_command_line
        (options, parser) = _parse_command_line(args=[])
        self.assertEquals(options.testrun_id, None)
        self.assertEquals(options.image_url, None)
        self.assertEquals(options.content_image_url, None)
        self.assertEquals(options.content_image_path, None)
        self.assertEquals(options.packages, None)
        self.assertEquals(options.host, False)
        self.assertEquals(options.dontflash, False)
        self.assertEquals(options.filter_options, "")
        self.assertEquals(options.verbose, False)
        self.assertEquals(options.otsserver, None)
        self.assertEquals(options.flasher_url, None)
        self.assertEquals(options.bootmode, None)
        self.assertEquals(options.testplan, None)
        parser.print_help() #check help text is set


class TestTestTarget(unittest.TestCase):

    def setUp(self):
        from ots.worker.conductor.testtarget import TestTarget
        from ots.worker.conductor.executor import TestRunData as TestRunData
        testrun = TestRunData( Options(), config = _conductor_config_simple() )
        self.testtarget = TestTarget(testrun)

    def test_str(self):
        self.assertRaises(Exception, self.testtarget.__str__)

    def test_flash(self):
        self.assertRaises(Exception, self.testtarget.prepare)

    def test_cleanup(self):
        self.testtarget.cleanup()

    def test_get_commands_to_show_test_environment(self):
        self.assertRaises(Exception, self.testtarget.get_commands_to_show_test_environment)

    def test_get_command_to_copy_file(self):
        self.assertRaises(Exception, self.testtarget.get_command_to_copy_file, "", "")

    def test_get_command_to_copy_testdef(self):
        self.assertRaises(Exception, self.testtarget.get_command_to_copy_testdef)

    def test_get_command_to_copy_results(self):
        self.assertRaises(Exception, self.testtarget.get_command_to_copy_results)

    def test_get_command_to_find_test_packages(self):
        self.assertRaises(Exception, self.testtarget.get_command_to_find_test_packages)

    def test_get_command_to_list_installed_packages(self):
        self.assertRaises(Exception, self.testtarget.get_command_to_list_installed_packages)

    def test_parse_for_packages_with_file(self):
        self.assertRaises(Exception, self.testtarget.parse_for_packages_with_file)

    def test_parse_installed_packages(self):
        self.assertRaises(Exception, self.testtarget.parse_installed_packages)


class TestHardware(unittest.TestCase):

    def setUp(self):
        from ots.worker.conductor.hardware import Hardware
        from ots.worker.conductor.executor import TestRunData as TestRunData
        self.config = _conductor_config_simple()
        self.testrun = TestRunData( Options(), config = self.config )
        self.mock_hw = Mock_Hardware(self.testrun)
        self.real_hw = Hardware(self.testrun) #for testing methods stubbed out in mock_hw

    def test_str(self):
        self.assertEquals(str(self.mock_hw), "Hardware")

    def test_get_commands_to_show_test_environment(self):
        zipped = self.mock_hw.get_commands_to_show_test_environment()
        self.assertTrue(type(zipped) == type(list()))

    def test_get_command_to_copy_file(self):
        cmd = self.mock_hw.get_command_to_copy_file("xxx", "yyy")
        self.assertTrue(cmd.find("xxx") != -1 and cmd.find("yyy") != -1)

    def test_get_command_to_copy_testdef(self):
        cmd = self.mock_hw.get_command_to_copy_testdef()
        self.assertTrue(cmd)

    def test_get_command_to_copy_results(self):
        cmd = self.mock_hw.get_command_to_copy_results()
        self.assertTrue(cmd)

    def test_get_command_to_find_test_packages(self):
        cmd = self.mock_hw.get_command_to_find_test_packages()
        self.assertTrue(cmd.find('dpkg') != -1)

    def test_get_command_to_list_installed_packages(self):
        cmd = self.mock_hw.get_command_to_list_installed_packages()
        self.assertTrue(cmd.find('dpkg') != -1)

    def test_fetch_file(self):
        url = "http://my.fake.server.com/path/filename"
        path = self.mock_hw._fetch_file(url) #urllib.urlretrieve and delete_file are stubbed out
        self.assertTrue(path.find("/tmp/tmp") == 0)
        self.assertTrue(path.find("/filename") > 0)

    def test_fetch_flasher(self):
        self.testrun.flasher_url = "http://my.fake.server.com/path/flasher"
        self.mock_hw._fetch_flasher()

    def test_fetch_release(self):
        self.testrun.image_url = "http://my.fake.server.com/path/image.bin"
        #we get OSError because file does not exist
        self.assertRaises(OSError, self.mock_hw._fetch_release)

    def test_fetch_content_image(self):
        self.testrun.content_image_url = "http://my.fake.server.com/path/image.bin"
        expected_path = os.path.join(self.config['tmp_path'], "image.bin")
        #we get OSError because file does not exist
        self.assertRaises(OSError, self.mock_hw._fetch_content_image)

    def test_cleanup(self):
        self.mock_hw.cleanup()

    def test_raise_download_error(self):
        self.assertRaises(ConductorError, self.mock_hw._raise_download_error, "")

    def test_flash_with_dontflash_option(self):
        self.testrun.dontflash = True
        self.mock_hw.prepare() #returns doing nothing

    def test_flash(self):
        #we get OSError because first image file does not exist.
        #TODO: improve when file size checks removed
        self.assertRaises(OSError, self.mock_hw.prepare)

    def test__flash(self): #testing private method
        self.mock_hw._flash() #all stubbed out, so expecting no exceptions


    # Below tests use real Hardware class instead of mock: (Add here all you can!)

    def test_read_file(self):
        content = self.real_hw._read_file(PATH_TO_TEST_CONF_FILE)
        expected_content = open(PATH_TO_TEST_CONF_FILE, "r").read()
        self.assertEquals(content, expected_content)

    def test_delete_file_eats_exceptions(self):
        self.real_hw._delete_file("non/existing/file") #shouldn't raise exception
        self.real_hw._delete_file("/") #existing dir, shouldn't raise exception
        self.real_hw._delete_file(None) #deleting not attempted
        self.real_hw._delete_file("") #deleting not attempted

    def test_md5_digest(self):
        digest = self.real_hw._md5_digest("any string")
        self.assertEquals(len(digest), 16)

    def test_md5_valid(self):
        #MD5 valid:
        self.assertEquals(self.real_hw._md5_valid(EMPTY_FILE, MD5_FOR_EMPTY_STRING), True)
        #MD5 invalid:
        #mock returns "" as file content but md5 for "" is a 16-byte string
        self.assertEquals(self.mock_hw._md5_valid("ununsed", "unused"), False)

    def test_add_execute_privileges(self):
        self.assertTrue(self.real_hw._add_execute_privileges(NON_EXISTING_FILE) != 0)

    def test_parse_installed_packages(self):
        lines = "ii  mypackage-tests   1.2.3   My very special tests\n"+\
                "ii  someotherpackage   0.0.1   Something\n"
        self.assertEquals(self.real_hw.parse_installed_packages(lines), ["mypackage-tests"])

    def test_parse_packages_with_file(self):
        lines = "somepackage: /usr/share/somepackage/tests.xml\n"+\
                "mypackage-tests: /usr/share/mypackage-tests/tests.xml\n"
        self.assertEquals(self.real_hw.parse_packages_with_file(lines), ["mypackage-tests"])


class TestRPMHardware(unittest.TestCase):

    def setUp(self):
        from ots.worker.conductor.hardware import RPMHardware as RPMHardware
        from ots.worker.conductor.executor import TestRunData as TestRunData
        self.testrun = TestRunData( Options(),
                                    config = _conductor_config_simple() )
        self.hw = RPMHardware(self.testrun)

    def test_get_command_to_find_test_packages(self):
        cmd = self.hw.get_command_to_find_test_packages()
        self.assertTrue(cmd.find('rpm') != -1)

    def test_get_command_to_list_installed_packages(self):
        cmd = self.hw.get_command_to_list_installed_packages()
        self.assertTrue(cmd.find('rpm') != -1)

    def test_parse_installed_packages(self):
        lines = "mypackage-test\n"+\
                "someotherpackage\n"
        self.assertEquals(self.hw.parse_installed_packages(lines), ["mypackage-test"])

    def test_parse_packages_with_file(self):
        lines = "somepackage\n"+\
                "mypackage-tests\n"
        self.assertEquals(self.hw.parse_packages_with_file(lines), ["mypackage-tests"])


class Test_Executor(unittest.TestCase):
    """
    Tests for Executor class and executor file.
    responseclient = None, stand_alone = True
    """

    def setUp(self):
        from ots.worker.conductor.executor import Executor as Executor
        from ots.worker.conductor.executor import TestRunData as TestRunData
        self.workdir = tempfile.mkdtemp("_test_conductor")
        self.testrun = TestRunData(Options(), config = _conductor_config_simple())
        self.testrun.workdir = self.workdir #inject our temp folder
        responseclient = None
        stand_alone = True
        self.executor = Mock_Executor(self.testrun, stand_alone, responseclient,
                                      hostname="hostname", testrun_timeout=60)
                #NOTE!! STUBBED OUT so far:
                #_test_execution_error_handler
                #_store_test_definition
                #_get_command_for_testrunner

        responseclient = Stub_ResponseClient("", "", 0)
        self.real_executor = Executor(self.testrun, stand_alone, responseclient,
                                      "hostname")

    def tearDown(self):
        subprocess.call("rm -rf "+self.workdir, shell=True) #created in setUp


    def test_run_tests_returns_true(self):
        """Test for _run_tests method when testrunner command succeeds"""
        self.testrun.base_dir = self.workdir #inject our temp folder
        path = self.workdir
        test_package = "my-tests"
        executor = Mock_Executor(self.testrun, True, None,
                                 hostname="hostname", testrun_timeout=60)
        expected_stdout_file = os.path.join(path, "%s_testrunner_stdout.txt" % test_package)
        expected_stderr_file = os.path.join(path, "%s_testrunner_stderr.txt" % test_package)
        #check that files do not exist yet
        self.assertFalse(os.path.isfile(expected_stdout_file))
        self.assertFalse(os.path.isfile(expected_stderr_file))
        status = executor._run_tests(test_package, time.time(), time.time() + 1)
        #check that _run_tests returned True
        self.assertTrue(status is True)
        #check that files were created
        self.assertTrue(os.path.isfile(expected_stdout_file))
        self.assertTrue(os.path.isfile(expected_stderr_file))

    def test_run_tests_returns_false(self):
        """Test for _run_tests method when testrunner command succeeds"""
        self.testrun.base_dir = self.workdir #inject our temp folder
        path = self.workdir
        test_package = "my-tests"
        executor = Mock_Executor(self.testrun, True, None,
                                 hostname="hostname", testrun_timeout=60)
        status = executor._run_tests(test_package, 0, 60)
        expected_stdout_file = os.path.join(path, "%s_testrunner_stdout.txt" % test_package)
        expected_stderr_file = os.path.join(path, "%s_testrunner_stderr.txt" % test_package)
        #check that _run_tests returned False
        self.assertTrue(status is False)

    def test_run_tests_returns_false_with_timeout(self):
        """Test for _run_tests method when testrunner command succeeds"""
        self.testrun.base_dir = self.workdir #inject our temp folder
        path = self.workdir
        test_package = "my-tests"
        executor = Mock_Executor_with_cmd(self.testrun, True, None,
                                          hostname="hostname", testrun_timeout=1)
        expected_stdout_file = os.path.join(path, "%s_testrunner_stdout.txt" % test_package)
        expected_stderr_file = os.path.join(path, "%s_testrunner_stderr.txt" % test_package)
        timer = time.time()
        status = executor._run_tests(test_package, timer, timer)
        #check that _run_tests returned True
        self.assertTrue(status is False)

    def _test_run_tests_2(self):  #TODO TEST DISABLED until testrunner_command can be injected to Mock_Executor
        """Test for _run_tests method when testrunner command fails"""
        testrunner_command = 'sh -c "exit 1"'
        executor = Mock_Executor(self.testrun, self.stand_alone,
                                 self.responseclient, "hostname",
                                 testrunner_command)
        executor.target = Stub_Hardware()
        self.testrun.base_dir = self.workdir
        #self.assertFalse(os.path.exists(...)) #files do not exist yet
        test_package = "my-tests"
        self.assertRaises(ConductorError, executor._run_tests, test_package)
        #TODO check that files were created

    def test_set_target_when_debian(self):
        from ots.worker.conductor.hardware import Hardware as Hardware
        self.executor.set_target()
        self.assertTrue(isinstance(self.executor.target, Hardware))
        self.assertEquals(str(self.executor.target), "Hardware")
        self.assertEquals(self.executor.env, "Hardware")

    def test_set_target_when_rpm(self):
        from ots.worker.conductor.hardware import RPMHardware as RPMHardware
        self.testrun.config['device_packaging'] = 'rpm'
        self.executor.set_target()
        self.assertTrue(isinstance(self.executor.target, RPMHardware))
        self.assertEquals(str(self.executor.target), "Hardware")
        self.assertEquals(self.executor.env, "Hardware")

    def test_set_target_when_hostbased(self):
        self.executor.testrun.is_host_based = True
        self.executor.set_target()
        self.assertEquals(str(self.executor.target), "Hardware")
        self.assertEquals(self.executor.env, "Host_Hardware")

    def test_execute_tests(self):
        #NOTE: This test goes through lots of code by calling many private methods.
        #But this test does not check which code was actually executed.
        self.testrun.id = "1"
        self.executor.env = "testenvironment"
        self.executor.target = Stub_Hardware()
        self.executor.chroot = Chroot(self.testrun)

        #test_package must match to string in Stub_Hardware
        test_package = "mypackage-test"

        path = os.path.join(self.workdir, "conductor", self.testrun.id,
                            self.executor.env)
        expected_stdout_file = \
                os.path.join(path, "%s_testrunner_stdout.txt" % test_package)
        expected_stderr_file = \
                os.path.join(path, "%s_testrunner_stderr.txt" % test_package)
        expected_env_info_file = os.path.join(path, \
                    "%s_environment_before_testing.txt" % self.executor.target)

        #Check that files do not exist yet
        self.assertFalse(os.path.isfile(expected_stdout_file))
        self.assertFalse(os.path.isfile(expected_stderr_file))
        self.assertFalse(os.path.isfile(expected_env_info_file))

        errors = self.executor.execute_tests()  #Here's the code to be tested.

        self.assertEquals(errors, 0)

        #Check that files were created.
        self.assertTrue(os.path.isfile(expected_stdout_file))
        self.assertTrue(os.path.isfile(expected_stderr_file))
        self.assertTrue(os.path.isfile(expected_env_info_file))


    def test_default_ssh_command_executor(self):
        #Successful command, should not raise exception
        cmd = self.executor._default_ssh_command_executor("ls", "my task")
        self.assertTrue(isinstance(cmd, Command))
        self.assertEquals(cmd.return_value, 0)

        #Commands raising ConductorError (Note: error_code is not checked!)
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, "nonexistingcommand", "")
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, "sleep 2", "", 1) #test timeout
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, 'sh -c "exit 1"', "")
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, 'sh -c "exit 127"', "")
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, 'sh -c "exit 128"', "")
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, 'sh -c "exit 129"', "")
        self.assertRaises(ConductorError, self.executor._default_ssh_command_executor, 'sh -c "exit 255"', "")

    def test_ssh_command_exception_handler(self):
        #Tests for CommandFailed
        exc = CommandFailed()
        cmd = Stub_Command("", return_value = 1)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")
        cmd = Stub_Command("", return_value = 127)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")
        cmd = Stub_Command("", return_value = 128)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")
        cmd = Stub_Command("", return_value = 129)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")
        cmd = Stub_Command("", return_value = 255)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")

        #Tests for not to raise exception with exit code other than 129-255
        cmd = Stub_Command("", return_value = 1)
        self.executor._ssh_command_exception_handler(exc, cmd, "", ignore_normal_CommandFailed = True)
        cmd = Stub_Command("", return_value = 127)
        self.executor._ssh_command_exception_handler(exc, cmd, "", ignore_normal_CommandFailed = True)
        cmd = Stub_Command("", return_value = 128)
        self.executor._ssh_command_exception_handler(exc, cmd, "", ignore_normal_CommandFailed = True)

        #Tests for ignore_normal_CommandFailed flag not to have effect with exit codes 129-255
        cmd = Stub_Command("", return_value = 129)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler,
                                          exc, cmd, "", ignore_normal_CommandFailed = True)
        cmd = Stub_Command("", return_value = 255)
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler,
                                          exc, cmd, "", ignore_normal_CommandFailed = True)

        #Tests for SoftTimeoutException and HardTimeOutException
        exc = SoftTimeoutException()
        cmd = Stub_Command("")
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")
        exc = HardTimeoutException()
        cmd = Stub_Command("")
        self.assertRaises(ConductorError, self.executor._ssh_command_exception_handler, exc, cmd, "")


    def test_get_command_for_testrunner_1(self):
        """Test for method when we should execute tests over ssh at device"""
        executor = self.real_executor
        executor.stand_alone = False
        command = executor._get_command_for_testrunner()
        self.assertTrue(command.find("testrunner-lite") != -1)
        self.assertTrue(command.find("root@192.168.2.15") != -1)
        self.assertTrue(command.find("logger") != -1)

    def test_get_command_for_testrunner_2(self):
        """Test for method when we should execute tests at device, standalone."""
        executor = self.real_executor
        command = executor._get_command_for_testrunner()
        self.assertTrue(command.find("testrunner-lite") != -1)
        self.assertTrue(command.find("root@192.168.2.15") != -1)
        self.assertTrue(command.find("logger") == -1) #should not be found

    def test_get_command_for_testrunner_host_based_1(self):
        """Test for method when we should execute tests at host"""
        executor = self.real_executor
        executor.stand_alone = False
        self.testrun.is_host_based = True #expose more code for testing

        command = executor._get_command_for_testrunner()
        print command
        self.assertTrue(command.find("testrunner-lite") != -1)
        self.assertTrue(command.find("root@192.168.2.15") == -1) #should not be found
        self.assertTrue(command.find("logger") != -1)

    def test_get_command_for_testrunner_host_based_2(self):
        """Test for method when we should execute tests at host, standalone"""
        executor = self.real_executor
        self.testrun.is_host_based = True #expose more code for testing

        command = executor._get_command_for_testrunner()
        self.assertTrue(command.find("testrunner-lite") != -1)
        self.assertTrue(command.find("root@192.168.2.15") == -1) #should not be found
        self.assertTrue(command.find("logger") == -1) #should not be found

    def test_testrunner_lite_error_handler(self):
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",1)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",2)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",3)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",4)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",5)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",6)
        self.assertRaises(ConductorError, self.executor._testrunner_lite_error_handler,"",7)

    def test_items_missing_from_all_items(self):
        from ots.worker.conductor.executor import items_missing_from_all_items
        missing = items_missing_from_all_items(["z"], ["x", "y"])
        self.assertEquals(missing, ["z"])
        missing = items_missing_from_all_items([], ["x", "y"])
        self.assertEquals(missing, [])
        missing = items_missing_from_all_items([], [])
        self.assertEquals(missing, [])
        missing = items_missing_from_all_items(["x", "y"], [])
        self.assertEquals(missing, ["x", "y"])

    def test_include_testrun_log_file(self):
        self.assertTrue(self.real_executor._include_testrun_log_file() in [0,1])


class TestDefaultFlasher(unittest.TestCase):
    """Tests for defaultflasher.py"""

    def test_exceptions(self):
        from ots.worker.conductor.defaultflasher import FlashFailed
        from ots.worker.conductor.defaultflasher import InvalidImage
        from ots.worker.conductor.defaultflasher import InvalidConfig
        from ots.worker.conductor.defaultflasher import ConnectionTestFailed

    def test_softwareupdater_flash(self):
        from ots.worker.conductor.defaultflasher import SoftwareUpdater
        sw_updater = SoftwareUpdater()
        sw_updater.flash("image1", "image2")

    def test_softwareupdater_flash_with_bootmode(self):
        from ots.worker.conductor.defaultflasher import SoftwareUpdater
        sw_updater = SoftwareUpdater()
        sw_updater.flash(image_path = "image1",
                         content_image_path = "image2",
                         boot_mode="normal")


if __name__ == '__main__':
    unittest.main()

