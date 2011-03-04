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

import os
import logging
from socket import gethostname
import configobj

from ots.common.routing.api import get_routing_key

from ots.server.server_config_filename import server_config_filename
from ots.server.distributor.api import taskrunner_factory
from ots.server.allocator.get_commands import get_commands

LOG = logging.getLogger(__name__)

def _storage_address():
    """
    rtype: C{str}
    rparam: The storage address 
    """
    server_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    conf = server_config_filename()
    config = configobj.ConfigObj(conf).get('ots.server.allocator')
    storage_host = config['storage_host']
    if not storage_host:
        storage_host = gethostname()
    storage_port = "1982" # TODO: DEPRECATED REMOVE AFTER CONDUCTOR IS CHANGED
    return "%s:%s"%(storage_host, storage_port)     



#####################
# PUBLIC METHOD
#####################

def primed_taskrunner(testrun_uuid, execution_timeout, distribution_model, 
                      device_properties,
                      image, hw_packages, host_packages,
                      emmc, testfilter, flasher, custom_distribution_model,
                      extended_options): 
    """
    Get a Taskrunner loaded with Tasks and ready to Run

    @type testrun_uuid: C{str}
    @param testrun_uuid: The unique identifier for the testrun

    @type execution_timeout: C{int}
    @param execution_timeout: The execution timeout in minutes

    @type distribution_model: C{str}
    @param distribution_model: The name of the distribution_model

    @type device_properties : C{dict}
    @param device_properties : A dictionary of device properties 
                                              this testrun requires
       
    @type image: C{str}
    @param image: The URL of the image
        
    @type hw_packages : C{list} of C{str}
    @param hw_packages: The hardware packages

    @type host_packages : C{list} of C{str}
    @param host_packages: The host packages

    @type emmc : C{str}
    @param emmc: Url to the additional content image (memory card image)

    @type testrun_uuid : C{str}
    @param testrun_uuid: The testrun uuid
        
    @type storage_address: C{str}
    @param storage_address: The storage address 

    @type testfilter: C{str}
    @param testfilter: The test filter string for testrunner-lite

    @type flasher: C{str}
    @param flasher: The URL of the flasher

    @type custom_distribution_model: C{callable}
    @param custom_distribution_model: A callable matching the default models
                                      in default_distribution_models.py

    @type extended_options : C{dict}
    @param extended_options : A dictionary of extended ots testrun options

    rtype: L{Taskrunner}
    rparam: A loaded Taskrunner 
    """

    routing_key = get_routing_key(device_properties)
    taskrunner = taskrunner_factory(routing_key, execution_timeout, 
                                    testrun_uuid)
    test_list = dict()
    if hw_packages:
        test_list['device'] = ",".join(hw_packages)
    if host_packages:
        test_list['host'] = ",".join(host_packages)

    # Server deals with minutes, conductor uses seconds, 
    execution_timeout = int(execution_timeout)*60

    cmds = get_commands(distribution_model,
                        image,
                        test_list,
                        emmc,
                        testrun_uuid,
                        _storage_address(),
                        testfilter,
                        execution_timeout,
                        flasher,
                        custom_distribution_model,
                        extended_options)
    for cmd in cmds:
        LOG.info("Added cmd '%s' to taskrunner" % (" ".join(cmd)))
        taskrunner.add_task(cmd)
    return taskrunner
