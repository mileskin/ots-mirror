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

from ots.server.monitor.hub_monitor import HubMonitor

class TestHubMonitor(unittest.TestCase):

    def test_monitors_iter(self):
        hub_monitor = HubMonitor("foo", "bar", "baz")
        #Make some monitors... for test purposes use the HubMonitor
        test_monitor_1 = HubMonitor("1", "1", "1")
        test_monitor_2 = HubMonitor("2", "2", "2")
        hub_monitor.add_monitor(test_monitor_1)
        hub_monitor.add_monitor(test_monitor_2)
        self.assertEquals(2, len(list(hub_monitor.monitors_iter())))
        self.assertEquals(2, 
                   len(list(hub_monitor.monitors_iter("ots.server.monitor"))))
        self.assertEquals(0, 
                   len(list(hub_monitor.monitors_iter("ots.server.hub"))))

if __name__ == "__main__":
    unittest.main()