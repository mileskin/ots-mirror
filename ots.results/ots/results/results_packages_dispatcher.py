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
ResultsProcessor that populates the PackageResults
"""

from ots.common.api import TestedPackages

from ots.results.results_processor_base import ResultsDispatcherBase
from ots.results.results_schema import Names, TRUE

class SignificantResultsDispatcher(ResultsDispatcherBase):
    """
    ResultsProcessor is closely associated with 
    the ResultsVisitor 

    Takes results from ElementTree elements and 
    collects the results which are significant
    depending on the policy
    """

    def __init__(self, insignificant_tests_matter):
        ResultsDispatcherBase.__init__(self)
        self.insignificant_tests_matter = insignificant_tests_matter

    @staticmethod
    def _is_significant(element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Elemment 

        @rtype: C{bool}
        @return: Is the element marked as not `insignificant`
        """
        is_significant = True
        items_dict = dict(element.items())
        if items_dict.has_key(Names.INSIGNIFICANT):
            insignificant = items_dict[Names.INSIGNIFICANT].lower()
            is_significant = not (insignificant ==  TRUE)
        return is_significant

    #############################################
    # Node Processing 
    #############################################
        
    def _case(self, element):
        """
        @type element: C{Element} 
        @param element: An ElementTree Element 
 
        Dispatch the `case` node
        """
        is_significant = self._is_significant(element)
        items_dict = dict(element.items())
        result = items_dict[Names.RESULT]
        if is_significant or self.insignicant_tests_matter:
            print 1111,result
        
