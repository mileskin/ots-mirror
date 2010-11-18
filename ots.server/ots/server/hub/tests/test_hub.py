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

import unittest

from socket import gethostname

from ots.common.framework.api import PublisherPluginBase
from ots.common.dto.api import OTSException

from ots.server.distributor.api import TaskRunner

from ots.server.hub.tests.component.mock_taskrunner \
                         import MockTaskRunnerResultsPass
from ots.server.hub.tests.component.mock_taskrunner \
                         import MockTaskRunnerError


from ots.server.hub.hub import Hub


options_dict = {"image" : "www.nokia.com" ,
                "rootstrap" : "www.meego.com",
                "packages" : "hw_pkg1-test pkg2-test pkg3-test",
                "plan" : "111",
                "execute" : "true",
                "gate" : "foo",
                "label": "bar",
                "hosttest" : "host_pkg1-test host_pkg2-test host_pkg3-test",
                "device" : "baz",
                "emmc" : "",
                "distribution-model" : "",
                "flasher" : "",
                "testfilter" : "",
                "input_plugin" : "bifh",
                "email" : "on",
                "email-attachments" : "on"}


class PublishersStub(PublisherPluginBase):
    
    def set_testrun_result(self, testrun_result):
        self.testrun_result = testrun_result

    def set_exception(self, exception):
        self.exception = exception

class TestHub(unittest.TestCase):

    def test_taskrunner(self):
        hub = Hub("pdt", 111, **options_dict)
        taskrunner = hub.taskrunner
        self.assertTrue(isinstance(taskrunner, TaskRunner))
        
    def test_run_pass(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        mock_taskrunner.run
        hub = Hub("pdt", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        
        hub.publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertTrue(hub.publishers.testrun_result)

    def test_run_error(self):
        mock_taskrunner = MockTaskRunnerError()
        mock_taskrunner.run
        hub = Hub("pdt", 111, **options_dict)
        hub._taskrunner = mock_taskrunner
        
        hub.publishers = PublishersStub(None, None, None, None)
        hub.run()
        self.assertTrue(isinstance(hub.publishers.exception, OTSException))


if __name__ == "__main__":
    unittest.main()
