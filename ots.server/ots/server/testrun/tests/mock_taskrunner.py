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

from ots.server.distributor.api import ERROR_SIGNAL
from ots.server.distributor.api import RESULTS_SIGNAL
from ots.server.distributor.api import PACKAGELIST_SIGNAL
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
        self._send_result(self.results_xml, "test_1")
        time.sleep(0.5)
        self._send_result(self.results_xml, "test_2")

    @staticmethod
    def _send_result(results_xml, name):
        result = ResultObject(name,
                              content = results_xml,
                              testpackage = name,
                              origin = "mock_task_runner",
                              environment = "hardware_test")
        kwargs = {OTSProtocol.RESULT : result}
        RESULTS_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

    @staticmethod
    def _send_testpackages():
        raise NotImplementedError

class MockTaskRunnerResultsMissing(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        kwargs = {OTSProtocol.ENVIRONMENT : "hardware_test",
                  OTSProtocol.PACKAGES : ["test_1", "test_2", "test_3"]}
        PACKAGELIST_SIGNAL.send(sender = "MockTaskRunner", **kwargs)

class MockTaskRunnerResultsFail(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        kwargs = {OTSProtocol.ENVIRONMENT: "hardware_test",
                  OTSProtocol.PACKAGES : ["test_1", "test_2"]}
        PACKAGELIST_SIGNAL.send(sender = "MockTaskRunner", **kwargs)


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
                  OTSProtocol.ERROR_INFO : "mock task runner"}
        ERROR_SIGNAL.send(sender = "MockTaskRunner", **kwargs)
