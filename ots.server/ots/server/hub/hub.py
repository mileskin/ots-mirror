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

import os
import logging
import datetime

from ots.server.hub.options import Options
from ots.server.hub.init_logging import init_logging
from ots.server.hub.persistence_layer import init_testrun, persist, \
                                             finished_run
from ots.server.hub.bifh_plugin_spike import target_packages
from ots.server.hub.email_plugin_spike import EmailPluginSpike

from ots.server.testrun.testrun import Testrun

LOG = logging.getLogger(__name__)

def run(sw_product, request_id, notify_list, run_test, **kwargs):
    """
    @type sw_product: C{string}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{string}
    @param request_id: An identifier for the request from the client

    @param notify_list: Email addresses for notifications
    @type product: C{list}
    """
    target_pkgs = target_packages(request_id)
    options = Options(**kwargs)
    testrun_id = init_testrun(sw_product, request_id, notify_list,
                              options.testplan_id,  options.gate,
                              options.label, options.hw_packages,
                              options.image, target_packages)
    init_logging(request_id, testrun_id)
    #
    #Preprocessing_steps_here
    #
    is_hw_enabled = bool(len(options.hw_packages))
    is_host_enabled = bool(len(options.host_packages))
    testrun = Testrun(run_test, is_hw_enabled, is_host_enabled)
    testrun.run()
    finished_run(datetime.datetime.now())


    email_plugin = EmailPluginSpike(notify_list)
    #
    #Some post_processing steps here?

    persist()

