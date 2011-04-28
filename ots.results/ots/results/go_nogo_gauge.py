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
Go / NoGo on the basis of results_xmls
"""

from ots.results.parse_results import parse_results
from ots.results.testrun_result import TestrunResult

def go_nogo_gauge(results_xmls, insignificant_tests_matter = False):
    """
    @type results_xmls: C{list} of C{file}
    @param results_xmls: A list of the result_xmls

    @rtype: L{TestrunResult}
    @return: PASS / FAIL / NO_CASES
    """
    ret_val = TestrunResult.NO_CASES
    aggregated_results = []
    for results_xml in results_xmls:
        all_passed = parse_results(results_xml.read(),
                                   insignificant_tests_matter)
        if all_passed is not None:
            aggregated_results.append(all_passed)
    if aggregated_results:
        if all(aggregated_results):
            ret_val = TestrunResult.PASS
        else:
            ret_val = TestrunResult.FAIL
    return ret_val
