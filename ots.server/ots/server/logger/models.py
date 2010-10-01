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

from django.db import models

class LogMessage(models.Model):
    """ Model for message logs
    """
    service = models.CharField(max_length=20, db_index=True)
    run_id = models.IntegerField(db_index=True)

    date = models.DateTimeField()
    remote_ip = models.CharField(max_length=40)
    remote_host = models.CharField(max_length=255)

    levelno = models.IntegerField()
    levelname = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    pathname = models.CharField(max_length=255)
    funcName = models.CharField(max_length=255, db_column='func_name')
    lineno = models.IntegerField()

    msg = models.TextField()
    exc_info = models.TextField(null=True, blank=True)
    exc_text = models.TextField(null=True, blank=True)
    args = models.TextField(null=True, blank=True)

    threadName = models.CharField(max_length=255, db_column='thread_name')
    thread = models.FloatField()
    created = models.FloatField()
    process = models.IntegerField()
    relativeCreated = models.FloatField(db_column='relative_created')
    msecs = models.FloatField()

    class Meta:
        db_table = 'log_messages'

    def __unicode__(self):
        return self.msg
