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

from ots.common.api import OTSProtocol, PROTOCOL_VERSION
from ots.common.api import ResultObject

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
        result = ResultObject(name,
                              content = results_xml,
                              testpackage = name,
                              origin = "mock_task_runner",
                              environment = environment)
        kwargs = {OTSProtocol.RESULT : result,
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.RESULT_OBJECT}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

    @staticmethod
    def _send_testpackages():
        raise NotImplementedError

class MockTaskRunnerResultsMissing(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        kwargs = {OTSProtocol.ENVIRONMENT : "hardware_test",
                  OTSProtocol.PACKAGES : ["test_1", "test_2", "test_3"],
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

class MockTaskRunnerResultsFail(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        kwargs = {OTSProtocol.ENVIRONMENT: "hardware_test",
                  OTSProtocol.PACKAGES : ["test_1", "test_2"],
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)


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
        kwargs = {OTSProtocol.ENVIRONMENT: "hardware_test",
                  OTSProtocol.PACKAGES : ["test_1", "test_2"],
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

        kwargs = {OTSProtocol.ENVIRONMENT: "host.unittest",
                  OTSProtocol.PACKAGES : ["test_1", "test_2"],
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

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
        kwargs = {OTSProtocol.ERROR_CODE : 6310,
                  OTSProtocol.ERROR_INFO : "mock task runner",
                  OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTRUN_ERROR}
        TASKRUNNER_SIGNAL.send(sender = "MockTaskRunner", **kwargs)
