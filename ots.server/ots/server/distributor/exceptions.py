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
Exceptions used by ots.server.distributor
"""

class OtsQueueDoesNotExistError(Exception):
    """Exception raised when queue does not exist in rabbitmq server"""
    pass

class OtsExecutionTimeoutError(Exception):
    """Exception raised if a task is not finished in time"""
    
    def __str__(self):
        return ("Server side timeout. (Worker went offline during "+\
                    "testrun or some tasks were not started in time)")

class OtsQueueTimeoutError(Exception):
    """Exception raised if none of the tasks was started before queue timeout"""
    def __init__(self, timeout_length, *args, **kwargs):
        self.timeout_length = timeout_length
        Exception.__init__(self, *args, **kwargs)

    def __str__(self):
        return ("The job was not started within %s minutes. "+\
                    "A worker in that devicegroup may be down or there may be"+\
                    " exceptional demand") % str(self.timeout_length / 60)
