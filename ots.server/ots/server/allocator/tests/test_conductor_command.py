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

"""Tests for ConductorEngine"""

import unittest

from ots.server.allocator.conductor_command import conductor_command

class TestConductorCommands(unittest.TestCase):

    def test_conductor_command_without_testpackages(self):
        options = {'bootmode': None, 'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30"}
        expected = ['conductor',  
                    "-u", 'www.nokia.com', '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options,
                                   host_testing = False)
        self.assertEquals(expected, result) 


    def test_conductor_command_with_emmc_flash(self):
        options = {'bootmode': None, 'image_url':"www.nokia.com", 'emmc_flash_parameter':"Gordon", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30" }
        expected = ['conductor',  
                    '-u', 'www.nokia.com', '-e', 'Gordon', 
                    '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)
        self.assertEquals(expected, result)

    def test_conductor_command_with_flasher_no_pkgs(self):

        options = {'bootmode': None, 'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"", 
                   'timeout':"30" }
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_device_pkgs(self):

        options = {'bootmode': None, 'image_url':"www.nokia.com", 'emmc_flash_parameter':"", 
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
                                   host_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_reboot_mode(self):

        options = {'image_url':"www.nokia.com", 'emmc_flash_parameter':"",
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30", 'bootmode':"normal", 'coverage_symbol_file_locations':""}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30', '-b', 'normal']

        result = conductor_command(options,
                                   host_testing = False)
        self.assertEquals(result, expected)


if __name__ == "__main__":
    unittest.main()
