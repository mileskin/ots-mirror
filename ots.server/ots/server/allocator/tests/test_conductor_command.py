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
        options = {'image_url':"www.nokia.com", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30",
                   'use_libssh2': False, 'resume': False}
        expected = ['conductor',  
                    "-u", 'www.nokia.com', '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options,
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(expected, result) 


    def test_conductor_command_with_flasher_content_parameter(self):
        options = {'image_url':"www.nokia.com", 'flasher_options':{'content_parameter':"Gordon"}, 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"", 'test_packages':"", 'timeout':"30",
                   'use_libssh2': False, 'resume': False}
        expected = ['conductor',  
                    '-u', 'www.nokia.com', '-e', 'Gordon', 
                    '-i', '1', '-c', 'foo', '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(expected, result)

    def test_conductor_command_with_flasher_no_pkgs(self):
        options = {'image_url':"www.nokia.com", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"", 
                   'timeout':"30", 'use_libssh2': False, 'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_device_pkgs(self):
        options = {'image_url':"www.nokia.com", 
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"", 
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30", 'use_libssh2': False, 'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30']

        result = conductor_command(options, 
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_bootmode_set(self):
        options = {'image_url':"www.nokia.com", 'flasher_options':{'bootmode':"normal"},
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30", 'use_libssh2': False,
                   'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30', '--flasher_options=bootmode:normal', 'normal']

        result = conductor_command(options,
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_flasher_bootmode_and_content_parameter_set(self):
        options = {'image_url':"www.nokia.com", 
                   'flasher_options':{'content_parameter':"Gordon", 'bootmode':"normal"},
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf", 'test_packages':"my-tests",
                   'timeout':"30", 'use_libssh2': False,
                   'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    "-t", "my-tests", '-m', '30', 
                    '--flasher_options=content_parameter:Gordon,bootmode:normal', 'normal']

        result = conductor_command(options,
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_testplan(self):
        options = {'image_url':"www.nokia.com",
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf", 'testplan_name' : "testplan.xml",
                   'timeout':"30", 'test_packages':'', 'use_libssh2': False,
                   'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    '-m', '30', '-p', 'testplan.xml']

        result = conductor_command(options,
                                   host_testing = False,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_testplan_host(self):
        options = {'image_url':"www.nokia.com",
                   'testrun_id':1, 'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf", 'testplan_name' : "testplan.xml",
                   'timeout':"30", 'test_packages':'', 'use_libssh2': False,
                   'resume': False}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    '-m', '30', '-p', 'testplan.xml', '-o']

        result = conductor_command(options,
                                   host_testing = True,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_libssh2(self):
        options = {'image_url':"www.nokia.com", 'testrun_id':1,
                   'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf",
                   'use_libssh2': True, 'resume': False,
                   'timeout':"30", 'test_packages':''}
        expected = ['conductor',
                    "-u", 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    '-m', '30', '--libssh2', '-o']

        result = conductor_command(options,
                                   host_testing = True,
                                   chroot_testing = False)
        self.assertEquals(result, expected)

    def test_conductor_command_with_resume(self):
        options = {'image_url':"www.nokia.com", 'testrun_id':1,
                   'storage_address':"foo", 'testfilter':"",
                   'flasherurl':"asdfasdf/asdf",
                   'use_libssh2': False, 'resume': True,
                   'timeout':"30", 'test_packages':''}
        expected = ['conductor',
                    '-u', 'www.nokia.com',
                    '-i', '1',
                    '-c', 'foo',
                    '--flasherurl', "asdfasdf/asdf",
                    '-m', '30', '--resume', '-o']

        result = conductor_command(options,
                                   host_testing=True,
                                   chroot_testing=False)
        self.assertEquals(result, expected)

if __name__ == "__main__":
    unittest.main()
