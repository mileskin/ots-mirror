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
Run a remote process or processes (tasks) through OTS client
"""

import sys
import logging

from ots.distributor.client import client_factory

LOG = logging.getLogger(__name__)

def run_remote_process(config_file, 
                       device_name, 
                       timeout, 
                       testrun_id, 
                       tasks):
    """
    Run a remote process or processes (tasks) and return when done.

    distribution_model: Name of model defining how each command is 
                        distributed to workers.

    commands: List of commands.
              Each command is a list containing executable and its parameters. 
    """

    success = False
    LOG.debug("Initialising OTS distributor using config file '%s'"\
              % (config_file))

    client = client_factory(device_name, timeout, config_file, testrun_id)

    LOG.debug("Running following commands on worker:")
    for task in tasks:
        LOG.debug("%s" % (" ".join(task)))

    success = client.connect().run(tasks, int(timeout))
    return success


def main():
    """Command line test client main method"""
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    log_handler = logging.StreamHandler()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)
    log_handler.setFormatter(formatter)
    log_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

    if len(sys.argv) < 6:
        print 'Usage: python run_remote_process.py config_file '\
            +'distribution_model device_name timeout testrun_id '\
            +'"command1 p1 p2" ["command2 p1 p2" ... ]'
        sys.exit()
    #config_file = sys.argv[1]
    #distribution_model = sys.argv[2]
    #device_name = sys.argv[3]
    #timeout = sys.argv[4]
    #testrun_id = sys.argv[5]
    args = sys.argv[1:5]
    for cmd in sys.argv[6:]:
        commands = cmd.split()
    args.append(commands)
    print "Run with result: ", run_remote_process(*args)

 
if __name__ == "__main__":
    main()
