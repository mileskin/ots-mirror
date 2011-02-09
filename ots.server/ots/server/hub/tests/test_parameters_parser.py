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

from ots.server.hub.parameters_parser import string_2_list, string_2_dict

class TestParametersParser(unittest.TestCase):

    def test_string_2_list(self):
        expected = ['mary', 'had', 'a', 'little', 'lamb']
        self.assertEquals(expected,
                          string_2_list("mary had a little lamb"))

    def test_string_2_dict(self):
        expected = {'veg': 'oranges', 'fruit': 'apples', 'meat': 'beef'}
        self.assertEquals(expected,
                          string_2_dict("fruit:apples"\
                                            " veg:oranges meat:beef"))

if __name__ == "__main__":
    unittest.main()
