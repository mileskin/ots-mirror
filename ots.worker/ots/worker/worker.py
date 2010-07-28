#!/usr/bin/python
# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: ___OSSO_CONTACT_NAME___ <___CONTACT_EMAIL___@nokia.com>
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
Top level script starts an AMQP server running
"""

import sys
import os
import logging 
import logging.handlers
import subprocess

import ConfigParser

from ots.worker.connection import Connection
from ots.worker.server import Server
from ots.worker.client import Client
from ots.worker.get_version import get_version 

logger = logging.getLogger(__name__)


STOP_SIGNAL_FILE = "/tmp/stop_ots_worker"

class Worker(object):
    """
    AMQP server tuned for OTS 
    """

    def __init__(self, vhost, host, port, username, password, queue, 
                       routing_key, services_exchange):
        """
        Initialise the class, read config, set up logging
        """
        self._vhost = vhost 
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._queue = queue 
        self._routing_key = routing_key 
        self._services_exchange = services_exchange
        self._timeout = None
   
    def _init_connection(self):
        """
        Initialises a connection object)
        """
        self._connection = Connection(self._vhost,
                                      self._host,
                                      self._port,
                                      self._username,
                                      self._password,
                                      self._queue,
                                      self._routing_key,
                                      self._services_exchange)
        self._connection.connect()

    def _init_server(self):
        """
        Initialises the worker server
        """
        self._server = Server(connection = self._connection,
                              client = self._client)

    def _init_client(self):
        """
        Initialises the worker client
        """
        self._client = Client(connection=self._connection)
        
    def start(self):
        """
        Starts the ots worker server running
        """
        logger.debug('Initialising the server')
        # If stop flag is there, remove it
        if os.path.exists(STOP_SIGNAL_FILE):
            os.system("rm -fr "+STOP_SIGNAL_FILE)
        self._init_connection()
        self._init_client()
        self._init_server()
        logger.debug("Starting the server. " + \
                         "{vhost:'%s', queue:'%s', routing_key:'%s'}" % 
                     (self._vhost,
                      self._queue,
                      self._routing_key))
        #Aaaand go....
        self._server.start()


def _init_logging(config_filename = None):
    """
    Initialise the logging 
    """
    formatter = \
        logging.Formatter\
        ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_filename = None
    if config_filename is not None:
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        try:
            log_filename = config.get("Worker", "log_file", None)
        except ConfigParser.NoOptionError:
            pass
    
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    #Switch between file and STDERR based logging depending on config
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

def _edit_config(config_filename):
    """
    Fire up nano to allow the editing of the config 
    """
    subprocess.call("nano %s"%(config_filename),shell=True)

def worker_factory(config_filename):
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
    queue = config.get('Worker','queue')
    routing_key = config.get('Worker','routing_key')
    services_exchange = config.get('Worker','services_exchange')
    
    if queue == "fix_me" or routing_key == "fix_me":
        _edit_config(config_filename)

        print
        print "Now restart ots_worker"
        print
        sys.exit()

    return Worker(vhost=vhost, host=host, port=port, username=username,
                  password=password, queue=queue, routing_key=routing_key, 
                  services_exchange=services_exchange)
       
def main():
    """
    Wrapper to provide an entry point for stdeb
    """
    from optparse import OptionParser
    parser = OptionParser()
    #
    parser.add_option("-c", "--config",
                      default = "/etc/ots.ini",
                      help= "the location of the config file")
    #
    parser.add_option("-v", "--version",
                      action = "store_true",
                      help = "the version number of ots.worker")
    #
    options, args = parser.parse_args()
    if options.version:
        print "Version:", get_version()
        sys.exit(1)
    #
    if not os.path.exists(options.config):
        print "Config file path '%s' does not exist!" % ( options.config )
        sys.exit(1)
    #
    _init_logging(options.config)
    worker = worker_factory(options.config)
    worker.start()

if __name__ == '__main__':
    main()
