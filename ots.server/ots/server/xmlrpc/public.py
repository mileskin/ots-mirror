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

"""
This module provides public interface for OTS server
"""

from ots.server.xmlrpc.request_handler import RequestHandler
import datetime
from ots.plugin.logger.models import LogMessage

#############################
# REQUEST_SYNC
#############################

def request_sync(sw_product, request_id, notify_list, options_dict):
    """
    Convenience function for the interface for the hub.
    Processes the raw parameters and fires a testrun

    @type sw_product: C{str}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{str}
    @param request_id: An identifier for the request from the client

    @type notify_list: C{list}
    @param notify_list: Email addresses for notifications

    @type options_dict: C{dict}
    @param options_dict: A dictionary of options
    """

    options_dict["notify_list"] = notify_list

    req_handler = RequestHandler(sw_product, request_id, **options_dict)
    return req_handler.run()

def latest_logs(seconds):
    """
    @param seconds: return logs from this many seconds ago to now
    @type: C{int}

    @rtype: C{list}
    @return: [ (run_id, date, module, levelname, message), ... ]
    """
    if seconds > 3600: # one hour
        # Prevent overly large requests that would interfere with production
        raise ValueError("Can only go back 1 hour (%s seconds requested)." \
            % seconds)
    cutoff = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
    return list(LogMessage.objects.filter(date__gte=cutoff).order_by('date')\
             .values_list('run_id', 'date', 'module', 'levelname', 'msg'))

