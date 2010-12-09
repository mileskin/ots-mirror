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

from ots.common.dto.api import Results, Packages
from ots.common.dto.api import OTSException
from ots.common.dto.api import DTO_SIGNAL

from ots.server.distributor.api import OtsExecutionTimeoutError

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
        results = Results(name, results_xml,
                          package = name,
                          hostname = "mock_task_runner",
                          environment = environment)
        DTO_SIGNAL.send(sender = "MockTaskRunner", 
                               dto = results)

    @staticmethod
    def _send_testpackages():
        raise NotImplementedError

class MockTaskRunnerResultsMissing(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        pkgs = Packages("hardware_test", ["test_1", "test_2", "test_3"])
        DTO_SIGNAL.send(sender = "MockTaskRunner",
                               dto = pkgs)

class MockTaskRunnerResultsFail(MockTaskRunnerResultsBase):

    @staticmethod
    def _send_testpackages():
        pkgs = Packages("hardware_test", ["test_1", "test_2"])
        DTO_SIGNAL.send(sender = "MockTaskRunner",
                               dto = pkgs)

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
        pkgs_1 = Packages("hardware_test", ["test_1", "test_2"])
        DTO_SIGNAL.send(sender = "MockTaskRunner",
                               dto = pkgs_1)
        pkgs_2 = Packages("host.unittest", ["test_1", "test_2"])
        DTO_SIGNAL.send(sender = "MockTaskRunner",
                               dto = pkgs_2)


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
        raise OtsExecutionTimeoutError("Mock")

####################################
# Error Scenarios Mocks
####################################

class MockTaskRunnerError(object):

    def run(self):
        exc = OTSException("mock task runner", 6310)
        DTO_SIGNAL.send(sender = "MockTaskRunner", 
                               dto = exc)

