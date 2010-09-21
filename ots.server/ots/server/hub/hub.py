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
Very much a spike
"""

import sys
import os
import logging

from ots.server.testrun.testrun import Testrun

from ots.server.hub.options import Options
from ots.server.hub.init_logging import init_logging
from ots.server.hub.plugins import ReportPlugin
from ots.server.hub.plugins import BifhPlugin

LOG = logging.getLogger(__name__)


#FIXME: Hackish implementation WIP whilst DataStoring in development 
from ots.report_plugin.tests.test_report_plugin import DataStoringStub 
DATA_STORING_STUB = DataStoringStub()


def run(sw_product, request_id, notify_list, run_test, **kwargs):
    """
    @type sw_product: C{string}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{string}
    @param request_id: An identifier for the request from the client

    @param notify_list: Email addresses for notifications
    @type product: C{list}
    """
    sw_product = sw_product.lower()
    bifh_plugin = BifhPlugin(request_id)
    target_packages = []
    if bifh_plugin is not None:
        target_packages = bifh_plugin.get_target_packages(request_id)

    #Options
    options = Options(**kwargs)
    #FIXME: Hackish initialisation as Datastoring is a WIP
    report_plugin = ReportPlugin(DATA_STORING_STUB,
                                 request_id,
                                 options.testplan_id,
                                 sw_product,
                                 options.gate,
                                 options.label,
                                 options.hw_packages,
                                 options.image,
                                 target_packages)
    if report_plugin is not None:
        init_logging(request_id, report_plugin.testrun_id)

    #Preprocessing_steps_here?

    try:
        LOG.debug("Initialising Testrun")
        is_hw_enabled = bool(len(options.hw_packages))
        is_host_enabled = bool(len(options.host_packages))
        testrun = Testrun(run_test, is_hw_enabled, is_host_enabled)
        result = testrun.run()
        LOG.debug("Testrun finished with result: %s"%(result))
        if report_plugin is not None:
            report_plugin.result = result
    except Exception, err:
        LOG.debug("Testrun Exception: %s"%(err))
        if report_plugin is not None:
            report_plugin.exception = sys.exc_info()[1]


    #Some post_processing steps here?
