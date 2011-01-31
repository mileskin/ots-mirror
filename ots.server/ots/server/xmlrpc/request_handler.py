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

from ots.server.hub.api import Hub
from ots.server.hub.parameters_parser import string_2_dict
from ots.server.xmlrpc.process_handler import ProcessHandler
from multiprocessing import Queue


LOG = logging.getLogger()

REQUEST_ERROR = 'ERROR'
REQUEST_FAIL = 'FAIL'
REQUEST_PASS = 'PASS'

class RequestHandler(object):
    
    def __init__(self, sw_product, request_id, **options_dict):
        LOG.info(("Request handler init(): swproduct: %s," \
                  " request_id: %s, options: %s") % \
                 (sw_product, request_id, options_dict))
        
        self.sw_product = sw_product
        self.request_id = request_id
        self.options_dict = options_dict
        
        self.process_handler = ProcessHandler()
        
        self.hubs_params = []
        self.process_queues = []
    
    def run(self):
        try:
            self._init_hub_params()
            
            for params in self.hubs_params:
                self.process_handler.add_process(_run_hub, params)
            
            # Check that we have tasks to run
            if not self.process_handler.child_processes:
                return REQUEST_ERROR
            
            # Start processes ...
            self.process_handler.start_processes()
            
            # Read process queues
            results = self._read_queues()
            
            # Join processes
            self.process_handler.join_processes()
            
            # Check return values from test runs
            return self._check_testruns_result_values(results.values())
        except ValueError:
            return REQUEST_ERROR

    #########################
    # HELPERS
    #########################
    
    def _init_hub_params(self):
        if self.options_dict.get('device'):
            device_specs = self.options_dict['device'].split(';')
            
            for spec in device_specs:
                # Check that we have valid device specs
                if not self._validate_devicespecs(spec):
                    continue
                
                options, pq = self._prepare_params(spec)
                
                self.process_queues.append(pq)
                self.hubs_params.append((pq,
                                         self.sw_product,
                                         self.request_id,
                                         options))
        else:
            options, pq = self._prepare_params()
            
            self.process_queues.append(pq)
            self.hubs_params.append((pq,
                                     self.sw_product,
                                     self.request_id,
                                     options))

    def _prepare_params(self, device_spec=None):
        options = copy.deepcopy(self.options_dict)
        if device_spec:
            options['device'] = device_spec
        
        return options, Queue()

    def _read_queues(self):
        """
        Returns testrun_id and result pairs
        
        @rtype: C{dict}
        @return: Dictionary that contains testrun_id and result pairs
        """
        queue_results = {}
        #import pdb; pdb.set_trace()
        for process_queue in self.process_queues:
            queue_results.update(process_queue.get())
        
        return queue_results
    
    def _check_testruns_result_values(self, result_values):
        """
        Checks overall testrun status and returns value
    
        @param result_values: List containing result values from executed testruns
        @type result_values: C{list}
    
        @rtype: C{list} consisting of C{string}
        @return: The converted string
        """
        if REQUEST_ERROR in result_values:
            return REQUEST_ERROR
        elif REQUEST_FAIL in result_values:
            return REQUEST_FAIL
        return REQUEST_PASS
    
    def _validate_devicespecs(self, device_specs):
        """
        Returns boolean value based on device_specs
        validation
    
        @param device_specs: String that contains device specifications
        @type options: C{Str}
    
        @rtype: C{Boolean}
        @return: True if device_specs are valid, False otherwise
        """
        spec_dict = string_2_dict(device_specs)
        
        for spec in spec_dict:
            if spec not in ['devicegroup', 'devicename', 'deviceid']:
                return False
        
        return True


def _run_hub(pq, sw_product, request_id, options_dict):
    hub = Hub(sw_product, request_id, **options_dict)
    result = hub.run()
    
    pq.put({hub.testrun_uuid : result})



