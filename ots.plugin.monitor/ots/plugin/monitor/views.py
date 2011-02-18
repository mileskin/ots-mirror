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
from django.db.models import Count

from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event
from ots.common.dto.api import MonitorType

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

def stats(event_list):
    
    event_category = {
                      "Queue time" : [MonitorType.TASK_INQUEUE, MonitorType.TASK_ONGOING],
                      "Flash time" : [MonitorType.DEVICE_FLASH, MonitorType.DEVICE_BOOT],
                      "Boot time" : [MonitorType.DEVICE_BOOT, MonitorType.TEST_EXECUTION],
                      "Total time" : [MonitorType.TESTRUN_REQUESTED, MonitorType.TESTRUN_ENDED],
                      }
    stats = dict()
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
            stats[category_name] = end_time - start_time
    return stats

def view_testrun_list(request):
    context_dict = {}
    
    testruns = Testrun.objects.filter(verdict = -1)
    ongoing_testruns = []
    queue_testruns = []
    
    for testrun in testruns:
        testrun_events = Event.objects.filter(testrun_id = testrun.id)
        state = testrun_state(testrun_events)
        if state  == "Queue":
            queue_testruns.append(testrun)
        elif state == "Ongoing":
            ongoing_testruns.append(testrun)


    context_dict['ongoing_testruns'] = ongoing_testruns
    context_dict['queue_testruns'] = queue_testruns
    template = loader.get_template('monitor/testrun_list.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_group_details(request, devicegroup=None):
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    testruns = Testrun.objects.select_related().filter(device_group=devicegroup)
    runs_on_group = testruns.count()
    finished = testruns.filter(event__event_name__exact="Testrun ended")
    finished_ids = finished.values_list('id',flat=True).distinct()
    #print finished_ids
    #ongoing = testruns.exclude(event__testrun_id__in=finished_ids)
    runs_finished = finished.count()
    context_dict['testruns'] = testruns.order_by('-event__event_receive')
    context_dict['devicegroup'] = devicegroup
    context_dict['finished'] = finished
    context_dict['runcount'] = runs_on_group
    runs_finished = testruns.filter(verdict__in=[0,1,2]).count()
    context_dict['finishedcount'] = runs_finished

    requestors = testruns.values_list('requestor',flat=True).distinct()
    reqs = 0
    toprtor = ''
    for requestor in requestors:
         reqsbyrtor = testruns.filter(requestor=requestor).count()
         print requestor+" has "+str(reqsbyrtor)
         if reqsbyrtor > reqs:
             reqs = reqsbyrtor
             toprtor = requestor
    #testruns.annotate(num_requests=Count('requestor'))
    print "top requestor "+toprtor+" / "+str(reqs)
    context_dict['top_requestor'] = toprtor
    context_dict['top_requests'] = reqs
    passed_runs = testruns.filter(verdict=0).count()
    failed_runs = testruns.filter(verdict=1).count()
    ongoing_runs= testruns.filter(verdict=-1).count()
    error_runs = testruns.filter(verdict=2).count()
    context_dict['passed_runs'] = passed_runs
    context_dict['failed_runs'] = failed_runs
    context_dict['ongoing_runs'] = ongoing_runs
    context_dict['error_runs'] = error_runs
    context_dict['error_rate'] = round((1.0*error_runs/runs_finished)*100,2)
    context_dict['pass_rate'] = round((1.0*passed_runs/runs_finished)*100,2)
    context_dict['fail_rate'] = round((1.0*failed_runs/runs_finished)*100,2)
     
    
    #error_runs,ongoing_runs,failed_runs,passed_runs,top_requests,top_requestor
    #Top req, finished, waiting , ongoing, error%
    #0=pass,1=fail,-1=ongoing,2=error
    
    template = loader.get_template('monitor/group_details_view.html')
    return HttpResponse(template.render(Context(context_dict)))