#!/usr/bin/python
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

#Disable spurious pylint warnings

#pylint: disable=E0611
#pylint: disable=F0401


"""
Top level script starts an Worker
"""

import os
import sys
import logging.handlers
import ConfigParser
from optparse import OptionParser

from ots.worker.connection import Connection
from ots.worker.task_broker import TaskBroker
from ots.common.helpers import get_logger_adapter


STOP_SIGNAL_FILE = "/tmp/stop_ots_worker"
DEFAULT_CONF = "/etc/ots/worker.conf"


class Worker(object):
    """
    Worker class
    """

    def __init__(self, vhost,
                       host,
                       port,
                       username,
                       password,
                       properties,
                       device_n=0):
        """
        Initialise the class, read config, set up logging
        """
        self._vhost = vhost
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._properties = properties
        self._timeout = None
        self._device_n = device_n
        self.log = get_logger_adapter(__name__)

    ###########################
    # AMQP Log Handler
    ###########################

    def start(self):
        """
        Starts the ots worker server running
        """
        self.log.info('Initialising the server')
        # If stop flag is there, remove it
        if os.path.exists(STOP_SIGNAL_FILE):
            os.system("rm -fr "+STOP_SIGNAL_FILE)
        self._connection = Connection(self._vhost,
                                      self._host,
                                      self._port,
                                      self._username,
                                      self._password)
        self._task_broker = TaskBroker(self._connection, 
                                       self._properties)
        self.log.info("Starting the worker " + \
                        "%d. server: %s:%s, device_properties: %s" % 
                    (self._device_n,
                     self._host,
                     self._port,
                     self._properties))
        self._task_broker.run()


def _init_logging(config_filename=None, device_n=0):
    """
    Initialise the logging 
    """
    formatter = \
        logging.Formatter \
            ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_filename = None
    if config_filename is not None:
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        try:
            log_filename = config.get("Worker", "log_file", None)
            if device_n != 0:
                name_array = os.path.splitext(log_filename)
                log_filename = "%s_%s%s" % (name_array[0],
                                             str(device_n),
                                             name_array[1])
        except ConfigParser.NoOptionError:
            pass

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)

    # Switch between file and STDERR based logging depending on configuration
    if log_filename is not None:
        log_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                maxBytes=5242880,
                                                backupCount=5,
                                                encoding="utf-8")
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(log_handler)

    output_handler = logging.StreamHandler()
    output_handler.setFormatter(formatter)
    output_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(output_handler)


def worker_factory(config_filename, device_n = 0):
    """
    Laborious boot strapping from config
    """
    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    vhost = config.get('Worker', 'vhost')
    host = config.get('Worker', 'host')
    port = config.getint('Worker','port')
    username = config.get('Worker','username')
    password = config.get('Worker','password')

    properties = dict(config.items("Device"))

    return Worker(vhost = vhost,
                  host = host,
                  port = port,
                  username = username,
                  password = password,
                  properties = properties,
                  device_n = device_n)


def main():
    """
    Wrapper to provide an entry point for stdeb
    """
    parser = OptionParser()

    parser.add_option("-c", "--config",
                      default=DEFAULT_CONF,
                      help="the location of the config file")

    parser.add_option("-v", "--version",
                      action="store_true",
                      help="the version number of ots.worker")

    parser.add_option("-n", "--number",
                      default=0,
                      type=int,
                      help="the worker instance number")

    options, args = parser.parse_args()

    if options.version:
        from ots.worker.version import __VERSION__
        print "Version:", __VERSION__
        sys.exit(1)

    if not os.path.exists(options.config):
        print "Config file path '%s' does not exist!" % ( options.config )
        sys.exit(1)

    _init_logging(options.config, options.number)
    worker = worker_factory(options.config, options.number)

    os.putenv("OTS_WORKER_NUMBER", str(options.number))
    worker.start()
    os.unsetenv("OTS_WORKER_NUMBER")

if __name__ == '__main__':
    main()
