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
import time

from ots.common.datatypes.api import ResultObject
from ots.common.datatypes.api import TestPackages

from ots.common.amqp.api import ResultMessage
from ots.common.amqp.api import ErrorMessage

from ots.server.distributor.api import TASKRUNNER_SIGNAL
from ots.server.distributor.api import OtsGlobalTimeoutError

import ots.results

#################################
# Results Scenarios Mocks
#################################

class MockTaskRunnerResultsBase(object):

    @property
    def results_xml(self):
        results_dirname = os.path.dirname(
                          os.path.abspath((ots.results.__file__)))
        results_file = os.path.join(results_dirname,
                                    "tests",
                                    "data",
                                    "dummy_results_file.xml")
        return open(results_file, "r").read()

    def run(self):
        self._send_testpackages()
        time.sleep(0.5)
        self._send_result("hardware_test", self.results_xml, "test_1")
        time.sleep(0.5)
        self._send_result("hardware_test", self.results_xml, "test_2")


    @staticmethod
    def _send_result(environment, results_xml, name):
        result_message = ResultMessage(name,
                                       content = results_xml,
                                       test_package = name,
                                       origin = "mock_task_runner",
                                       environment = environment)
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", 
                               message = result_message)

    @staticmethod
    def _send_testpackages():
        raise NotImplementedError

class MockTaskRunnerResultsMissing(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        msg = TestPackages("hardware_test", ["test_1", "test_2", "test_3"])
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner",
                               message = msg)

class MockTaskRunnerResultsFail(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        msg = TestPackages("hardware_test", ["test_1", "test_2"])
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner",
                               message = msg)

class MockTaskRunnerResultsPass(MockTaskRunnerResultsBase):

    @property
    def results_xml(self):
        results_dirname = os.path.dirname(
                          os.path.abspath((ots.results.__file__)))
        results_file = os.path.join(results_dirname,
                                    "tests",
                                    "data",
                                    "dummy_pass_file.xml")
        return open(results_file, "r").read()

    @staticmethod
    def _send_testpackages():
        msg = TestPackages("hardware_test", ["test_1", "test_2"])
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner",
                               message = msg)
        msg = TestPackages("host.unittest", ["test_1", "test_2"])
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner",
                               message = msg)


    def run(self):
        self._send_testpackages()
        self._send_result("hardware_test", self.results_xml, "test_1")
        self._send_result("hardware_test", self.results_xml, "test_2")
        self._send_result("host.unittest", self.results_xml, "test_1")
        self._send_result("host.unittest", self.results_xml, "test_2")


####################################
# Timeout Scenarios Mocks
####################################

class MockTaskRunnerTimeout(object):

    def run(self):
        raise OtsGlobalTimeoutError("Mock")

####################################
# Error Scenarios Mocks
####################################

class MockTaskRunnerError(object):

    def run(self):
        msg = ErrorMessage("mock task runner", 6310)
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", 
                               message = msg)

