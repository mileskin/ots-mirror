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



#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401

import ConfigParser
import os

from ots.server.distributor.taskrunner import TaskRunner
from ots.server.config import config_file_name

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
        config_file = config_file_name()

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
                                                         "timeout_task_start"),
                            testrun_timeout = config.getint("Client",
                                                     "timeout_worker_testrun"))
    return taskrunner

