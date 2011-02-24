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
Visitors for the Tests Results and Test Definition
"""

class ElementTreeVisitor(object):
    """
    Extrinsic Visitor for the ElementTree Data Structure
    """

    _processors = []

    def add_processor(self, processor):
        """
        @type processor: C{ElementProcessorBase
        @param dispatcher: Dispatch strategy
        """
        self._processors.append(processor)

    def visit(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element 

        Preorder Tree Traversal dispatching elements on route
        """
        for processor in self._processors:
            processor.process_element(element)
        map(self.visit, element.getchildren())
                
