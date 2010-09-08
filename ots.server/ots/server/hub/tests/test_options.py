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

from ots.server.hub.options import Options
from ots.server.hub.options import _string_2_dict, _string_2_list

class TestOptions(unittest.TestCase):

    def test_string_2_list(self):
        expected = ['mary', 'had', 'a', 'little', 'lamb']
        self.assertEquals(expected,
                           _string_2_list("mary had a little lamb"))

    def test_string_2_dict(self):
        expected = {'veg': 'oranges', 'fruit': 'apples', 'meat': 'beef'}
        self.assertEquals(expected,
                           _string_2_dict("fruit:apples"\
                                           " veg:oranges meat:beef"))
    def test_image_url(self):
        options = Options({})
        self.assertEquals('', options.image_url)
        options = Options({"image" : "www.nokia.com"})
        self.assertEquals("www.nokia.com", options.image_url)

    def test_rootstrap(self):
        options = Options({})
        self.assertEquals('', options.rootstrap)
        options = Options({"rootstrap" : "www.nokia.com"})
        self.assertEquals("www.nokia.com", options.rootstrap)

    def test_hw_packages(self):
        options = Options({})
        self.assertEquals([], options.hw_packages)
        options = Options({"packages": "pkg_1 pkg_2 pkg_3"})
        self.assertEquals(["pkg_1", "pkg_2", "pkg_3"], options.hw_packages)

    def hosttest_packages(self):
        options = Options({})
        self.assertEquals([], options.host_packages)
        options = Options({"packages": "pkg_1 pkg_2 pkg_3"})
        self.assertEquals(["pkg_1", "pkg_2", "pkg_3"], options.hw_packages)

    def test_testplan_id(self):
        options = Options({"plan" : "1111"})
        self.assertEquals("1111", options.testplan_id)

    def test_execute(self):
        options = Options({"execute" : "true"})
        self.assertTrue(options.execute)
        options = Options({"execute" : "false"})
        self.assertFalse(options.execute)

    def test_gate(self):
        options = Options({})
        self.assertTrue(options.gate is None)
        options = Options({"gate" : "foo"})
        self.assertEquals("foo", options.gate)

    def test_label(self):
        options = Options({})
        self.assertTrue(options.label is None)
        options = Options({"label" : "foo"})
        self.assertTrue("label", options.label)

    def test_device(self):
        options = Options({"device" : "fruit:apples"\
                                           " veg:oranges meat:beef"})
        self.assertEquals({'veg': 'oranges',
                           'fruit': 'apples',
                           'meat': 'beef'}, options.device)

    def test_emmc(self):
        options = Options({"emmc" : "foo"})
        self.assertEquals("foo", options.emmc)

    def test_emmcurl(self):
        options = Options({"emmc" : "foo"})
        self.assertEquals("foo", options.emmcurl)

    def test_package_distributed(self):
        options = Options({"distribution_model" : "perpackage"})
        self.assertTrue(options.is_package_distributed)
        options = Options({"distribution_model" : "foo"})
        self.assertFalse(options.is_package_distributed)

    def test_flasher(self):
        options = Options({"flasher" : "www.nokia.com"})
        self.assertEquals("www.nokia.com", options.flasher)

    def test_testfilter(self):
        options = Options({"testfilter" : '"hello world"'})
        self.assertEquals('\'"\\\'hello world\\\'"\'',
                          repr(options.testfilter))

    def test_is_client_bifh(self):
        options = Options({"input_plugin" : "bifh"})
        self.assertTrue(option.is_client_bifh)
        options = Option{"input_plugin" : "foo"})
        self.assertFalse(option.is_client_bifh)

if __name__ == "__main__":
    unittest.main()
