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

from ots.server.hub.options import Options, string_2_dict, string_2_list


class TestOptions(unittest.TestCase):

    def test_string_2_list(self):
        expected = ['mary', 'had', 'a', 'little', 'lamb']
        self.assertEquals(expected,
                          string_2_list("mary had a little lamb"))

    def test_string_2_dict(self):
        expected = {'veg': 'oranges', 'fruit': 'apples', 'meat': 'beef'}
        self.assertEquals(expected,
                          string_2_dict("fruit:apples"\
                                            " veg:oranges meat:beef"))
    def test_image(self):
        options = Options(**{"image" :"www.nokia.com"})
        self.assertEquals("www.nokia.com", options.image)

    def test_hw_packages(self):
        kwargs = {"image" : "www.nokia.com",
                 "packages": "pkg_1 pkg_2 pkg_3"}
        self.assertRaises(ValueError, Options, **kwargs)
        kwargs = {"image" : "www.nokia.com",
                 "packages": "pkg_1-tests pkg_2-tests pkg_3-tests"}
        options = Options(**kwargs)
        self.assertEquals(["pkg_1-tests", "pkg_2-tests", "pkg_3-tests"],
                          options.hw_packages)

    def test_host_packages(self):
        kwargs = {"image" : "www.nokia.com"}
        options = Options(**kwargs)
        self.assertEquals([], options.host_packages)
        kwargs = {"image" : "www.nokia.com",
                 "hosttest": "pkg_1-tests pkg_2-tests pkg_3-tests"}
        options = Options(**kwargs)
        self.assertEquals(["pkg_1-tests", "pkg_2-tests", "pkg_3-tests"],
                          options.host_packages)

    def test_emmc(self):
        kwargs = {"image" : "www.nokia.com",
                  "emmc" : "foo"}
        options = Options(**kwargs)
        self.assertEquals("foo", options.emmc)

    def test_priority(self):
        kwargs = {"image" : "www.nokia.com",
                  "distribution_model" : "perpackage"}
        options = Options(**kwargs)
        self.assertEquals(1, options.priority)
        kwargs = {"image" : "www.nokia.com",
                  "distribution_model" : "foo"}
        options = Options(**kwargs)
        self.assertEquals(2, options.priority)

    def test_flasher(self):
        kwargs = {"image" : "www.nokia.com",
                  "flasher" : "www.meego.com"}
        options = Options(**kwargs)
        self.assertEquals("www.meego.com", options.flasher)

    def test_testfilter(self):
        kwargs = {"image" : "www.nokia.com",
                  "testfilter" : '"hello world"'}
        options = Options(**kwargs)
        self.assertEquals('\'"\\\'hello world\\\'"\'',
                          repr(options.testfilter))

if __name__ == "__main__":
    unittest.main()
