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
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event
from ots.common.dto.api import MonitorType


ROW_AMOUNT_IN_PAGE = 50


def _paginate(request,list_items):
    """paginates list of items

        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

        @type list_items: C{list} or C{QuerySet}
        @param list_items: list of items to be paginated

        @rtype: L{list} or L{QuerySet}
        @return: Returns items on page
    
    """
    paginator = Paginator(list_items,ROW_AMOUNT_IN_PAGE)
    try: 
        page = int(request.GET.get('page','1'))
    except ValueError:
        page = 1
    try:
        list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        list = paginator.page(paginator.num_pages)
    return list

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
    top_request_count = 0
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

    testruns = []

    device_groups = Testrun.objects.values_list('device_group',
                                                flat=True).distinct()

    for device_group in device_groups:
        tr_view = TestrunView()
        dg_data = Testrun.objects.filter(device_group=device_group,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])

        (tr_view.top_requestor, tr_view.top_request_count) = _top_requestor(dg_data)
        tr_view.device_group = device_group
        tr_view.runs = dg_data.count()
        tr_view.finished = dg_data.filter(state__in=['2', '3', '4']).count()
        tr_view.waiting = dg_data.filter(state='0').count()
        tr_view.ongoing = dg_data.filter(state='1').count()
        tr_view.error_ratio = _calculate_error_ratio(dg_data)
        testruns.append(tr_view)
    
    context_dict['testruns'] = testruns
    template = loader.get_template('monitor/index.html')
    return HttpResponse(template.render(Context(context_dict)))

def _top_requestor(device_group_data):
    req_list = device_group_data.values("requestor"). \
        annotate(Count('requestor')).order_by("-requestor__count")
    
    if len(req_list) > 0:
        return req_list[0].get('requestor'), req_list[0].get('requestor__count')
    
    return None,0


def _calculate_error_ratio(device_group_data):
    errors = float(device_group_data.filter(state__in=['4']).count())
    others = float(device_group_data.filter(state__in=['2', '3']).count())
    if others != 0.0:
        error_ratio = errors / others * 100
    else:
        error_ratio = 0.0
    return "%.1f" % error_ratio

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
    
    context_dict['testruns'] = _paginate(request,testruns)
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


def view_group_details(request, devicegroup):
    """ Shows testruns and details of device group view

        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

        @type devicegroup: C{string}
        @param devicegroup: name of device group

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    context_dict.update(_handle_date_filter(request))
    
    #fetch testruns
    testruns = Testrun.objects.filter(device_group=devicegroup,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])
    
    
    runs_finished = testruns.filter(state__in=[2,3,4]).count()
    
    context_dict['testruns'] = _paginate(request,testruns.order_by('state', 'start_time'))
    context_dict['devicegroup'] = devicegroup
    context_dict['runcount'] = testruns.count()
    context_dict['finishedcount'] = runs_finished

    #fetch top requestor for testruns
    context_dict['top_requestor'], context_dict['top_requests'] = _top_requestor(testruns)
        
    #calculate average times
    queue_time = 0
    queue_count = 0
    flash_time = 0
    flash_count = 0
    exec_time = 0
    exec_count = 0
    clients = []
    for testrun in testruns:
        clients.extend(testrun.host_worker_instances.split(','))
        run_stats = stats(Event.objects.filter(testrun_id = testrun.id))
        
        for stat in run_stats:
            if stat.name == "Queue time":
                queue_time += stat.delta.seconds
                queue_count += 1 
            if stat.name == "Flash time":
                flash_time += stat.delta.seconds
                flash_count += 1
            if stat.name == "Execution time":
                exec_time += stat.delta.seconds
                exec_count += 1
    
    clients = list(set(clients))
    context_dict['num_of_clients'] = len(clients)
    context_dict['avg_queue'] = round(queue_time/queue_count/60.0,1)
    context_dict['avg_flash'] = round(flash_time/flash_count/60.0,1)
    context_dict['avg_execution'] = round(exec_time/exec_count/60.0,1)
    
    #get run counts
    passed_runs = testruns.filter(state=2).count()
    failed_runs = testruns.filter(state=3).count()
    error_runs = testruns.filter(state=4).count()
    
    context_dict['passed_runs'] = passed_runs
    context_dict['failed_runs'] = failed_runs
    context_dict['error_runs'] = error_runs
    context_dict['ongoing_runs'] = testruns.filter(state=1).count()
    
    #calculate rates
    context_dict['error_rate'] = round((1.0*error_runs/runs_finished)*100,2)
    context_dict['pass_rate'] = round((1.0*passed_runs/runs_finished)*100,2)
    context_dict['fail_rate'] = round((1.0*failed_runs/runs_finished)*100,2)  
    
    template = loader.get_template('monitor/group_details_view.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_requestor_details(request, requestor):
    """ Shows testruns by requestor view

        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

        @type requestor: C{string}
        @param requestor: emali address of requestor

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }
    
    context_dict.update(_handle_date_filter(request))
    
    #Fetch testruns
    testruns = Testrun.objects.filter(requestor=requestor,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])

    context_dict['requestor'] = requestor
    context_dict['testruns'] = _paginate(request,testruns)
    context_dict['total_count'] = testruns.count()
    context_dict['onqueue_count'] = testruns.filter(state = 0).count()
    context_dict['execution_count'] = testruns.filter(state = 1).count()
    
    template = loader.get_template('monitor/requestor_details.html')
    return HttpResponse(template.render(Context(context_dict)))

