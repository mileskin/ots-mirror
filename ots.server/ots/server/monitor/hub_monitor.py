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

"""
API Proposal

HubMonitor is a root Container class for 
the Monitors for the individual Components 


The Monitors themselves are just container objects 
"""

class HubMonitor(object):

    def __init__(self, sw_product, request_id, testrun_uuid):
        """
        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param: The unique identifier for the testrun
        """
        self.sw_product = sw_product 
        self.request_id = request_id
        self.testrun_uuid = testrun_uuid
        self._monitors = []

    def add_monitor(self, monitor):
        """
        @type monitor: L{Monitor}
        @param monitor: A monitor from an OTS Component
        """
        self._monitors.append(monitor)

    def monitors_iter(self):
        """
        @ytype : L{ots.common.dto.monitor}
        @yparam : The Monitor  
        """
        for monitor in self._monitors:
            yield monitor
            
