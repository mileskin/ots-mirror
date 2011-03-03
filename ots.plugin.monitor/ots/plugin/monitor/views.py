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

import datetime
import time

from django.http import HttpResponse
from django.conf import settings
from django.template import loader, Context
from django.db.models import Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event
from ots.common.dto.api import MonitorType

ROW_AMOUNT_IN_PAGE = 50

#
# Helping classes and functions
#
class TestrunView():
    device_group = None
    top_requestor = None
    top_request_count = 0
    runs = 0
    finished = 0
    waiting = 0
    ongoing = 0
    errors = 0
    error_ratio = 0.0

class Stats(object):
    name = ""
    delta = 0
    
    def __init__(self, name, delta):
        self.name = name
        self.delta = delta

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
    """
    Checks date filter from the HTTP request
    and saves new time to session.
    
    @type request: C{django.http.HttpResponse}
    @param request: Django HTTP response
    
    @rtype C{dict}
    @rparam Filter start and end time as datetime and string
    """
    date_dict = dict()
    
    default_start = datetime.datetime.fromtimestamp(time.time() - 24 * 3600)
    default_end = datetime.datetime.fromtimestamp(time.time() + 2* 3600)
    
    start_time = None
    end_time = None
    follow = request.session.get('follow')
    
    print follow
    
    if request.method == 'POST':
        post = request.POST
        if "submit_clear" in post:
            start_time = default_start
            end_time = default_end
            follow = True
        else:
            follow = False
            try:
                start_time = datetime.datetime.strptime(post.get("startdate"), "%Y-%m-%d %H:%M")
            except ValueError:
                start_time = datetime.datetime(year=1900, month=1, day=1)
            try:
                end_time = datetime.datetime.strptime(post.get("enddate"), "%Y-%m-%d %H:%M")
            except ValueError:
                end_time = datetime.datetime.now()
    else:
        # By 
        if follow is None:
            follow = True
        
        if follow:
            start_time = default_start
            end_time = default_end
        else:
            start_time  = request.session.get("datefilter_start")
            end_time  =  request.session.get("datefilter_end")
    
    date_dict['datefilter_start']  = start_time
    date_dict['datefilter_end']  = end_time
    date_dict['follow']  = follow
    
    request.session.update(date_dict)
    
    date_dict['datefilter_start_str']  = start_time.strftime("%Y-%m-%d %H:%M")
    date_dict['datefilter_end_str']  = end_time.strftime("%Y-%m-%d %H:%M")
    
    return date_dict

def _top_requestor(device_group_data):
    """    
    @type request: C{django.http.HttpResponse}
    @param request: Django HTTP response
    
    @rtype C{str}, C{int}
    @rparam Top requester name and amount of test requests
    """
    
    req_list = device_group_data.values("requestor"). \
        annotate(Count('requestor')).order_by("-requestor__count")
    
    if len(req_list) > 0:
        return req_list[0].get('requestor'), req_list[0].get('requestor__count')
    
    return None,0

def _generate_stats_from_events(event_list):
    """
    Generates statistic from testrun events
    
    @type event_list: C{Event}
    @param event_list: Event database model
    
    @rtype C{dict}
    @rparam Dictionary of event statistics
    """
    
    event_category = {
                      "Queue time" : [MonitorType.TASK_INQUEUE, MonitorType.TASK_ONGOING],
                      # BOOT event not supported yet
                      "Flash time" : [MonitorType.DEVICE_FLASH, MonitorType.TEST_EXECUTION],
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

def _calculate_testrun_stats(testruns):
    """
    Calculates pass,fail,error rations and
    current status amount.
    
    @type testruns: C{Testrun}
    @param testruns: Testrun database model
    
    @rtype C{dict}
    @rparam TDictionary of testrun statistic
    """
    retDict = dict()
    retDict["inqueue_ration"] = 0
    retDict["ongoing_ration"] = 0
    retDict["passed_ration"] = 0
    retDict["failed_ration"] = 0
    retDict["error_ration"] = 0
    
    
    total_count = testruns.count()
    inqueue_count = testruns.filter(state = 0).count()
    ongoing_count = testruns.filter(state = 1).count()
    passed_count = testruns.filter(state = 2).count()
    failed_count = testruns.filter(state = 3).count()
    error_count = testruns.filter(state = 4).count()
    finished_count = passed_count + failed_count + error_count

    retDict["runs"] = total_count
    retDict["inqueue"] = inqueue_count
    retDict["ongoing"] = ongoing_count
    retDict["passed"] = passed_count
    retDict["failed"] = failed_count
    retDict["error"] = error_count
    retDict["finished"] = finished_count
    
    if total_count > 0:
        retDict['inqueue_ration'] = (100.0*inqueue_count/total_count)
        retDict['ongoing_ration'] = (100.0*ongoing_count/total_count)
    if finished_count >0:
        retDict['passed_ration'] = (100.0*passed_count/finished_count)
        retDict['failed_ration'] = (100.0*failed_count/finished_count)
        retDict['error_ration'] = (100.0*error_count/finished_count)
    
    return retDict

#
# Monitor WebUI Views
#

def main_page(request):
    """
    Index page for viewing summary from all test runs.
    @type request: L{HttpRequest}
    @param request: HttpRequest of the view
    """
    
    context_dict = dict()
    
    context_dict.update(_handle_date_filter(request))

    testruns = []
    start = time.time()
    device_groups = Testrun.objects.values_list('device_group',
                                                flat=True).distinct()

    for device_group in device_groups:
        tr_view = TestrunView()
        dg_data = Testrun.objects.filter(device_group=device_group,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])

        tr_view.device_group = device_group
        tr_view.top_requestor,tr_view.top_request_count = _top_requestor(dg_data)
        testrun_stats = _calculate_testrun_stats(dg_data)
        tr_view.runs = testrun_stats.get("runs")
        tr_view.waiting = testrun_stats.get("inqueue")
        tr_view.ongoing = testrun_stats.get("ongoing")
        tr_view.errors =  testrun_stats.get("error")
        tr_view.finished = testrun_stats.get("finished")
        tr_view.error_ratio = "%.1f" % testrun_stats.get("error_ration")
        
        testruns.append(tr_view)
    
    context_dict['testruns'] = testruns
    t = time.time()-start
    print "main_page",t
    template = loader.get_template('monitor/index.html')
    return HttpResponse(template.render(Context(context_dict)))


def view_testrun_list(request, device_group = None):
    """
    List testruns
    
    @type request: L{HttpRequest}
    @param request: HttpRequest of the view
    
    @type queue_name: L{device_group}
    @param queue_name: Name of the device group   
    """
    
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    start = time.time()
    testruns = Testrun.objects.filter( 
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])
    
    state_filter = request.GET.get("state", "")
    requestor_filter = request.GET.get("requestor", "")
    device_group_filter = request.GET.get("group", "")
    
    context_dict["state"] = state_filter
    context_dict["group"] = device_group_filter
    context_dict["requestor"] = requestor_filter
    
    if state_filter != "":
        state_filter = "%s" % state_filter
        if state_filter == "finished":
            testruns = testruns.filter(state__in = [2,3,4])
        else:
            state_filter = "%d" % int(state_filter)
            testruns = testruns.filter(state__in = state_filter)
    
    if requestor_filter != "":
        requestor_filter = "%s" % requestor_filter
        testruns = testruns.filter(requestor = requestor_filter)
        
    if device_group_filter != "":
        device_group_filter = "%s" % device_group_filter
        testruns = testruns.filter(device_group = device_group_filter)
    
    testruns = testruns.order_by("state")
    
    testrun_stats = _calculate_testrun_stats(testruns)
    

    context_dict['testruns'] = _paginate(request,testruns)
    context_dict['total_count'] = testrun_stats.get("runs")
    
    context_dict['inqueue_count'] = "%d (%.1f %%)" % (testrun_stats.get("inqueue"), testrun_stats.get("inqueue_ration"))
    context_dict['ongoing_count'] = "%d (%.1f %%)" % (testrun_stats.get("ongoing"), testrun_stats.get("ongoing_ration"))
    context_dict['passed_count'] = "%d (%.1f %%)" % (testrun_stats.get("passed"), testrun_stats.get("passed_ration"))
    context_dict['failed_count'] = "%d (%.1f %%)" % (testrun_stats.get("failed"), testrun_stats.get("failed_ration"))
    context_dict['error_count'] = "%d (%.1f %%)" % (testrun_stats.get("error"), testrun_stats.get("error_ration"))
    
    t = time.time()-start
    print "view_testrun_list",t
    template = loader.get_template('monitor/testrun_list.html')
    return HttpResponse(template.render(Context(context_dict)))

def view_testrun_details(request, testrun_id):
    """
    Testrun details view
    
    @type request: L{HttpRequest}
    @param request: HttpRequest of the view
    
    @type testrun_id: L{str}
    @param testrun_id: Testrun id   
    """
    
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    start = time.time()
    testrun = Testrun.objects.get(testrun_id = testrun_id)
    events = Event.objects.filter(testrun_id = testrun.id)
    
    testrun_stats = _generate_stats_from_events(events)
    
    context_dict["testrun"] = testrun
    context_dict["events"] = events
    context_dict["testrun_stats"] = testrun_stats
    
    t = time.time()-start
    print "view_testrun_details",t
    template = loader.get_template('monitor/testrun_details.html')
    return HttpResponse(template.render(Context(context_dict)))


def view_group_details(request, devicegroup):
    """ Shows testruns and details of device group view

        @type request: L{HttpRequest}
        @param request: HttpRequest of the view

        @type devicegroup: L{string}
        @param devicegroup: name of device group
        
        @type state: L{string}
        @param state: filter test runs with state
        
        @type requestor: L{string}
        @param requestor: filter test runs with requestor
    """
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    start = time.time()
    
    #fetch testruns
    testruns = Testrun.objects.filter(device_group=devicegroup,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])


    state_filter = request.GET.get("state", "")
    requestor_filter = request.GET.get("requestor", "")
    
    context_dict["state"] = state_filter
    context_dict["requestor"] = requestor_filter
    
    if state_filter != "":
        state_filter = "%s" % state_filter
        if state_filter == "finished":
            testruns = testruns.filter(state__in = [2,3,4])
        else:
            state_filter = "%d" % int(state_filter)
            testruns = testruns.filter(state__in = state_filter)
    
    if requestor_filter != "":
        requestor_filter = "%s" % requestor_filter
        testruns = testruns.filter(requestor = requestor_filter)

    testrun_stats = _calculate_testrun_stats(testruns)
    runs_finished = testrun_stats.get("finished")
    
    context_dict['testruns'] = _paginate(request, testruns.order_by('state', 'start_time'))
    context_dict['devicegroup'] = devicegroup
    context_dict['runcount'] = testrun_stats.get("runs")
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
        run_stats = _generate_stats_from_events(Event.objects.filter(testrun_id = testrun.id))
        
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
    
    if len(clients):
        clients = list(set(clients))
    
    context_dict['num_of_clients'] = len(clients)
    if queue_count:
        context_dict['avg_queue'] = round(queue_time/queue_count/60.0,1)
    if flash_count:
        context_dict['avg_flash'] = round(flash_time/flash_count/60.0,1)
    if exec_count:
        context_dict['avg_execution'] = round(exec_time/exec_count/60.0,1)
    
    #get run counts
    passed_runs = testrun_stats.get("passed")
    failed_runs = testrun_stats.get("failed")
    error_runs = testrun_stats.get("error")
    inqueue_runs = testrun_stats.get("inqueue")
    
    context_dict['passed_runs'] = passed_runs
    context_dict['failed_runs'] = failed_runs
    context_dict['error_runs'] = error_runs
    context_dict['ongoing_runs'] = testrun_stats.get("ongoing")
    context_dict['inqueue_runs'] = inqueue_runs
    context_dict['error_rate'] = "%.1f" % testrun_stats.get("error_ration")
    context_dict['pass_rate'] = "%.1f" % testrun_stats.get("passed_ration")
    context_dict['fail_rate'] = "%.1f" % testrun_stats.get("failed_ration")
        
    t = time.time()-start
    print "view_group_details",t
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
    context_dict = dict()
    
    context_dict.update(_handle_date_filter(request))
    start = time.time()
    #Fetch testruns
    testruns = Testrun.objects.filter(requestor=requestor,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])

    testruns = testruns.order_by("state")
    testrun_stats = _calculate_testrun_stats(testruns)
    
    context_dict['requestor'] = requestor
    context_dict['testruns'] = _paginate(request, testruns)
    context_dict['total_count'] = testrun_stats.get("runs")
    
    context_dict['inqueue_count'] = "%d (%.1f %%)" % (testrun_stats.get("inqueue"), testrun_stats.get("inqueue_ration"))
    context_dict['ongoing_count'] = "%d (%.1f %%)" % (testrun_stats.get("ongoing"), testrun_stats.get("ongoing_ration"))
    context_dict['passed_count'] = "%d (%.1f %%)" % (testrun_stats.get("passed"), testrun_stats.get("passed_ration"))
    context_dict['failed_count'] = "%d (%.1f %%)" % (testrun_stats.get("failed"), testrun_stats.get("failed_ration"))
    context_dict['error_count'] = "%d (%.1f %%)" % (testrun_stats.get("error"), testrun_stats.get("error_ration"))
    
    t = time.time()-start
    print "view_requestor_details",t
    template = loader.get_template('monitor/requestor_details.html')
    return HttpResponse(template.render(Context(context_dict)))
