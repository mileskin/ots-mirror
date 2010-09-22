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


#Disable spurious pylint warnings

#pylint: disable-msg=E0611
#pylint: disable-msg=F0401


"""
A Task 
"""

import uuid

from ots.common.amqp.messages import TaskCondition

class TaskException(Exception):
    """Task Exception"""
    pass


#############################
# Task 
#############################

class Task(object):
    """
    A Task currently run as a command 
    Defines state behaviour and holds current state

    Has a unique id 
    """

    _WAITING = "WAITING" 
    _STARTED = "STARTED"
    _FINISHED = "FINISHED"

    #condition, current, next_state
    transition_table = [(TaskCondition.START, _WAITING, _STARTED, ),
                        (TaskCondition.FINISH, _STARTED, _FINISHED)]

    current_state = "WAITING"

    def __init__(self, command, timeout):
        """
        @type command: C{list} 
        @param command: The CL params as a list
 
        @type timeout C{int} 
        @param timeout: The timeout for the command

        """
        self.command = command 
        self._timeout = timeout
        self.task_id = uuid.uuid1().hex

    def transition(self, condition):
        """
        Trigger a state transition 

        @type condition: C{string} 
        @param condition: The condition 
        """
        transition_table = self.transition_table
        if not condition in [row[0] for row in transition_table]:
            raise TaskException("Unknown condition '%s'" % (condition))
        for row in transition_table:
            if row[0] == condition and self.current_state == row[1]:
                self.current_state = row[2]
                break
        else:
            msg = "No transition %s->'%s'->" % (self.current_state, condition)
            raise TaskException(msg)
    
    @property
    def is_finished(self):
        """
        Has the Task finished the run?

        @rtype is_finished: C{bool} 
        @param is_finished: Is the Task in the finished state 
        """
        return self.current_state == self._FINISHED
