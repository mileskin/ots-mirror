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

from ots.server.hub.options import Options, string_2_dict, string_2_list
from StringIO import StringIO

class TestOptions(unittest.TestCase):

    def test_image(self):
        options = Options(**{"image" :"www.nokia.com", "distribution_model": "default"})
        self.assertEquals("www.nokia.com", options.image)

    def test_hw_packages(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                 "packages": "pkg_1 pkg_2 pkg_3"}
        self.assertRaises(ValueError, Options, **kwargs)
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                 "packages": "pkg_1-tests pkg_2-tests pkg_3-tests"}
        options = Options(**kwargs)
        self.assertEquals(["pkg_1-tests", "pkg_2-tests", "pkg_3-tests"],
                          options.hw_packages)

    def test_host_packages(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default"}
        options = Options(**kwargs)
        self.assertEquals([], options.host_packages)
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                 "hosttest": "pkg_1-tests pkg_2-tests pkg_3-tests"}
        options = Options(**kwargs)
        self.assertEquals(["pkg_1-tests", "pkg_2-tests", "pkg_3-tests"],
                          options.host_packages)
        
    def test_hw_testplans(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                 "hw_testplans": [["plan1", "foo"], ["plan2", "bar"]]}
        options = Options(**kwargs)
        self.assertEquals(len(options.hw_testplans), 2)
        self.assertTrue(isinstance(options.hw_testplans[0], StringIO))

    def test_host_testplans(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                 "host_testplans": [["plan1", "foo"], ["plan2", "bar"]]}
        options = Options(**kwargs)
        self.assertEquals(len(options.host_testplans), 2)
        self.assertTrue(isinstance(options.host_testplans[0], StringIO))

    def test_emmc(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                  "emmc" : "foo"}
        options = Options(**kwargs)
        self.assertEquals("foo", options.emmc)

    def test_distribution_model(self):
        kwargs = {"image" : "www.nokia.com",
                  "distribution_model" : "perpackage",
                  "packages": "asdf-tests"}
        options = Options(**kwargs)
        self.assertEquals("perpackage", 
                          options.distribution_model)

    def test_distribution_model_validation(self):
        kwargs = {"image" : "www.nokia.com",
                  "distribution_model" : "perpackage"}
        self.assertRaises(ValueError, Options, **kwargs)

    def test_flasher(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                  "flasher" : "www.meego.com"}
        options = Options(**kwargs)
        self.assertEquals("www.meego.com", options.flasher)

    def test_testfilter(self):
        kwargs = {"image" : "www.nokia.com", "distribution_model": "default",
                  "testfilter" : '"hello world"'}
        options = Options(**kwargs)
        self.assertEquals('\'"\\\'hello world\\\'"\'',
                          repr(options.testfilter))

if __name__ == "__main__":
    unittest.main()
