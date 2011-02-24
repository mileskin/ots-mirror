# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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
Django models file for package data
"""

from django.db import models

class Package(models.Model):
    """
    Model for test package
    """

    package_name = models.CharField(db_index=True, max_length=255)
 
    class Meta:
        """
        Meta class for model
        """
        db_table = 'distribution_package'

class History(models.Model):
    """
    Model for test package
    """
    
    VERDICT_CHOICES = (
        (u'0', u'none'),
        (u'1', u'pass'),
        (u'2', u'fail'),
        (u'3', u'error'),
    )
    
    package_id = models.ForeignKey(Package)
    start_time = models.DateTimeField(auto_now=True)
    # Duration in seconds
    duration = models.PositiveIntegerField()
    testrun_id = models.CharField(max_length=32)
    verdict = models.CharField(max_length=2, choices=VERDICT_CHOICES)
 
    class Meta:
        """
        Meta class for model
        """
        db_table = 'distribution_history'