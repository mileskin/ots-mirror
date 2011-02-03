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

"""
Module for handling OTS requests
"""

#import logging
import copy

from ots.server.hub.api import Hub
from ots.server.hub.parameters_parser import string_2_dict
from ots.server.xmlrpc.process_handler import ProcessHandler
from multiprocessing import Queue
from unittest import TestResult


#LOG = logging.getLogger()

REQUEST_ERROR = 'ERROR'
REQUEST_FAIL = 'FAIL'
REQUEST_PASS = 'PASS'

class RequestHandler(object):
    """
    Handles OTS requests and splits them to several parallel testruns if
    needed.
    """
    
    def __init__(self, sw_product, request_id, **options_dict):
        
        #LOG.info(("Request handler init(): swproduct: %s," \
        #          " request_id: %s, options: %s") % \
        #         (sw_product, request_id, options_dict))
        
        self.sw_product = sw_product
        self.request_id = request_id
        self.options_dict = options_dict
        
        self.process_handler = ProcessHandler()
        
        self.hubs_params = []
        self.process_queues = []
    
    def run(self):
        """
        Start testruns in separate processes and collect results
        """
        
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
            return _check_testruns_result_values(results.values())
        except ValueError:
            return REQUEST_ERROR

    #########################
    # HELPERS
    #########################
    
    def _init_hub_params(self):
        """
        Initialize parameters for each testrun
        """
        
        if self.options_dict.get('device'):
            device_specs = self.options_dict['device'].split(';')
            
            for spec in device_specs:
                # Check that we have valid device specs
                if not _validate_devicespecs(spec):
                    continue
                
                options, queue = self._prepare_params(spec)
                
                self.process_queues.append(queue)
                self.hubs_params.append((queue,
                                         self.sw_product,
                                         self.request_id,
                                         options))
        else:
            options, queue = self._prepare_params()
            
            self.process_queues.append(queue)
            self.hubs_params.append((queue,
                                     self.sw_product,
                                     self.request_id,
                                     options))

    def _prepare_params(self, device_spec=None):
        """
        Set device specifications and return copy of parameters and a new
        queue
        """
        
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
        
        for process_queue in self.process_queues:
            queue_results.update(process_queue.get())
        
        return queue_results




def _check_testruns_result_values(result_values):
    """
    Checks overall testrun status and returns value

    @param result_values: List containing result values from executed
                          testruns. 
    @type result_values: C{list} consisting of C{unittest.TestResult}

    @rtype: C{string}
    @return: Result value testruns
    """
    
    if not len(result_values):
        return REQUEST_ERROR
    
    for value in result_values:
        if len(value.errors):
            return REQUEST_ERROR
    
    for value in result_values:
        if len(value.failures):
            return REQUEST_FAIL
    
    return REQUEST_PASS

def _validate_devicespecs(device_specs):
    """
    Returns boolean value based on device_specs validation

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


def _run_hub(queue, sw_product, request_id, options_dict):
    """
    Function to run a hub and save the testrun result to queue.
    
    @param queue: Process queue
    @type queue: L{multiprocess.Queue}

    @param sw_product: Software product
    @type sw_product: C{string}

    @param request_id: request ID
    @type request_id: C{string}

    @param options_dict: Options dictionary for Hub
    @type options_dict: C{dict}
    
    """
    
    hub = Hub(sw_product, request_id, **options_dict)
    result = hub.run()
    
    queue.put({hub.testrun_uuid : result})



