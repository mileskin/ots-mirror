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

from ots.common.datatypes.environment import Environment

class Packages(dict):
    """
    The container for `Packages`
    Essentially gives a klass signature to a dictionary
    and provides some convenience methods
    """

    def __init__(self, environment, packages):
        """
        @type environment : L{ots.common.datatypes.environment.Environment} or
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
        @rtype: C{list} of C{str}
        @rparam: The names of the environments
        """
        envs = [key.environment for key in self.keys()]
        envs.sort()
        return envs

    
    def packages(self, environment):
        """
        @type: L{ots.common.datatypes.environment.Environment} or C{str}
        @param: The environment or the name of the environment

        @rtype: C{list} of C{str}
        @rparam: The names of the packages
        """
        if isinstance(environment, str):
            return self[Environment(environment)]
        return self[environment]
