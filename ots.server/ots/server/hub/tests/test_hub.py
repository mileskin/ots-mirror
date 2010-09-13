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

from ots.common.framework.load_plugins import load_plugins

from ots.server.testrun.tests.mock_taskrunner import MockTaskRunnerResultsPass
from ots.server.hub.hub import run

options_dict = {"image" : "www.nokia.com" ,
                "rootstrap" : "www.meego.com",
                "packages" : "hw_pkg1-test pkg2-test pkg3-test",
                "plan" : "111",
                "execute" : "true",
                "gate" : "foo",
                "label": "bar",
                "hosttest" : "host_pkg1-test host_pkg2-test host_pkg3-test",
                "device" : "baz",
                "emmc" : "",
                "distribution-model" : "",
                "flasher" : "",
                "testfilter" : "",
                "input_plugin" : "bifh",
                "email" : "on",
                "email-attachments" : "on"}

class TestHub(unittest.TestCase):

    def test_run(self):
        mock_taskrunner = MockTaskRunnerResultsPass()
        run("foo", "bar", "baz",
            mock_taskrunner.run, **options_dict)

if __name__ == "__main__":
    unittest.main()
