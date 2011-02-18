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
Django models file for monitoring data
"""

# Ignoring class has no __init__ method
# pylint: disable=W0232
# Ignoring too few public methods
# pylint: disable=R0903

from django.db import models

class Testrun(models.Model):
    """
    Model for testrun data
    """
    testrun_id = models.CharField(db_index=True, max_length=32)
    device_group = models.CharField(max_length=255)
    queue = models.CharField(max_length=255)
    configuration = models.CharField(max_length=255)
    host_worker_instances = models.TextField()
    requestor = models.EmailField()
    request_id = models.CharField(max_length=255)
    error = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now=True)
    state = models.PositiveIntegerField()
    
    class Meta:
        """
        Meta class for model
        """
        db_table = 'monitor_testrun'


class Event(models.Model):
    """
    Model for Event data
    """
    testrun_id = models.ForeignKey(Testrun)
    event_name = models.CharField(max_length=255)
    event_emit = models.DateTimeField(auto_now=True)
    event_receive = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for model
        """
        db_table = 'monitor_event'

