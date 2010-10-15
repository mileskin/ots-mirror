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

#WIP Refactoring 0.1....

"""
Generates Conductor commands for use with CL
"""

import warnings

warnings.warn("Conductor will have a Python API", 
              DeprecationWarning)

COMMAND_DICT = {"image_url" : "-u",
                "emmc" : "-e",
                "testrun_id" : "-i",
                "storage_address" : "-c",
                "testfilter" : "-f",
                "flasher" : "--flasherurl",
                "testpackages" : "-t"}

def _conductor_command(image_url,
                       emmc_flash_parameter,
                       testrun_id,
                       storage_address,
                       test_filter,
                       flasher,
                       testpackages):
    ret_val = []
    params = locals()
    for param_name, opt in COMMAND_DICT.items():
        ret_val.append(opt)
        ret_val.append(params[param_name])
    return ret_val

def _perpackage_distribution_cmds(image_url, 
                                  hw_packages,
                                  host_packages,
                                  emmc, 
                                  testrun_uuid, 
                                  storage_address, 
                                  testfilter,
                                  flasher):
    """
    One Conductor command per Testpackage
    """

    commands = []
    if not (hw_packages + host_packages):
        raise ValueError("No hardware or host packages defined")
    for testpackages in hw_packages + host_packages:
        cmd = _conductor_command(image_url,
                                 emmc_flash_parameter,
                                 testrun_id,
                                 storage_address,
                                 test_filter,
                                 flasher,
                                 testpackages)
        commands.append(cmd)
    if host_packages:
        commands.append('-o')
    return commands


def _single_distribution_cmds(image_url, 
                              hw_packages,
                              host_packages,
                              emmc, 
                              testrun_uuid, 
                              storage_address, 
                              testfilter,
                              flasher):
    """
    Creates One Command for all Testpackages
    """  
    testpackages =  ",".join(hw_packages)
    commmand = _conductor_command(image_url,
                                  emmc_flash_parameter,
                                  testrun_id,
                                  storage_address,
                                  test_filter,
                                  flasher,
                                  testpackages)
    

    if host_packages:
        command.append(';')
        testpackages =  ",".join(host_packages)
        cmd = _conductor_command(image_url,
                                 emmc_flash_parameter,
                                 testrun_id,
                                 storage_address,
                                 test_filter,
                                 flasher,
                                 testpackages)
    
        command.extend(cmd)
        command.append('-o')
    return [command]


##################################
# Public
##################################

def get_commands(is_package_distributed,
                 image_url, 
                 hw_packages,
                 host_packages,
                 emmc, 
                 testrun_uuid, 
                 storage_address, 
                 testfilter,
                 flasher):
    """
    Returns a list of conductor commands
    """
    if is_package_distributed:
        cmds = _perpackage_distribution_cmds(test_list, options)
    else:
        cmds = _single_distribution_cmds(test_list, options)
    return cmds
