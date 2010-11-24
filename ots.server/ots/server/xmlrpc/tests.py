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

"""Unit tests for xmlrpc interface and handleprocesses modules"""

import unittest

import logging

from ots.server.xmlrpc.public import request_sync
from ots.server.xmlrpc.public import REQUEST_ERROR as REQUEST_ERROR
from ots.server.xmlrpc.public import _repack_options
from ots.server.xmlrpc.public import _string_2_list
from ots.server.xmlrpc.public import _run_test 
from ots.server.xmlrpc.public import _check_testruns_result_values
from ots.server.xmlrpc.public import _parse_multiple_devicegroup_specs
from ots.server.xmlrpc.public import _read_queues
from ots.server.xmlrpc.public import _prepare_testrun
from ots.server.xmlrpc.public import _create_testruns
from ots.server.xmlrpc.public import _validate_devicespecs
from ots.server.xmlrpc.handleprocesses import HandleProcesses

from multiprocessing import Process, Queue
import ots.server.xmlrpc.public as public

class TestrunHost(object):
    """Mocked TestRunHost"""

    def __init__(self):
        print "Fake TestRunHost initialised"

    def init_testrun(self,
                     request,
                     program,
                     options,
                     notify_list,
                     test_packages,
                     image_url,
                     rootstrap_url):

        self.request = request
        self.program = program
        self.options = options
        self.notify_list = notify_list
        self.test_packages = test_packages
        self.image_url = image_url
        self.rootstrap_url = rootstrap_url

        global testdata_init_testrun
        testdata_init_testrun = [request,
                                 program,
                                 options,
                                 notify_list,
                                 test_packages,
                                 image_url,
                                 rootstrap_url]

    def register_ta_plugins(self):
        pass

    def register_results_plugins(self):
        pass

    def run(self):
        pass

    def testrun_result(self):
        return "PASS"

#################################
# Stubs
################################

class DummyHost(object):
    """Another mocked TestRunHost"""

    def init_testrun(self, request, testrun_id, program,
                           options, notify_list, test_packages,
                           image_url, rootstrap_url):
        pass

    def register_ta_plugins(self):
        pass

    def register_results_plugins(self):
        pass

    def run(self):
        pass

    def publish_result_links(self):
        pass

    def cleanup(self):
        pass

    def testrun_result(self):
        return "PASS"


def _get_dummy_host(*args):
    return DummyHost()


class DummyHostRaises(DummyHost):

    def run(self):
        raise

def _get_dummy_host_raises(*args):
    return DummyHostRaises()

class DummyHostFails(DummyHost):
    
    def testrun_result(self):
        return "NOT_PASS"


def _get_dummy_host_fails(*args):
    return DummyHostFails()


def _get_dummy_host_None(*args):
    return None

#########################################

class Test_xmlrpc_interface(unittest.TestCase):

    def test_request_sync(self):
        self.req_id = "123007"

        self.image_url = 'http://image_url'
        self.rootstrap_url = 'http://rootstrap_url'

        self.sw_product = 'swproduct'
        self.email_list = ['nonexisting@notexistingdomain.foobar']

        self.interface_options = dict()
        self.interface_options['device'] = 'devicegroup:not_real_device'
        self.interface_options['packages'] = "foobar-tests foobaz-tests  "  #Here are the extra spaces!
        self.interface_options['testfilter'] = "testsuite=testsuite2"

        self.interface_options['image'] = self.image_url
        self.interface_options['rootstrap'] = self.rootstrap_url
        self.interface_options['execute'] = "false"

        result = request_sync(self.sw_product, self.req_id, self.email_list, self.interface_options)

        self.assertEquals(result, 'ERROR')

    def test_request_sync_multiple_devicegroups_with_empy_child_processes_list(self):
        """
        Try request_sync with errorneous 'device' option. Should return ERROR since no process instances are created for
        multiple devicegroup.
        """
        self.req_id = "123007"

        self.image_url = 'http://image_url'
        self.rootstrap_url = 'http://rootstrap_url'

        self.sw_product = 'swproduct'
        self.email_list = ['nonexisting@notexistingdomain.foobar']

        self.interface_options = dict()
        self.interface_options['device'] = 'syntaxerror:foobazored_device;syntaxerror:bogus_device;syntaxerror:huuhaa_device'
        self.interface_options['packages'] = "foobar-tests foobaz-tests  "  #Here are the extra spaces!
        self.interface_options['testfilter'] = "testsuite=testsuite2"

        self.interface_options['image'] = self.image_url
        self.interface_options['rootstrap'] = self.rootstrap_url

        result = request_sync(self.sw_product, self.req_id, self.email_list, self.interface_options)

        self.assertEquals(result, 'ERROR')

    def test_request_sync_multiple_devicegroups_with_invalid_devicegroup_syntax(self):
        """
        New format for devicegroup is 'devicegroup:groupname property:value', meaning that properties for devicegroup are separated with whitespace,
        it's not valid to add whitespace after devicegroup value: 'devicegroup: groupname property:value'
        """
        self.req_id = "123007"

        self.image_url = 'http://image_url'
        self.rootstrap_url = 'http://rootstrap_url'

        self.sw_product = 'swproduct'
        self.email_list = ['nonexisting@notexistingdomain.foobar']

        self.interface_options = dict()
        self.interface_options['device'] = 'devicegroup: foobazored_device'
        self.interface_options['packages'] = "foobar-tests foobaz-tests  "  #Here are the extra spaces!
        self.interface_options['testfilter'] = "testsuite=testsuite2"

        self.interface_options['image'] = self.image_url
        self.interface_options['rootstrap'] = self.rootstrap_url

        result = request_sync(self.sw_product, self.req_id, self.email_list, self.interface_options)

        self.assertEquals(result, 'ERROR')

    def test_repack_options(self):
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC',
                   'email-attachments': 'off'}

        expected = {'engine': ['this', 'is', 'the', 'engine'], 
                    'device': [{'a': '1', 'c': '3', 'b': '2'}], 
                    'emmc': 'EMMC', 
                    'hosttest': ['this', 'is', 'a', 'hosttest'],
                    'email-attachments': False}
        self.assertEquals(expected, _repack_options(options))

    def test_repack_options_extra_options(self): 
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC',
                   'foo': 'FOO',
                   'bar': 'BAR'}

        expected = {'engine': ['this', 'is', 'the', 'engine'], 
                    'device': [{'a': '1', 'c': '3', 'b': '2'}], 
                    'emmc': 'EMMC', 
                    'hosttest': ['this', 'is', 'a', 'hosttest'],
                    'foo':'FOO',
                    'bar':'BAR'}
        self.assertEquals(expected, _repack_options(options))

    def test_repack_options_multiple_device_groups(self):
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'devicegroup:foobar;devicegroup:foobazor b:2',
                   'emmc': 'EMMC',
                   'email-attachments': 'off'}

        expected = {'engine': ['this', 'is', 'the', 'engine'],
                    'device': [{'devicegroup':'foobar'}, \
                              {'b': '2', 'devicegroup': 'foobazor'}],
                    'emmc': 'EMMC',
                    'hosttest': ['this', 'is', 'a', 'hosttest'],
                    'email-attachments': False}
        self.assertEquals(expected, _repack_options(options))

    def test_repack_options_email_attachments(self):
        options = {'email-attachments': 'on'}
        expected = {'email-attachments': True}
        self.assertEquals(expected, _repack_options(options))
        options = {'email-attachments': 'off'}
        expected = {'email-attachments': False}
        self.assertEquals(expected, _repack_options(options))

    def test_string_2_list(self):
        expected = ['mary', 'had', 'a', 'little', 'lamb']
        self.assertEquals(expected, 
                          _string_2_list("mary had a little lamb"))

    def test_parse_multiple_devicegroup_specs(self):
        expected = [{'devicegroup': 'group1'}, {'devicegroup': 'group2', 'sim': 'operator'}]
        args = "devicegroup:group1;devicegroup:group2 sim:operator"
        self.assertEquals(expected,
           _parse_multiple_devicegroup_specs(args))

    def test_parse_multiple_devicegroup_specs_invalid_data(self):
        """
        Whitespaces are used to separate devicegroup properties and are not allowed between
        devicegroup key and it's value
        """
        args = "devicegroup: group1 sim:operator2;devicegroup: group2 sim:operator2"
        try:
            _parse_multiple_devicegroup_specs(args)
        except IndexError:
            pass

    def test_one_devicespec_devicegroup(self):
        options = {'device': [{'devicegroup': 'foobar_1'}], \
                   'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 1)
        self.assertTrue(len(process_queues) == 1)

    def test_one_devicespec_devicegroup_two_devicegroups(self):
        options = {'device': [{'devicegroup': 'foobar_1'}, \
                   {'devicegroup': 'foobar_2'}], 'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 2)
        self.assertTrue(len(process_queues) == 2)

    def test_multiple_devicespecs(self):
        options = {'device': [{'devicegroup': 'foobar_1', 'devicename': 'mydevice', \
                   'deviceid': '1'}], 'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 1)
        self.assertTrue(len(process_queues) == 1)

    def test_multiple_devicespecs_two_devicegroups(self):
        options = {'device': [{'devicegroup': 'foobar_1', 'devicename': 'device1', \
                   'deviceid': '1'}, {'devicegroup': 'foobar_2', 'devicename': 'device2', \
                   'deviceid': '2'}], 'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 2)
        self.assertTrue(len(process_queues) == 2)

    def test_with_bogus_devicespec(self):
        options = {'device': [{'bogusspec': 'foobazor'}], \
                   'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 0)

    def test_with_devicename_and_deviceid_devicespec(self):
        options = {'device': [{'devicename': 'test1', 'deviceid': '1'}], \
                   'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')

        self.assertTrue(len(testrun_list) == 1)

    def test_with_devicename_devicespec(self):
        options = {'device': [{'devicename': 'test1'}], \
                   'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')
        
        self.assertTrue(len(testrun_list) == 1)

    def test_with_deviceid_devicespec(self):
        options = {'device': [{'deviceid': '1'}], \
                   'timeout': '1'}
        testrun_list, process_queues = \
            _create_testruns(options, 'request', 'program', 'noemail@nodomain.nodot', \
                'foobar-tests', 'https://image_url', 'http://roostrap_url')
       
        self.assertTrue(len(testrun_list) == 1)

    def test_validate_devicespecs_true(self):
        devicespecs = ['devicegroup', 'devicename', 'deviceid']
        self.assertTrue(_validate_devicespecs(devicespecs))
        self.assertTrue(_validate_devicespecs([devicespecs[0]]))
        self.assertTrue(_validate_devicespecs([devicespecs[1]]))
        self.assertTrue(_validate_devicespecs([devicespecs[2]]))

    def test_validate_devicespecs_false(self):
        devicespecs = ['devicegroup', 'devicename', 'bogusspec']
        self.assertFalse(_validate_devicespecs(devicespecs))

        devicespecs = ['foobarspec']
        self.assertFalse(_validate_devicespecs(devicespecs))

    def test_prepare(self):
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC'}

        new_options, pq = _prepare_testrun(options)
        self.assertEquals(type(pq), type(Queue()))
        self.assertEquals(options, new_options)
        self.assertFalse(options is new_options)

    def test_check_result_values(self):
        return_error = ['ERROR', 'FAIL', 'PASS']
        self.assertEqual('ERROR', _check_testruns_result_values(return_error))

        return_error = ['FAIL', 'PASS']
        self.assertEqual('FAIL', _check_testruns_result_values(return_error))

        return_error = ['PASS','PASS']
        self.assertEqual('PASS', _check_testruns_result_values(return_error))

    def test_run_test_passed(self):
        #Override host with stub
        public._get_testrun_host = _get_dummy_host

        log = logging.getLogger(__name__)
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC'}

        self.assertEquals("PASS", 
                          _run_test(log, "request", "testrun_id", 
                                    "program", options, 
                                    ["foo@bar.com"], ["p1", "p2"], 
                                     "image", "rootstrap"))
        
    def test_run_test_raises(self):
        #Override host with stub
        public._get_testrun_host = _get_dummy_host_raises

        log = logging.getLogger(__name__)
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC'}

        self.assertEquals("ERROR", 
                          _run_test(log, "request", "testrun_id", 
                                    "program", options, 
                                    ["foo@bar.com"], ["p1", "p2"], 
                                     "image", "rootstrap"))

    def test_run_test_fails(self):
        #Override host with stub
        public._get_testrun_host = _get_dummy_host_fails

        log = logging.getLogger(__name__)
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC'}

        self.assertEquals("FAIL", 
                          _run_test(log, "request", "testrun_id", 
                                    "program", options, 
                                    ["foo@bar.com"], ["p1", "p2"], 
                                     "image", "rootstrap"))
        
    def test_run_no_test_host(self):
        #Override host with stub
        public._get_testrun_host = _get_dummy_host_None

        log = logging.getLogger(__name__)
        options = {'hosttest': 'this is a hosttest',
                   'engine': 'this is the engine',
                   'device': 'a:1 b:2 c:3',
                   'emmc': 'EMMC'}

        self.assertEquals("FAIL", 
                          _run_test(log, "request", "testrun_id", 
                                    "program", options, 
                                    ["foo@bar.com"], ["p1", "p2"], 
                                     "image", "rootstrap"))
        

class Test_handleprocess(unittest.TestCase):

    def test_start_processes_and_read_process_queues(self):
        def _run_process(pq, id, string):
            pq.put({id:string})

        process_queues = []
        process_handler = HandleProcesses()
        p1q = Queue()
        p2q = Queue()
        process_handler.add_process(_run_process, (p1q, "1", "ping"))
        process_handler.add_process(_run_process, (p2q, "2", "pong"))
        process_queues.append(p1q)
        process_queues.append(p2q)

        process_handler.start_processes()
        ret = _read_queues(process_queues)
        process_handler.join_processes()

        self.assertEquals(ret["1"], "ping")
        self.assertEquals(ret["2"], "pong")

if __name__ == '__main__':
    unittest.main()
