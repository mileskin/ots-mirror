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
Factory method to create TaskRunner from a config file 
"""

import configobj

from ots.server.server_config_filename import server_config_filename
from ots.server.distributor.taskrunner import TaskRunner

def taskrunner_factory(routing_key,
                       execution_timeout,
                       testrun_id,
                       config_file=None):
    """
    Instantiate a Taskrunner from the config file

    @type routing_key : C{str}  
    @param routing_key : The routing_key for the Task

    @type execution_timeout: C{int}  
    @param execution_timeout: The timeout for the remote commands

    @type testrun_id: C{int}  
    @param testrun_id: The Testrun id 

    @type config_file: C{str}  
    @param config_file: The fqname of the config file

    @rtype: L{TaskRunner}  
    @return: The TaskRunner
    """
    if not config_file:
        config_file = server_config_filename()

    config = configobj.ConfigObj(config_file).get("ots.server.distributor")

    taskrunner = TaskRunner(username = config["username"],
                            password = config["password"],
                            host = config["host"],
                            vhost = config["vhost"],
                            services_exchange = routing_key,
                            port = config.as_int("port"), 
                            routing_key = routing_key,
                            testrun_id = testrun_id,
                            execution_timeout = execution_timeout,
                            queue_timeout = config.as_int("timeout_task_start"),
                            controller_timeout = \
                                config.as_int("timeout_for_preparation"))
    return taskrunner


