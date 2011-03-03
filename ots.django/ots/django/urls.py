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
Django main url file
"""

from django.conf.urls.defaults import patterns, include, handler500, handler404
from django.conf import settings

args = ['',
    (r'^logger/', include('ots.plugin.logger.urls')),
    (r'^monitor/', include('ots.plugin.monitor.urls')),

    (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),

    (r'^services/$', 'ots.plugin.monitor.views.service'),
]

##################################################
# Switch for serving js content in Dev/Production
##################################################

if True:
    args += [(r'^demo_chart$', 'ots.plugin.monitor.views.demo_chart'),
             (r'^(?P<path>.*)$', 'django.views.static.serve',
              {'document_root': settings.STATIC}),]

##################################################

urlpatterns = patterns(*args)
