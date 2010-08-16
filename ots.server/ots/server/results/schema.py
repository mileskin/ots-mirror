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
Provides Class based access to Schema definition
"""

import os 

import xml.etree.cElementTree as ElementTree 

##################

TRUE = "true"
FALSE = "false"


###############
# ElementTree 
###############

_NAME = 'name'
_VALUE = 'value'

#################################
# XSD DEFINITION
#################################


OTS_TESTDEFINITION = "OTS_TESTDEFINITION"
TESTDEFINITION_RESULTS_XSD = "testdefinition-results.xsd"
SCHEMA_FILENAME = os.path.join(os.environ[OTS_TESTDEFINITION], 
                               TESTDEFINITION_RESULTS_XSD)


class ElementDispatcher(object):

    names = []
    values = []

    def dispatch_element(self, element): 
        items_dict = dict(element.items())
        name = items_dict.get(_NAME, None)
        if name:
            self.names.append(name)
        value = items_dict.get(_VALUE, None)
        if value:
            self.values.append(value)

class ElementTreeVisitor(object):
    """
    Extrinsic Visitor for the ElementTree Data Strucuture
    """

    _dispatchers = []

    def add_dispatcher(self, dispatcher):
       self._dispatchers.append(dispatcher)

    def visit(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element 

        Preorder Tree Traversal doing the 
        'Pre' and 'Post' processing for the processors 
        """
        for dispatcher in self._dispatchers:
            dispatcher.dispatch_element(element)
        for child_node in element.getchildren():
            self.visit(child_node)

class TestResultsSchemaMeta(type):
    """
    Metaclass to set attributes of the 
    appropriately named superclass
    on the basis of the Schema
    """

    def __new__(cls, name, bases, dct):
        new = type.__new__(cls, name, bases, dct)
        xsd = open(SCHEMA_FILENAME, "r").read()
        visitor = ElementTreeVisitor()
        element_dispatcher = ElementDispatcher()
        visitor.add_dispatcher(element_dispatcher)
        root = ElementTree.fromstring(xsd)
        visitor.visit(root)
        tags = getattr(element_dispatcher, name.lower())
        for tag in tags:
            setattr(new, tag.upper(), tag)
        return new

    def __init__(cls, name, bases, dct):
        super(TestResultsSchemaMeta, cls).__init__(name, bases, dct)


class Names(object):
    """
    Names of the Schema Tags as Defined in the XSD
    """

    __metaclass__ = TestResultsSchemaMeta


class Values(object):
    """
    Values of the Schema Tags as Defined in the XSD
    """

    __metaclass__ = TestResultsSchemaMeta
