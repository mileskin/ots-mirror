# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
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

"""
Script taken from E-P's development.py and
hacked to allow unittest of time deltas
"""

import json
import uuid
import datetime
import random
from datetime import datetime, timedelta

from itertools import cycle

from ots.common.dto.monitor import MonitorType

################################
# FIXMEs
################################

# 1. Duplication on `error` (results infra reports this)... perhaps pragmatic
# 2. What is state?
# 3. Granularity of events is seconds
# 4. What's the workers stuff about?


####################
# VARS
####################

NUM_OF_TESTRUNS = 300
NUM_OF_TESTPACKAGES = 10

#For this test the device groups have
#exagerated characteristics

DEVICE_GROUPS = ["complete_run", 
                 "faulty_flasher", 
                 "stuck_in_queue"]

QUEUE = ["common_%s"%dg for dg in DEVICE_GROUPS]

REQUESTORS = cycle(['top_dog@acme.com']*10 + 
                   ['middle_man@acme.com']*5 + 
                   ['bottom_of_the_pile@acme.com'])

EVENT_COUNT = 0

######################################

def _create_events(event_sequence, testrun_id, start_time):

    retlist = []
    
    for idx, event_name in enumerate(event_sequence):
        event = dict()
        event["model"] = "monitor.Event"
        event["pk"] = _create_events.event_count
        fields = dict()
        fields["testrun_id"] = testrun_id
        fields["event_name"] = event_name
        emit_time = start_time + timedelta(minutes = (idx + 1)*idx)
        fields["event_emit"] = emit_time.strftime("%Y-%m-%d %H:%M")
        rec_time = emit_time + timedelta(minutes = 1)
        fields["event_receive"] = rec_time.strftime("%Y-%m-%d %H:%M")
        event["fields"] = fields
        _create_events.event_count += 1
        retlist.append(event)
    return retlist

_create_events.event_count = 0

def get_fields(start_time, idx):
    fields = dict()
    fields["testrun_id"] = str(uuid.uuid1().hex)
    fields["device_group"] = DEVICE_GROUPS[idx%len(DEVICE_GROUPS)]
    fields["queue"] = QUEUE[idx%len(DEVICE_GROUPS)]
    fields["configuration"] = "configuration"
    fields["requestor"] = REQUESTORS.next()
    fields["request_id"] = random.randint(1,12345)
    fields["start_time"] = start_time.strftime("%Y-%m-%d %H:%M")
    state = random.randint(0,4) # What is this?
    fields["state"] = state
    return fields

def _get_event_sequence(device_group):
    event_sequence = [MonitorType.TESTRUN_REQUESTED, 
                          MonitorType.TASK_INQUEUE]
    if device_group == "complete_run":
        event_sequence += [MonitorType.TASK_ONGOING,
                           MonitorType.DEVICE_FLASH,
                           MonitorType.DEVICE_BOOT,
                           MonitorType.TEST_EXECUTION,
                           MonitorType.TEST_PACKAGE_ENDED]
    if device_group == "faulty_flasher":
        event_sequence += [MonitorType.TASK_ONGOING,
                           MonitorType.DEVICE_FLASH,
                           MonitorType.DEVICE_FLASH,
                           MonitorType.DEVICE_FLASH]
    return event_sequence

init_time = datetime.strptime("2011-02-01","%Y-%m-%d")

def main():
    json_data = []
    for idx in xrange(NUM_OF_TESTRUNS):
        testrun = dict()
        testrun["model"] = "monitor.Testrun"
        testrun["pk"] = idx
        start_time = init_time + timedelta(minutes = idx)
        fields = get_fields(init_time, idx)
        testrun["fields"] = fields 
        
        #
        workers = ""
        for x in xrange(random.randint(1,3)):
            workers += "ots_worker_" + str(x) + ","
        workers = workers[0:(len(workers)-1)]
        fields["host_worker_instances"] = workers
        #
        json_data.append(testrun)
        event_sequence = _get_event_sequence(fields["device_group"])
        events = _create_events(event_sequence, 
                                idx, 
                                start_time)
        json_data.extend(events)
    
    json_file = open("test_set.json", 'w')
    json_file.write(json.dumps(json_data))
    json_file.close()


if __name__ == "__main__":
    main()
    
