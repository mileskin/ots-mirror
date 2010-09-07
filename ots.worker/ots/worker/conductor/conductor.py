#!/usr/bin/python
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


import logging
import logging.handlers
import os
import sys
from optparse import OptionParser
from socket import gethostname

from helpers import parse_config

from conductor_config import DEBUG_LOG_FILE
from conductor_config import HTTP_LOGGER_PATH
from executor import TestRunData
from executor import Executor
from hardware import Hardware
from conductorerror import ConductorError
from ots.worker.api import ResponseClient


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
                    help="URL to image (.bin) or rootstrap (.tgz or tar.gz)",
                    metavar="URL")

    parser.add_option("-t", "--testpkgs", dest="packages", action="store",
                    type="string",
                    help="List of test packages separated by comma. If not "\
                         "given, all packages found in image/roootstrap are "\
                         "executed.", 
                    metavar="TESTPKGS")

    parser.add_option("-o", "--host", dest="host", action="store_true",
                    default=False,
                    help="Execute tests on host. Requires use of -t.")

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
                    help="URL to content image. Enables content image flashing.",
                    metavar="CONTENTIMAGEURL")

    parser.add_option("-E", "--contentimagepath", dest="content_image_path", 
                    action="store", type="string",
                    help="Local path to content image. Enables content image "\
                         "flashing.",
                    metavar="CONTENTIMAGEPATH")

    parser.add_option("-f", "--filter", dest="filter_options", action="store", 
                    type="string", 
                    default="",
                    help="Testrunner filter options to select tests.",
                    metavar="OPTIONS")
    
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", 
                    default=False,
                    help="Enable verbosity to debug")

    parser.add_option("--dontflash", dest="dontflash", action="store_true", 
                    default=False,
                    help="Do not set up target. Skips image/rootstrap "\
                         "downloading, flasher and Scratchbox setup.")

    parser.add_option("--configfile", dest="config_file", action="store", 
                    type="string", 
                    help="Path to configuration file",
                    metavar="PATH")

    parser.add_option("--flasherurl", dest="flasher_url", action="store", 
                    type="string",
                    help="URL to Flasher tool",
                    metavar="FLASHERURL")

    (options, args) = parser.parse_args(args)

    return (options, parser)


def _setup_logging(verbose):
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

    log_file = os.path.expanduser(DEBUG_LOG_FILE)
    debug_handler = logging.handlers.RotatingFileHandler(log_file,
                                                maxBytes=5242880,
                                                backupCount=5)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    root_logger.addHandler(output_handler)
    root_logger.addHandler(debug_handler)
    return root_logger


def _add_http_logger(server_host, testrun_id):
    """
    Add http logger handler into logging. 
    Associate it with given testrun in server. Returns root_logger.
    """
    http_handler = logging.handlers.HTTPHandler(server_host, 
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
    if options.image_url is None:
        sys.stderr.write("Missing mandatory argument (url)\n")
        return False
    if options.host and not options.packages:
        sys.stderr.write("Missing test packages. "\
              "Host-based testing requires specifying test packages!\n")
        return False
    if (options.testrun_id and not options.otsserver) \
            or (not options.testrun_id and options.otsserver):
        # Note: For testing purposes it's OK to leave both parameters out!
        sys.stderr.write("Missing testrun ID or otsserver. "\
              "Both are needed to communicate with OTS!\n")
        return False
    return True


def _read_conductor_config(config_file, default_file = ""):
    """
    Read and parse conductor configuration file. 
    If config_file is None or does not exist, default_file is tried. 
    If neither of the two files exists, raise exception. Returns dictionary.
    """
    def parse_list(string):
        """
        Parse comma-separated list of values from given string.
        Remove possible quotes surrounding any value. Return values as list.
        """
        return [ item.strip().strip('"\'') for item in string.split(",") ]

    if config_file and os.path.exists(config_file):
        config = parse_config(config_file, "conductor")
    elif default_file and os.path.exists(default_file):
        config = parse_config(default_file, "conductor")
    else:
        raise Exception("Configuration file missing")

    config['files_fetched_after_testing'] = \
            parse_list(config['files_fetched_after_testing'])
    config['commands_to_show_environment'] = \
            parse_list(config['commands_to_show_environment'])

    return config


def _initialize_remote_connections(otsserver, testrun_id):
    """
    Initialise ResponseClient and http_logger. Return ResponseClient object if 
    everything succeeds or None if anything fails. Log details about failure.
    """
    log = logging.getLogger("conductor")
    responseclient = None
    host, port = otsserver.split(":")

    try:
        _add_http_logger(host, testrun_id)
    except:
        log.error("Unknown error in initializing http logger to server "\
                  "%s!" % host)
        log.debug("Traceback follows:", exc_info=True)
        return None

    try:
        resposenclient = ResponseClient(host, testrun_id)
        responseclient.connect()
    except:
        log.error("Unknown error in initializing OTS client connecting "\
                      "to %s! (Using OtsResponseClient)" % (host))
        
    return responseclient


def main():
    """ Main function """

    (options, parser) = _parse_command_line(sys.argv[1:])
    if not _check_command_line_options(options):
        parser.print_help()
        sys.exit(1)

    stand_alone = not options.testrun_id and not options.otsserver

    _setup_logging(options.verbose)
    log = logging.getLogger("conductor")

    responseclient = None

    if not stand_alone:
        responseclient = _initialize_remote_connections(options.otsserver, 
                                                    options.testrun_id)
        if not responseclient:
            sys.exit(1)

    log.debug(70*"=") #for log file
    log.info("Starting conductor at %s" % gethostname())
    log.info("Incoming command line parameters: %s" \
                % " ".join([arg for arg in sys.argv[1:]]))
    log.debug("os.getenv('USERNAME') = %s" % os.getenv('USERNAME'))
    log.debug("os.environ.get('HOME') = %s" % os.environ.get("HOME"))
    log.debug("os.getcwd() = %s" % os.getcwd())

    log.debug("Reading configuration file")

    config = _read_conductor_config(options.config_file, "/etc/conductor.conf")

    try:
        testrun = TestRunData(options, config)
        executor = Executor(testrun, stand_alone, responseclient, gethostname())
        executor.set_target(Hardware(testrun))
    except:
        log.error("Unknown error while creating test!")
        log.error("Traceback follows:", exc_info=True)
        sys.exit(1)

    log.info("Testrun ID: %s  Environment: %s" % (options.testrun_id, 
                                                  executor.env))

    if options.filter_options:
        log.debug("Filtering enabled: %s" % options.filter_options)

    errors = 0
    try:
        errors = executor.execute_tests()
    except ConductorError, exc:
        log.error("%s (ots error code: %s)" % (exc.error_info, exc.error_code))
        if not stand_alone:
            responseclient.set_error(exc.error_info, exc.error_code)
        log.info("Testing in %s ended with error." % executor.env)
        sys.exit(0)
    except:
        log.error("Unknown error when trying to execute tests.")
        log.error("Traceback follows:", exc_info = True)
        if not stand_alone:
            responseclient.set_error(str(sys.exc_info()[1]), "999")
        log.info("Testing in %s ended with error." % executor.env)
        sys.exit(0)

    if errors:
        log.info("Testing in %s done. Execution error reported on %i "\
                 "test packages." % (executor.env, errors))
    else:
        log.info("Testing in %s done. No errors." % executor.env)


if __name__ == '__main__':
    main()

