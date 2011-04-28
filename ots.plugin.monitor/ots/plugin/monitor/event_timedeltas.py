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

"""
Event Time Deltas
@newfield yield: Yield, Yields
"""
 
from ots.plugin.monitor.models import Event

from ots.common.dto.api import MonitorType

def event_sequence():
    """
    @rtype: C{list} of C{str}
    @return: The interesting Events in chrono order for the Testrun
    """
    return [MonitorType.TESTRUN_REQUESTED, MonitorType.TASK_INQUEUE, 
            MonitorType.TASK_ONGOING, MonitorType.DEVICE_FLASH, 
            MonitorType.DEVICE_BOOT, MonitorType.TEST_EXECUTION, 
            MonitorType.TEST_PACKAGE_ENDED]

###########################################
# EventTimeDeltas
##########################################


class EventTimeDeltas(object):
    """
    Queries the database through the ORM to 
    Get the time deltas for an Events Sequence 
    for a specified (or all) Device Group(s).
    
    e.g. 
    the call:
       >>> deltas_iter(1,4,1)
       might yield:
       "testrun_id1", [[1],[2],[3],[4],[5],[6]]  # For a Clean run
       "testrun_id2", [[1],[2],[3,3,3],[],[],[]] # Rptd iteration step 3
       "testrun_id3", [[1],[2],[],[],[],[]])]    # Stopped at step 2
       
    """

    def __init__(self, device_group = None):
        """
        @type device_group: C{str} or None
        @param device_group: The name of the device group
        """
        self._device_group = device_group 
        self._events_query_sets_cache = None
        self._events_cache = None
        self._all_testrun_ids = None

    ############################################
    # Private Methods
    ############################################

    def _get_events(self):
        """
        The events (filtered by device group if appropriate)
        @rtype: C{django.db.models.query.QuerySet}
        """
        if self._events_cache is None:
            if self._device_group is None:      
                self._events_cache = Event.objects.filter()
            else:
                self._events_cache = Event.objects.filter(
                    testrun_id__device_group__exact = self._device_group)
        return self._events_cache

    _events = property(_get_events) 

    def _get_events_query_sets(self):
        """
        The events for the event sequence
        @rtype:  C{list} of C{django.db.models.query.QuerySet}
        """
        if self._events_query_sets_cache is None:
            self._events_query_sets_cache = \
                     [self._events.filter(event_name = ev_name) 
                                      for ev_name in event_sequence()]
        return self._events_query_sets_cache

    _events_query_sets = property(_get_events_query_sets)

    def _get_all_testrun_ids(self):
        """
        All the testrun ids
        @rtype:  C{list} of C{str} 
        """
        if self._all_testrun_ids is None:
            self._all_testrun_ids = self._events.values_list('testrun_id', 
                                              flat=True).distinct()
        return self._all_testrun_ids

    all_testrun_ids = property(_get_all_testrun_ids)
                
    def _testrun_ids(self, start, stop, step):
        """
        @type start: C{int} or None
        @param start: The start index of the iteration

        @type stop: C{int} or None
        @param stop: The stop index of the iteration

        @type step: C{int} or None
        @param step: The step of the iteration
        
        @rtype:  C{list} of C{str}
        @return: A list of testrun_ids that correspond to the event sequence
        """
        
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.all_testrun_ids)
        if step is None:
            step = 1
            
        return self.all_testrun_ids[start:stop][::step]

    def _get_event_times(self, testrun_id, idx):
        """
        @type testrun_id: C{str}
        @param testrun_id: The testrun id

        @type idx: C{int}
        @param idx: The index into the `_events_query_set`

        @rtype: C{list} of C{datetime.datetime}
        @return: The times of the events 
        """
        times = []
        try:
            query_set = self._events_query_sets[idx]
            times = [ev.event_receive 
                     for ev in query_set.filter(testrun_id = testrun_id)]
        except query_set.model.DoesNotExist:
            pass
        return times

    def _event_dts(self, prev_event_times, this_event_times):
        """
        @type prev_event_times:  C{list} of C{datetime.datetime}
        @param prev_event_times: The time(s) of a monitoring event

        @type this_event_times:  C{list} of C{datetime.datetime}
        @param this_event_times: The time(s) of a subsequent monitoring event

        @rtype: C{list} of C{int}
        @return: The timedelta(s) for the step in the Testrun sequence 
        """
        ret_val = []
        if prev_event_times and this_event_times:
            deltatime = (this_event_times[0] - prev_event_times[-1]).seconds
            ret_val.append(deltatime)
            for idx in range(1, len(this_event_times)):
                deltatime = (this_event_times[idx] - 
                             this_event_times[idx-1]).seconds
                ret_val.append(deltatime)
        return ret_val

    ###########################################
    # Public Method
    ###########################################

    def deltas_iter(self, start, stop, step):
        """
        @type start: C{int} or None
        @param start: The start index of the iteration

        @type stop: C{int} or None
        @param stop: The stop index of the iteration

        @type step: C{int} or None
        @param step: The step of the iteration
        
        @yield: C{tuple} of (C{str}, [C{list} of [C{list} of C{float}]])
                A tuple of the testrun_id and the time deltas
                for all the steps in the testrun 
        """
        for testrun_id in self._testrun_ids(start, stop, step):
            dts = []
            start_time = None
            for event_idx in range(1, len(self._events_query_sets)):
                if start_time is None:
                    prev_event_times = self._get_event_times(testrun_id, 
                                                             event_idx - 1)
                this_event_times = self._get_event_times(testrun_id, 
                                                         event_idx)
                ev_dts = self._event_dts(prev_event_times, this_event_times)
                dts.append(ev_dts)
                prev_event_times = this_event_times
            yield (testrun_id, dts)
