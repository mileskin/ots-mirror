# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Mikko Makinen <mikko.al.makinen@nokia.com>
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

import logging
from ots.server.hub.api import Hub, result_to_string
from ots.server.distributor.api import TaskRunner


LOG = logging.getLogger()

################################
# HACKISH TESTING CAPABILITIES
################################

DEBUG = False

if DEBUG:
    from ots.server.hub.tests.component.mock_taskrunner import \
                                       MockTaskRunnerResultsPass


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

    #FIXME legacy interface 
    @type options_dict: C{dict}
    @param options_dict: A dictionary of options
    """
    
    LOG.info(("Incoming request: program: %s,"\
                  " request: %s, notify_list: %s, "\
                  "options: %s") %\
                 (sw_product, request_id, notify_list, options_dict))

    options_dict["notify_list"] = notify_list

    hub = Hub(sw_product, request_id, **options_dict)
    if DEBUG:
        hub._taskrunner = MockTaskRunnerResultsPass()
    return result_to_string(hub.run())
