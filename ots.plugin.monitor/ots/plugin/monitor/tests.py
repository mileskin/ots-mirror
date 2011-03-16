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

from datetime import datetime, timedelta

from django.test import TestCase

from ots.common.dto.monitor import Monitor, MonitorType
from ots.plugin.monitor.monitor_plugin import MonitorPlugin
from ots.plugin.monitor.models import Testrun, Event
from ots.plugin.monitor.views import get_timedeltas
from ots.plugin.monitor.event_timedeltas import EventTimeDeltas, event_sequence
from ots.common.dto.monitor import Monitor, MonitorType

def _create_monitor_plugin(request_id):
    """
    Create monitor plugin instance
    """
    kwargs = {'notify_list': ['ots@localhost'],
              'emmc': '',
              'email_attachments': 'off',
              'distribution_model': 'default',
              'timeout': '60',
              'device': {'devicegroup': 'examplegroup'},
              'packages': 'test-definition-tests',
              'email': 'on'}

    return MonitorPlugin(request_id,
                         "testrun_uuid",
                         "sw_product",
                         "image",
                         **kwargs)


class TestMonitorPlugin(unittest.TestCase):
    """
    Unit tests for monitor plugin
    """
    _kwargs_str = "{'notify_list': ['ots@localhost'], " \
        "'emmc': '', 'email_attachments': 'off', 'distribution_model': " \
        "'default', 'timeout': '60', 'device': {'devicegroup': " \
        "'examplegroup'}, 'packages': 'test-definition-tests', 'email': 'on'}"

    def test_init(self):
        request_id = 'test_init'
        _create_monitor_plugin(request_id)
        tr = Testrun.objects.filter(request_id=request_id)

        self.assertTrue(tr.values()[0].get('testrun_id') == 'testrun_uuid')
        self.assertTrue(tr.values()[0].get('device_group') == 'examplegroup')
        self.assertTrue(str(tr.values()[0].get('configuration')) == self._kwargs_str)
        self.assertTrue(tr.values()[0].get('host_worker_instances') == '')
        self.assertTrue(tr.values()[0].get('requestor') == 'ots@localhost')
        self.assertTrue(tr.values()[0].get('request_id') == request_id)

    def test_add_monitor_event_ongoing(self):
        """
        Test add_monitor_event when event name is TASK_ONGOING
        """
        request_id = 'test_add_monitor_event_ongoing'
        mp = _create_monitor_plugin(request_id)
        monitor = Monitor(MonitorType.TASK_ONGOING,
                          "sender",
                          "description")
        mp.add_monitor_event(monitor)
        event = Event.objects.values()

        tr = Testrun.objects.filter(request_id=request_id)
        self.assertTrue(event.values()[len(event)-1].get('testrun_id_id') \
                            == tr.values()[0].get('id'))
        self.assertTrue(event.values()[len(event)-1].get('event_name') \
                            == MonitorType.TASK_ONGOING)
        self.assertTrue(tr.values()[len(tr)-1].get('state') == '1')

    def test_add_monitor_event_inqueue(self):
        """
        Test add_monitor_event when event name is TASK_INQUEUE
        """
        request_id = 'test_add_monitor_event_inqueue'
        mp = _create_monitor_plugin(request_id)
        monitor = Monitor(MonitorType.TASK_INQUEUE,
                          "sender",
                          "description")
        mp.add_monitor_event(monitor)
        event = Event.objects.values()

        tr = Testrun.objects.filter(request_id=request_id)
        self.assertTrue(event.values()[len(event)-1].get('testrun_id_id') \
                            == tr.values()[0].get('id'))
        self.assertTrue(event.values()[len(event)-1].get('event_name') \
                            == MonitorType.TASK_INQUEUE)
        self.assertTrue(tr.values()[len(tr)-1].get('state') == '0')


class TestEventSequence(unittest.TestCase):

    def test_event_sequence(self):
        expected = ['Testrun requested', 'Task in queue', 
                    'Task is ongoing', 'Device flashing', 
                    'Device booting', 'Test execution', 
                    'Test package ended']
        self.assertEquals(expected, event_sequence())

class TestEventTimeDeltas(TestCase):

    fixtures = ['time_deltas_fixtures.json']

    def test_get_events(self):
        ev_dt = EventTimeDeltas()
        expected = 100*2 + 100*7 + 100*6
        self.assertEquals(expected, len(ev_dt._events))
        ev_dt = EventTimeDeltas("complete_run")
        self.assertEquals(100*7, len(ev_dt._events))
        
    def test_get_events_query_sets(self):
        ev_dt = EventTimeDeltas()
        self.assertEquals(7, len(ev_dt._events_query_sets))
    
    def test_testrun_ids(self):
        ev_dt = EventTimeDeltas()
        self.assertEquals([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                          ev_dt._testrun_ids(0, 10, 1))
        self.assertEquals([9, 7, 5, 3, 1],
                          ev_dt._testrun_ids(0, 10, -2))
        expected = [i for i in range(300)]
        self.assertEquals(expected, ev_dt._testrun_ids(None, None, None))

    def test_get_event_times(self):
        ev_dt = EventTimeDeltas()
        expected = "2011-02-01 00:01"
        self.assertEquals(expected,
              ev_dt._get_event_times(0, 0)[0].strftime("%Y-%m-%d %H:%M"))

    def test_event_dts(self):
        ev_dt = EventTimeDeltas()
        t = datetime.strptime("2011-02-01","%Y-%m-%d")
        t1s = [t + timedelta(minutes = i*i) for i in range(5)]
        t2s = [t1s[-1] + timedelta(minutes = (i+1)*(i+1)) for i in range(5)]
        self.assertEquals([60, 180, 300, 420, 540],
                          ev_dt._event_dts(t1s, t2s))
        self.assertEquals([], ev_dt._event_dts([], t1s))
        self.assertEquals([], ev_dt._event_dts(t1s, []))
  
    def test_deltas_iter(self):
        ev_dt = EventTimeDeltas()
        dts = list(ev_dt.deltas_iter(0,10,1))
        self.assertEquals(10, len(dts))
        expected = (0, [[120], [240], [360], [480], [600], [720]])
        self.assertEquals(expected, dts[0])
        ev_dt = EventTimeDeltas("faulty_flasher")
        dts = list(ev_dt.deltas_iter(0,4,2))
        self.assertEquals(2, len(dts))
        expected = (7, [[120], [240], [360, 480, 600], [], [], []])
        self.assertEquals(expected, dts[1])

class TestJSONRPC_API(TestCase):
    
    fixtures = ['time_deltas_fixtures.json']

    def test_dts_iter(self):
       
        dts = get_timedeltas(None, 0, 10, 1, None)
        self.assertEquals(10, len(dts))
        expected = (0, [[120], [240], [360], [480], [600], [720]])
        self.assertEquals(expected, dts[0])
       

if __name__ == "__main__":
    unittest.main()
