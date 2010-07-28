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

"""
Factory method to create TaskRunner from a config file 
"""

DEFAULT_CONFIG_FILE = "/etc/ots-server.ini"

#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401

import ConfigParser
import os

from ots.server.distributor.taskrunner import TaskRunner

def taskrunner_factory(device_group,
                       timeout,
                       testrun_id,
                       config_file=None):
    """
    Instantiate a Taskrunner from the config file

    @type device_group: C{string }  
    @param device_group: The device group under test

    @rtype timeout: C{int}  
    @return timeout: The timeout

    @type config_file: C{string}  
    @param config_file: The fqname of the config file

    @type testrun_id: C{int}  
    @param testrun_id: The Testrun id 

    @rtype taskrunner: L{TaskRunner}  
    @return taskrunner: The TaskRunner
    """

    if not config_file:
        config_file = _default_config_filename()

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    taskrunner = TaskRunner(username = config.get("Client", "username"),
                            password = config.get("Client", "password"),
                            host = config.get("Client", "host"),    
                            vhost = config.get("Client", "vhost"),
                            services_exchange = device_group,
                            port = config.getint("Client", "port"), 
                            routing_key = device_group,
                            testrun_id = testrun_id,
                            timeout = timeout,
                            queue_timeout = config.getint("Client", 
                                                          "timeout_task_start"))
    return taskrunner


def _default_config_filename():
    """
    Returns the default config file path.

    Tries /etc/ots-server.ini first. If that does not work, tries config.ini
    from ots.server.distributor directory
    """
    if os.path.exists(DEFAULT_CONFIG_FILE):
        return DEFAULT_CONFIG_FILE

    distributor_dirname = os.path.dirname(os.path.abspath(__file__))
    distributor_config_filename = os.path.join(distributor_dirname,
                                               "config.ini")
    if not os.path.exists(distributor_config_filename):
        raise Exception("%s not found"%(distributor_config_filename))
    return distributor_config_filename
