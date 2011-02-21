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

class TestrunView():
    device_group = None
    top_requestor = None
    runs = 0
    finished = 0
    waiting = 0
    ongoing = 0
    error_ratio = 0.0


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

    testruns = []

    device_groups = Testrun.objects.values_list('device_group',
                                                flat=True).distinct()

    for device_group in device_groups:
        tr_view = TestrunView()
        dg_data = Testrun.objects.filter(device_group=device_group)

        tr_view.device_group = device_group
        tr_view.top_requestor = _top_requestor(dg_data)
        tr_view.runs = dg_data.count()
        tr_view.finished = dg_data.filter(state__in=['3', '4', '5']).count()
        tr_view.waiting = dg_data.filter(state='1').count()
        tr_view.ongoing = dg_data.filter(state='2').count()
        tr_view.error_ratio = _calculate_error_ratio(dg_data)
        testruns.append(tr_view)
    
    context_dict['testruns'] = testruns
    template = loader.get_template('monitor/index.html')
    return HttpResponse(template.render(Context(context_dict)))

def _top_requestor(device_group_data):
    req_list = device_group_data.values("requestor"). \
        annotate(Count('requestor')).order_by("-requestor__count")
    return req_list[0].get('requestor')


def _calculate_error_ratio(device_group_data):
    errors = float(device_group_data.filter(state__in=['5']).count())
    others = float(device_group_data.filter(state__in=['3', '4']).count())
    error_ratio = errors / others * 100
    return "%.1f" % error_ratio

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
                      "Execution time" : [MonitorType.TEST_EXECUTION, MonitorType.TESTRUN_ENDED],
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
    runs_finished = testruns.filter(verdict__in=[0,1,2]).count()
    
    context_dict['testruns'] = testruns.order_by('-event__event_receive')
    context_dict['devicegroup'] = devicegroup
    context_dict['runcount'] = runs_on_group
    
    context_dict['finishedcount'] = runs_finished

    requestors = testruns.values_list('requestor',flat=True).distinct()
    reqs = 0
    toprtor = ''
    for requestor in requestors:
         reqsbyrtor = testruns.filter(requestor=requestor).count()
         if reqsbyrtor > reqs:
             reqs = reqsbyrtor
             toprtor = requestor
    
    context_dict['top_requestor'] = toprtor
    context_dict['top_requests'] = reqs
    
    queue_times = []
    exec_times = []
    flash_times = []
    clients = []
    for testrun in testruns:
        clients.extend(testrun.host_worker_instances.split(','))
        run_stats = stats(Event.objects.filter(testrun_id = testrun.id))
        if "Queue time" in run_stats:
            queue_times.append(run_stats['Queue time'])
        if "Flash time" in run_stats:
            flash_times.append(run_stats['Flash time'])
        if "Execution time" in run_stats:
            exec_times.append(run_stats['Execution time'])
    
    #print clients
    #sclient = set(clients)
    #print sclient
    #clients = list(sclient)
    clients = list(set(clients))
    #print clients
    context_dict['num_of_clients'] = len(clients)
    context_dict['avg_flash'] = sum(flash_times,0.0)/len(flash_times)
    context_dict['avg_queue'] = sum(queue_times,0.0)/len(queue_times)
    context_dict['avg_execution'] = sum(exec_times,0.0)/len(exec_times)
    
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
