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
A module for generating conductor commands based on testrun options
"""


def _conductor_command(options, host_testing):
    """
    Creates a conductor command from the arguments. 

    options[test_packages]: String with test package names. Multiple 
                            packages must be separated by comma, without 
                            spaces. String may be empty.
                            Packages are either for device or for host. 

    host_testing: Whether options[test_packages] is assumed to contain 
                  tests for host. True or False.

    Returns: 
        cmd: A list. First item is shell executable. 
             The rest of the items are command line parameters.
    """
    # The old cmd line command is used for backward compatibility
    # TODO: Change 'kickstart' to 'conductor'
    cmd = ["/usr/bin/kickstart"]
    cmd.extend( ["-u", options['image_url']] )
    if options['emmc_flash_parameter']:
        cmd.extend( ["-e", options['emmc_flash_parameter']] )
    if options['testrun_id']:
        cmd.extend( ["-i", str(options['testrun_id'])] )
    if options['storage_address']:
        cmd.extend( ["-c", options['storage_address']] )
    if options['testfilter']:
        cmd.extend( ["-f", options['testfilter']] )
    if options['flasherurl']:
        cmd.extend( ["--flasherurl", options['flasherurl']] )
    if options['test_packages']:
        cmd.extend( ["-t", options['test_packages']] )
    if options['testrun_timeout']:
        cmd.extend( ["-e", options['testrun_timeout']] )

    if host_testing == True:
        cmd.extend( ['-o'] )

    return cmd


def _perpackage_distribution_cmds(test_list, options):
    """Creates a separate task (conductor command) for each test package"""

    commands = []

    if not test_list:
        raise ValueError("test_list not defined for distribution model")

    if 'device' in test_list:
        for test_package in test_list['device'].split(","):
            options['test_packages'] = test_package
            cmd = _conductor_command(options, host_testing = False)
            commands.append(cmd)

    if 'host' in test_list:
        for test_package in test_list['host'].split(","):
            options['test_packages'] = test_package
            cmd = _conductor_command(options, host_testing = True)
            commands.append(cmd)

    return commands


def _default_distribution_cmds(test_list, options):
    """Creates one task (one command line) for all test packages"""

    single_cmd = []

    if not test_list:
        options['test_packages'] = ""
        cmd = _conductor_command(options, host_testing = False)
        single_cmd.extend(cmd)

    if 'device' in test_list:
        options['test_packages'] = test_list['device']
        cmd = _conductor_command(options, host_testing = False)
        single_cmd.extend(cmd)

    if 'host' in test_list:
        options['test_packages'] = test_list['host']
        cmd = _conductor_command(options, host_testing = True)
        # If there are device tests, have a ; to do them both.
        # Note: This means they're run under one timeout, in one shell.
        #       Coming improvements in task distribution could soon
        #       facilitate in improving this too.
        if single_cmd:
            single_cmd.append(';')
        single_cmd.extend(cmd)

    return [single_cmd]


##################################
# Public
##################################


def get_commands(distribution_model,
                 image_url, 
                 test_list, 
                 emmc_flash_parameter, 
                 testrun_id, 
                 storage_address, 
                 test_filter,
                 testrun_timeout,
                 flasher=""):
    """Returns a list of conductor commands based on the options"""

    options = dict()
    options['image_url'] = image_url
    options['emmc_flash_parameter'] = emmc_flash_parameter
    options['testrun_id'] = testrun_id
    options['storage_address'] = storage_address
    options['testfilter'] = test_filter
    options['testrun_timeout'] = testrun_timeout
    options['flasherurl'] = flasher

    cmds = []
    if distribution_model == "perpackage":
        cmds = _perpackage_distribution_cmds(test_list,
                                              options)
    else:
        cmds = _default_distribution_cmds(test_list,
                                          options)
    return cmds
