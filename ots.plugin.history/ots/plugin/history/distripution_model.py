# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Ville Ilvonen <ville.p.ilvonen@nokia.com>
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

from ots.server.allocator.conductor_command import conductor_command
from ots.plugin.history.models import Package, History
from schedule_algo import group_packages
import logging
import string

LOG = logging.getLogger(__name__)

def get_test_package_history(test_packages):
    """
    Returns dictionary of test packages and their latest execution
    time. If time not available, then it is none
    
    @type test_list: L{List}
    @param test_list: List of test packages
    
    @rtype: C{dict}
    @return: Dictionary of test package names and execution times  
    
    """
    
    history_list = dict()
    
    for package in test_packages:
        
        db_package = Package.objects.filter(package_name = package)
        duration = None
        
        if db_package.count() > 0:
            db_package = db_package[0]
            history = History.objects.filter(package_id = db_package.id).\
                        order_by("-start_time")[:1]
            duration = history[0].duration
        
        history_list[package] = duration
    
    return history_list
            

def history_model(test_list, options):
    """
    Test package distribution based on history.

    @type test_list: L{List}
    @param test_list: List of test packages

    @type options: L{Options}
    @param options: Testrun options in an ots.server.hub.options object
    
    @rtype: C{list}
    @return: List of conductor_commands 

    """

    commands = []
    
    if not test_list:
        raise ValueError("test_list not defined for distribution model")

    if 'device' in test_list:
        test_packages = test_list['device'].split(",")
        test_history = get_test_package_history(test_packages)
        
        package_groups = group_packages(test_history)
        
        for group in package_groups:
            options['test_packages'] = string.join(group, ",")
            LOG.debug(group)
            cmd = conductor_command(options, host_testing = False)
            LOG.debug(cmd)
            commands.append(cmd)

    return commands
    

def get_model(options):
    """This is the factory method.

    @type options: L{Options}
    @param options: Testrun options in an ots.server.hub.options object

    @rtype: C{callable}
    @return: A callable 

    """
    return history_model
