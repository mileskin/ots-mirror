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
from ots.common.datatypes.packages import Packages

class TestTestPackages(unittest.TestCase):
    
    def test_init(self):
        environment = Environment("env")
        packages = Packages(environment, ["pkg_1", "pkg_2"])
        self.assertEquals(environment,  packages.keys()[0])
        self.assertEquals(["pkg_1", "pkg_2"], packages.values()[0])
           
    def test_environments(self):
        environment = Environment("env1")
        packages = Packages(environment, ["pkg_1", "pkg_2"])
        packages.update({Environment("env2") : []})
        self.assertEquals(["env1", "env2"], packages.environments)

    def test_packages(self):
        environment = Environment("env1")
        packages = Packages(environment, ["pkg_1", "pkg_2"])
        packages.update({Environment("env2") : []})
        self.assertEquals(["pkg_1", "pkg_2"], 
                          packages.packages(environment))
        self.assertEquals(["pkg_1", "pkg_2"],
                          packages.packages("env1"))

    def test_getitem(self):
        environment = Environment("env1")
        packages = Packages(environment, ["pkg_1", "pkg_2"])
        self.assertEquals(["pkg_1", "pkg_2"], 
                          packages[Environment("env1")])

    def test_update(self):
        environment = Environment("env1")
        packages_1 = Packages(environment, ["pkg_1", "pkg_2"])
        packages_2 = Packages(environment, ["pkg_3", "pkg_4"])
        packages_1.update(packages_2)
        self.assertEquals(['pkg_1', 'pkg_2', 'pkg_3', 'pkg_4'],
                          packages_1.packages("env1"))


if __name__ == "__main__":
    unittest.main()
