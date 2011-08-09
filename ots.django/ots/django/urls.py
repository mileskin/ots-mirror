# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
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

from django.conf.urls.defaults import patterns, include
from django.conf import settings

def _append_url(url_list, app):
    try:
        mod = __import__(app[1])
    except ImportError:
        return
    url_list.append((app[0], include(app[1])))


args = ['',
    (r'xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc',),
]

_append_url(args, (r'^logger/', 'ots.plugin.logger.urls'))
_append_url(args, (r'^monitor/', 'ots.plugin.monitor.urls'))
_append_url(args, (r'^services/', 'ots.plugin.monitor.views.service'))


##################################################
# Switch for serving js content in Dev/Production
##################################################

if False:
    args += [(r'^demo_chart$', 'ots.plugin.monitor.views.demo_chart'),
             (r'^(?P<path>.*)$', 'django.views.static.serve',
              {'document_root': settings.STATIC}),]

##################################################

urlpatterns = patterns(*args)
