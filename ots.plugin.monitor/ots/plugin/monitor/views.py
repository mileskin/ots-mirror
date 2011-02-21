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
import time
import socket
from copy import deepcopy

from django.http import HttpResponse
from django.conf import settings
from django.template import loader, Context
from django import forms
from django.forms.formsets import formset_factory

from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event
from ots.common.dto.api import MonitorType

ROW_AMOUNT_IN_PAGE = 50

def _handle_date_filter(request):
    date_dict = dict()
    
    if request.method == 'POST':
        post = request.POST
        try:
            date_dict['datefilter_start'] = datetime.datetime.strptime(post.get("startdate"), "%Y-%m-%d %H:%M")
        except ValueError:
            date_dict['datefilter_start'] = datetime.datetime(year=1900, month=1, day=1)
        try:
            date_dict['datefilter_end'] = datetime.datetime.strptime(post.get("enddate"), "%Y-%m-%d %H:%M")
        except ValueError:
            date_dict['datefilter_end'] = datetime.datetime.now()
    else:
        date_dict['datefilter_start']  = request.session.get("datefilter_start", datetime.datetime.fromtimestamp(time.time()-24*3600))
        date_dict['datefilter_end']  =  request.session.get("datefilter_end",datetime.datetime.now())
    
    request.session.update(date_dict)
    
    date_dict['datefilter_start_str']  = date_dict['datefilter_start'].strftime("%Y-%m-%d %H:%M")
    date_dict['datefilter_end_str']  = date_dict['datefilter_end'].strftime("%Y-%m-%d %H:%M")
    
    return date_dict

def main_page(request):
    """
        Index page for viewing summary from all test runs.
        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

    """
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    context_dict.update(_handle_date_filter(request))
    
    context_dict['queues']  = ""
    
    template = loader.get_template('monitor/index.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_queue_details(request,queue_name=None):
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    context_dict.update(_handle_date_filter(request))
    
    testruns = Testrun.objects.filter(queue=queue_name)
    context_dict['testruns'] = testruns
    context_dict['queue_name'] = queue_name
    template = loader.get_template('monitor/queue_details_view.html')
    return HttpResponse(template.render(Context(context_dict)))

def testrun_state(testrun_events):
    """
    Returns testrun's current state:
        Queue,
        Ongoing,
        Finished,
    """
    
    if len(testrun_events.filter(event_name = MonitorType.TESTRUN_ENDED)) > 0:
        return "Finished"
    elif len(testrun_events.filter(event_name = MonitorType.TASK_ONGOING)) > 0:
        return "Ongoing"
    else:
        return "Queue"

class Stats(object):
    name = ""
    delta = 0
    
    def __init__(self, name, delta):
        self.name = name
        self.delta = delta
    

def stats(event_list):
    
    event_category = {
                      "Queue time" : [MonitorType.TASK_INQUEUE, MonitorType.TASK_ONGOING],
                      "Flash time" : [MonitorType.DEVICE_FLASH, MonitorType.DEVICE_BOOT],
                      "Boot time" : [MonitorType.DEVICE_BOOT, MonitorType.TEST_EXECUTION],
                      "Total time" : [MonitorType.TESTRUN_REQUESTED, MonitorType.TESTRUN_ENDED],
                      }
    stats = []
    for (category_name, category_events) in event_category.iteritems():
        start_time = None
        end_time = None
        start_event = category_events[0]
        end_event = category_events[1]
        for event in event_list:
            if start_time != None and end_time != None:
                break
            
            if start_event == event.event_name:
                start_time = event.event_emit
                continue
            if end_event == event.event_name:
                end_time = event.event_emit
                continue         
        if start_time != None and end_time != None:
            stats.append(Stats(category_name, end_time - start_time))

    return stats

def view_testrun_list(request, device_group = None):
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    
    testruns = Testrun.objects.filter(state__lt = 2, 
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])
    
    if device_group:
        testruns = testruns.filter(device_group = device_group)
    
    testruns = testruns.order_by("-state")
    
    ongoing_testruns = []
    queue_testruns = []
    
    total_count = testruns.count()
    onqueue_count = testruns.filter(state = 0).count()
    execution_count = testruns.filter(state = 1).count()
    
    context_dict['testruns'] = testruns
    context_dict['total_count'] = total_count
    context_dict['onqueue_count'] = onqueue_count
    context_dict['execution_count'] = execution_count
    
    template = loader.get_template('monitor/testrun_list.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_testrun_details(request, testrun_id):
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    
    testrun = Testrun.objects.get(testrun_id = testrun_id)
    events = Event.objects.filter(testrun_id = testrun.id)
    
    testrun_stats = stats(events)
    
    context_dict["testrun"] = testrun
    context_dict["events"] = events
    context_dict["testrun_stats"] = testrun_stats
    
    template = loader.get_template('monitor/testrun_details.html')
    return HttpResponse(template.render(Context(context_dict)))

