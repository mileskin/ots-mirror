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
import datetime

NUM_OF_TESTPACKAGES = 1000
NUM_OF_TESTRUNS = 10000

def main():
    
    json_data = []
    history_count = 1
    for i in xrange(NUM_OF_TESTPACKAGES):
        package = dict()
        package["model"] = "history.Package"
        package["pk"] = i
        
        fields = dict()
        fields["package_name"] = "test-package" + str(i) + "-tests"    
        package["fields"] = fields
        
        json_data.append(package)
        
    for y in xrange(NUM_OF_TESTRUNS):
        history = dict()
        history["model"] = "history.History"
        history["pk"] = history_count
        
        fields = dict()
        fields["package_id"] = random.randint(1, NUM_OF_TESTPACKAGES)
        fields["duration"] = random.randint(5, 60) * 60
        fields["testrun_id"] = uuid.uuid4().hex
        fields["verdict"] = random.randint(0,4)    
        history["fields"] = fields
        history_count += 1
        
        json_data.append(history)
    
    json_file = open("development.json", 'w')
    json_file.write(json.dumps(json_data))
    json_file.close()


if __name__ == "__main__":
    main()
    
