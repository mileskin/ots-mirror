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

import os

import unittest

from ots.common.dto.ots_exception import OTSException

from ots.server.distributor.api import OtsExecutionTimeoutError

from ots.common.framework.api import PublisherPluginBase

from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerResultsMissing
from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerResultsFail
from ots.server.hub.tests.component.mock_taskrunner import MockTaskRunnerTimeout
from ots.server.hub.tests.component.mock_taskrunner import MockTaskRunnerError
from ots.server.hub.tests.component.mock_taskrunner import \
                                             MockTaskRunnerResultsPass

import ots.results.api

from ots.results.api import PackageException

"""
Component test for Hub

Mocks OTS from the Distributor down 
"""

DEBUG = False

from ots.server.hub.api import Hub

class PublisherStub(PublisherPluginBase):

    exception = None

    def set_exception(self, exception):
        self.exception = exception 

class TestHubComponent(unittest.TestCase):

    def test_run_results_pass(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        ret_val = hub.run()
        self.assertTrue(ret_val.wasSuccessful())

    def test_run_results_missing(self):
        mock_taskrunner = MockTaskRunnerResultsMissing()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        publisher = PublisherStub(*[None]*4)
        hub._publishers._publishers.append(publisher)
        hub.run()
        self.assertTrue(isinstance(publisher.exception, PackageException))
        
    def test_run_results_fail(self):
        mock_taskrunner = MockTaskRunnerResultsFail() 
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner 
        ret_val = hub.run()
        self.assertFalse(ret_val.wasSuccessful())

    def test_run_global_timeout(self):
        #Not really a test more an illustration of behaviour
        mock_taskrunner = MockTaskRunnerTimeout()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        publisher = PublisherStub(*[None]*4)
        hub._publishers._publishers.append(publisher)
        hub.run()
        self.assertTrue(isinstance(publisher.exception, 
                                   OtsExecutionTimeoutError))

    def test_run_model_taskrunner_error(self):
        mock_taskrunner = MockTaskRunnerError()
        hub = Hub("example_sw_product", 111, image="image")
        hub._taskrunner = mock_taskrunner
        publisher = PublisherStub(*[None]*4)
        hub._publishers._publishers.append(publisher)
        hub.run()
        self.assertTrue(isinstance(publisher.exception, OTSException))

if __name__ == "__main__":
    if DEBUG:
        import logging
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)
        log_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(log_handler)
    unittest.main()
