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
Demo to use the taskrunner from the CL

FIXME
"""
import os
import sys
import logging

import ConfigParser

import ots.server
from ots.server.version import __VERSION__

from ots.server.distributor.taskrunner_factory import taskrunner_factory

def init_logging(config_filename):
    """
    Initialise the logging.
    """
    config = ConfigParser.ConfigParser()
    config.read(config_filename)
    try:
        log_filename = config.get("Client", "log_file", None)
    except ConfigParser.NoOptionError:
        log_filename = None

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    #Switch between file and STDERR based logging depending on config
    if log_filename is not None and os.path.exists(config_filename):
        log_handler = logging.FileHandler(log_filename,
                                          encoding = "utf-8")
    else:
        log_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

def main():
    """Entry point for command line testing"""

    from optparse import OptionParser
    parser = OptionParser()

    cfg_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "config.ini")

    parser.add_option("-v", "--version",
                      action = "store_true",
                      help = "the version number of ots.distributor")
    parser.add_option("-d", "--device",
                      default = "foo",
                      help = "the device to be used")
    parser.add_option("-t", "--timeout",
                      default = 30,
                      help = "the timeout")
    parser.add_option("-c", "--config",
                      default = cfg_filename,
                      help = "the config filename")
    parser.add_option("-r", "--command",
                      default = "echo hello world",
                      help = "the command to run")

    # parse command line args
    options = parser.parse_args()[0]

    if options.version:
        print "Version:", __VERSION__
        sys.exit(1)

    if not os.path.exists(options.config):
        print "Config file path '%s' does not exist!" % ( options.config )
        sys.exit(1)

    init_logging(options.config)

    testrun_id = ''
    taskrunner = taskrunner_factory(options.device,
                                    options.timeout,
                                    testrun_id,
                                    options.config)
    taskrunner.add_task([options.command])
    taskrunner.run()

if __name__ == '__main__':
    main()
