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

import unittest
import time

from ots.server.distributor.timeout import Timeout
from ots.server.distributor.exceptions import OtsExecutionTimeoutError
from ots.server.distributor.exceptions import OtsQueueTimeoutError



class TestTimeout(unittest.TestCase):

    def test_queue_timeout_raised(self):
        def run(): # A dummy timeouting function
            time.sleep(3)
        queue_timeout = 1
        execution_timeout = 1
        controller_timeout = 1
        timeout = Timeout(execution_timeout, 
                          queue_timeout, 
                          controller_timeout)
        timeout.start_queue_timeout()
        self.assertRaises(OtsQueueTimeoutError, run)

    def test_queue_timeout_not_raised(self):
        self.done = False
        def run(): # A dummy not timeouting function
            self.done = True
        queue_timeout = 1
        execution_timeout = 1
        controller_timeout = 1
        timeout = Timeout(execution_timeout, 
                          queue_timeout, 
                          controller_timeout)
        timeout.start_queue_timeout()
        run()
        self.assertTrue(self.done)

    def test_global_timeout_raised(self):
        def run(): # A dummy timeouting function
            time.sleep(3)
        queue_timeout = 1
        controller_timeout = 1
        execution_timeout = 1
        timeout = Timeout(execution_timeout, 
                          queue_timeout, 
                          controller_timeout)
        timeout.start_queue_timeout()
        timeout.task_started()
        self.assertRaises(OtsExecutionTimeoutError, run)

    def test_stop(self):
        self.done = False
        def run(): # A dummy timeouting function
            time.sleep(2)
            self.done = True

        queue_timeout = 1
        controller_timeout = 1
        execution_timeout = 1
        timeout = Timeout(execution_timeout, 
                          queue_timeout, 
                          controller_timeout)
        timeout.start_queue_timeout()
        timeout.stop()
        run()
        self.assertTrue(self.done)


if __name__ == "__main__":
    unittest.main()
