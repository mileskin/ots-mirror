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

from StringIO import StringIO
from ots.common.datatypes.environment import Environment

class Results(object):
    """
    The Results XML and associated metadata
    """

    def __init__(self, name, content, 
                       package = None, origin = None, environment = None):
        """
        @type name : C{str}
        @param name : The name of the results_xml

        @type content : C{str}
        @param content : The xml content

        @type package : C{str}
        @param package : The associated package

        @type origin : C{str}
        @param origin : The origin

        @type environment : C{str}
        @param environment : The name of the Environment
        """
        self.results_xml = StringIO(content)
        self.results_xml.name = name
        self.package = package
        self.origin = origin
        self.environment = Environment(environment)

