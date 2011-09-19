#!/usr/bin/python
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

""" Conductor main file """

import logging
import logging.handlers
import os
import sys
import signal
from optparse import OptionParser
from socket import gethostname

from ots.worker.conductor.helpers import parse_list, \
                                         parse_config

from ots.worker.conductor.conductor_config import DEBUG_LOG_FILE
from ots.worker.conductor.conductor_config import HTTP_LOGGER_PATH
from ots.worker.conductor.executor import TestRunData
from ots.worker.conductor.executor import Executor
from ots.worker.conductor.conductorerror import ConductorError
from ots.worker.api import ResponseClient
from ots.common.helpers import get_logger_adapter
from ots.common.framework.flasher_plugin_base import FlashFailed

DEFAULT_CONFIG = "/etc/ots/conductor.conf"
OPT_CONF_SUFFIX = ".conf"
LOG = get_logger_adapter("conductor")


class ExecutorSignalHandler(object):
    """Signal handler to catch signals from testrunner-lite"""

    def __init__(self, executor):
        """
        Initialization

        @type command: C{obj}
        @param command: Executor
        """
        self._executor = executor

    def reboot_device(self, sig_num, frame):
        """
        Function to trigger device reboot
        
        @type sig_num: C{int}
        @param sig_num: Signal number

        @type frame: None
        @param frame: Current stack frame
        """
        LOG.debug("'%s' signal received from testrunner-lite" % sig_num)

        trlite_command = self._executor.trlite_command

        if not trlite_command:
            LOG.warning("SIGUSR1 caught but no testrunner-lite running")
            return

        try:
            LOG.info("SIGUSR1 signal received from testrunner-lite,"
                     " rebooting...")
            self._executor.target.reboot()
        except ConductorError, err:
            LOG.error("Bootup failed: %s" % err)
            trlite_command.send_signal(signal.SIGTERM)
            return

        self._executor.save_environment_details()
        LOG.debug("Sending signal SIGUSR1 to process %s" % trlite_command.pid)
        trlite_command.send_signal(signal.SIGUSR1)


def _parse_command_line(args):
    """
    Parse command line options (args) and set default values to them.
    For those options that have no default value specified, default = None.
    Returns tuple: (options, parser).
    """

    usage = "Usage: %prog [options] \n" + \
            "Example: " + \
            "%prog -u http://url/to/fiascoimage/in/..../image.bin -t demo-tests"

    parser = OptionParser(usage=usage)

    parser.add_option("-u", "--imageurl", dest="image_url", action="store", 
                    type="string",
                    help="URL to main flash image file",
                    metavar="URL")
    
    parser.add_option("-U", "--imagepath", dest="image_path", action="store", 
                    type="string",
                    help="Path to main flash image file",
                    metavar="PATH")

    parser.add_option("-t", "--testpkgs", dest="packages", action="store",
                    type="string",
                    help="List of test packages separated by comma. If not "\
                         "given, all packages found in image/roootstrap are "\
                         "executed.", 
                    metavar="TESTPKGS")

    parser.add_option("-o", "--host", dest="host", action="store_true",
                    default=False,
                    help="Execute tests on host. Requires use of -t.")

    parser.add_option("-C", "--chrooted", dest="chrooted", action="store_true",
                    default=False,
                    help="Execute tests inside a chroot. Requires "\
                         "-t and -r or -R.")

    parser.add_option("-i", "--id", dest="testrun_id", action="store", 
                    type="string",
                    help="OTS unique testrun ID. (Do not use if running "\
                         "conductor outside OTS!)",
                    metavar="ID")

    parser.add_option("-c", "--otsserver", dest="otsserver", action="store", 
                    type="string",
                    help="OTS Server address and port. (Do not use if "\
                         "running conductor outside OTS!)",
                    metavar="ADDRESS:PORT")

    parser.add_option("-e", "--contentimageurl", dest="content_image_url",
                    action="store", type="string",
                    help="URL to content image. Enables content image "\
                         "flashing.",
                    metavar="CONTENTIMAGEURL")

    parser.add_option("-E", "--contentimagepath", dest="content_image_path", 
                    action="store", type="string",
                    help="Local path to content image. Enables content image "\
                         "flashing.",
                    metavar="CONTENTIMAGEPATH")

    parser.add_option("-r", "--rootstrapurl", dest="rootstrap_url",
                    action="store", type="string",
                    help="URL to an i386 rootstrap. If chrooted testing "\
                        "is enabled, tests will be run chrooted inside this "\
                        "rootstrap.",
                    metavar="ROOTSTRAPURL")

    parser.add_option("-R", "--rootstrappath", dest="rootstrap_path",
                    action="store", type="string",
                    help="Local path to an i386 rootstrap. If chrooted "\
                        "testing is enabled, tests will be run chrooted inside "\
                        "this rootstrap.",
                    metavar="ROOTSTRAPPATH")

    parser.add_option("-f", "--filter", dest="filter_options", action="store", 
                    type="string", 
                    default="",
                    help="Testrunner filter options to select tests.",
                    metavar="OPTIONS")
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", 
                    default=False,
                    help="Enable verbosity to debug")

    parser.add_option("-m", "--timeout", dest="timeout", action="store",
                    default="0",
                    help="Enable global timeout for testruns")

    parser.add_option("--dontflash", dest="dontflash", action="store_true", 
                    default=False,
                    help="Do not set up target. Skips image downloading "\
                         "and flashing.")

    parser.add_option("--configfile", dest="config_file", action="store", 
                    type="string", 
                    help="Path to configuration file",
                    metavar="PATH")

    parser.add_option("-p", "--testplan", dest="testplan", action="store",
                      type="string",
                      help="Test plan file",
                      metavar="TESTPLAN")

    parser.add_option("--flasherurl", dest="flasher_url", action="store", 
                    type="string",
                    help="URL to Flasher tool",
                    default=None,
                    metavar="FLASHERURL")

    parser.add_option("--libssh2", dest="use_libssh2",
                      action="store_true", default=False,
                      help="Use testrunner-lite libssh2 support")

    parser.add_option("--resume", dest="resume",
                      action="store_true", default=False,
                      help="Use testrunner-lite resume functionality")

    parser.add_option("--flasher_options", dest="flasher_options", action="store",
                      type="string",
                      help="Options to pass to the flasher module",
                      metavar="FLASHER_OPTIONS")

    (options, args) = parser.parse_args(args)

    if os.getenv("OTS_WORKER_NUMBER"):
        options.device_n = int(os.getenv("OTS_WORKER_NUMBER"))
    else:
        options.device_n = 0

    return (options, parser)


def _setup_logging(verbose, device_number):
    """
    Initializes logging with 2 handlers:
     - stdout will log messages defined by output_level.
     - DEBUG_LOG_FILE will receive all messages. It is a rotating file handler.
    Returns root_logger
    """

    if verbose:
        output_level = logging.DEBUG
    else:
        output_level = logging.INFO

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG)

    output_handler = logging.StreamHandler(sys.stdout)
    output_handler.setLevel(output_level)
    output_handler.setFormatter(formatter)

    log_file = os.path.expanduser(DEBUG_LOG_FILE % device_number)
    debug_handler = logging.handlers.RotatingFileHandler(log_file,
                                                maxBytes=5242880,
                                                backupCount=5)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    root_logger.addHandler(output_handler)
    root_logger.addHandler(debug_handler)
    return root_logger


def _add_http_logger(server_host, testrun_id, device_n):
    """
    Add http logger handler into logging. 
    Associate it with given testrun in server. Returns root_logger.
    """
    http_handler = logging.handlers.HTTPHandler( \
                            server_host, 
                            HTTP_LOGGER_PATH % str(testrun_id), 
                            "POST")
    root_logger = logging.getLogger()
    http_handler.setLevel(logging.INFO)
    root_logger.addHandler(http_handler)
    return root_logger


def _check_command_line_options(options):
    """
    Return True if mandatory command line options are given.
    Return False if mandatory options are missing or if any given option is 
    invalid.
    """
    if options.otsserver:
        try:
            host, port = options.otsserver.split(":")
        except ValueError:
            sys.stderr.write("Invalid OTS server parameter: %s\n"\
                             % (options.otsserver))
            return False
        if not host or not port:
            sys.stderr.write("Invalid OTS server parameter: %s\n"\
                             % (options.otsserver))
            return False
    if options.image_url is None :
        sys.stderr.write("Missing mandatory argument (url)\n")
        return False

    if (options.host or options.chrooted) and not options.packages and not options.testplan:
        sys.stderr.write("Missing test packages. " \
              "Host-based and chrooted testing require specifying test" \
              "packages!\n")
        return False
    if options.chrooted and not (options.rootstrap_url 
            or options.rootstrap_path):
        sys.stderr.write("Missing rootstrap. " \
            "Chroot-based testing requires specifying a rootstrap!\n")
        return False
    if (options.testrun_id and not options.otsserver) \
            or (not options.testrun_id and options.otsserver):
        # Note: For testing purposes it's OK to leave both parameters out!
        sys.stderr.write("Missing testrun ID or otsserver. "\
              "Both are needed to communicate with OTS!\n")
        return False
    return True


def _parse_conductor_config(config_file, current_config_dict=None):
    """
    Read and parse conductor configuration file. 
    If config_file is None or does not exist, default_file is tried. 
    If neither of the two files exists, raise exception. Returns dictionary.
    """

    if not os.path.isfile(config_file):
        raise Exception("Configuration file missing")

    if not current_config_dict:
        current_config_dict = {}
        # Make sure these parameters will be parsed as lists.
        for conf_param in ['files_fetched_after_testing', \
                           'pre_test_info_commands_debian', \
                           'pre_test_info_commands_rpm', \
                           'pre_test_info_commands']:
            current_config_dict[conf_param] = []

    return parse_config(config_file, "conductor", current_config_dict)


def _read_configuration_files(config_file, device_n):
    """
    Read main configuration file and optional custom configuration
    files.
    """

    if not (config_file and os.path.exists(config_file)):
        config_file = _default_config_file()

    # Try if there is separated config file
    if device_n != 0:
        default_path = os.path.splitext(DEFAULT_CONFIG)
        new_config_path = default_path[0] + "_%d" % device_n + default_path[1]
        
        if os.path.exists(new_config_path):
            config_file = new_config_path

    LOG.info("using config file %s" % config_file)
    
    config_dict = _parse_conductor_config(config_file)

    if config_dict.has_key('custom_config_folder'):
        custom_folder = config_dict['custom_config_folder']

        # Update config_dict with optional config parameters
        config_dict = _read_optional_config_files(custom_folder, config_dict)

    return config_dict


def _default_config_file():
    """
    Return default config file. Returns it from /etc/ots/ if exists or
    if not then the one in the source tree
    """

    if os.path.exists(DEFAULT_CONFIG):
        return DEFAULT_CONFIG
 
    conductor_dirname = os.path.dirname(os.path.abspath(__file__))
    conductor_config_filename = os.path.join(conductor_dirname, "conductor.conf")

    if not os.path.exists(conductor_config_filename):
        raise Exception("%s not found"%(conductor_config_filename))

    return conductor_config_filename


def _read_optional_config_files(custom_folder, config_dict):
    """
    Reads all .conf files from specified directory
    """

    log = logging.getLogger("conductor")

    try:
        contents = os.listdir(custom_folder)
    except (OSError, IOError), error:
        LOG.warning("Error listing directory %s: %s" % (custom_folder, error))
    else:
        for custom_config_file in contents:
            if len(custom_config_file) > len(OPT_CONF_SUFFIX) \
                and custom_config_file[len(custom_config_file) \
                - len(OPT_CONF_SUFFIX):] == OPT_CONF_SUFFIX:
                custom_config = \
                     _parse_conductor_config(custom_folder + \
                                    '/' + custom_config_file, config_dict)
                config_dict = custom_config

    return config_dict


def _initialize_remote_connections(otsserver, testrun_id, device_n):
    """
    Initialise ResponseClient and http_logger. Return ResponseClient object if 
    everything succeeds or None if anything fails. Log details about failure.
    """
    log = logging.getLogger("conductor")
    responseclient = None
    host, port = otsserver.split(":")

    try:
        _add_http_logger(host, testrun_id, device_n)
    except:
        LOG.error("Unknown error in initializing http logger to server "\
                  "%s!" % host)
        LOG.debug("Traceback follows:", exc_info=True)
        return None

    try:
        responseclient = ResponseClient(host, testrun_id)
        responseclient.connect()
    except:
        LOG.error("Unknown error in initializing OTS client connecting "\
                      "to %s! (Using OtsResponseClient)" % (host))

    return responseclient


def main():
    """ Main function """

    (options, parser) = _parse_command_line(sys.argv[1:])
    if not _check_command_line_options(options):
        parser.print_help()
        sys.exit(1)

    stand_alone = not options.testrun_id and not options.otsserver

    device_n = 0
    if options.device_n:
        device_n = options.device_n
    _setup_logging(options.verbose, device_n)

    responseclient = None

    if not stand_alone:
        responseclient = _initialize_remote_connections(options.otsserver,
                                                        options.testrun_id,
                                                        device_n)
        if not responseclient:
            sys.exit(1)

    LOG.debug(70*"=") #for log file
    LOG.info("Starting conductor at %s" % gethostname())
    LOG.info("Incoming command line parameters: %s" \
                % " ".join([arg for arg in sys.argv[1:]]))
    LOG.debug("os.getenv('USERNAME') = %s" % os.getenv('USERNAME'))
    LOG.debug("os.environ.get('HOME') = %s" % os.environ.get("HOME"))
    LOG.debug("os.getcwd() = %s" % os.getcwd())

    LOG.debug("Reading configuration file")

    config = _read_configuration_files(options.config_file, device_n)

    try:
        timeout = float(options.timeout)
        testrun = TestRunData(options, config)
        executor = Executor(testrun, stand_alone, responseclient, \
                            gethostname(), timeout)
        executor.set_target()
    except ValueError, err:
        LOG.error("Error: %s" % err)
        sys.exit(1)
    except Exception:
        LOG.error("Unknown error while creating test!")
        LOG.error("Traceback follows:", exc_info=True)
        sys.exit(1)

    LOG.info("Testrun ID: %s  Environment: %s" % (options.testrun_id, 
                                                  executor.env))

    executor_signal_handler = ExecutorSignalHandler(executor)
    signal.signal(signal.SIGUSR1,
                  executor_signal_handler.reboot_device)

    if options.filter_options:
        LOG.debug("Filtering enabled: %s" % options.filter_options)

    errors = 0
    try:
        errors = executor.execute_tests()
    except ConductorError, exc:
        LOG.error("%s (ots error code: %s)" % (exc.error_info, exc.error_code))
        if not stand_alone:
            responseclient.set_error(exc.error_info, exc.error_code)
        LOG.info("Testing in %s ended with error." % executor.env)
        sys.exit(0)
    except:
        LOG.error("Unknown error when trying to execute tests.")
        LOG.error("Traceback follows:", exc_info = True)
        if not stand_alone:
            responseclient.set_error(str(sys.exc_info()[1]), "999")
        LOG.info("Testing in %s ended with error." % executor.env)
        sys.exit(0)

    if errors:
        LOG.info("Testing in %s done. Execution error reported on %i "\
                 "test packages." % (executor.env, errors))
    else:
        LOG.info("Testing in %s done. No errors." % executor.env)


if __name__ == '__main__':
    main()

