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

from ots.common.datatypes.environment import Environment

class TestEnvironment(unittest.TestCase):
    
    def test_is_host_test(self):
        env = Environment("environment")
        self.assertFalse(env.is_host)
        env = Environment("host.environment")
        self.assertTrue(env.is_host)

    def test_is_hardware(self):
        env = Environment("environment")
        self.assertFalse(env.is_hw)
        env = Environment("hardware")
        self.assertTrue(env.is_hw)

    def test_is_equals(self):
        env_1 = Environment("environment1")
        env_2 = Environment("environment1")
        env_3 = Environment("environment2")
        self.assertEquals(env_1, env_2)
        self.assertNotEquals(env_1, env_3)
       
if __name__ == "__main__":
    unittest.main()
