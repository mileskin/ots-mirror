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


from ots.server.hub.options import Options
from ots.server.hub.persistence_layer import init_testrun

def run(sw_product, request_id, notify_list, **kwargs):
    """
    @type sw_product: C{string}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{string}
    @param request_id: An identifier for the request from the client

    @param notify_list: Email addresses for notifications
    @type product: C{list}
    """

    options = Options(kwargs)
    init_testrun(sw_product, request_id, notify_list,
                 options.testplan_id,  options.gate, options.label,
                 options.hw_packages, options.image_url, options.rootstrap)
