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

from ots.server.hub.sandbox import Sandbox
from ots.server.hub.options import Options
from ots.server.hub.options_factory import OptionsFactoryException

class CantStringify(object):
    
    def __str__(self):
        raise ValueError



options_dict = {"image" : "www.nokia.com" ,
                "rootstrap" : "www.meego.com",
                "packages" : "hw_pkg1-test pkg2-test pkg3-test",
                "plan" : "111",
                "hosttest" : "host_pkg1-test host_pkg2-test host_pkg3-test",
                "device" : "devicegroup:foo",
                "emmc" : "",
                "distribution-model" : "",
                "flasher" : "",
                "testfilter" : "",
                "input_plugin" : "bifh",
                "email" : "on",
                "email-attachments" : "on",
                "foo" : 11111}



class TestSandbox(unittest.TestCase):

    def test_sw_product(self):
        sandbox = Sandbox(CantStringify(), 111)
        self.assertEquals("example_sw_product", sandbox.sw_product)

    def test_request_id(self):
        sandbox = Sandbox(111, CantStringify())
        self.assertEquals("default_request_id", sandbox.request_id)

    def test_testrun_uuid(self):
        sandbox = Sandbox(111, 111)
        self.assertTrue(isinstance(sandbox.testrun_uuid, str))

    def test_options_raises(self):
        sandbox = Sandbox(111, 111, **options_dict)
        self.assertTrue(isinstance(sandbox.options, Options))
        def _raise():
            raise sandbox.exc_info()[0]
        self.assertRaises(OptionsFactoryException, _raise)
    
if __name__ == "__main__":
    unittest.main()
