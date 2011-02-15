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

NUM_OF_TESTRUNS = 100
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
    
    for i in xrange(NUM_OF_TESTRUNS):
        testrun = dict()
        testrun["model"] = "monitor.Testrun"
        testrun["pk"] = i
        
        fields = dict()
        fields["testrun_id"] = str(uuid.uuid1())
        fields["device_group"] = "example_device_group"
        fields["queue"] = "sw product"
        fields["configuration"] = "configuration"
        fields["host_worker_instances"] = "ots.worker1,ots.worker2"
        fields["requestor"] = "esa-pekka.miettinen@digia.com"
        fields["request_id"] = "666"
        fields["error"] = ""

        
        testrun["fields"] = fields
        json_data.append(testrun)
        
        for y in xrange(NUM_OF_TESTPACKAGES):
            package = dict()
            package["model"] = "monitor.Package"
            package["pk"] = package_count
            fields = dict()
            fields["testrun_id"] = i
            fields["package_name"] = "test-package-" + str(y)
            fields["status"] = random.randint(0,1)
            fields["duration"] = random.randint(2,60)
            
            package["fields"] = fields
            json_data.append(package)
            
            package_count += 1
        
        for y in xrange(NUM_OF_EVENTS):
            event = dict()
            event["model"] = "monitor.Event"
            event["pk"] = event_count
            fields = dict()
            fields["testrun_id"] = i
            fields["event_name"] = event_list[random.randint(0, len(event_list)-1)]
            fields["event_emit"] = time.time()
            fields["event_receive"] = time.time() + 1
            
            event["fields"] = fields
            json_data.append(event)
            
            event_count += 1
            
    json_file = open("development.json", 'w')
    json_file.write(json.dumps(json_data))
    json_file.close()


if __name__ == "__main__":
    main()
    