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

import unittest

from socket import gethostname

from ots.common.framework.api import PublisherPluginBase
from ots.common.dto.api import OTSException

import ots.server.hub.sandbox as sandbox

from ots.server.distributor.api import TaskRunner

from ots.server.hub.tests.component.mock_taskrunner \
                         import MockTaskRunnerResultsPass
from ots.server.hub.tests.component.mock_taskrunner \
                         import MockTaskRunnerResultsFail
from ots.server.hub.tests.component.mock_taskrunner \
                         import MockTaskRunnerError


from ots.server.hub.hub import Hub

class CantStringify(object):
    
    def __str__(self):
        raise ValueError


options_dict = {"image" : "www.nokia.com",
                "rootstrap" : "www.meego.com",
                "packages" : "hw_pkg1-test pkg2-test pkg3-test",
                "chroottest" : "chroot_pkg1-tests chroot_pkg2-tests",
                "plan" : "111",
                "execute" : "true",
                "gate" : "foo",
                "label": "bar",
                "hosttest" : "host_pkg1-test host_pkg2-test host_pkg3-test",
                "device" : "devicegroup:foo",
                "emmc" : "",
                "distribution-model" : "",
                "flasher" : "",
                "testfilter" : "",
                "email" : "on",
                "email-attachments" : "on",
                "notify_list": "asdf@asdf"}


class PublishersStub(PublisherPluginBase):
    
    def set_testrun_result(self, testrun_result):
        self.testrun_result = testrun_result

    def set_exception(self, exception):
        self.exception = exception

class FaultyPublishersStub(PublisherPluginBase):

    def set_testrun_result(self, testrun_result):
        self.testrun_result = testrun_result
    
    def set_monitors(self, monitors):
        raise Exception("Failing publisher plugin")

class TestHubRun(unittest.TestCase):

    def test_pass(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub("example_sw_product", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        hub._publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertEquals(hub._publishers.testrun_result, "PASS")

    def test_fail(self):
        mock_taskrunner = MockTaskRunnerResultsFail()
        mock_taskrunner.run 
        hub = Hub("example_sw_product", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        hub._publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertEquals(hub._publishers.testrun_result, "FAIL")

    def test_error(self):
        mock_taskrunner = MockTaskRunnerError()
        mock_taskrunner.run
        hub = Hub("example_sw_product", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        hub._publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertTrue(isinstance(hub._publishers.exception, Exception))
        testrun_result = hub._publishers.testrun_result
        self.assertEquals(hub._publishers.testrun_result, "ERROR")

    def test_server_faulty_error(self):
        mock_taskrunner = MockTaskRunnerError()
        mock_taskrunner.run
        hub = Hub("example_sw_product", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        hub._publishers = FaultyPublishersStub(None, None, None, None)
        hub.run()
        testrun_result = hub._publishers.testrun_result
        self.assertEquals(hub._publishers.testrun_result, "ERROR")

class TestHubProperties(unittest.TestCase):

    def test_sw_product(self):
        hub = Hub(CantStringify(), 111)
        self.assertEquals("example_sw_product", hub.sw_product)

    def test_request_id(self):
        hub = Hub(111, CantStringify())
        self.assertEquals("default_request_id", hub.request_id)

    def test_extended_options_dict(self):
        hub = Hub(111, 111)
        expected = {'email_attachments': 'off', 'email': 'on'}
        self.assertEquals(expected, hub.extended_options_dict)
        hub = Hub("example_sw_product", 111)
        expected = {'email_attachments': 'off', 'email': 'on'}
        self.assertEquals(expected, hub.extended_options_dict)

    def test_image(self):
        hub = Hub(111, 111)
        self.assertEquals("no_image", hub.image)
        hub = Hub("example_sw_product", 111, image = "foo")
        self.assertEquals("foo", hub.image)

    def test_testrun_uuid(self):
        hub = Hub(111, 111)
        self.assertTrue(isinstance(hub.testrun_uuid, str))

    def test_is_hw_enabled(self):
        hub = Hub("example_sw_product", 111, image = "foo", 
                  packages = "a-tests b-tests c-tests")
        self.assertTrue(hub.is_hw_enabled)
        hub = Hub("example_sw_product", 111, image = "foo")
        self.assertFalse(hub.is_hw_enabled)

    def test_is_host_enabled(self):
        hub = Hub("example_sw_product", 111, image = "foo", 
                  hosttest = "a-tests b-tests c-tests")
        self.assertTrue(hub.is_host_enabled)
        hub = Hub("example_sw_product", 111, image = "foo")
        self.assertFalse(hub.is_host_enabled)
        
    def test_options(self):
        hub = Hub(111, 111, image = "foo", distribution_model = "default")
        self.assertEquals(0, hub.options.timeout)
        hub = Hub("example_sw_product", 1111, image = "foo")
        self.assertEquals(60, hub.options.timeout)

    def test_taskrunner(self):
        hub = Hub("example_sw_product", 111, **options_dict)
        taskrunner = hub.taskrunner
        self.assertTrue(isinstance(taskrunner, TaskRunner))
        
    def test_device_properties(self):
        hub = Hub("example_sw_product", 111, image="foo",
                  device = "devicegroup:examplegroup")
        taskrunner = hub.taskrunner
        self.assertTrue(isinstance(taskrunner, TaskRunner))
        
    def test_host_test_plan(self):
        hub = Hub("example_sw_product", 111, image="foo",
                  host_testplans = [["name", "bar"]])
        taskrunner = hub.taskrunner
        self.assertTrue(isinstance(taskrunner, TaskRunner))
        
    def test_device_test_plan(self):
        hub = Hub("example_sw_product", 111, image="foo",
                  hw_testplans = [["name", "bar"]])
        taskrunner = hub.taskrunner
        self.assertTrue(isinstance(taskrunner, TaskRunner))

class TestHubFailSafePublishing(unittest.TestCase):

    def test_bad_params(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub(CantStringify(), CantStringify())
        hub._taskrunner = mock_taskrunner
        hub._publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertEquals(hub._publishers.testrun_result, "ERROR")
        self.assertTrue(isinstance(hub._publishers.exception, ValueError))

if __name__ == "__main__":
    unittest.main()
