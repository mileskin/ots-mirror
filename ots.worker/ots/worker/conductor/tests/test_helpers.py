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

from ots.worker.conductor.helpers import parse_list, \
                                         parse_config


class TestHelpers(unittest.TestCase):
    """Unit tests for helpers.py functions"""

    def test_parse_config(self):
        dirname = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        config_file_path = os.path.join(dirname, "conductor.conf")

        # Read configuration file and check correct parameters values
        config_dict = parse_config(config_file_path, "conductor")

        self.assertEquals(config_dict["device_packaging"], "rpm")
        self.assertEquals(config_dict["custom_config_folder"],
                          "/etc/conductor")
        self.assertEquals(config_dict["pre_test_info_commands_debian"],
                          "'initctl list', 'dpkg -l'")
        self.assertEquals(config_dict["pre_test_info_commands_rpm"],
                          "'chkconfig', 'rpm -qa'")
        self.assertEquals(config_dict["pre_test_info_commands"],
                          "'uname -a', 'pwd', 'uptime', 'ps', 'lsmod',\n"
                          "'top -n1 -b', 'df', 'ifconfig', 'route -n',\n"
                          "'printenv'")
        self.assertEquals(config_dict["files_fetched_after_testing"],
                          "\"/var/log/messages\"")
        self.assertEquals(config_dict["tmp_path"], "/tmp/")

        # Check that parameter update works (_update_config_items fuction)
        current_config = {'device_packaging': 'rpm',
                          'pre_test_info_commands_debian':
                          "'initctl lst', 'dpkg -o'"}
        config_dict = parse_config(config_file_path,
                                   "conductor", current_config)
        self.assertEquals(config_dict["device_packaging"], "rpm")
        self.assertEquals(config_dict["pre_test_info_commands_debian"],
                          "'initctl list', 'dpkg -l'")

    def test_parse_list(self):
        self.assertEquals(parse_list("'param1', 'param2'"),
                          ['param1', 'param2'])
        self.assertEquals(parse_list("'param,1', 'param2'"),
                          ['param,1', 'param2'])
        self.assertEquals(parse_list("param1, param2"),
                          ['param1', 'param2'])
        self.assertEquals(parse_list("param1,param2"),
                          ['param1', 'param2'])
        self.assertEquals(parse_list("\"param,1\",\"param2\""),
                          ['param,1', 'param2'])
        self.assertEquals(parse_list(
            "'param 1'    ,      ' param,.;:?2', param3"),
                          ['param 1', ' param,.;:?2', 'param3'])


if __name__ == "__main__":
    unittest.main()
