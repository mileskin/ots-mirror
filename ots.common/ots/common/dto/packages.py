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

"""
The Container for the `Packages`
"""

from ots.common.dto.environment import Environment

class Packages(dict):
    """
    Associates a list of Packages with an Environment
    the logic for amalgamating the data
    """

    def __init__(self, environment, packages):
        """
        @type environment : L{ots.common.dto.environment.Environment} or
                            C{str}
        @param environment: The environment for the test packages 

        @type packages: C{list} of C{str}
        @param packages: The test packages
        """
        if isinstance(environment, str):
            environment = Environment(environment)
        dict.__init__(self)
        self[environment] = packages

    @property
    def environments(self):
        """
        The names of the environments
        @rtype: C{list} of C{str}
        """
        envs = [key.environment for key in self.keys()]
        envs.sort()
        return envs

    
    def packages(self, environment):
        """
        @type environment: L{ots.common.dto.environment.Environment} or C{str}
        @param environment: The environment or the name of the environment

        @rtype: C{list} of C{str}
        @return: The names of the packages
        """
        if isinstance(environment, str):
            return self[Environment(environment)]
        return self[environment]

    def update(self, packages):
        """
        Updates the packages extending lists on matching keys

        @type packages: L{ots.common.dto.environment.Packages} 
        @param packages: Packages
        """
        for env, pkgs in packages.items():
            if self.has_key(env):
                self[env].extend(pkgs)
            else:
                self[env] = pkgs
            
    def __str__(self):
        return str(dict([(str(k), v) for k, v in self.items()]))
