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

from pickle import loads, dumps
from ots.common.protocol import get_version as get_ots_protocol_version
from ots.common.protocol import OTSMessageIO, \
                                OTSProtocol, \
                                MessageException, \
                                _pack_message, \
                                _unpack_message

class AMQPMessageStub:
    body = None

class TestMessageIO(unittest.TestCase):

    def test_unpack_message(self):
        message = AMQPMessageStub()
        message.body = dumps("foo") 
        self.assertRaises(MessageException, OTSMessageIO.unpack_message, message)
        message.body = dumps({})
        self.assertRaises(MessageException, OTSMessageIO.unpack_message, message)
        message.body = dumps({OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST})
        self.assertRaises(MessageException, OTSMessageIO.unpack_message, message)
        message.body = dumps({OTSProtocol.MESSAGE_TYPE : OTSProtocol.TESTPACKAGE_LIST,
                              'environment' : "foo",
                              'packages' : "bar",
                              'version' : get_ots_protocol_version()})
        expected = {'environment': 'foo', 
                    'packages': 'bar', 
                    'message_type': 'TESTPACKAGE_LIST',
                    'version' : get_ots_protocol_version()}
        self.assertTrue(expected, OTSMessageIO.unpack_message(message))

    def test_pack_command_message(self):
        command = ["foo", "bar", "baz"]
        queue = "test"
        timeout = 1
        task_id = 1111111
        message = OTSMessageIO.pack_command_message(command, 
                                       queue, 
                                       timeout, 
                                       task_id)
        expected = {'response_queue': 'test', 
                    'command': ['foo', 'bar', 'baz'], 
                    'timeout': 1, 
                    'task_id': 1111111,
                    'version' : get_ots_protocol_version()}
        self.assertEquals(expected, loads(message.body))

    def test_state_change_message(self):
        msg_started = OTSProtocol.state_change_message('1', OTSProtocol.STATE_TASK_STARTED)
        msg_finished = OTSProtocol.state_change_message('1', OTSProtocol.STATE_TASK_FINISHED)
        self.assertNotEquals(msg_started.body, msg_finished.body)
        for msg in [msg_started.body, msg_finished.body]:
            self.assertTrue('STATE_CHANGE' in msg)
        self.assertTrue('started' in msg_started.body)
        self.assertTrue('finished' in msg_finished.body)

    def test_pack_and_unpack_result_message(self):
        values = ["bogus.file", "bazfoo content", "foobar origin", "package",
                  "my environment"]
        packed_msg = OTSMessageIO.pack_result_message(values[0], values[1],
                                                      values[2], values[3],
                                                      values[4])


        result_obj, version = OTSMessageIO.unpack_result_message(packed_msg)

        self.assertEquals(version, get_ots_protocol_version())
        # Check that we have correct values
        self.assertEquals(result_obj.name(), values[0])
        self.assertEquals(result_obj.get_content(), values[1])
        self.assertEquals(result_obj.get_origin(), values[2])
        self.assertEquals(result_obj.get_testpackage(), values[3])
        self.assertEquals(result_obj.get_environment(), values[4])
            
    def test_pack_and_unpack_testrun_status_message(self):
        my_state = "TESTING"
        my_status_info = "1,2,3 testing ..."
        packed_msg = OTSMessageIO.pack_testrun_status_message(my_state, my_status_info)
        state, status_info, version = OTSMessageIO.unpack_testrun_status_message(packed_msg)
        
        self.assertEquals(version, get_ots_protocol_version())
        # Check that we have correct values
        self.assertEquals(my_state, state)
        self.assertEquals(my_status_info, status_info)

    def test_pack_and_unpack_testrun_error_message(self):
        my_error_info = "Let's error"
        my_error_code = "007"
        packed_msg = OTSMessageIO.pack_testrun_error_message(my_error_info, my_error_code)
        error_info, error_code, version = OTSMessageIO.unpack_testrun_error_message(packed_msg)

        self.assertEquals(version, get_ots_protocol_version())
        # Check that we have correct values
        self.assertEquals(my_error_info, error_info)
        self.assertEquals(my_error_code, error_code)

    def test_pack_and_unpack_testpackage_list_message(self):
        my_environment = "my environment"
        my_packages = ["box 1", "box 2"]
        packed_msg = OTSMessageIO.pack_testpackage_list_message(my_environment, my_packages)
        environment, packages, version = OTSMessageIO.unpack_testpackage_list_message(packed_msg)

        self.assertEquals(version, get_ots_protocol_version())
        # Check that we have correct values
        self.assertEquals(my_environment, environment)
        self.assertEquals(my_packages, packages)


if __name__ == "__main__":
    unittest.main()
