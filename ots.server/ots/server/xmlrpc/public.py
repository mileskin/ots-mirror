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
import copy

from ots.server.hub.api import Hub, result_to_string, OptionsFactory
from ots.server.xmlrpc.process_handler import ProcessHandler


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

    LOG.info(("Incoming request: program: %s," \
              " request: %s, notify_list: %s, " \
              "options: %s") % \
             (sw_product, request_id, notify_list, options_dict))

    options_dict["notify_list"] = notify_list

    # hub = Hub(sw_product, request_id, **options_dict)
    req_handler = RequestHandler(sw_product, request_id, **options_dict)
    
    # TODO: Check tests
    #if DEBUG:
    #    hub._taskrunner = MockTaskRunnerResultsPass()
    
    #return result_to_string(hub.run())
    return req_handler.run()



class RequestHandler(object):
    
    def __init__(self, sw_product, request_id, **options_dict):
        self.sw_product = sw_product
        self.request_id = request_id
        self.options_dict = options_dict
        
        self.process_handler = ProcessHandler()
        self._options_factory = OptionsFactory(self.sw_product, options_dict)
        
        self.hubs = None
    
    def run(self):
        self._create_hubs()
        return self._run_hubs()

    #########################
    # HELPERS
    #########################
    
    def _create_hubs(self):
        #testrun_list = []
        #process_queues = []
        
        #if self._options_factory.processed_core_options_dict['device']:
        #    pass
        #else:
        import pdb; pdb.set_trace()
        self.hubs = Hub(self.sw_product,
                        self.request_id,
                        **self.options_dict)

    def _run_hubs(self):
        return self.hubs.run()
    
    
