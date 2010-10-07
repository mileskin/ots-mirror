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

from ots.server.hub.options_factory import _default_options_dict
from ots.server.hub.options_factory import options_factory

class TestOptionsFactory(unittest.TestCase):
    
    def test_default_options_dict(self):
        expected = {'devicegroup' : 'examplegroup'}
        d = _default_options_dict("example_sw_product")
        self.assertEquals(expected, d["device"])

    def test_options_factory(self):
        options = options_factory("example_sw_product",
                                  {"image" : "www.nokia.com",
                                  "email-attachments" : "on",
                                   "device" : "foo:bar"})
        self.assertTrue(options.is_email_attachments_on)
        expected = {'foo' : 'bar'}
        self.assertEquals(expected, options.device)
        


if __name__ == "__main__":
    unittest.main()
