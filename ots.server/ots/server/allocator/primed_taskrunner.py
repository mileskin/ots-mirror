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

import os
from socket import gethostname
import ConfigParser

from ots.common.framework.api import config_filename
from ots.server.distributor.api import taskrunner_factory
from ots.server.allocator.conductor_commands import get_commands

def _storage_address():
    """
    rtype: C{str}
    rparam: The storage address 
    """
    server_path = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    conf = config_filename("ots_allocator", server_path)
    config = ConfigParser.ConfigParser()
    config.read(conf)
    storage_host = str(config.get('ots.server.allocator', 'storage_host'))
    if not storage_host:
        storage_host = gethostname()
    storage_port = str(config.get('ots.server.allocator', 'storage_port'))  
    return "%s:%s"%(storage_host, storage_port)     



#####################
# PUBLIC METHOD
#####################

def primed_taskrunner(testrun_uuid, timeout, priority, device,
                      image, hw_packages, host_packages,
                      emmc, testfilter, flasher, publishers): 
    """
    Get a Taskrunner loaded with Tasks and ready to Run

    @type testrun_uuid: C{str}
    @param testrun_uuid: The unique identifier for the testrun

    @type timeout: C{int}
    @param timeout: The timeout in minutes

    @type: C{dict}
    @param: A dictionary of device properties this testrun requires
       
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

    @type publishers: # FIXME
    @param publishers: #FIXME 

    rtype: L{Taskrunner}
    rparam: A loaded Taskrunner 
    """

    is_package_distributed = False
    if priority == 1:
        is_package_distributed = True

    taskrunner = taskrunner_factory(device, timeout, testrun_uuid)
    cmds = get_commands(is_package_distributed, image, hw_packages,
                        host_packages, emmc, testrun_uuid, _storage_address(),
                        testfilter, flasher)
    for cmd in cmds:
        taskrunner.add_task(cmd)
    return taskrunner
