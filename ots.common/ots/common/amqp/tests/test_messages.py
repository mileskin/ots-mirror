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

import ots.common

from ots.common.resultobject import ResultObject 
from ots.common.amqp.messages import CommandMessage, ResultMessage
from ots.common.amqp.messages import StatusMessage, ErrorMessage
from ots.common.amqp.messages import TestPackageListMessage
from ots.common.amqp.messages import pack_message, unpack_message


class TestMessages(unittest.TestCase):
    
    def test_command_message(self): 
        cmd_msg = CommandMessage(["echo", "hello world"], 
                                  "response_queue", "task_id") 
        packed_msg = pack_message(cmd_msg)
        rec_msg = unpack_message(packed_msg)
        self.assertEquals("echo hello world", rec_msg.command)
        self.assertEquals("response_queue", rec_msg.response_queue)
        self.assertEquals("task_id", rec_msg.task_id)
        self.assertEquals(ots.common.__VERSION__, rec_msg.__version__)

    def test_result_message(self):
        res_msg =  ResultMessage("foo.txt", "foo", "pkg_1", 
                                 "unittest", "meego")
        packed_msg = pack_message(res_msg)
        rec_msg = unpack_message(packed_msg)
        self.assertTrue(isinstance(rec_msg.result, ResultObject))

    def test_status_message(self):
        status_msg = StatusMessage("state", "status_info")
        packed_msg = pack_message(status_msg)
        rec_msg = unpack_message(packed_msg)
        self.assertEquals("state", rec_msg.state)       
        self.assertEquals("status_info", rec_msg.status_info)
               
    def test_error_message(self):
        error_msg = ErrorMessage("error_info", "error_code")
        packed_msg = pack_message(error_msg)
        rec_msg = unpack_message(packed_msg)
        self.assertEquals("error_info", rec_msg.error_info)       
        self.assertEquals("error_code", rec_msg.error_code)

    def test_test_package_list(self):
        pkg_msg = TestPackageListMessage("environment", ["pkg1", "pkg2"])
        packed_msg = pack_message(pkg_msg)
        rec_msg = unpack_message(packed_msg)
        self.assertEquals("environment", rec_msg.environment)       
        self.assertEquals(["pkg1", "pkg2"], rec_msg.packages)

if __name__ == "__main__":
    unittest.main()
