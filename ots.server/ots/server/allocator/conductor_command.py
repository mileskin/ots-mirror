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


def conductor_command(options, host_testing):
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
    cmd = ["conductor"]
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
    # Use global timeout as conductor testrun timeout
    if options['timeout']:
        cmd.extend( ["-m", str(options['timeout'])] )

    if host_testing == True:
        cmd.extend( ['-o'] )

    return cmd


def get_commands(distribution_model,
                  image_url,
                  test_list,
                  emmc_flash_parameter,
                  testrun_id,
                  storage_address,
                  test_filter,
                  timeout,
                  flasher="",
                  custom_distribution_models = []):
    """Returns a list of conductor commands based on the options"""

    options = dict()
    options['image_url'] = image_url
    options['emmc_flash_parameter'] = emmc_flash_parameter
    options['testrun_id'] = testrun_id
    options['storage_address'] = storage_address
    options['testfilter'] = test_filter
    options['flasherurl'] = flasher
    options['timeout'] = str(timeout)

    cmds = []

    # Try custom distribution models first                                                                              
    for dist in custom_distribution_models:
        if distribution_model == dist[0]:
            return(dist[1](test_list, options))


    # Or use defaults                                                                                                   
    if distribution_model == "perpackage":
        cmds = perpackage_distribution(test_list,
                                       options)
    else: # Default to single task distribution if nothing else matches                                                 
        cmds = single_task_distribution(test_list,
                                        options)
    return cmds
