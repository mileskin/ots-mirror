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

# Ignoring class has no __init__ method
# pylint: disable=W0232
# Ignoring too few public methods
# pylint: disable=R0903

"""Django models file"""

from django.db import models, connection


class LogManager(models.Manager):
    """Extra manager for LogMessage model"""
    def get_latest_messages(self):
        """Get the latest message for each testrun"""
        cursor = connection.cursor()
        cursor.execute("""
                        SELECT MAX(id) FROM log_messages
                        GROUP BY run_id
                        """)
#                       SELECT id FROM log_messages,
#                       (SELECT MAX(created) mcred FROM log_messages
#                       GROUP BY run_id) AS maxcreated
#                       WHERE created = maxcreated.mcred
#                       """)
        return self.get_query_set().filter(
                        id__in=[row[0] for row in cursor.fetchall()])


class LogMessage(models.Model):
    """Model for message logs"""
    service = models.CharField(max_length=20, db_index=True)
    run_id = models.CharField(db_index=True, max_length=32)

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

    userDefinedId = models.CharField(max_length=255, blank=True,
                                     default='', db_column='user_defined_id')

    objects = LogManager()

    class Meta:
        """Meta class for model"""
        db_table = 'log_messages'

    def __unicode__(self):
        """Unicode function for table"""
        return self.msg
