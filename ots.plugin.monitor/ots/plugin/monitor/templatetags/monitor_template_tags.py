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

# Ignoring: Invalid name "register" 
#           (should match (([A-Z_][A-Z1-9_]*)|(__.*__))$)
# register should be written lowercase letters
# pylint: disable=C0103

"""
Template tags for monitor
"""

import time, logging, datetime
from django import template
register = template.Library()

@register.filter
def convert_epoch_to_string(value):
    """
    Converts epoch value to string
    """
    return time.ctime(float(value))

@register.filter
def result_judge(levelname, levelnumber):
    """
    If loglevel is error or bigger, mark it with red tag
    """
    if int(levelnumber) >= logging.ERROR:
        strOut = '<div class="red"><b>%s</b></div>' % levelname
    else:
        strOut = levelname
    return strOut

@register.filter
def calculate_delta(starttime):
    """
    Calculates delta time
    """
    currenttime = datetime.datetime.now()
    strout = (currenttime - starttime)
    return strout

@register.filter
def calculate_delta_sec(starttime):
    """
    Calculate delta time between seconds
    """
    currenttime = time.time()
    strout = (currenttime - starttime)
    return strout

@register.filter
def format_datetime(currenttime):
    """
    Formats datetime for nicer format
    """
    strout = currenttime.strftime("%Y-%m-%d %H:%M:%S")
    return strout

@register.filter
def strip_email(email):
    """
    Strips the end of email address
    """
    if email is not None:
        return email.split('@')[0]

@register.filter
def state_as_string(state):
    """
    Change state (integer) to string
    """
    retStr = "In queue"
    if state == "1":
        retStr = "Ongoing"
    elif state == "2":
        retStr = "Passed"
    elif state == "3":
        retStr = "Failed"
    elif state == "4":
        retStr = "Error"
    return retStr

@register.filter
def logger_url(runid):
    """
    Reverse django python path to url
    """
    
    url = "http://logger_plugin_not_installed/%s" % (runid)
    try:
        from ots.plugin.logger.views import basic_testrun_viewer
        from django.core.urlresolvers import reverse
        url = reverse(basic_testrun_viewer, args=[runid])
    finally:
        return url

@register.filter
def format_orderby(current, order):
    if current is None or current == '':
        return order
    base = current
    if current[0] == '-':
        base = current[1:]

    if base == order:
        if current[0]=='-':
            return order
        else:
            return '-%s'%order
    return order

@register.filter
def order_dir(current, order):
    if current is None or current == '':
        return ''
    base = current
    if current[0] == '-':
        base = current[1:]
    if base == order:
        if current[0]=='-':
            return 'desc'
        else:
            return 'asc'
    return ''
