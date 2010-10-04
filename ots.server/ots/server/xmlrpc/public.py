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
import re

from ots.server.testrun_host.testrun_host import TestrunHost


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



PLAN_NAME = "Testplan %s"
REQUEST_ERROR = 'ERROR'

# Django Models are metaclasses 
# pylint: disable-msg=E1101

#############################################
# PUBLIC METHODS
#############################################

def request_sync(program, request, notify_list, options):
    """
    Fires the test request and waits for it to finish

    @param program: program
    @type product: C{string}

    @param request: BUILD request id 
    @type product: C{string}

    @param notify_list: Email addresses for notifications 
    @type product: C{list}

    @param options: Parameters that affect the test request behaviour 
    @type product: C{dict}

    @rtype: C{string}
    @return: Pass / Fail or Error
    """

    #Important: We are relaxed about what is supplied by the client.
    #Deduce as much as possible, apply defaults for missing parameters 

    result = REQUEST_ERROR

    #Unpack the necessary parameters out of the options dict
    image_url = options.get("image", '')
    rootstrap_url = options.get("rootstrap", '')
    test_packages = _string_2_list(options.get("packages",""))
    testplan_id =  options.get('plan', None)
    is_executed =  options.get('execute') != 'false'
    testrun_timeout = options.get('testrun_timeout')
    #
    options = _repack_options(options)
    #
    if is_executed:
        testrun_id = extension_points.init_new_testrun(program,
                                                       testplan_id = testplan_id,
                                                       testplan_name = PLAN_NAME % request,
                                                       gate = options.get('gate', "unknown"),
                                                       label = options.get('label', "unknown"))

        if testrun_id is not None:
            #Now we have the id the logging can commence
            _initialize_logger(request, testrun_id)
            log = logging.getLogger(__name__)
            log.info(("Incoming request: program: %s,"\
                      " request: %s, notify_list: %s, "\
                      "options: %s") %\
                      (program, request, notify_list, options))
            #
            result = _run_test(log, request, testrun_id, 
                            program, options, notify_list,
                            test_packages, image_url, rootstrap_url,
                            testrun_timeout)
    return result

###########################################
# HELPER METHODS
###########################################

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
    @type product: C{string}

    @rtype: C{list} consisting of C{string}
    @return: The converted string
    """
    if string:
        spaces = re.compile(r'\s+')
        return spaces.split(string.strip())
    else:
        return []

def _string_2_dict(string):
    """
    Converts a spaced string of form 'foo:1 bar:2 baz:3'
    to a dictionary

    @param string: The string for conversion  
    @type product: C{string}

    @rtype: C{dict} consisting of C{string}
    @return: The converted string
    """
    spaces = re.compile(r'\s+')
    return dict([ pair.split(':', 1) for pair \
                       in spaces.split(string) if ':' in pair ])

def _repack_options(options):
    """
    Converts the options as provided by the client (for example build machine)
    into the form accepted by OTS

    @param options: The options parameters 
    @type product: C{dict}

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
            = _string_2_dict(options.get("device",""))
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
              test_packages, image_url, rootstrap_url, testrun_timeout):

    """
    Run the test on the TestrunHost

    @param log: The python logger
    @type log: L{logging.Logger}


    @param request: BUILD request id 
    @type product: C{string}

    @param testrun_id: The OTS testrun_id
    @type testrun_id: C{string}

    @param program: Software program
    @type program: C{string}

    @param options: Parameters that affect the test request behaviour 
    @type product: C{dict}

    @param notify_list: Email addresses for notifications 
    @type product: C{list}
    
    @param test_packages: A list of test packages. May be empty list.
    @type notify_list: C{list}

    @param image_url: The url of the image
    @type image)url: C{string}

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
                              rootstrap_url,
                              testrun_timeout)

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
