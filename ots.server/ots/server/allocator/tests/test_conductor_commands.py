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
from ots.server.allocator.conductor_commands import ConductorCommands

class TestConductorCommands(unittest.TestCase):

    def test_command(self):
        c = ConductorCommands("image_url", "emmc", 111, "storage_address",
                              "testfilter", "flasher", "timeout")
        command = c._command("testpackages")
        expected = ['--flasherurl', 'flasher',
                    '-t', 'testpackages',
                    '-u', 'image_url',
                    '-m', 'timeout',
                    '-e', 'emmc',
                    '-f', 'testfilter',
                    '-c', 'storage_address',
                    '-i', 111]
        self.assertEquals(expected, command)

    def test_single(self):
        c = ConductorCommands("image_url", "emmc", "testrun_uuid",
                            "storage_address", "testfilter", "flasher",
                            "timeout")
        expected =[
            ['conductor',
             '--flasherurl', 'flasher', '-t', 'foo,bar', '-u', 'image_url',
             '-m', 'timeout', '-e', 'emmc', '-f', 'testfilter',
             '-c', 'storage_address', '-i', 'testrun_uuid',
             ';',
             '--flasherurl', 'flasher', '-t', 'baz', '-u', 'image_url',
             '-m', 'timeout', '-e', 'emmc', '-f', 'testfilter',
             '-c', 'storage_address', '-i', 'testrun_uuid', '-o']]
        command = c.single(["foo", "bar"], ["baz"])
        self.assertEquals(expected, command)
        
    def test_multiple(self):
        c = ConductorCommands("image_url", "emmc", "testrun_uuid",
                            "storage_address", "testfilter", "flasher",
                            "timeout")

        commands = c.multiple(["foo", "bar"], ["baz"])
        expected = [
                    ['conductor', '--flasherurl', 'flasher', '-t', 'foo',
                     '-u', 'image_url', '-m', 'timeout', '-e', 'emmc',
                     '-f', 'testfilter', '-c', 'storage_address',
                     '-i', 'testrun_uuid'],
                    ['conductor', '--flasherurl', 'flasher', '-t', 'bar',
                     '-u', 'image_url', '-m', 'timeout', '-e', 'emmc',
                     '-f', 'testfilter', '-c', 'storage_address',
                     '-i', 'testrun_uuid'],
                    ['conductor', '--flasherurl', 'flasher', '-t', 'baz',
                     '-u', 'image_url', '-m', 'timeout', '-e', 'emmc',
                     '-f', 'testfilter', '-c', 'storage_address',
                     '-i', 'testrun_uuid', '-o']]
        self.assertEquals(expected, commands) 

    def test_multiple_no_pkgs(self):
        c = ConductorCommands("image_url", "emmc", "testrun_uuid",
                            "storage_address", "testfilter", "flasher",
                            "timeout")
        self.assertRaises(ValueError, c.multiple, [], [])
        
if __name__ == "__main__":
    unittest.main()
