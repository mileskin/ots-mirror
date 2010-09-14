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

# PLACEHOLDER

import datetime

def _testplan_name(request_id):
    """
    @type request: C{string}
    @param request: An identifier for the request from the client

    @rtype: C{string}
    @rparam: The testplan name
    """
    return "Testplan %s"%(request_id)

#FIXME: imagename and sw_version in upload

class PersistencePlugin(object):

    """
    Spike to define the interface for the
    Persistence plugin
    """

    def __init__(self, request_id, testplan_id, sw_product,
                       gate, label,  hw_packages, image, target_packages):

        """
        @type request_id: C{string}
        @param request_id: An identifier for the request from the client

        @type testplan_id: C{str}
        @param testplan_id: The Testplan ID

        @type sw_product: C{string}
        @param sw_product: Name of the sw product this testrun belongs to

        @type gate: C{str}
        @param gate: TODO

        @param label: C{str}
        @type label: TODO

        @type hw_packages: C{list}
        @param hw_packages: A list of the hardware packages

        @type image: C{str}
        @param image: The image URL

        @param target_packages: C{list}
        @type target_packages: The target packages
        """
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self._testrun_id = None
        self._error_info = None
        self._error_code = None

    @property
    def testrun_id(self):
        """
        @type: C{str}
        @rparam: Testrun ID
        """
        return self._testrun_id

    def _set_error(self, exception):
        """
        @type: L{Exception}
        @param: Exception
        """
        pass

    @property
    def _get_error(self):
        return self._error_code, self_error_info

    error = property(_get_error, _set_error)

    def _set_result(self, result):
        """
        @param result: L{ots.results.TestrunResult}
        @param result: The results of the testrun
        """
        self.end_time = datetime.datetime.now()
        self._result = result

    @property
    def _get_result(self):
        """
        @param result: L{ots.results.TestrunResult}
        @param result: The results of the testrun
        """
        return self._result

    result = property(_get_result, _set_result)
