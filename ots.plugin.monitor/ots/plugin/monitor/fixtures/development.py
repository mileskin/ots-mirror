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
Script for creating development data to database.
"""

import json
import inspect
import uuid
import random
import time

from ots.common.dto.monitor import MonitorType

NUM_OF_TESTRUNS = 1000
NUM_OF_TESTPACKAGES = 10
NUM_OF_EVENTS = 10

def main():
    
    json_data = []
    
    event_list = []
    package_count = 1
    event_count = 1
    
    for (event, value) in inspect.getmembers(MonitorType):
        if event[0] != "_":
            event_list.append(value)
    
    print event_list
    
    for i in xrange(NUM_OF_TESTRUNS):
        testrun = dict()
        testrun["model"] = "monitor.Testrun"
        testrun["pk"] = i
        
        tr_id = str(uuid.uuid1().hex)
        fields = dict()
        fields["testrun_id"] = tr_id
        fields["device_group"] = "example_device_group"
        fields["queue"] = "sw product"
        fields["configuration"] = "configuration"
        fields["host_worker_instances"] = "ots.worker1,ots.worker2"
        fields["requestor"] = "esa-pekka.miettinen@digia.com"
        fields["request_id"] = "666"
        fields["error"] = ""
        fields["verdict"] = random.randint(-1,3)

        
        testrun["fields"] = fields
        json_data.append(testrun)
        
        last_time = 0
        state = fields["verdict"]
        for y in event_list:
            randnum = random.randint(0,1)
            
            if state == -1:
                
                # If 1, then testrun is in execution phase
                if randnum == 1:
                    if y == MonitorType.ETESTRUN_ENDED:
                        break
                else:
                    if y == MonitorType.CTASK_ONGOING:
                        break                    
                    
            
            last_time = time.time() + random.randint(10,100) + last_time
            event = dict()
            event["model"] = "monitor.Event"
            event["pk"] = event_count
            fields = dict()
            fields["testrun_id"] = i
            fields["event_name"] = y
            fields["event_emit"] = last_time
            fields["event_receive"] = last_time + 1
            
            event["fields"] = fields
            json_data.append(event)
            
            event_count += 1
            
    json_file = open("development.json", 'w')
    json_file.write(json.dumps(json_data))
    json_file.close()


if __name__ == "__main__":
    main()
    