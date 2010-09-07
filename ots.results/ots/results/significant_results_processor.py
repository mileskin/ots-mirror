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

from ots.results.results_processor_base import ResultsProcessorBase
from ots.results.results_schema import Names, TRUE

class SignificantResultsProcessor(ResultsProcessorBase):
    """
    SignificantResultsProcessor is closely associated with
    the ResultsVisitor

    Takes results from ElementTree elements and
    collects the results which are significant
    depending on the policy

    The `all_passed` attribute holds the state of the
    significant elements.
    """

    def __init__(self, insignificant_tests_matter):
        ResultsProcessorBase.__init__(self)
        self.insignificant_tests_matter = insignificant_tests_matter
        self.all_passed = None

    @staticmethod
    def _is_insignificant(element):
        """
        @type element: C{Element}
        @param element: An ElementTree Elemment

        @rtype: C{bool}
        @return: Is the element marked as not `insignificant`
        """
        insignificant = False
        items_dict = dict(element.items())
        if items_dict.has_key(Names.INSIGNIFICANT):
            insignificant = items_dict[Names.INSIGNIFICANT].lower()
            insignificant = (insignificant ==  TRUE)
        return insignificant

    def _is_processed(self, element):
        """
        @type element: C{Element}
        @param element: An ElementTree Elemment

        @rtype: C{bool}
        @return: True if the element is to be processed, False otherwise
        """
        is_insignificant = self._is_insignificant(element)
        return not is_insignificant or \
                     (is_insignificant and self.insignificant_tests_matter)

    @staticmethod
    def _result(element):
        """
        @type element: C{Element}
        @param element: An ElementTree Elemment

        @rtype: C{bool} or None
        @return: True for `pass`, False for `fail` and 'N/A'
        """
        items_dict = dict(element.items())
        results_dict = {"PASS": True,
                        "FAIL": False,
                        "N/A": False}
        result = items_dict[Names.RESULT].upper()
        return results_dict[result]

    #############################################
    # Node Processing
    #############################################

    def _case(self, element):
        """
        @type element: C{Element}
        @param element: An ElementTree Element

        Visit the `case` node
        """
        if self._is_processed(element):
            results = self._result(element)
            if self.all_passed is None:
                self.all_passed = result
            else:
                self.all_passed = result and self.all_passed
