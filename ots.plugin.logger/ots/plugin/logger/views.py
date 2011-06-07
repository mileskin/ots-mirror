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

"""
Logger creates and views log messages

Example of creating log message::

  import logging
  import logging.handlers
  logger = logging.getLogger('mylogger_name')
  http_handler = logging.handlers.HTTPHandler(host_address,
                 '/logging/%s/%s/' % (servicename, run_id),method='POST',)
  logger.setLevel(logging.DEBUG)
  logger.addHandler(http_handler)
  
  logger.debug('debug message')
  logger.info('info message')
  logger.warn('warning message')
  logger.error('error message')
  logger.critical('critical message')

"""
import datetime
import socket
from copy import deepcopy

from django.http import HttpResponse
from django.conf import settings
from django.template import loader, Context
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from ots.plugin.logger.models import LogMessage

ROW_AMOUNT_IN_PAGE = 50

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

def create_message(request, servicename=None, run_id=None, worker_id=None):
    """ Creates log message to database.

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view. Request method must be POST.

        @type servicename: C{str}
        @param servicename: Service name (e.g. ots)

        @type run_id: C{int}
        @param run_id: Run id

        @type worker_id: C{int}
        @param worker_id: Worker id

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse.
    """
    if request.method == 'POST':

        if 'REMOTE_HOST' in request.META:
            remote_host = request.META['REMOTE_HOST'] #This can be empty also
        else:
            remote_host = ""

        if not remote_host: # If host name is empty, try to look up

            if request.META['REMOTE_ADDR'] == "127.0.0.1": # localhost
                remote_host = socket.gethostname()
            else:
                remote_host = socket.gethostbyaddr(request.META['REMOTE_ADDR'])[0]

        if not remote_host: # If host is still empty, use IP
            remote_host = request.META['REMOTE_ADDR']

        if worker_id:
            remote_host += '/' + worker_id

        instance = LogMessage(
            service         = servicename,
            run_id          = str(run_id),
            date            = datetime.datetime.now(),
            remote_ip       = request.META['REMOTE_ADDR'],
            remote_host     = remote_host,
            levelno         = int(request.POST['levelno']),
            levelname       = request.POST['levelname'],
            name            = request.POST['name'],
            module          = request.POST['module'],
            filename        = request.POST['filename'],
            pathname        = request.POST['pathname'],
            funcName        = request.POST['funcName'],
            lineno          = int(request.POST['lineno']),
            msg             = request.POST['msg'],
            exc_info        = str(request.POST['exc_info']) != 'None' and \
                str(request.POST['exc_info']) or None,
            exc_text        = request.POST['exc_text'] != 'None' and \
                request.POST['exc_text'] or None,
            args            = request.POST['args'] != 'None' and \
                request.POST['args'] or None,
            threadName      = request.POST['threadName'],
            thread          = float(request.POST['thread']),
            created         = float(request.POST['created']),
            process         = int(request.POST['process']),
            relativeCreated = float(request.POST['relativeCreated']),
            msecs           = float(request.POST['msecs']),
            )
        instance.save()

        return HttpResponse('Message saved')
    else:
        return HttpResponse('Request method is not POST')

def basic_testrun_viewer(request, run_id=None):
    """ Shows all messages in list view for given servicename and run id

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @type run_id: C{int}
        @param run_id: Run id

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    context_dict = {
        'run_id'    : str(run_id),
        'MEDIA_URL' : settings.MEDIA_URL,
        }

    messages = LogMessage.objects.filter(run_id=run_id).order_by("date")
    context_dict['starttime'] = messages[0].date
    context_dict['messages'] = messages

    template = loader.get_template('logger/basic_testrun_view.html')
    return HttpResponse(template.render(Context(context_dict)))

def advanced_message_viewer(request):
    """ Shows all messages in list view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    post_data = request.method == 'POST' and deepcopy(request.POST) or {}

    # Services
    post_data['services'] = ['All'] + \
        [str(item) for item in LogMessage.objects.values_list(
        'service', flat=True).distinct().order_by('service')]
    

    if request.method == 'POST':
        if post_data['selected_service'] != post_data['original_service']:
            post_data['selected_run']    = ''
            post_data['selected_module'] = 'All'
            post_data['selected_level']  = 'All'
        post_data['first_index'] = int(post_data['first_index'])
        if not post_data['selected_run'].isdigit():
            post_data['selected_run']    = ''
            
        # Paging
        if 'previous_page.x' in post_data:
            post_data['first_index'] -= ROW_AMOUNT_IN_PAGE
        elif 'next_page.x' in post_data:
            post_data['first_index'] += ROW_AMOUNT_IN_PAGE
        else:
            post_data['first_index'] = 0
    else:
        post_data['selected_service'] = (len(post_data['services']) > 1) \
            and post_data['services'][1] or 'All'
        post_data['selected_run']     = ''
        post_data['selected_module']  = 'All'
        post_data['selected_level']   = 'All'
        post_data['selected_order']   = 'newest_first'
        post_data['first_index']      = 0

    post_data['modules'] = ['All'] + \
        [str(item) for item in LogMessage.objects.filter(
        service=post_data['selected_service']).values_list(
        'module', flat=True).distinct().order_by('module')]

    post_data['levels'] = ['All'] + \
        [str(item) for item in LogMessage.objects.filter(
        service=post_data['selected_service']).values_list(
        'levelname', flat=True).distinct().order_by('levelname')]

    # Fetching messages
    if post_data['selected_service'] != 'All':
        messages = LogMessage.objects.filter(
            service=post_data['selected_service']).order_by('date', 'id')
    else:
        messages = LogMessage.objects.all().order_by('date', 'id')
    if post_data['selected_order'] != 'creation_order':
        messages = messages.reverse()

    # Filtering rows
    if post_data['selected_run']:
        messages = messages.filter(run_id=long(post_data['selected_run']))
    if post_data['selected_module'] != 'All':
        messages = messages.filter(module=post_data['selected_module'])
    if post_data['selected_level'] != 'All':
        messages = messages.filter(levelname=post_data['selected_level'])

    # Pages
    last_index = post_data['first_index'] + ROW_AMOUNT_IN_PAGE - 1
    post_data['show_prev'] = post_data['first_index'] and 1 or 0
    post_data['show_next'] = (last_index < messages.count()-1) and 1 or 0
    post_data['messages']  = messages[post_data['first_index']:last_index]

    post_data['MEDIA_URL'] = settings.MEDIA_URL
    template = loader.get_template('logger/advanced_message_view.html')
    return HttpResponse(template.render(Context(post_data)))

def view_message_details(request, log_id=None):
    """ Shows message details view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @type log_id: C{int}
        @param log_id: Message's database id

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    # Fetching row
    message = LogMessage.objects.filter(id=log_id)
    if message.count():
        message = message[0]

    template = loader.get_template('logger/message_details_view.html')
    context_dict = {
        'message'   : message,
        'MEDIA_URL' : settings.MEDIA_URL,
        }
    return HttpResponse(template.render(Context(context_dict)))

def view_workers(request):
    """ Shows workers view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    
    message = []
    
    
    for remote_host, remote_ip in LogMessage.objects.values_list(
         'remote_host', 'remote_ip').distinct().order_by('remote_host'):
        data = dict()
        data['remote_host'] = remote_host
        data['remote_ip'] = remote_ip
        msgs = LogMessage.objects.filter(remote_host=remote_host).order_by('-date')
        date = msgs[:1][0].date
        
        msg = msgs[:1][0].msg
        if len(msg) > 40:
            msg = msg[0:37] + '...'
        data['msg'] = msg
        data['date'] = str(date).split('.')[:1][0]
        message.append(data)

    # Sort hosts to have latest as first
    message.sort(key=lambda data: data['date'], reverse=True)
   
    template = loader.get_template('logger/workers_view.html')
    context_dict = {
        'message'   : message,
        'MEDIA_URL' : settings.MEDIA_URL,
        }
    return HttpResponse(template.render(Context(context_dict)))

def view_worker_details(request, remote_host=None):
    """ Shows message details view

        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

        @type remote_host: C{str}
        @param remote_host: Worker's host name

        @rtype: L{HttpResponse}
        @return: Returns HttpResponse containing the view.
    """
    run_ids = LogMessage.objects.filter(remote_host=remote_host)
    run_ids = run_ids.values_list('run_id').distinct()

    messages = []
    
    for run in run_ids:
        message = LogMessage.objects.filter(run_id = run[0]).order_by('-date')[0]
        messages.append(message)
    
    messages = sorted(messages, key=lambda message: message.date, reverse=True)

    template = loader.get_template('logger/advanced_message_view.html')
    context_dict = {
        'messages'   : messages,
        'remote_host': remote_host,
        }
    return HttpResponse(template.render(Context(context_dict)))

def main_page(request):
    """
        Index page for viewing summary from all test runs.
        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

    """
    context_dict = {
    'MEDIA_URL' : settings.MEDIA_URL,
    }

    messages = LogMessage.objects.get_latest_messages().order_by('-created')
    
    context_dict['messages']  = _paginate(request,messages)
    template = loader.get_template('logger/index.html')
    return HttpResponse(template.render(Context(context_dict)))

def filter_message_viewer(request):
    """
        Page for viewing filtered messages from all test runs.
        @type request: C{HttpRequest}
        @param request: HttpRequest of the view

    """
    post_data = request.method == 'POST' and deepcopy(request.POST) or {}
    
    post_data['services'] = ['All'] + \
        [str(item) for item in LogMessage.objects.values_list(
        'service', flat=True).distinct().order_by('service')]
        
    if request.method == 'POST':
        if post_data['selected_service'] != post_data['original_service']:
            post_data['selecter_run'] = ''
            post_data['selected_host'] = 'All'
            post_data['selected_module'] = 'All'
            post_data['selected_level']  = 'All'
            post_data['selected_message'] = ''
        post_data['first_index'] = int(post_data['first_index'])
                    
        # Paging
        if 'previous_page' in post_data:
            post_data['first_index'] -= ROW_AMOUNT_IN_PAGE
        elif 'next_page' in post_data:
            post_data['first_index'] += ROW_AMOUNT_IN_PAGE
        else:
            post_data['first_index'] = 0
    else:
        post_data['selected_service'] = (len(post_data['services']) > 1) \
            and post_data['services'][1] or 'All'
        post_data['selected_run']     = ''
        post_data['selected_host']    = 'All'
        post_data['selected_module']  = 'All'
        post_data['selected_level']   = 'All'
        post_data['selected_order']   = 'newest_first'
        post_data['first_index']      = 0
        post_data['selected_message'] = ''
    
    if 'use_regexp' in post_data:
        post_data['use_regexp'] = True
    else:
        post_data['use_regexp'] = False
    
    post_data['modules'] = ['All'] + \
        [str(item) for item in LogMessage.objects.filter(
        service=post_data['selected_service']).values_list(
        'module', flat=True).distinct().order_by('module')]

    post_data['levels'] = ['All'] + \
        [str(item) for item in LogMessage.objects.filter(
        service=post_data['selected_service']).values_list(
        'levelname', flat=True).distinct().order_by('levelname')]
      
    post_data['hosts'] = ['All'] + \
        [str(item) for item in LogMessage.objects.distinct(
        ).values_list('remote_host', flat=True).order_by('remote_host')]

    # Fetching messages
    if post_data['selected_service'] != 'All':
        messages = LogMessage.objects.filter(
            service=post_data['selected_service']).order_by('date', 'id')
    else:
        messages = LogMessage.objects.all().order_by('date', 'id')
    
    if post_data['selected_order'] != 'creation_order':
        messages = messages.reverse()

    # Filtering rows
    if post_data['selected_message'] != '':
        if post_data['use_regexp']:
            messages = messages.filter(msg__regex=post_data['selected_message'])
        else:
            messages = messages.filter(msg__icontains=post_data['selected_message'])
    if post_data['selected_run'] != '':
        messages = messages.filter(run_id=post_data['selected_run'])
    if post_data['selected_host'] != 'All':
        messages = messages.filter(remote_host=post_data['selected_host'])
    if post_data['selected_module'] != 'All':
        messages = messages.filter(module=post_data['selected_module'])
    if post_data['selected_level'] != 'All':
        messages = messages.filter(levelname=post_data['selected_level'])
      
    
    post_data['messages'] = messages
    post_data['MEDIA_URL'] = settings.MEDIA_URL
    
    # Pages
    last_index = post_data['first_index'] + ROW_AMOUNT_IN_PAGE - 1
    post_data['show_prev'] = post_data['first_index'] and 1 or 0
    post_data['show_next'] = (last_index < messages.count()-1) and 1 or 0
    post_data['messages']  = messages[post_data['first_index']:last_index]
    
    
    template = loader.get_template('logger/filter_message_view.html')
    return HttpResponse(template.render(Context(post_data)))
