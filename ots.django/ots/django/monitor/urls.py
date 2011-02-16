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
File for django urls
"""

# Ignoring naming pattern
# pylint: disable=C0103

from django.conf.urls.defaults import patterns, include, handler500, handler404

from ots.django.monitor.views import main_page
from ots.django.monitor.views import view_queue_details

urlpatterns = patterns('',
    (r'^view/$', main_page),
    (r'^view/queue/(?P<queue_name>[^/]+)/$',view_queue_details),
    (r'^view/testrun/(?P<testrun_id>[^/]+)/$',view_testrun_details),
    #(r'^view/queue/$',view_queue_details),
)
