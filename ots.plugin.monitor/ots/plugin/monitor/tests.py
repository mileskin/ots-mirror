# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Ville Ilvonen <ville.p.ilvonen@nokia.com>
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

from ots.plugin.monitor.monitor_plugin import MonitorPlugin
from ots.plugin.monitor.models import Testrun, Event
from ots.common.dto.monitor import Monitor, MonitorType


class TestMonitorPlugin(unittest.TestCase):
    """
    Unit tests for monitor plugin
    """
    def testInit(self):
        kwargs = {'notify_list': ['elias.luttinen@digia.com'],
                  'emmc': '',
                  'email_attachments': 'off',
                  'distribution_model': 'default',
                  'timeout': '60',
                  'device': {'devicegroup': 'examplegroup'},
                  'packages': 'test-definition-tests',
                  'email': 'on'}
        
        kwargs_str = "{'notify_list': ['elias.luttinen@digia.com'], " \
        "'emmc': '', 'email_attachments': 'off', 'distribution_model': " \
        "'default', 'timeout': '60', 'device': {'devicegroup': " \
        "'examplegroup'}, 'packages': 'test-definition-tests', 'email': 'on'}"

        mp = MonitorPlugin("request_id",
                           "testrun_uuid",
                           "sw_product",
                           "image",
                           **kwargs)

        tr = Testrun.objects.filter(request_id="request_id")

        self.assertTrue(tr.values()[0].get('testrun_id') == 'testrun_uuid')
        self.assertTrue(tr.values()[0].get('device_group') == 'examplegroup')
        self.assertTrue(str(tr.values()[0].get('configuration')) == kwargs_str)
        self.assertTrue(tr.values()[0].get('host_worker_instances') == '')
        self.assertTrue(tr.values()[0].get('requestor') == 'elias.luttinen@digia.com')
        self.assertTrue(tr.values()[0].get('request_id') == 'request_id')

    def test_set_monitors(self):
        pass

if __name__ == "__main__":
    unittest.main()
