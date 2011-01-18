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
example custom distribution model
"""

from ots.server.allocator.conductor_command import conductor_command

def custom_model(test_list, options):
    """
    Implement your distribution model here. Examples can be found in
    ots.server.allocator.default_distribution_models
    """

    commands = []

    if not test_list:
        raise ValueError("test_list not defined for distribution model")

    if 'device' in test_list:
        for test_package in test_list['device'].split(","):
            options['test_packages'] = test_package
            cmd = conductor_command(options, host_testing = False)
            commands.append(cmd)

    if 'host' in test_list:
        for test_package in test_list['host'].split(","):
            options['test_packages'] = test_package
            cmd = conductor_command(options, host_testing = True)
            commands.append(cmd)
    return commands

def get_model(options):
    """This is the factory method.

    @type options: L{Options}
    @param options: The package name

    @rtype: C{callable}
    @return: A callable 

    """
    
    return custom_model
