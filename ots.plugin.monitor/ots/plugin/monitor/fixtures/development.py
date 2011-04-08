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
Script for creating development data to database.
"""

import json
import inspect
import uuid
import random
import time
import datetime
from ots.common.dto.monitor import MonitorType

NUM_OF_TESTRUNS = 1000
NUM_OF_TESTPACKAGES = 10

DEVICE_GROUPS = ["meego_n900", "meego_netbook", "meego_aava"]
QUEUE = ["common_n900", "common_netbook", "common_aava"]
REQUESTORS = ['esa-pekka.miettinen@digia.com', 'elias.luttinen@digia.com', 'ville.niutanen@digia.com']

EVENT_COUNT = 0

def _generate_events(event_list, testrun_id, timestamp):

    global EVENT_COUNT
    
    retlist = []
    
    for event_name in event_list:
        event = dict()
        event["model"] = "monitor.Event"
        event["pk"] = EVENT_COUNT
        fields = dict()
        fields["testrun_id"] = testrun_id
        fields["event_name"] = event_name
        fields["event_emit"] = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        fields["event_receive"] = datetime.datetime.fromtimestamp(timestamp + random.randint(1,10)).strftime("%Y-%m-%d %H:%M")
        
        event["fields"] = fields
        EVENT_COUNT += 1
        
        timestamp += random.randint(1,60) * 60
        
        retlist.append(event)
    
    return retlist

def main():
    
    json_data = []
    
    for i in xrange(NUM_OF_TESTRUNS):
        testrun = dict()
        testrun["model"] = "monitor.Testrun"
        testrun["pk"] = i
        
        tr_id = str(uuid.uuid1().hex)
        fields = dict()
        fields["testrun_id"] = tr_id
        fields["device_group"] = DEVICE_GROUPS[random.randint(0, len(DEVICE_GROUPS)-1)]
        fields["queue"] = QUEUE[random.randint(0, len(QUEUE)-1)]
        fields["configuration"] = "configuration"
        fields["requestor"] = REQUESTORS[random.randint(0, len(REQUESTORS)-1)]
        fields["request_id"] = random.randint(1,12345)
        
        timestamp = time.time() - (random.randint(1, 48) * 30 * 60)
        
        fields["start_time"] = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        

        state = random.randint(0,4)
        fields["state"] = state
        testrun["fields"] = fields
        
        event_list = []
        
        #Queue state
        if state == 0:
            event_list = [MonitorType.TESTRUN_REQUESTED, 
                          MonitorType.TASK_INQUEUE]
            fields["host_worker_instances"] = ""
            fields["error"] = ""
        # Execution state
        elif state >= 1:
            event_list = [MonitorType.TESTRUN_REQUESTED, 
                          MonitorType.TASK_INQUEUE,
                          MonitorType.TASK_ONGOING,
                          MonitorType.DEVICE_FLASH,
                          MonitorType.DEVICE_BOOT,
                          MonitorType.TEST_EXECUTION,
                          ]
            workers = ""
            for x in xrange(random.randint(1,3)):
                workers += "ots_worker_" + str(x) + " "
            
            workers = workers[0:(len(workers)-1)]
                
            fields["host_worker_instances"] = workers
            fields["error"] = ""
            
            # Pass / Fail state
            if state >= 2:
                event_list.append(MonitorType.TESTRUN_ENDED)
            
            # Error state
            if state == 4:
                fields["error"] = "Error code: " + str(random.randint(666,1000))       

        
        json_data.append(testrun)
        json_data.extend(_generate_events(event_list, i, timestamp))
    
    
    json_file = open("development.json", 'w')
    json_file.write(json.dumps(json_data))
    json_file.close()


if __name__ == "__main__":
    main()
    
