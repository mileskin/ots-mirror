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
Generates Conductor commands for use with CL
"""

import warnings

warnings.warn("Conductor will have a Python API", 
              DeprecationWarning)

#######################################
# Dict mapping  Option Name -> CL opt
#######################################

COMMAND_DICT = {"image_url" : "-u",
                "emmc" : "-e",
                "testrun_uuid" : "-i",
                "storage_address" : "-c",
                "testfilter" : "-f",
                "flasher" : "--flasherurl",
                "testpackages" : "-t",
                "timeout" : "-m"}

#######################################
# Conductor Commands
#######################################

class ConductorCommands(object):
    """
    Generates CLs for the Conductor 
    from Options
    """

    def __init__(self, image_url, emmc, testrun_uuid,
                       storage_address, testfilter, flasher, timeout):
        """
        @type image_url: C{str}
        @param image_url: The URL of the image

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

        @type timeout: FIXME
        """
        self.image_url = image_url 
        self.emmc = emmc
        self.testrun_uuid = testrun_uuid
        self.storage_address = storage_address
        self.testfilter = testfilter 
        self.flasher = flasher
        self.timeout = timeout

    def _get_param(self, param_name, testpackages):
        """
        FIXME
        """
        ret_val = None
        if param_name == "testpackages":
            if testpackages != '':
                ret_val= testpackages
        else:
            param = getattr(self, param_name)
            if param != '' and param != '""':
                ret_val = param
        return ret_val
                
    
    def _command(self, testpackages):
        """
        Create a Conductor CL

        @type testpackages : C{str}
        @param testpackages: The testpackages

        @rtype: C{str}
        @rparam: A Conductor command
        """
        ret_val = []
        for param_name, opt in COMMAND_DICT.items():
            param = self._get_param(param_name, testpackages)
            if param is not None:
                ret_val.append(opt)
                ret_val.append(param)
        return ret_val

    def single(self, hw_packages, host_packages):
        """
        Create a single nested Conductor command
        i.e. One CL for all Testpackages
 
        @type hw_packages : C{list} of C{str}
        @param hw_packages: The hardware packages

        @type host_packages : C{list} of C{str}
        @param host_packages: The host packages

        @rtype: A C{list} of C{str} 
        @rparam: Conductor commands
        """
        testpackages =  ",".join(hw_packages)
        command =  ["conductor"] 
        command.extend(self._command(testpackages))
        if host_packages:
            command.append(';')
            testpackages =  ",".join(host_packages)
            cmd = self._command(testpackages)
            cmd.append('-o')
            command.extend(cmd)
        return [command]

    def multiple(self, hw_packages, host_packages):
        """
        Creates a Conductor command for each Testpackage
 
        @type hw_packages : C{list} of C{str}
        @param hw_packages: The hardware packages

        @type host_packages : C{list} of C{str}
        @param host_packages: The host packages

        @rtype: A C{list} of C{str} 
        @rparam: Conductor commands
        """
        commands = []
        if not (hw_packages + host_packages):
            raise ValueError("No hardware or host packages defined")
        for testpackages in hw_packages:
            cmd = ["conductor"]
            cmd.extend(self._command(testpackages))
            commands.append(cmd)
        for testpackages in host_packages:
            cmd = ["conductor"]
            cmd.extend(self._command(testpackages))
            cmd.append('-o')
            commands.append(cmd)
        return commands

##################################
# GET COMMANDS
##################################

def get_commands(is_package_distributed,
                 image_url, 
                 hw_packages,
                 host_packages,
                 emmc, 
                 testrun_uuid, 
                 storage_address, 
                 testfilter,
                 flasher,
                 timeout):
    """
    Returns a list of conductor commands
    
    @type image_url: C{str}
    @param image_url: The URL of the image
        
    @type is_package_distributed : C{bool}
    @param is_package_distributed : Is the test distributed 
                                         on a perpackage basis?

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

    @type timeout : FIXME

    @rtype: A C{list} of C{str} 
    @rtype: Conductor commands
    """
   
    commands = ConductorCommands(image_url, emmc, testrun_uuid,
                                 storage_address, testfilter, 
                                 flasher, timeout)
    if is_package_distributed:
        return commands.multiple(hw_packages, host_packages)
    else:
        return commands.single(hw_packages, host_packages)
  
