# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

""" DTO messages for Monitoring """

import time

class MonitorType(object):
    """
    Class which defines all static Monitor types
    """
    
    UNKNOWN = "Unknown"

    # Emitted in Hub after plug-ins are loaded
    TESTRUN_REQUESTED = "Testrun requested"

    # Emitted in taskrunner when tasks are added to queue
    # Description: task.id
    TASK_INQUEUE = "Task in queue"

    # OTS worker sends this event when processes a task
    # Description: task.id
    # Sender: OTS worker host name
    TASK_ONGOING = "Task is ongoing"

    # OTS worker sends this when the task is done
    # Description: task.id
    # Sender: host name
    TASK_ENDED = "Task is ended"

    # Emitted in taskrunner when tasks are added to queue
    TESTRUN_ENDED = "Testrun ended"

    # Conductor sends this event when starts flashing
    # Description: image url
    DEVICE_FLASH = "Device flashing"

    # Conductor sends this event when flashing is done
    DEVICE_BOOT = "Device booting"

    # Conductor sends this event when execution starts
    TEST_EXECUTION = "Test execution"
    
    # Conductor sends this event when starting test package execution
    # Description: test package name
    TEST_PACKAGE_STARTED = "Test package started"

    # Conductor sends this event when test package has been executed
    # Description: test package name
    TEST_PACKAGE_ENDED = "Test package ended"

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
        @type event_type: L{MonitorType}
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
        Event type
        @rtype: L{MonitorType}
        """
        return self._event_type

    @property    
    def emitted(self):
        """
        Creation time in seconds
        @rtype: C{int}
        """
        return self._event_emitted

    @property    
    def received(self):
        """
        Emit time in seconds
        @rtype: C{int}
        """
        return self._event_received

    def set_received(self, value = None):
        """
        @type value: C{int}
        @param value: Received time in seconds
        """
        if value is None:
            value = time.time()
        self._event_received = value

    @property    
    def sender(self):
        """
        Event sender
        @rtype: C{str}
        """
        return self._sender

    @sender.setter    
    def sender(self, value = None):
        """
        @type value: C{str}
        @param value: Event sender setter
        """
        self._sender = value

    @property    
    def description(self):
        """
        Event description
        @rtype: C{str}
        """
        return self._description

    @description.setter 
    def description(self, value = None):
        """
        @type value: C{str}
        @param value: Event description setter
        """
        self._description = value
