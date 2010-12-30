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

"""
The Container for a the Result file
"""
from StringIO import StringIO
from ots.common.dto.environment import Environment

RESULT_XML_PATTERN = "tatam_xml_testrunner_results_for"
DEFINITION_XML_PATTERN = "test_definition_for_"

class Results(object):
    """
    The Result file and associated metadata
    """

    def __init__(self, name, content, 
                       package = None, hostname = None, environment = None):
        """
        @type name : C{str}
        @param name : The name of the result file

        @type content : C{str}
        @param content : file content

        @type package : C{str}
        @param package : The associated package

        @type hostname : C{str}
        @param hostname : The hostname of the machine conducting the tests

        @type environment : C{str}
        @param environment : The name of the Environment
        """
        self.data = StringIO(content)
        self.data.name = name
        self.package = package
        self.hostname = hostname
        self.environment = Environment(environment)

    @property
    def name(self):
        return self.data.name

    @property
    def is_result_xml(self):
        """
        @rtype : C{bool}
        @rparam : True if this is a result xml
        """
        if self.name.startswith(RESULT_XML_PATTERN):
            return True
        else:
            return False

    @property 
    def is_definition_xml(self):
        """
        @rtype : C{bool}
        @rparam : True if this is a test definition xml
        """
        if self.name.startswith(DEFINITION_XML_PATTERN):
            return True
        else:
            return False
