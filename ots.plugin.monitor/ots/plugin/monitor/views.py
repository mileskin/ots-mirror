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

# Ignoring: Class 'LogMessage' has no 'objects' member
# pylint: disable=E1101
# Ignoring: Unused argument 'request'
# pylint: disable=W0613

"""
monitor creates and views log messages

Example of creating log message:

import logging
import logging.handlers
monitor = logging.getmonitor('mymonitor_name')
http_handler = logging.handlers.HTTPHandler(host_address,
                                            '/logging/%s/%s/' % (servicename, run_id),
                                            method='POST',)
monitor.setLevel(logging.DEBUG)
monitor.addHandler(http_handler)

monitor.debug('debug message')
monitor.info('info message')
monitor.warn('warning message')
monitor.error('error message')
monitor.critical('critical message')
"""
import datetime
import socket
from copy import deepcopy

from django.http import HttpResponse
from django.conf import settings
from django.template import loader, Context

from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event

ROW_AMOUNT_IN_PAGE = 50

def main_page(request):
    """
        Index page for viewing summary from all test runs.
        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

    """
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    queues = Testrun.objects.values('queue').distinct()    
    
    context_dict['queues']  = queues
    template = loader.get_template('monitor/index.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_queue_details(request,queue_name=None):
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    testruns = Testrun.objects.filter(queue=queue_name)
    context_dict['testruns'] = testruns
    context_dict['queue_name'] = queue_name
    template = loader.get_template('monitor/queue_details_view.html')
    return HttpResponse(template.render(Context(context_dict)))