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

"""Unit tests for ots.worker.command"""

import unittest
import time
from ots.worker import command
import os
import subprocess

DUMMY_TIMEOUT_VALUE = 100
TIMEOUT = 10
RETRIES = 10

class TestCommand(unittest.TestCase):
    """Unittest for Command class"""
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_str(self):
        cmd_object = command.Command("echo x")
        self.assertTrue(str(cmd_object))

    def testWrappedCommand(self):
        wrapper = 'wrapper "%s"'
        cmd = "command"
        cmd_object = command.Command(cmd, wrapper=wrapper)
        expected = 'wrapper "command"'
        self.assertEquals(cmd_object.command, expected)

    def testWrappedCommandWithEmptyWrapper(self):
        wrapper = ""
        cmd = "command"
        cmd_object = command.Command(cmd, wrapper=wrapper)
        expected = 'command'
        self.assertEquals(cmd_object.command, expected)
        
    def testAlreadyExecuted(self):
        cmd = command.Command("",DUMMY_TIMEOUT_VALUE)
        self.assertFalse(cmd.already_executed())
        cmd.execute()
        self.assertTrue(cmd.already_executed())
        
    def testGetStdout(self):
        cmd = command.Command("echo jee",DUMMY_TIMEOUT_VALUE)
        cmd.execute()
        self.assertEquals(cmd.stdout, "jee\n")

    def testGetStderr(self):
        cmd = command.Command("echo jee >&2",DUMMY_TIMEOUT_VALUE)
        cmd.execute()
        self.assertEquals(cmd.stderr, "jee\n")

    def testGetExecutionTime(self):
        cmd = command.Command("sleep 0.5")
        cmd.execute()
        self.assertAlmostEquals(cmd.execution_time, 0.5, 1)

    def testGetReturnValue(self):
        cmd = command.Command("echo 0",DUMMY_TIMEOUT_VALUE)
        self.assertEquals(cmd.return_value, None)
        cmd.execute()
        self.assertEquals(cmd.return_value, 0)
        
    def testSoftTimeout(self):
        cmd = command.Command("sleep 5", 0.5)
        self.failUnlessRaises(command.SoftTimeoutException, cmd.execute)
        
    def testHardTimeout(self):
        cmd = command.Command("sleep 5", 100, 0.5)
        self.failUnlessRaises(command.HardTimeoutException, cmd.execute)
        
    def testTimeoutingSubSubProcesses(self):
        cmd = command.Command('echo "sleep 3;exit 5"|bash', 0.1, 1000)

        # There should be a timeout
        self.failUnlessRaises(command.SoftTimeoutException, cmd.execute)

        # If command is killed properly it should not return 5:
        self.assertNotEquals(cmd.return_value, 5)

        # If sub process was killed properly, execution time should be much
        # less than 3 seconds.
        self.assert_(cmd.execution_time < 2.5 )

        
    def testExecuteWithRetriesFailingCommand(self):
        cmd = command.Command("echo jee")
        self.failUnlessRaises(command.FailedAfterRetries,
                              cmd.execute_with_retries, 5, 5)
    
    def testExecuteWithRetriesTimeoutingCommand(self):
        cmd = command.Command("sleep 5", 0.2)
        self.failUnlessRaises(command.FailedAfterRetries,
                              cmd.execute_with_retries, 5, 5)

    def testExecuteWithRetriesSuccessfulCommand(self):
        cmd = command.Command("echo jee")
        self.assertAlmostEquals(cmd.execute_with_retries(5, 0), 1)



if __name__ == '__main__':
    unittest.main()
    
    
