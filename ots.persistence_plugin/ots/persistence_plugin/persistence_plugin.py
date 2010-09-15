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
Spike API
"""

import logging
import datetime

from ots.common.framework.plugin_base import PluginBase

from ots.persistence_plugin.django_model_delegate import init_testrun
from ots.persistence_plugin.django_model_delegate import set_testrun_result
from ots.persistence_plugin.django_model_delegate import set_testrun_error

def _testplan_name(request_id):
    """
    @type request_id: C{string}
    @param request_id: An identifier for the request from the client

    @rtype: C{string}
    @rparam: The testplan name
    """
    return "Testplan %s"%(request_id)


def _image_name(image):
    """
    @type image: C{string}
    @param image: The image url

    @rtype: C{string}
    @rparam: The image name
    """

    return image.split("/")[-1]

#FIXME: imagename and sw_version in upload

class PersistencePlugin(PluginBase):

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
        self.end_time = None
        self._testrun_id = None
        self._error_info = None
        self._error_code = None
        #
        testplan_name = _testplan_name(request_id)
        image_name = _image_name(image)
        self._testrun_id = init_testrun(request_id, testrun_id, testplan_id,
                                        label, image, image_name, sw_version,
                                        cmt, target_packages)


    ###############################

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
        #FIXME
        set_testrun_error

    @property
    def _get_error(self):
        return self._error_code, self_error_info

    error = property(_get_error, _set_error)

    def _set_result(self, result):
        """
        @param result: L{ots.results.TestrunResult}
        @param result: The results of the testrun
        """
        set_test_run_result(result)
        self._result = result

    @property
    def _get_result(self):
        """
        @param result: L{ots.results.TestrunResult}
        @param result: The results of the testrun
        """
        return self._result

    result = property(_get_result, _set_result)
