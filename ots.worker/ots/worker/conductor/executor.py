# -*- coding: utf-8 -*-
# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
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

"""Test executor"""

import logging
import os
import subprocess
import re
import time

from ots.worker.command import Command
from ots.worker.command import SoftTimeoutException
from ots.worker.command import HardTimeoutException
from ots.worker.command import CommandFailed

from conductor_config import * #internal constants
from conductorerror import ConductorError

class TestRunData(object):
    """
    TestRunData analyzes build request specific information from url and 
    test packages given as parameters .
    """
    
    def __init__(self, options, config):

        self.log = logging.getLogger("conductor")
        self.config = config

        self.id = options.testrun_id
        self.image_url = options.image_url
        self.image_path = None  #TODO Add image_path parameter behind cmd line option -U.
        self.content_image_url = options.content_image_url   #content_image_url is preferred over content_image_path
        self.content_image_path = options.content_image_path #content_image_path may later get overwritten.
        self.flasher_url = options.flasher_url

        self.test_packages = []
        self.requested_test_packages = []
        if options.packages:
            self.requested_test_packages = options.packages.split(',')

        self.is_host_based = options.host
        self.dontflash = options.dontflash

        self.filter_string = \
                options.filter_options.replace('"', '\\"').replace("'", '\\"')
                # Any type of quotation mark must be replaced with 
                # backslash-escaped doublequote!

        #Result folders:
        self.workdir = os.path.expanduser(CONDUCTOR_WORKDIR) #"~"
        self.base_dir = None
        self.pre_test_dir = None
        self.post_test_dir = None

        self.image_filename = ""
        
        self._parse_image_filename_from_url()
        self._validate_content_image_path()

        if not self.image_filename.endswith(HW_SUFFIX):
            raise Exception("File name must end with %s!" % HW_SUFFIX)

        self.testdef_src = None
        self.results_src = None
        self.src_result_folder = None
        self.testdef_target_dir = None
        self.results_target_dir = None
        self.dst_testdef_file_path = None
        self.result_file_path = None #This is src and dst

    def _parse_image_filename_from_url(self):
        """ 
        Parse filename from URL.
        """
        fields = self.image_url.split('/')
        self.image_filename = fields[-1] # filename is the last field of url
        self.log.debug("image filename = %s" % self.image_filename)

    def _validate_content_image_path(self):
        """
        Checks that content_image_path is valid. Throws exception if path is not valid. 
        None is considered valid and it indicates disabling content image flashing.
        """
        if self.content_image_path != None:
            if not os.path.isfile(self.content_image_path):
                raise Exception("Invalid content image path!")


###############################################################################

class Executor(object):
    """Test executor"""

    def __init__(self, testrun, stand_alone, responseclient = None, 
                 hostname = "unknown"):

        self.log = logging.getLogger("conductor")
        self.testrun = testrun
        self.stand_alone = stand_alone
        self.config = testrun.config
        self.responseclient = responseclient
        self.hostname = hostname 

        self.target = None #Test target object. Implements its own __str__().
        self.env = None    #Test environment name. String.


    # public methods

    def set_target(self, target):
        """
        Sets test target and test environment for test execution.
        self.env == "<targetname>" or "Host_<targetname>", e.g. Host_Hardware.
        """
        self.target = target
        if self.testrun.is_host_based:
            self.env = "Host_%s" % str(self.target)
        else:
            self.env = str(self.target)

    def execute_tests(self):
        """Execute the tests"""

        if not self.target:
            raise Exception("Test target not specified!")

        # Empty previous testrun.log before running tests
        subprocess.call(TESTRUN_LOG_CLEANER, shell=True)
        try:
            errors = self._execute_tests()
        finally: #exceptions are not caught here. They just pass by.
            self.target.cleanup()
            self._set_status("FINISHED", self.testrun.image_filename)

        return errors


    # Private methods

    def _execute_tests(self):
        """Execute the tests"""

        self._create_testrun_folder()
        self._set_status("FLASHING", self.testrun.image_filename)
        self.target.prepare()
        self._define_test_packages()
        self._fetch_environment_details()

        errors = 0
        for test_package in self.testrun.test_packages:

            self.log.info("Beginning to execute test package: %s" %test_package)

            try:
                self._set_paths(test_package)
                self._create_result_folders(test_package)
                self._install_package(test_package)
                self._fetch_test_definition(test_package)
                self._set_status("TESTING", test_package)
                self._run_tests(test_package)
                self._set_status("STORING_RESULTS", test_package)
                self._store_result_files(self.testrun.results_target_dir, 
                                         test_package)
                self._remove_package(test_package)

            except ConductorError, exc:
                self._test_execution_error_handler(exc, test_package)
                errors += 1

            self.log.info("Finished executing test package: %s" % test_package)

        self._fetch_files_after_testing()

        # Include /var/log/testrun.log file
        self._include_testrun_log_file()

        return errors


    def _include_testrun_log_file(self):
        # Include /var/log/testrun.log file
        try:
            os.stat(TESTRUN_LOG_FILE)
        except OSError:
            self.log.warning("Can't stat() testrun log file %s" %\
                             (TESTRUN_LOG_FILE))
            return 1
        else:
            self.log.info("Storing testrun log file %s" % (TESTRUN_LOG_FILE))
            self._store_result_file(TESTRUN_LOG_FILE, \
                                    test_package = "undefined")
        return 0


    def _test_execution_error_handler(self, exc, test_package):
        """
        Handler for ConductorError exceptions raised during test execution.
        """
        self.log.error("Test execution error: %s " % exc.error_info)
        if not self.stand_alone:
            self.responseclient.set_error(exc.error_info, exc.error_code)


    def _create_testrun_folder(self):
        """
        Create local folder for all result files related to this test run.
        NOTE: All folders are inside self.testrun.workdir
        """

        #conductor executes as root.
        dir1 = "conductor"
        dir12 = os.path.join(dir1, "%s" % self.testrun.id)
        dir123 = os.path.join(dir12, "%s" % self.env)

        os.chdir(self.testrun.workdir)

        subprocess.call('rm -rf %s' % dir123, shell=True) #removes dir3 only

        #"chmod -R" only affects last dir in path so let's go through all dirs.
        #chmod 777 changes all the rights it can depending on user privileges.
        subprocess.call('mkdir -p %s'  % dir123, shell=True)
        subprocess.call('chmod 777 %s' % dir1, shell=True) 
        subprocess.call('chmod 777 %s' % dir12, shell=True)
        subprocess.call('chmod 777 %s' % dir123, shell=True)

        pre_test_dir  = os.path.join(dir123, "pre")
        post_test_dir = os.path.join(dir123, "post")

        subprocess.call('mkdir -p ' +pre_test_dir, shell=True)
        subprocess.call('chmod 777 '+pre_test_dir, shell=True)
        subprocess.call('mkdir -p ' +post_test_dir, shell=True)
        subprocess.call('chmod 777 '+post_test_dir, shell=True)

        self.testrun.base_dir      = os.path.join(self.testrun.workdir, dir123)
        self.testrun.pre_test_dir  = os.path.join(self.testrun.workdir, 
                                                  pre_test_dir)
        self.testrun.post_test_dir = os.path.join(self.testrun.workdir, 
                                                  post_test_dir)

        self.log.debug("Local folder for result files: %s" \
                        % self.testrun.base_dir)
        self.log.debug("Folder for pre test files: %s" \
                        % self.testrun.pre_test_dir)
        self.log.debug("Folder for post test files: %s" \
                        % self.testrun.post_test_dir)


    def _set_paths(self, test_package):
        """Set file paths and target directories."""

        if self.testrun.is_host_based:
            self.testrun.src_result_folder = os.path.join(\
                "~/testrunner_results", test_package)
        else:
            self.testrun.src_result_folder = os.path.join(\
                "/root/testrunner_results", test_package)

        #common paths
        self.testrun.testdef_src = "/usr/share/%s/%s" \
                                % (test_package, TEST_DEFINITION_FILE_NAME)

        self.testrun.results_src = os.path.join(\
                self.testrun.src_result_folder, "*")

        self.testrun.testdef_target_dir = os.path.join(\
                self.testrun.base_dir, test_package, "testdef")
        self.testrun.results_target_dir = os.path.join(\
                self.testrun.base_dir, test_package, "results")

        self.testrun.dst_testdef_file_path = os.path.join(\
                self.testrun.testdef_target_dir, TEST_DEFINITION_FILE_NAME)
        self.testrun.result_file_path = os.path.join(\
            self.testrun.results_target_dir, 
            self._testrunner_result_file(test_package)) #This is src and dst


    def _testrunner_result_file(self, test_package):
        """Returns name of testrunner result file for given test package"""
        return "tatam_xml_testrunner_results_for_%s.xml" % test_package

    def _create_result_folders(self, test_package):
        """Create local folders to save copies of results for test package"""

        if not all([self.testrun.results_target_dir, 
                    self.testrun.testdef_target_dir]):
            raise Exception("Folder(s) undefined")

        subprocess.call('mkdir -p ' + self.testrun.results_target_dir, 
                        shell=True)
        subprocess.call('chmod -R 777 '+ self.testrun.results_target_dir, 
                        shell=True)
        subprocess.call('mkdir -p ' + self.testrun.testdef_target_dir, 
                        shell=True)
        subprocess.call('chmod -R 777 ' + self.testrun.testdef_target_dir, 
                        shell=True)

    
    def _install_package(self, test_package):
        """Install package to host. Do nothing if not host-based testing"""

        if not self.testrun.is_host_based:
            return

        self.log.info("Updating available packages")
        cmdstr = "apt-get update"
        self.log.debug(cmdstr)
        if subprocess.call(cmdstr, shell=True):
            self.log.warning("Error updating packages, trying anyways...")

        self.log.info("Installing test package %s" % test_package)
        cmdstr = "apt-get install %s --yes --force-yes" % test_package
        self.log.debug(cmdstr)
        if subprocess.call(cmdstr, shell=True):
            self.log.warning("Error installing %s, trying anyways..." \
                             % test_package)


    def _remove_package(self, test_package):
        """
        Remove installed test package. Do nothing if not host-based testing.
        """

        if not self.testrun.is_host_based:
            return

        self.log.info("Removing test package %s" % test_package)
        cmdstr = "apt-get remove %s --yes --force-yes" % test_package
        self.log.debug(cmdstr)
        if subprocess.call(cmdstr, shell=True):
            self.log.warning("Error while removing %s, continuing anyways..." \
                             % test_package)

        cmdstr = "apt-get autoremove --yes --force-yes"
        self.log.debug(cmdstr)
        if subprocess.call(cmdstr, shell=True):
            self.log.warning("Error while autoremoving, continuing anyways...")


    def _store_test_definition(self, path, test_package):
        """
        Stores test definition as raw file and as parsed package data object 
        with ResponseClient.
        """

        # Store as raw file
        filename = "test_definition_for_%s.xml" % str(test_package)
        self._store_result_file(path, test_package, filename)


    def _store_result_files(self, directory, test_package):
        """Stores all result files from results directory with ResponseClient."""

        if self.stand_alone:
            self.log.warning("Skipped storing result files to OTS server")
            return

        files = os.listdir(directory)
        for name in files:
            self._store_result_file(os.path.join(directory, name), test_package)


    def _create_new_file(self, path, content):
        """Create new file to given path and write given content in it."""
        name = os.path.basename(path)
        try:
            env = open(path, "w")
            env.write(content)
            env.close()
        except IOError:
            error_info = "IOError when creating result file %s for "\
                         "environment %s." % (name, self.env)
            self.log.warning(error_info)
            self.log.debug("Local file: %s" % path)
            self.log.debug("Traceback follows:", exc_info = True)
            raise ConductorError(error_info, "110")
        else:
            self.log.debug("Created new file: %s" % path)


    def _store_result_file(self, path, test_package, new_filename = None):
        """
        Stores one result file with ResponseClient.
        If new_filename is given, file will be shown with that name in server 
        side.
        """

        name = path.split('/')[-1]
        if new_filename:
            name = str(new_filename)

        if self.stand_alone:
            self.log.warning("Skipped storing file %s to OTS server" % name)
            return

        origin = self.hostname

        self.log.debug("Storing %s test result file %s" % (self.env, name))

        try:
            result_file = open(os.path.expanduser(path))
            self.responseclient.add_result(name, result_file.read(), origin,
                                           test_package, self.env)
            result_file.close()
        except IOError:
            error_info = "Result file %s not available (test package %s, "\
                         "environment %s)" % (name, test_package, self.env)
            self.log.warning(error_info)
            self.log.debug("Local file: %s" % path)
            raise ConductorError(error_info, "102")


    def _set_status(self, state, status_info):
        """Set state of testrun on OTS info service"""
        if not self.stand_alone:
            self.responseclient.set_state(state, status_info)
        else:
            self.log.warning("Skipped setting testrun state to (%s, %s)"\
                             % (state, status_info))


    def _default_ssh_command_executor(self, cmdstr, task, timeout = 180):
        """Ssh command executor with default timeout and error handling.

        Executes given ssh command as an instance of Command class.
        Returns the instance if the ssh command returned 0 (success).
        If the command returns with non-zero exit code, raises ConductorError 
        containing error message based on the exit code.
        """

        cmd = Command(cmdstr, soft_timeout = timeout, hard_timeout = timeout+5)
        try:
            cmd.execute()
        except (CommandFailed, SoftTimeoutException, HardTimeoutException), exc:
            self._ssh_command_exception_handler(exc, cmd, task.lower())
        else:
            self.log.debug("%s finished succesfully" % task.lower())
            return cmd


    def _ssh_command_exception_handler(self, exc, cmd, task, 
                                       ignore_normal_CommandFailed = False):
        """
        Exception handler for ssh commands executed by conductor. 

        exc is the exception to be handled.
        cmd must be an instance of Command class.

        Raises ConductorError with error message based on exit code of the 
        command or because the command timed out.

        If ignore_normal_CommandFailed = True and exit code of ssh command
        is *not* 129-255, such failure is ignored and ConductorError not raised.
        """

        if isinstance(exc, CommandFailed):

            ret = cmd.return_value

            if ret == 255:
                raise ConductorError("DEVICE REBOOTED "\
                    "(platform/hardware error) while %s" % task, "1051")

            elif ret > 128 and ret < 255:
                signal = ret-128
                raise ConductorError("Error in %s: killed by signal %s"\
                    % (task, signal), "1052")

            if not ignore_normal_CommandFailed:
                raise ConductorError("Error in %s: %s returned %s"\
                    % (task, cmd.command, ret), "105")

        elif isinstance(exc, (SoftTimeoutException, HardTimeoutException)):

            raise ConductorError("DEVICE GOT STUCK "\
                "(platform/hardware error) while %s" % task, "1053")

    
    def _fetch_test_definition(self, test_package):
        """
        Fetch test definition file for test_package and store its content to 
        server.
        """
        task = "Fetching test definition"
        self.log.info(task)

        cmdstr = self._get_command_to_copy_testdef()
        self._default_ssh_command_executor(cmdstr, task)

        self._store_test_definition(self.testrun.dst_testdef_file_path, 
                                    test_package)


    def _run_tests(self, test_package):
        """
        Runs tests in hardware or at host.
        Writes two files (for stderr and stdout) in folder testrun.base_dir
        """

        self.log.info("Running tests in %s..." % test_package)

        file_stdout = "%s_testrunner_stdout.txt" % test_package
        file_stderr = "%s_testrunner_stderr.txt" % test_package
        path_stdout = os.path.join(self.testrun.base_dir, file_stdout)
        path_stderr = os.path.join(self.testrun.base_dir, file_stderr)

        cmdstr = self._get_command_for_testrunner()
        self.log.info("Testrunner-lite command: %s" % cmdstr)
        cmd = Command(cmdstr) #no timeout
        try:
            cmd.execute()
        except CommandFailed:
            self._testrunner_lite_error_handler(cmdstr, cmd.return_value)
        finally:
            self._create_new_file(path_stdout, cmd.stdout)
            self._create_new_file(path_stderr, cmd.stderr)
            self._store_result_file(path_stdout, test_package)
            self._store_result_file(path_stderr, test_package)


    def _testrunner_lite_error_handler(self, cmdstr, return_value):
        """
        Handler for non-zero exit codes returned by testrunner-lite.
        Raises ConductorError with appropriate error message.
        """
        error_msg = "Command %s returned %s" % (cmdstr, return_value)
        if return_value == TESTRUNNER_SSH_FAILS:
            self.log.error(error_msg +" (ssh failure)")
            raise ConductorError("SSH connection failed "\
                                 "while running tests!", "151")
        elif return_value == TESTRUNNER_PARSING_FAILS:
            self.log.error(error_msg)
            raise ConductorError("Definition file parsing fails "\
                                 "while running tests!", "152")
        elif return_value == TESTRUNNER_VALIDATION_FAILS:
            self.log.error(error_msg)
            raise ConductorError("Definition file validation fails "\
                                 "while running tests!", "153")
        elif return_value == TESTRUNNER_RESULT_FOLDER_FAILS:
            self.log.error(error_msg)
            raise ConductorError("Can not create output folder for results "\
                                 "while running tests!", "154")
        elif return_value == TESTRUNNER_XML_READER_FAILS:
            self.log.error(error_msg)
            raise ConductorError("Failed to create xml reader for parsing "\
                                 "while running tests!", "155")
        elif return_value == TESTRUNNER_RESULT_LOGGING_FAILS:
            self.log.error(error_msg)
            raise ConductorError("Failed to initialize result logging "\
                                 "while running tests!", "156")
        else:
            self.log.error(error_msg)
            raise ConductorError("Testrunner-lite failed with unknown exit code %s"\
                                 % return_value, "150")


    def _fetch_results(self, test_package):
        """Retrieve the test results and store them to server"""
        
        task = "Fetching test results"
        self.log.info(task)

        cmdstr = self._get_command_to_copy_results()
        self._default_ssh_command_executor(cmdstr, task)



    
    def _define_test_packages(self):
        """
        Determine what test packages are to be executed. 
        Always scan test target for all installed test packages. 
        ConductorError is raised if user-defined packages are not found among 
        installed packages. 
        If there are no user-defined packages, all installed packages are set
        to be executed.
        """

        requested = self.testrun.requested_test_packages

        if self.testrun.is_host_based:
            if not requested:
                raise Exception("Test packages not defined for host-based "\
                                "testing")
            self.testrun.test_packages = requested

        else:
            all_pkgs = self._scan_for_test_packages()

            if not all_pkgs:
                raise ConductorError("No test packages found in image!", "1081")

            if requested:
                missing = items_missing_from_all_items(requested, all_pkgs)
                if missing:
                    raise ConductorError("Test package(s) missing in image: %s"\
                                         % ",".join(missing), "1082")
                self.testrun.test_packages = requested
            else:
                self.testrun.test_packages = all_pkgs


        self.log.info("Test packages to be executed: %s" \
                      % ",".join(self.testrun.test_packages))

        if not self.stand_alone: 
            self.responseclient.add_executed_packages(self.env, 
                                                  self.testrun.test_packages)
        else:
            self.log.warning("Skipped setting executed test packages to OTS "\
                             "server")


    def _scan_for_test_packages(self):
        """
        Scan for test packages in hardware containing tests.xml file. 
        Return names of test packages as a sorted list.

        # dpkg -l
        ...
        ii  accounts-qt0    ...   0.19-1+0m6         ... Accounts frame...
        ii  accounts-ui     ...   0.0.12-1.0rtc+0m6  ... accounts...
        ...

        # dpkg -S tests.xml
        testrunner-tests: /usr/share/testrunner-tests/tests.xml
        libqmsystem-tests: /usr/share/libqmsystem-tests/tests.xml
        testrunner-tests: /usr/share/testrunner/testdata/filter_tests.xml
        testrunner-tests: /usr/share/testrunner/testdata/sample_automatic_tests.xml
        """

        #Fetch list of packages whose name matches to predefined pattern
        task = "Scanning for installed test packages"
        self.log.info(task)

        cmdstr = self.target.get_command_to_list_installed_packages()
        cmd = self._default_ssh_command_executor(cmdstr, task.lower())

        test_pkg_pattern = re.compile("ii\s\s"\
            "(?P<name>\S+-test|\S+-tests|\S+-benchmark)\s+"\
            "(?P<ver>\S+)\s+"\
            "(?P<desc>.*)$", re.MULTILINE)

        test_pkg_data = re.findall(test_pkg_pattern, cmd.stdout)
        test_packages = [ name for (name, ver, desc) in test_pkg_data ]
        test_packages.sort()

        #Fetch list of good looking folder names that contain tests.xml file
        task = "Scanning for packages containing tests.xml"
        self.log.info(task)

        cmdstr = self.target.get_command_to_find_test_packages()
        cmd = self._default_ssh_command_executor(cmdstr, task.lower())

        path_pattern = re.compile("/usr/share/"\
                "(\S+-test|\S+-tests|\S+-benchmark)/tests.xml$", re.MULTILINE)
        possible_pkgs_with_file = re.findall(path_pattern, cmd.stdout)

        #Remove candidates that are not found in both lists
        for pkg in test_packages[:]:
            if pkg not in possible_pkgs_with_file:
                test_packages.remove(pkg)
                
        return test_packages


    def _fetch_environment_details(self):
        """
        Read test environment details into file. Store file to server.
        If executing of any of the commands fails, it is logged but that will
        not abort test execution.
        """

        self.log.info("Reading information about test environment (%s) "\
                      "into file" % self.target)

        path = os.path.join(self.testrun.base_dir,
                    "%s_environment_before_testing.txt" % self.target)

        content = ""
        content += "%s environment before test execution:\n\n" % self.target

        for cmdstr, plain_cmd in self.target.get_commands_to_show_test_environment():

            self.log.debug(cmdstr)
            content += "==== %s ====\n" % plain_cmd

            cmd = Command(cmdstr, soft_timeout = 10, hard_timeout = 15)
            try:
                cmd.execute()
            except (SoftTimeoutException, HardTimeoutException):
                self.log.warning("Command '%s' timed out!" % cmdstr)
                content += "Command timed out\n\n"
            except CommandFailed:
                self.log.warning("Command '%s' failed!" % cmdstr)
                content += "Command failed\n\n"
            else:
                content += cmd.stdout+"\n"

        self.log.debug("Finished reading information about test environment")

        self._create_new_file(path, content)

        #may raise ConductorError for IOErrors or any exception from ResponseClient
        self._store_result_file(path, test_package = "undefined") 

    
    def _fetch_files_after_testing(self):
        """Fetch predefined set of files after testing. Store files to server"""

        dest_path = self.testrun.post_test_dir
        error_counter = 0
        for src_path in self.config['files_fetched_after_testing']:

            self.log.info("Fetching file %s from %s" % (src_path, self.target))
            name = os.path.basename(src_path)
            if not name:
                self.log.warning("Invalid path: %s" % src_path)
                continue

            cmdstr = self.target.get_command_to_copy_file(src_path, dest_path)
            cmd = Command(cmdstr, soft_timeout = 10, hard_timeout = 15)

            while error_counter < SSH_CONNECTION_RETRIES:
                error_counter += 1
                try:
                    cmd.execute()
                except (SoftTimeoutException, HardTimeoutException):
                    self.log.warning("Failed to fetch file %s (command %s "\
                        "timed out)" % (src_path, cmdstr))
                except CommandFailed:
                    self.log.warning("Failed to fetch file %s (command %s "\
                        "returned %s)" % (src_path, cmdstr, cmd.get_return_value()))
                else:
                    self.log.debug("File fetched successfully")
                    break

                if error_counter < SSH_CONNECTION_RETRIES:
                    self.log.warning("Retrying (%d) to fetch file after (%d) seconds sleep..."\
                                    % (error_counter, SSH_RETRY_INTERVAL))
                    time.sleep(SSH_RETRY_INTERVAL)

        subprocess.call('chmod -R a+r '+dest_path, shell=True) #easier to debug

        self._store_result_files(dest_path, test_package = "undefined")


    ### Methods that contain implementation for Host-based testing:

    def _get_command_to_copy_testdef(self):
        """Command used to copy test definition to testrun data folder."""
        if self.testrun.is_host_based:
            return LOCAL_COMMAND_TO_COPY_FILE % \
                    (self.testrun.testdef_src, self.testrun.testdef_target_dir)

        return self.target.get_command_to_copy_testdef()

    def _get_command_to_copy_results(self):
        """Command used to copy test result files to testrun data folder."""
        if self.testrun.is_host_based:
            #No need to copy. Files were immediately saved to final destination
            return "" 

        return self.target.get_command_to_copy_results()

    def _get_command_for_testrunner(self):
        """
        Constructs and returns command for testrunner-lite. 

        Command line options are included with following conditions:
        - Http-logger option is given if we're not running stand-alone.
        - Testfilter option is given if filter string has been specified.
        - Remote-testing option is given if we're not doing host-based 
          testing.
        """

        http_logger_option = ""
        if not self.stand_alone:
            path = HTTP_LOGGER_PATH % str(self.testrun.id)
            url = "%s%s" % (self.responseclient.host, path) #http:// not needed
            http_logger_option = TESTRUNNER_LOGGER_OPTION % url

        filter_option = ""
        if self.testrun.filter_string:
            filter_option = TESTRUNNER_FILTER_OPTION \
                                    % self.testrun.filter_string

        remote_option = ""
        if not self.testrun.is_host_based:
            remote_option = TESTRUNNER_SSH_OPTION

        workdir = os.path.expanduser(TESTRUNNER_WORKDIR)

        cmd = CMD_TESTRUNNER % (workdir, 
                                self.testrun.dst_testdef_file_path, 
                                self.testrun.result_file_path, 
                                filter_option,
                                http_logger_option,
                                remote_option)

        return cmd


def items_missing_from_all_items(items, all_items):
    """Returns list of items that are not in all_items list."""
    missing = []
    for item in items:
        if item not in all_items:
            missing.append(item)
    return missing

