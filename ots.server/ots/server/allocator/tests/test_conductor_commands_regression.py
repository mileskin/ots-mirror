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

import unittest
from ots.server.allocator.conductor_commands import ConductorCommands, get_commands
from ots.server.hub.options_factory import OptionsFactory
       
def conductor_command(options_dict, host_testing):
    """
    Adapts the 

    """
    image = options_dict["image_url"]
    options = OptionsFactory("pdt", options_dict)()
    #FIXME
    is_package_distributed = False
    storage_address = options_dict["storage_address"]
    return get_commands(is_package_distributed,
                        options.image, 
                        options.hw_packages,
                        options.host_packages,
                        options.emmc, 
                        '1',
                        storage_address, 
                        options.testfilter,
                        options.flasher,
                        options.timeout)

class TestConductorCommandsRegression(unittest.TestCase):

    def assert_commands_equal(self, cmd1, cmd2):
        self.assertEquals(cmd1[0], cmd2[0])
        def cmd_2_dict(cmd): 
            return dict(zip(cmd[0::2], cmd[1::2]))
        dict_1, dict_2 = cmd_2_dict(cmd1[1:]), cmd_2_dict(cmd2[1:])
        self.assertEquals(dict_1, dict_2)

    def test_conductor_command_without_testpackages(self):
        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30" }
        expected = ['conductor',  
                    "-u", 'www.nokia.com', '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options,
                                   host_testing = False)[0]
        self.assert_commands_equal(expected, result)

    def test_conductor_command_with_emmc_flash(self):
        options = {'image_url':"www.nokia.com", 
                   'emmc_flash_parameter':"Gordon", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30" }
        expected = ['conductor',  
                    '-u', 'www.nokia.com', '-e', 'Gordon', 
                    '-i', '1', '-c', 'foo', '-m', '30']
        result = conductor_command(options, 
                                   host_testing = False)[0]
        self.assert_commands_equal(expected, result)

    def test_conductor_command_with_flasher_no_pkgs(self):
        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"", 
                   'timeout':"30" }
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)[0]
        self.assert_commands_equal(expected, result)

    def test_conductor_command_with_flasher_device_pkgs(self):
        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30" }
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                   '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)[0]
        self.assert_commands_equal(expected, result)

if __name__ == "__main__":
    unittest.main()
