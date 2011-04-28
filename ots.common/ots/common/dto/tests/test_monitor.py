# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

from ots.common.dto.monitor import Monitor, MonitorType
import datetime
import time

class TestTestPackages(unittest.TestCase):
    
    def test_init(self):
        created = time.time()
        monitor = Monitor(MonitorType.UNKNOWN, "unittests", "description")
        self.assertEquals(monitor.type, MonitorType.UNKNOWN )
        self.assertEquals(monitor.sender, "unittests" )
        self.assertEquals(monitor.description, "description" )
        self.assertTrue(monitor.emitted >= created)
    
    def test_setters(self):
        monitor = Monitor(MonitorType.UNKNOWN, "unittests", "description")
        monitor.sender = "unittests2"
        monitor.description = "description2"
        self.assertEquals(monitor.sender, "unittests2" )
        self.assertEquals(monitor.description, "description2" )
        
    def test_received(self):
        received = time.time() + 10
        monitor = Monitor(MonitorType.UNKNOWN, "unittests", "description")
        monitor.set_received(received)
        self.assertTrue(monitor.received == received)
        self.assertTrue(monitor.received != monitor.emitted)
           

if __name__ == "__main__":
    unittest.main()
