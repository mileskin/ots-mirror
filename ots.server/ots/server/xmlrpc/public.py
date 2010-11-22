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
ots public xml-rpc interface
"""

import logging
import logging.handlers
import datetime
import copy
import re

from multiprocessing import Queue
from ots.server.testrun_host.testrun_host import TestrunHost
from ots.server.xmlrpc.handleprocesses import HandleProcesses

# Extension point mechanism
try:
    from ots_extensions import extension_points
except ImportError: # If no extension points found, use the empty default
    from ots.server.testrun_host import \
        example_extension_points as extension_points

try:    
    from ots_extensions import ots_config
except ImportError: # If no custom config found, use the default
    from ots.server.testrun_host import default_ots_config as ots_config


REQUEST_ERROR = 'ERROR'
REQUEST_FAIL = 'FAIL'
REQUEST_PASS = 'PASS'

# Django Models are metaclasses 
# pylint: disable-msg=E1101

#############################################
# PUBLIC METHODS
#############################################

def request_sync(program, request, notify_list, options):
    """
    Fires the test request and waits for it to finish

    @param program: program
    @type program: C{string}

    @param request: BUILD request id 
    @type request: C{string}

    @param notify_list: Email addresses for notifications 
    @type notify_list: C{list}

    @param options: Parameters that affect the test request behaviour 
    @type options: C{dict}

    @rtype: C{string}
    @return: Pass / Fail or Error
    """

    #Important: We are relaxed about what is supplied by the client.
    #Deduce as much as possible, apply defaults for missing parameters 

    #Unpack the necessary parameters out of the options dict
    image_url = options.get("image", '')
    rootstrap_url = options.get("rootstrap", '')
    test_packages = _string_2_list(options.get("packages",""))
    # TODO: This is for unit testing purposes. Remove if possible.
    is_executed =  options.get('execute') != 'false'

    try:
        options = _repack_options(options)
    except IndexError:
        return REQUEST_ERROR

    if not is_executed:
        return REQUEST_ERROR

    # Create process handler and testrun and start them
    process_handler = HandleProcesses()
    testrun_list, process_queues =  _create_testruns(options, request, \
                                        program, notify_list, test_packages, \
                                        image_url, rootstrap_url)
    for testrun in testrun_list:
        process_handler.add_process(_execute_testrun, testrun)

    # Check that we have tasks to run
    if not process_handler.child_processes:
        return REQUEST_ERROR

    # Start processes ...
    process_handler.start_processes()
    # Read process queues
    results = _read_queues(process_queues)
    # Join processes
    process_handler.join_processes()

    # Check return values from testruns
    return _check_testruns_result_values(results.values())

###########################################
# HELPER METHODS
###########################################

def _execute_testrun(pq, request, program, current_options, notify_list,
                     test_packages, image_url, rootstrap_url):
    """
    Starting point for process that handles testrun. Starts logging, execute
    _run_test and puts result to queue    

    @param pq: Process queue
    @type pq: L{multiprocess.Queue}

    @param request: request id 
    @type request: C{string}

    @param program: Software program 
    @type program: C{string}

    @param current_options: Parameters that affect the test request behaviour 
    @type current_options: C{dict}

    @param notify_list: Email addresses for notifications 
    @type notify_list: C{list}
    
    @param test_packages: A list of test packages. May be empty list.
    @type test_packages: C{list}

    @param image_url: The url of the image
    @type image_url: C{string}

    @param rootstrap_url: The url of the roostrap
    @type rootstrap_url: C{string}
    """
    # Default result
    result = REQUEST_ERROR

    testrun_id = extension_points.create_testrun_id(program, request, \
                                                    current_options)

    if testrun_id is not None:
        #Now we have the id the logging can commence
        _initialize_logger(request, testrun_id)
        log = logging.getLogger(__name__)
        log.info(("Incoming request: program: %s,"\
                  " request: %s, notify_list: %s, "\
                  "options: %s") %\
                  (program, request, notify_list, current_options))

        result = _run_test(log, request, testrun_id,
                           program, current_options, notify_list,
                           test_packages, image_url, rootstrap_url)

    pq.put({testrun_id : result})

def _read_queues(process_queues):
    """
    Returns testrun_id and result pairs

    @param process_queues: List that contains queues used by processes
    @type process_queues: C{list}

    @rtype: C{dict}
    @return: Dictionary that contains testrun_id and result pairs
    """
    queue_results = {}
    for process_queue in process_queues:
        queue_results.update(process_queue.get())
    return queue_results

def _check_testruns_result_values(result_values):
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

def _create_testruns(options, request, program, notify_list,
                    test_packages, image_url, rootstrap_url):
    """
    Returns testrun_list and process_queues

    @param options: Dict that contains data for testrun
    @type options: C{dict}

    @param request: BUILD request id 
    @type request: C{string}

    @param program: Software program
    @type program: C{string}

    @param notify_list: Email addresses for notifications 
    @type notify_list: C{list}
    
    @param test_packages: A list of test packages. May be empty list.
    @type test_packages: C{list}

    @param image_url: The url of the image
    @type image_url: C{string}

    @param rootstrap_url: The url of the roostrap
    @type rootstrap_url: C{string}

    @rtype: C{dict}, C(Queue)
    @return: testrun_list which contains arguments in tuple
             for each subprocess
    """
    testrun_list = []
    process_queues = []

    if options.get('device'):
        # Separate devigroups for different testrun_id's
        for devicespec in options['device']:
            current_options, pq = _prepare_testrun(options)
            process_queues.append(pq)

            # Check that we have valid devicespecs
            if not _validate_devicespecs(devicespec.keys()):
                continue

            # Fetch devicespecs
            if devicespec.get('devicegroup'):
                current_options['device'] = \
                                {'devicegroup': devicespec['devicegroup']}
            if devicespec.get('devicename'):
                current_options['device']['devicename'] = \
                                devicespec['devicename']
            if devicespec.get('deviceid'):
                current_options['device']['deviceid'] = \
                                devicespec['deviceid']

            testrun_list.append((pq, request, program, current_options, \
                                 notify_list, test_packages, image_url, \
                                 rootstrap_url))
    else:
        current_options, pq = _prepare_testrun(options)
        process_queues.append(pq)
        testrun_list.append((pq, request, program, current_options, \
                             notify_list, test_packages, image_url, \
                             rootstrap_url))

    return testrun_list, process_queues

def _validate_devicespecs(devicespecs):
    """
    Returns boolean value based on devicespecs
    validation

    @param devicespecs: List that contains devicespecs
    @type options: C{List}

    @rtype: C{Boolean}
    @return: True if devicespecs are valid, False otherwise
    """
    for devicespec in devicespecs:
        if devicespec not in ['devicegroup', 'devicename', 'deviceid']:
            return False
    return True

def _prepare_testrun(options):
    """
    Returns deepcopy of options and process queue

    @param options: Dict that contains data for testrun
    @type options: C{dict}

    @rtype: C{dict}, C(Queue)
    @return: deepcopy of dictionary and process queue
    """
    return copy.deepcopy(options), Queue()

def _generate_log_id_string(build_id, testrun_id):
    """
    Generates the log file name
    """
    request_id = "testrun_%s_request_%s_"% (testrun_id, build_id)
    request_id += str(datetime.datetime.now()).\
        replace(' ','_').replace(':','_').replace('.','_')
    return request_id

def _initialize_logger(build_id, testrun_id):
    """
    initializes the logger
    """
    log_id_string = _generate_log_id_string(build_id, testrun_id)
    log = logging.getLogger()
    for handler in log.handlers:
        log.root.removeHandler(handler)

    level = logging.DEBUG
    format = '%(asctime)s  %(module)-12s %(levelname)-8s %(message)s'
    hdlr = logging.FileHandler(ots_config.log_directory+log_id_string)
    hdlr.setLevel(level)
    fmt = logging.Formatter(format)
    hdlr.setFormatter(fmt)
    log.addHandler(hdlr)
    log.setLevel(level)

    if ots_config.http_logging_enabled:
        from ots.server.logger.localhandler import LocalHttpHandler
        httphandler = LocalHttpHandler(testrun_id)
        httphandler.setLevel(logging.INFO)
        log.addHandler(httphandler)
    return log

def _get_testrun_host(log):
    """
    Factory method for TestrunHost
    """
    try:
        host = TestrunHost()
    except:
        log.exception("Failed to create TestrunHost")
        host = None
    return host

def _string_2_list(string):
    """
    Converts a spaced string to an array

    @param string: The string for conversion  
    @type string: C{string}

    @rtype: C{list} consisting of C{string}
    @return: The converted string
    """
    if string:
        spaces = re.compile(r'\s+')
        return spaces.split(string.strip())
    else:
        return []

def _parse_multiple_devicegroup_specs(string):
    """
    Converts a spaced string of form 'devicegroup:one sim:operator1;
    devicegroup:two sim:operator2' to a dictionary

    @param string: The string for conversion  
    @type string: C{string}

    @rtype: C{dict} consisting of C{string}
    @return: The converted string
    """
    temp_array = []
    devicegroups = []
    for splitted_str in string.split(';'):
        temp_array.append(splitted_str.split())
    for devicegroup in temp_array:
        unit_dict = {}
        for prop in xrange(len(devicegroup)):
            prop_pair = devicegroup[prop].split(':', 1)
            unit_dict.update({prop_pair[0]: prop_pair[1]})
        devicegroups.append(unit_dict)

    return devicegroups

def _repack_options(options):
    """
    Converts the options as provided by the client (for example build machine)
    into the form accepted by OTS

    @param options: The options parameters 
    @type options: C{dict}

    @rtype: C{dict} 
    @return: The conditioned options parameters
    """
    conditioned_options = {}
    if 'hosttest' in options:
        conditioned_options["hosttest"] \
            = _string_2_list(options.get("hosttest",""))
    if 'engine' in options:
        conditioned_options["engine"] \
            = _string_2_list(options.get("engine", ""))
    if 'device' in options:
        conditioned_options["device"] \
            = _parse_multiple_devicegroup_specs(options.get("device", ""))
    if 'emmc' in options:
        conditioned_options['emmc'] = options['emmc']
    if 'email-attachments' in options:
        if options['email-attachments'] == 'on':
            conditioned_options['email-attachments'] = True
        else:
            conditioned_options['email-attachments'] = False

    #Currently some options are still not defined at interface level
    #so pass on anything that comes our way
    options.update(conditioned_options)
    return options

def _run_test(log, request, testrun_id, program, options, notify_list,
              test_packages, image_url, rootstrap_url):

    """
    Run the test on the TestrunHost

    @param log: The python logger
    @type log: L{logging.Logger}

    @param request: BUILD request id 
    @type request: C{string}

    @param testrun_id: The OTS testrun_id
    @type testrun_id: C{string}

    @param program: Software program
    @type program: C{string}

    @param options: Parameters that affect the test request behaviour 
    @type options: C{dict}

    @param notify_list: Email addresses for notifications 
    @type notify_list: C{list}
    
    @param test_packages: A list of test packages. May be empty list.
    @type test_packages: C{list}

    @param image_url: The url of the image
    @type image_url: C{string}

    @param rootstrap_url: The url of the roostrap
    @type rootstrap_url: C{string}
    
    @rtype: C{string} 
    @return: 'PASS', 'FAIL' or 'ERROR'
    """
    result = "FAIL"
    host = _get_testrun_host(log)
    if host is not None:
        try:
            host.init_testrun(request,
                              testrun_id,
                              program,
                              options,
                              notify_list,
                              test_packages,
                              image_url,
                              rootstrap_url)

            host.register_ta_plugins()
            host.register_results_plugins()
            host.run()
            if host.testrun_result() == "PASS":
                result = "PASS"
        except:
            log.exception("Error in testrun")
            result = REQUEST_ERROR
        finally:
            host.publish_result_links()
            host.cleanup()
            log.debug("Root log handlers: %s" % str(log.root.handlers))
            for handler in log.root.handlers:
                log.root.removeHandler(handler)
    return result
