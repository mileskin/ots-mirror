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

def _testplan_name(request_id):
    """
    @type request: C{string}
    @param request: An identifier for the request from the client

    @rtype: C{string}
    @rparam: The testplan name
    """
    return "Testplan %s"%(request_id)

def init_testrun(swproduct, request_id, notify_list,
                 testplan_id,  gate, label,  hw_packages,
                 image_url, target_packages):

    """
    @type sw_product: C{string}
    @param sw_product: Name of the sw product this testrun belongs to

    @type request_id: C{string}
    @param request_id: An identifier for the request from the client

    @type testplan_id: C{str}
    @param testplan_id: The Testplan ID

    @type gate: C{str}
    @param gate: TODO

    @param label: C{str}
    @type label: TODO

    @type hw_packages: C{list}
    @param hw_packages: A list of the hardware packages

    @type image_url: C{str}
    @param image_url: The image URL

    @param rootstrap: C{str}
    @type rootstrap: TODO

    @param target_packages: C{list}
    @type target_packages: The target packages

    @rparam: C{str}
    @rtype: Testrun ID

    Persists the Metadata associated with the run
    and returns a testrun ID
    """
    #Intended replacement for
    # - testrun_host.init_testrun
    # - ndbpluging.init_new_testrun
    pass


def finished_run(datetime):
    pass

def persist():
    pass
