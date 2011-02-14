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


import time

class MonitorType(object):
    UNKNOWN = "Unknown"
    TESTRUN_REQUESTED = "Testrun requested"
    TASK_INQUEUE = "Task in queue"
    TASK_ONGOING = "Task is ongoing"
    TASK_ENDED = "Task is ended"
    TESTRUN_ENDED = "Testrun ended"
    
    DEVICE_FLASH_STARTED = "Device flash started"
    DEVICE_FLASH_ENDED = "Device flash ended"
    DEVICE_BOOT_STARTED = "Device boot started"
    DEVICE_BOOT_ENDED = "Device boot ended"
    
    TEST_PACKAGE_STARTED = "Test package started"
    TEST_PACKAGE_ENDED = "Test package ended"
    
    RESULTS = "Worker storing results"

class Monitor(object):
    """
    Monitor event class
    """

    def __init__(self, 
                 event_type = MonitorType.UNKNOWN, 
                 sender = None, 
                 description = None, 
                 **kw):
        """
        @type event_type: C{MonitorType}
        @param event_type: Event type

        @type sender : C{str}
        @param sender : Event sender

        @type description : C{str}
        @param description : Event description

        """
        self._event_type = event_type
        self._event_emitted = time.time()
        self._event_received = None
        self._sender = sender
        self._description = description
    
    @property    
    def type(self):
        """
        @rtype: C{MonitorType}
        @param: Event type
        """
        return self._event_type

    @property    
    def emitted(self):
        """
        @rtype: C{int}
        @param: Creation time in seconds
        """
        return self._event_emitted

    @property    
    def received(self):
        """
        @rtype: C{int}
        @param: Emit time in seconds
        """
        return self._event_received
    
    @received.setter
    def received(self, value = None):
        """
        @rtype: C{int}
        @param: Received time in seconds
        """
        if value is None:
            value = time.time()
        self._event_received = value
    
    @property    
    def sender(self):
        """
        @rtype: C{str}
        @param: Event sender
        """
        return self._sender
    
    @sender.setter    
    def sender(self, value = None):
        """
        @rtype: C{str}
        @param: Event sender setter
        """
        self._sender = value

    @property    
    def description(self):
        """
        @rtype: C{str}
        @param: Event description
        """
        return self._description
    
    @description.setter 
    def description(self, value = None):
        """
        @rtype: C{str}
        @param: Event description setter
        """
        self._description = value