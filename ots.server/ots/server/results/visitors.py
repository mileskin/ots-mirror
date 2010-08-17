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
Visitors for the Tests Results and Test Definition
"""

class ElementTreeVisitor(object):
    """
    Extrinsic Visitor for the ElementTree Data Structure
    """

    _dispatchers = []

    def add_dispatcher(self, dispatcher):
        """
        @type dispatcher: C{ElementDispatcherBase
        @param dispatcher: Dispatch strategy
        """
        self._dispatchers.append(dispatcher)

    def visit(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element 

        Preorder Tree Traversal dispatching elements on route
        """
        for dispatcher in self._dispatchers:
            dispatcher.dispatch_element(element)
        for child_node in element.getchildren():
            self.visit(child_node)

class ResultsVisitor(ElementTreeVisitor):
    """
    Visitor for the Test Results XML

    Adapted to allow for backward compatibility 
    with the original pattern

    Closely associated with ResultsProcessorBase
    """

    _processors = []

    def __init__(self):
        ElementTreeVisitor.__init__(self)

    def add_processor(self, processor):
        """
        @type element: L{ots.server.results.ResultsProcessorBase} 
        @param element: A results processor

        Add a processor to accept nodes in tree traversal
        """
        #FIXME This is to maintain a migration path from 
        #the original implementation
        #Conventionally the Visitor Pattern 
        #just dispatches the node
        self._dispatchers.append(processor)
        self._processors.append(processor)

    def visit(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element 

        Extends the ElementTreeVisitor to perform
        'post processing' backward compatibility
        """
        ElementTreeVisitor.visit(self, element)
        #FIXME review the necessity of this
        for processor in self._processors:
            processor.post_process(element)
