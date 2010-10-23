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

from ots.report_plugin.report_plugin import ReportPlugin
from ots.results.api import TestrunResult

class TestrunStub(object):
    sw_version = None

class DataStoringStub(object):

    #TODO: There is a significant amount of
    #Sequential Coupling in DataStoring
    #Currently the stub makes no attempt to
    #replicate that

    testrun = TestrunStub()
    request_id = None
    testplan_id = None
    gate = None
    label = None
    result = None
    error_info = None
    error_code = None

    def set_or_create_request(self, request_id):
        self.request_id = request_id

    def set_or_create_label(self, label):
        self.label = label

    def set_or_create_testplan(self, name, gate):
        self.testplan_id = name
        self.gate = gate
        self.testplan = 1

    def new_testrun(self, result, starttime = None, endtime = None,
                                 error_code = None, error_info = None,
                                 finished = False, imagename = None,
                                 imageurl = None):

        return 42

    def set_or_create_swproduct(self, name):
        self.sw_product = name


    def set_testrun_result(self, result = None):
        self.result = result

    def set_testrun_error_code(self, code = None):
        self.error_code = code
        
    def set_testrun_error_info(self, info = None):
        self.error_info = info
        
class TestReportPlugin(unittest.TestCase):

    def test_init(self):
        data_storing = DataStoringStub()
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])
        self.assertEquals("req", data_storing.request_id)
        self.assertEquals("tp", data_storing.testplan_id)
        self.assertEquals("gate", data_storing.gate)
        self.assertEquals("label", data_storing.label)

    def test_testrun_id(self):
        data_storing = DataStoringStub()
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])

        self.assertEquals(42, report_plugin.testrun_id)

    def test_set_exception(self):
        class UnittestException(Exception):
            error_code = "bar"
            pass
        ut_exception = UnittestException("foo")
        data_storing = DataStoringStub() 
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])
        report_plugin.exception = ut_exception
        self.assertEquals("foo", data_storing.error_info)
        self.assertEquals("bar", data_storing.error_code)

    def test_get_exception(self):
        class UnittestException(Exception):
            error_code = "bar"
            pass
        ut_exception = UnittestException("foo")
        data_storing = DataStoringStub() 
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])
        report_plugin.exception = ut_exception
        self.assertEquals("foo", str(report_plugin.exception)) 

    def test_set_result(self):
        data_storing = DataStoringStub() 
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])
        report_plugin.result = TestrunResult.PASS
        self.assertEquals("PASS", data_storing.result)
        

    def test_get_result(self):
        data_storing = DataStoringStub() 
        report_plugin = ReportPlugin(data_storing, "req", "tp",
                                     "pdt", "gate", "label",
                                     ["hw_pkg1"], "www.nokia.com",
                                     ["tgt_pkg1"])
        report_plugin.result = TestrunResult.PASS
        self.assertEquals(TestrunResult.PASS, report_plugin.result)

if __name__ == '__main__':
    unittest.main()
