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
Essentially provides a kind of 'Strategy' behaviour 
for the `accept` method on a node for the tree
traversal performed by ResultsVisitor

Sublclasses provide methods that correspond to the name
of the Element that they are processing e.g.

{{{
    def _preproc_case(self, element):
        #pre processes 'case'

    def _postproc_case(self, element):
        #post processes 'case'
}}}
"""

    
class ResultsProcessorBase(object):
    """
    Closely associated with the ResultsVisitor class
   
    Supported implementation relies not only 
    dispatch of the node but a 'post_processor' step
    """

    @staticmethod
    def _pre_tag_method_name(tag):
        """
        @type tag: C{string} 
        @param tag: The tag name

        @rtype: C{string}
        @return: The preprocessor method name associated with the tag
        """
        return "_preproc_%s" % (tag)

    @staticmethod
    def _post_tag_method_name(tag):
        """
        @type tag: C{string} 
        @param tag: The tag name

        @rtype: C{string}
        @return: The postprocessor method name associated with the tag
        """
        return "_postproc_%s" % (tag)

    def _process(self, method_name, *args):
        """
        @type method_name: C{string} 
        @param tag: The name of the method

        Safe dispatches of the method_name for the args
        """
        if hasattr(self, method_name):
            func = getattr(self, method_name)
            return func(*args)
                  
    def dispatch_element(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element

        Dispatch the element
        """
        method_name = self._pre_tag_method_name(element.tag)
        return self._process(method_name, element)

    def post_process(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element

        'Postprocess' the element
        """
        method_name = self._post_tag_method_name(element.tag)
        return self._process(method_name)
