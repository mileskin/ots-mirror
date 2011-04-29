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

# Ignoring: Class 'LogMessage' has no 'objects' member
# pylint: disable=E1101
# Ignoring: Unused argument 'request'
# pylint: disable=W0613

import datetime
import time
import logging 
import csv

from xml.dom.minidom import getDOMImplementation

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.conf import settings
from django.template import loader, Context
from django.db.models import Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ots.common.dto.api import MonitorType
from ots.plugin.monitor.models import Testrun
from ots.plugin.monitor.models import Event
from ots.plugin.monitor.jsonrpc_service import JSONRPCService, jsonremote 
from ots.plugin.monitor.event_timedeltas import EventTimeDeltas, event_sequence
from ots.plugin.monitor.models import Testrun, Event
from ots.plugin.monitor.templatetags.monitor_template_tags import format_datetime,calculate_delta,strip_email


ROW_AMOUNT_IN_PAGE = 50

LOG = logging.getLogger(__name__) 

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

class table_writer(object):
    def __init__(self,filename=None,delimiter='|'):
        self.filename = filename
        self.delimiter = delimiter
        self.response = None
        self.writer = None
        self.row = None
        self.item = None
        self.top = None
    def create_filename(self,filename='',extension=''):
        if filename == None or filename == '':
            filename = 'ots_table'
        if extension == '':
            return filename
        dot = filename.find('.')
        if dot != -1:
            if filename[dot+1:] == extension:
                return filename
        return "%s.%s"%(filename,extension)
            
            
    def create_header(self,row):
        pass
    def new_row(self,name='row'):
        pass
    def new_item(self,title=''):
        pass
    def add_data(self,data):
        pass
    def finalize_row(self):
        pass
    def finalize(self):
        return self.response

class csv_table_writer(table_writer):
    def __init__(self,filename=None,delimiter='|'):
        self.filename = self.create_filename(filename,'csv')
        self.delimiter = delimiter
        self.response = HttpResponse(mimetype='text/csv')
        self.response['Content-Disposition'] = 'attachment; filename=%s'%self.filename
        self.writer = csv.writer(self.response,delimiter = self.delimiter)
    def create_header(self,row):
        if len(row):
            self.writer.writerow(row)
    def new_row(self,name='row'):
        self.row = []
    def add_data(self,data):
        self.row.append(data)
    def finalize_row(self):
        self.writer.writerow(self.row)

class xml_table_writer(table_writer):
    def __init__(self,filename=None,delimiter='|'):
        self.filename = self.create_filename(filename,'xml')
        self.response = HttpResponse(mimetype='text/xml')
        self.response['Content-Disposition'] = 'attachment; filename=%s'%self.filename
        impl = getDOMImplementation()
        self.writer = impl.createDocument(None,self.filename,None)
        self.top = self.writer.documentElement
    def new_row(self,name='row'):
        self.row = self.writer.createElement(name)
    def new_item(self,title=''):
        self.item = self.writer.createElement(title)
    def add_data(self,data):
        if data != '':
            node = self.writer.createTextNode(str(data))
            self.item.appendChild(node)
            self.row.appendChild(self.item)
    def finalize_row(self):
        self.top.appendChild(self.row)
    def finalize(self):
        self.writer.writexml(self.response)
        return self.response

def export_table(tabledata,rowdata,titledata=[],type='csv',filename=None,
                 csv_delimiter='|',data_unit_name='row'):
    """
        export list of items in given format
        
        Used for exporting tables from views.
        iterates through given tabledata and formats and writes
        attributes selected with rowdata.  

        @type tabledata: C{list} or C{QuerySet}
        @param tabledata: list of items to be exported

        @type rowdata: C{list}
        @param rowdata: list of item variables to be exported and how to handle them
        
        @type titledata: C{list}
        @param titledata: list of 'column' names to be used otherwise rowdata variable names is used
        
        @type type: C{str}
        @param type: type of export writer to be used (csv/xml)
        
        @type filename: C{str}
        @param filename: filename for the exported data
        
        @type csv_delimiter: C{str}
        @param csv_delimiter: delimiter to be used in csv format
        
        @type data_unit_name: C{str}
        @param data_unit_name: name of row item to be used in xml format

        @rtype: L{HttpResponse}
        @return: Returns items on table in attacment and formated to given format
    
    """

    if type == 'csv':
        writer = csv_table_writer(filename,csv_delimiter)
    else:
        writer = xml_table_writer(filename)
    writer.create_header(titledata)
    for data in tabledata:
        writer.new_row(data_unit_name)
        for i, item in enumerate(rowdata):
            func_end = item.find('|')
            if func_end == -1:
                attr_name = item
                func_name = ''
            else:
                attr_name = item[func_end+1:]
                func_name = item[:func_end]
            if len(titledata)>=i:
                title = titledata[i]
            else:
                title = attr_name
            if hasattr(data,attr_name):
                writer.new_item(title)
                attr = getattr(data,attr_name)
                if func_name in globals():
                    func = globals()[func_name]
                    writer.add_data(str(func(attr)))
                    continue
                writer.add_data(attr)
                continue
            writer.add_data('')
        writer.finalize_row()
    return writer.finalize()

def _paginate(request,list_items):
    """paginates list of items

        @type request: C{HttpResponse}
        @param request: HttpRequest of the view

        @type list_items: C{list} or C{QuerySet}
        @param list_items: list of items to be paginated

        @rtype: C{list} or C{QuerySet}
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
    
    @type request: C{HttpResponse}
    @param request: Django HTTP response
    
    @rtype: C{dict}
    @return: Filter start and end time as datetime and string
    """
    date_dict = dict()
    
    default_start = datetime.datetime.fromtimestamp(time.time() - 24 * 3600)
    default_end = datetime.datetime.fromtimestamp(time.time() + 2* 3600)
    
    start_time = None
    end_time = None
    follow = request.session.get('follow')
    
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
    @type device_group_data: C{QuerySet}
    @param device_group_data: QuerySet of testruns
    
    @rtype: C{str}, C{int}
    @return: Top requester name and amount of test requests
    """
    
    req_list = device_group_data.values("requestor"). \
        annotate(Count('requestor')).order_by("-requestor__count")
    
    if len(req_list) > 0:
        return req_list[0].get('requestor'), req_list[0].get('requestor__count')
    
    return None,0

def _generate_stats_from_events(event_list):
    """
    Generates statistic from testrun events
    
    @type event_list: L{Event<ots.plugin.monitor.models.Event>}
    @param event_list: Event database model
    
    @rtype: C{dict}
    @return: Dictionary of event statistics
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

def _calculate_average_from_events(event_list,start_event,end_event):
    """
    Calculates average time from testrun events
    
    @type event_list: L{Event<ots.plugin.monitor.models.Event>}
    @param event_list: Event database model
    
    @type start_event: L{MonitorType<ots.common.dto.api.MonitorType>}
    @param start_event: start event
    
    @type end_event: L{MonitorType<ots.common.dto.api.MonitorType>}
    @param end_event: end event
    
    @rtype: C{int}
    @return: Average time between start and end events
    """
    #src_events = event_list.filter(event_name__in=[start_event, end_event]).order_by('testrun_id')
    start_time = None
    end_time = None
    total_time = 0
    event_count = 0
    #for event in src_events:
    for event in event_list.filter(event_name__in=[start_event, end_event]).order_by('testrun_id', 'event_emit').iterator():
        #pdb.set_trace()
        if start_time != None and end_time != None:
            if start_time > end_time:
                end_time = None
                continue
            total_time += (end_time-start_time).seconds
            event_count += 1
            start_time = None
            end_time = None
            continue
        if start_event == event.event_name:
            start_time = event.event_emit
            continue
        if end_event == event.event_name:
            end_time = event.event_emit
            continue
    if start_time != None and end_time != None:
        total_time += (end_time-start_time).seconds
        event_count += 1
    if event_count:
        return total_time/event_count
    return 0
def _calculate_testrun_stats(testruns):
    """
    Calculates pass,fail,error rations and
    current status amount.
    
    @type testruns: L{Testrun<ots.plugin.monitor.models.Testrun>}
    @param testruns: Testrun database model
    
    @rtype: C{dict}
    @return: TDictionary of testrun statistic
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
    @type request: C{HttpRequest}
    @param request: HttpRequest of the view
    """
    
    context_dict = dict()
    
    context_dict.update(_handle_date_filter(request))

    testruns = []
    device_groups = Testrun.objects.values_list('device_group',
                                                flat=True).distinct()
    
    export = request.GET.get("export", "")
    orderby_filter = request.GET.get("orderby", "")
    context_dict["orderby"] = orderby_filter
    
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
        
        if tr_view.waiting == 0 and tr_view.ongoing == 0 \
           and tr_view.errors == 0 and tr_view.finished == 0:
            continue
        
        testruns.append(tr_view)
    
    if orderby_filter != None and orderby_filter != '':
        reverse=False
        if orderby_filter[0] == '-':
            reverse=True
            orderby_filter = orderby_filter[1:]
        if hasattr(TestrunView(),orderby_filter):
            testruns.sort(key=lambda testrunview: getattr(testrunview,orderby_filter),reverse=reverse)
        
    
    context_dict['testruns'] = testruns
    if export != '':
        header_row = ['Device group','Top Requestor','Top Requestor runs','Runs','Finished','Waiting','Ongoing','Error','Error Rate']
        data_row = ['device_group','strip_email|top_requestor','top_request_count','runs','finished','waiting','ongoing','errors','error_ratio']
        return export_table(testruns,data_row,header_row,type=export,data_unit_name='testrun',filename='ots_mainpage')
    template = loader.get_template('monitor/index.html')
    
    return HttpResponse(template.render(Context(context_dict)))


def view_testrun_list(request, device_group = None):
    """
    List testruns
    
    @type request: C{HttpRequest}
    @param request: HttpRequest of the view
    
    @type device_group: L{str}
    @param device_group: Name of the device group   
    """
    
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    testruns = Testrun.objects.filter( 
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])
    
    state_filter = request.GET.get("state", "")
    requestor_filter = request.GET.get("requestor", "")
    device_group_filter = request.GET.get("group", "")
    orderby_filter = request.GET.get("orderby", "")
    export = request.GET.get("export", "")
    
    context_dict["state"] = state_filter
    context_dict["group"] = device_group_filter
    context_dict["requestor"] = requestor_filter
    context_dict["orderby"] = orderby_filter
    
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
    
    if orderby_filter != "":
        orderby_filter = "%s" % orderby_filter
        if orderby_filter == "start_time" or orderby_filter == "-start_time":
            testruns = testruns.order_by(orderby_filter)
        else:
            testruns = testruns.order_by(orderby_filter, "-start_time")
    else:
        testruns = testruns.order_by("state", "-start_time")
    
    testrun_stats = _calculate_testrun_stats(testruns)
    

    context_dict['testruns'] = _paginate(request,testruns)
    context_dict['total_count'] = testrun_stats.get("runs")
    
    context_dict['inqueue_count'] = "%d (%.1f %%)" % (testrun_stats.get("inqueue"), testrun_stats.get("inqueue_ration"))
    context_dict['ongoing_count'] = "%d (%.1f %%)" % (testrun_stats.get("ongoing"), testrun_stats.get("ongoing_ration"))
    context_dict['passed_count'] = "%d (%.1f %%)" % (testrun_stats.get("passed"), testrun_stats.get("passed_ration"))
    context_dict['failed_count'] = "%d (%.1f %%)" % (testrun_stats.get("failed"), testrun_stats.get("failed_ration"))
    context_dict['error_count'] = "%d (%.1f %%)" % (testrun_stats.get("error"), testrun_stats.get("error_ration"))
    
    template = loader.get_template('monitor/testrun_list.html')
    if export != '':
        header_row = ['State','Run ID','Start time','Active time','Device group','Requestor','Workers']
        data_row = ['state','testrun_id','format_datetime|start_time','calculate_delta|start_time','device_group','strip_email|requestor','host_worker_instances']
        return export_table(testruns,data_row,header_row,type=export,data_unit_name='testrun',filename='testrun_list')
    return HttpResponse(template.render(Context(context_dict)))

def view_testrun_details(request, testrun_id):
    """
    Testrun details view
    
    @type request: C{HttpRequest}
    @param request: HttpRequest of the view
    
    @type testrun_id: L{str}
    @param testrun_id: Testrun id   
    """
    
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))
    testrun = Testrun.objects.get(testrun_id = testrun_id)
    events = Event.objects.filter(testrun_id = testrun.id)
    
    testrun_stats = _generate_stats_from_events(events)
    
    context_dict["testrun"] = testrun
    context_dict["events"] = events
    context_dict["testrun_stats"] = testrun_stats
    
    template = loader.get_template('monitor/testrun_details.html')
    return HttpResponse(template.render(Context(context_dict)))


def view_group_details(request, devicegroup):
    """ Shows testruns and details of device group view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @type devicegroup: C{str}
        @param devicegroup: name of device group
    """
    context_dict = {}
    
    context_dict.update(_handle_date_filter(request))

    #fetch testruns
    testruns = Testrun.objects.filter(device_group=devicegroup,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])

    state_filter = request.GET.get("state", "")
    requestor_filter = request.GET.get("requestor", "")
    orderby_filter = request.GET.get("orderby", "")
    export = request.GET.get("export", "")
    
    context_dict["state"] = state_filter
    context_dict["requestor"] = requestor_filter
    context_dict["orderby"] = orderby_filter
    
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
    
    if orderby_filter != "":
        orderby_filter = "%s" % orderby_filter
        if orderby_filter == "start_time" or orderby_filter == "-start_time":
            testruns = testruns.order_by(orderby_filter)
        else:
            testruns = testruns.order_by(orderby_filter, '-start_time')
    else:
        testruns = testruns.order_by('state', '-start_time')

    testrun_stats = _calculate_testrun_stats(testruns)
    runs_finished = testrun_stats.get("finished")

    context_dict['testruns'] = _paginate(request, testruns)

    context_dict['devicegroup'] = devicegroup
    context_dict['runcount'] = testrun_stats.get("runs")
    context_dict['finishedcount'] = runs_finished

    #fetch top requestor for testruns
    context_dict['top_requestor'], context_dict['top_requests'] = _top_requestor(testruns)
    
    clients = []
    event_list = Event.objects.filter(testrun_id__in=testruns.values_list('id',flat=True))
    queue_avg = _calculate_average_from_events(event_list,MonitorType.TASK_INQUEUE,MonitorType.TASK_ONGOING)
    flash_avg = _calculate_average_from_events(event_list,MonitorType.DEVICE_FLASH,MonitorType.TEST_EXECUTION)
    execute_avg = _calculate_average_from_events(event_list,MonitorType.TEST_EXECUTION, MonitorType.TESTRUN_ENDED)
    
    clients_list = testruns.values_list('host_worker_instances',flat=True)
    for client in clients_list:
        clients.extend(client.split(','))
        
    if len(clients):
        clients = list(set(clients))
    
    context_dict['num_of_clients'] = len(clients)
    context_dict['avg_queue'] = queue_avg
    context_dict['avg_flash'] = flash_avg
    context_dict['avg_execution'] = execute_avg
    if queue_avg:
        context_dict['avg_queue'] = round(queue_avg/60.0,1)
    if flash_avg:
        context_dict['avg_flash'] = round(flash_avg/60.0,1)
    if execute_avg:
        context_dict['avg_execution'] = round(execute_avg/60.0,1)
    
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
        
    template = loader.get_template('monitor/group_details_view.html')
    if export != '':
        header_row = ['State','Id','Start time','Active time','Requestor','Req Id','Error','Workers']
        data_row = ['state','testrun_id','format_datetime|start_time','calculate_delta|start_time','requestor','request_id','error','host_worker_instances']
        return export_table(testruns,data_row,header_row,type=export,data_unit_name='testrun',filename='group_details')
    return HttpResponse(template.render(Context(context_dict)))

def view_requestor_details(request, requestor):
    """ Shows testruns by requestor view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @type requestor: C{str}
        @param requestor: emali address of requestor

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    context_dict = dict()
    
    context_dict.update(_handle_date_filter(request))
    #Fetch testruns
    testruns = Testrun.objects.filter(requestor=requestor,
                                      start_time__gte = context_dict["datefilter_start"],
                                      start_time__lte = context_dict["datefilter_end"])
    
    context_dict['groups'] = testruns.values_list('device_group',flat=True).distinct()
    testrun_stats = _calculate_testrun_stats(testruns)

    state_filter = request.GET.get("state", "")
    orderby_filter = request.GET.get("orderby", "")
    device_group_filter = request.GET.get("group", "")
    export = request.GET.get("export", "")
    
    context_dict["state"] = state_filter
    context_dict["group"] = device_group_filter
    context_dict["orderby"] = orderby_filter
    
    if state_filter != "":
        state_filter = "%s" % state_filter
        if state_filter == "finished":
            testruns = testruns.filter(state__in = [2,3,4])
        else:
            state_filter = "%d" % int(state_filter)
            testruns = testruns.filter(state__in = state_filter)
    
    if device_group_filter != "":
        device_group_filter = "%s" % device_group_filter
        testruns = testruns.filter(device_group = device_group_filter)
        
    if orderby_filter != "":
        orderby_filter = "%s" % orderby_filter
        if orderby_filter == "start_time" or orderby_filter == "-start_time":
            testruns = testruns.order_by(orderby_filter)
        else:
            testruns = testruns.order_by(orderby_filter, '-start_time')
    else:
        testruns = testruns.order_by('state', '-start_time')

    
    context_dict['requestor'] = requestor
    context_dict['testruns'] = _paginate(request, testruns)
    context_dict['total_count'] = testrun_stats.get("runs")
    
    context_dict['inqueue_count'] = "%d (%.1f %%)" % (testrun_stats.get("inqueue"), testrun_stats.get("inqueue_ration"))
    context_dict['ongoing_count'] = "%d (%.1f %%)" % (testrun_stats.get("ongoing"), testrun_stats.get("ongoing_ration"))
    context_dict['passed_count'] = "%d (%.1f %%)" % (testrun_stats.get("passed"), testrun_stats.get("passed_ration"))
    context_dict['failed_count'] = "%d (%.1f %%)" % (testrun_stats.get("failed"), testrun_stats.get("failed_ration"))
    context_dict['error_count'] = "%d (%.1f %%)" % (testrun_stats.get("error"), testrun_stats.get("error_ration"))
    
    template = loader.get_template('monitor/requestor_details.html')
    if export != '':
        header_row = ['State','Run ID','Start time','Active time','Device group','Workers']
        data_row = ['state','testrun_id','format_datetime|start_time','calculate_delta|start_time','device_group','host_worker_instances']
        return export_table(testruns,data_row,header_row,type=export,data_unit_name='testrun',filename='requestor_details')
    return HttpResponse(template.render(Context(context_dict)))


###########################################
# JSONRPC API FOR CHARTS 
###########################################

def demo_chart(request):
    request.session.set_expiry(datetime.datetime.now() + 
                               datetime.timedelta(1))
    request.session.save()
    return render_to_response('demo_chart.html')


service = JSONRPCService()


@jsonremote(service)
def get_timedeltas(request, start, stop, step, device_group):
    """
    Providing the time deltas for all the steps in a testrun 
    associated with a testrun_id. 

    The order of the testrun_ids are chronological 
    (or reverse chrono for a -1 step)

    @type start: C{int}
    @param start: The start index of the iteration

    @type stop: C{int}
    @param stop: The stop index of the iteration

    @type step: C{int}
    @param step: The step of the iteration

    @type device_group: C{str}
    @param device_group: The name of the device group 
                         None returns all device groups 
   
    @rtype: A C{list} of [C{tuple} of (C{str}, 
                         [C{list} of 
                         [C{list} of C{float}]])]
    @return: A tuple of the testrun_id and the time deltas
                  for all the steps in the testrun 
    """
    ev_dt =  EventTimeDeltas(device_group)
    return list(ev_dt.deltas_iter(start, stop, step))

service.add_method('get_timedeltas', get_timedeltas)

@jsonremote(service)
def get_event_sequence(request):
    """
    @rtype: C{list} of C{str}            
    @return: The sequence of interesting events  
    """   
    return event_sequence()

service.add_method('get_event_sequence', get_event_sequence)

@jsonremote(service)
def get_total_no_of_testruns(request, device_group):
    """
    @type device_group: C{str}
    @param device_group: The name of the device group 
                         None returns all device groups 
   
    @rtype: C{int},            
    @return: The no of recorded runs of the device group  
    """
    ev_dt =  EventTimeDeltas(device_group)
    return len(ev_dt.all_testrun_ids)

service.add_method('get_total_no_of_testruns', get_total_no_of_testruns)

@jsonremote(service) 
def get_testrun_states(request, testrun_ids):
    """
    @type testrun_ids: C{list} of C{str}
    @param testrun_ids: The testrun ids to query
                        
    @rtype: C{list} of C{str} or None            
    @return: A corresponding list of states  
    """
    ret_val = []
    for testrun_id in testrun_ids:
        try:
            testrun = Testrun.objects.get(id = testrun_id)
            ret_val.append(testrun.state)
        except ObjectDoesNotExist:
            LOG.error("No Testrun for id: '%s'"%(testrun_id))
            ret_val.append(None)
    return ret_val
   
service.add_method('get_testrun_states', get_testrun_states)
