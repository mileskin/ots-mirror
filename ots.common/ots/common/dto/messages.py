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
The Message clases allow remote control
beween the sub-systems
"""

import ots.common
import StringIO

############################
# TASK CONDITIONS
###########################

class TaskCondition(object):
    """
    The conditions that trigger state changes on the Tasks
    """

    START = 'start'
    FINISH = 'finish'


###########################
# MESSAGE BASE
###########################

class MessageBase(object):
    
    __version__ = ots.common.__VERSION__


###########################
# COMMAND MESSAGE
###########################

class CommandMessage(MessageBase):
    """
    Encapsulates a Command
    """

    QUIT = 'quit'
    IGNORE = 'ignore'

    def __init__(self, command, response_queue, task_id, 
                 timeout = 60, xml_file = None, min_worker_version = None):
        """
        @type command: C{list}
        @param command: The CL params

        @type queue : C{str}
        @param queue : The queue to post the message

        @type timeout : C{int}
        @param timeout : The timeout for the Task

        @type task_id : C{int}
        @param task_id : The Task ID
        
        @type xml_file : C{StringIO}
        @param xml_file : XML test plan

        @type min_worker_version: C{str}
        @type min_worker_version: The minimum acceptable worker version 
        """
        self.command = " ".join(command)
        self.response_queue = response_queue
        self.task_id = task_id 
        self.timeout = timeout
        self.xml_file = xml_file
        self.min_worker_version = min_worker_version

    @property    
    def is_quit(self):
        """
        @rtype: C{bool}
        @param: Should the Worker quit
        """
        return self.command == self.QUIT

    @property 
    def is_ignore(self):
        """
        @rtype: C{bool}
        @param: Should the Worker ignore
        """
        #FIXME: Explain the point of this
        return self.command == self.IGNORE

################################
# STATE CHANGE MESSAGE
################################

class StateChangeMessage(MessageBase):
    """
    Message to trigger a State Change
    """

    def __init__(self, task_id, condition):
        self.task_id = task_id 
        self.condition = condition

    @property 
    def is_start(self):
        """
        @rtype: C{bool}
        @param: Is this a start condition
        """
        return self.condition == TaskCondition.START

    @property
    def is_finish(self):
        """
        @rtype: C{bool}
        @param: Is this a finish condition
        """
        return self.condition == TaskCondition.FINISH
