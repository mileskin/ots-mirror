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
Essentially provides Strategy type behaviour 
for the `accept` method on a node for the tree
traversal performed by ResultsVisitor
"""

def _set_attrs(klass):
    #FIXME set from XSD
    tags = ["testresults", "suite", "set", 
            "case", "step", "expected_result",
            "return_code", "start", "end", 
            "stdout", "stderr"]
    def _base_method(self, *args):
        pass 
    for tag in tags:
        if not hasattr(klass, klass._pre_tag_method_name(tag)):
            setattr(klass, klass._pre_tag_method_name(tag), _base_method)
        if not hasattr(klass, klass._post_tag_method_name(tag)):
            setattr(klass, klass._post_tag_method_name(tag), _base_method)


class ResultsProcessorMeta(type):
    
    def __new__(cls, name, bases, dct):
        new = type.__new__(cls, name, bases, dct)
        _set_attrs(new)
        return new

    def __init__(cls, name, bases, dct):
        super(ResultsProcessorMeta, cls).__init__(name, bases, dct)

class ResultsProcessorException(Exception):
    pass
    
class ResultsProcessorBase(object):
    """
    Closely associated with the ResultsVisitor class
   
    """

    __metaclass__ = ResultsProcessorMeta

    @staticmethod
    def _pre_tag_method_name(tag):
        """
        @type tag: C{string} 
        @param tag: The tag name

        @rtype: C{string}
        @return: The preprocessor method name associated with the tag
        """
        return "_preproc_%s"%(tag)

    @staticmethod
    def _post_tag_method_name(tag):
        """
        @type tag: C{string} 
        @param tag: The tag name

        @rtype: C{string}
        @return: The postprocessor method name associated with the tag
        """
        return "_postproc_%s"%(tag)

    def _process(self, method_name, *args):
        """
        @type method_name: C{string} 
        @param tag: The name of the method

        Safe dispatches of the method_name for the args
        """
        if hasattr(self, method_name):
            fn = getattr(self, method_name)
            fn(*args)
                  
    def dispatch_element(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element

        Preprocess the element
        """
        method_name = self._pre_tag_method_name(element.tag)
        self._process(method_name, element)

    def post_process(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element

        Postprocess the element
        """
        method_name = self._post_tag_method_name(element.tag)
        self._process(method_name)
