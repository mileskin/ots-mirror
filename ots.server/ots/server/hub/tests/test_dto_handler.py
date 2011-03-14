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

import logging
import logging.handlers

from ots.common.dto.api import Results
from ots.common.dto.api import Packages
from ots.common.dto.api import Monitor 

from ots.server.hub.dto_handler import DTOHandler

class HandlerStub(logging.Handler):

    expected_msg = None

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        assert(record.msg == self.expected_msg)

class TestDTOHandler(unittest.TestCase):

    def tearDown(self):
        log = logging.getLogger()
        for handler in log.handlers:
            log.removeHandler(handler)

        

    def test_results(self):
        dto_handler = DTOHandler()
        results = Results("tatam_xml_testrunner_results_for_foo" , "<test>bar</test>", package = "pkg1",
                          environment = "unittest")
        dto_handler._results(results)
        self.assertEquals(["pkg1"], 
                          dto_handler.tested_packages.packages("unittest"))
        dto_handler._results(results)
        self.assertEquals(["pkg1", "pkg1"], 
                          dto_handler.tested_packages.packages("unittest"))

    def test_packages(self):
        dto_handler = DTOHandler()
        pkgs = Packages("env", ["pkg1", "pkg2"])
        dto_handler._packages(pkgs)
        pkgs = Packages("env", ["pkg3", "pkg4"])
        dto_handler._packages(pkgs)
        self.assertEquals(["pkg1", "pkg2", "pkg3", "pkg4"],
                           dto_handler.expected_packages.packages("env"))

    def test_callback_exception(self):
        dto_handler = DTOHandler()
        class TestException(Exception):
            pass
        
        dto_handler._callback(signal = None, dto = TestException())
        self.assertEquals(len(dto_handler.exceptions), 1)
        self.assertTrue(isinstance(dto_handler.exceptions[0], TestException))

    def test_callback_log_record(self):
      
        logging.basicConfig(filename = "/dev/null",
                            level=logging.DEBUG)
        logger = logging.getLogger()
        log_handler = HandlerStub()
        log_handler.setLevel(logging.DEBUG)
        
        logger.addHandler(log_handler)
        record = logging.LogRecord("unittest", logging.DEBUG, "foo", 2,
                                   "bar", "baz", None)
        log_handler.expected_msg = "bar"
        dto_handler = DTOHandler()
        dto_handler._callback(signal = None, dto = record)
        logger.removeHandler(log_handler)
        
        
       

if __name__ == "__main__":
    unittest.main()
