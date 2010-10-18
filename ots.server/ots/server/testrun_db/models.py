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
A minimalistic database for storing information about testruns. Results are not
stored here because this is not a reporting database.

Responsibilities:

- Provide unique testrun ID.
- Store all input parameters. This makes restarting runs possible.
- Provide statistics / debugging data for system maintainers.
- Store links to external systems (For example testrun results in a reporting
  tool

"""

from django.db import models



class Options(models.Model):
    """A Model for storing incoming testrun options"""
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=1024)



class Testrun(models.Model):
    """A Model for storing testrun data"""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    imageurl = models.CharField(max_length=3000, blank=True)
    build_id = models.CharField(max_length=20, blank=True)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    swproduct = models.CharField(max_length=50, blank=True, default="")
    result = models.CharField(max_length=50, blank=True, default="")
    error_code = models.CharField(max_length=20, blank=True)
    error_info = models.CharField(max_length=765, blank=True)
    state = models.CharField(max_length=50, blank=True, default="STARTED")
    status_info = models.CharField(max_length=765, blank=True,
                default="Testrun created")
    options = models.ForeignKey(Options, null=True, blank=True)


class Link(models.Model):
    """An external link to information related to an OTS testrun"""

    testrun = models.ForeignKey(Testrun)
    url = models.TextField()
    description = models.TextField()
    
