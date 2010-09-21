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
from ots.server.input.default import Default



class testDefaultPlugin(unittest.TestCase):
    

    def setUp(self):

        self.plugin = Default()
            
    def tearDown(self):
        pass

        
    def test_store_url(self):
        self.plugin.store_url("asdf","asdf")

    def test_get_changed_packages(self):
        self.plugin.get_changed_packages(3)

    def test_store_file(self):
        self.plugin.store_file("asdf", "asdf", "asdf", "asdf")





if __name__ == '__main__':
    unittest.main()
