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
Functions for interfacing with the DB
"""

from ots.server.testrun_db.models import Testrun, Link

def init_new_testrun(swproduct, testplan_id=None, testplan_name="",
                    gate=None, label=None):
    """
    Creates a new testrun into DB and returns testrun ID. 

    testplan_id, testplan_name, gate and label parameters are ignored

    TODO: Change the interface so that we get all initial data the db stores

    @param swproduct: Name of the sw product this testrun belongs to
    @type swproduct: C{string}

    @return: Testrun id
    @rtype: C{int}
    """

    run = Testrun(swproduct = swproduct)
    run.save()
    return run.id


def update_testrun(testrun_object, testrun_id):
    """
    Updates testrun information in DB. New info is read from testrun_object.

    @param testrun_object: Testrun object.
    @type testrun_object: L{Testrun}

    @param testrun_id: Testrun id in the DB.
    @type testplan_id: C{int}
    """
    testrun = Testrun.objects.get(id=testrun_id)
    state, status_info = testrun_object.get_state()
    testrun.imageurl = testrun_object.get_image_url()
    testrun.build_id = testrun_object.get_request_id()
    testrun.starttime = testrun_object.get_start_time()
    testrun.endtime = testrun_object.get_end_time()
    testrun.result = testrun_object.get_result()
    testrun.error_code = testrun_object.get_error_code()
    testrun.error_info = testrun_object.get_error_info()
    testrun.state = state
    testrun.status_info = status_info
    testrun.save()

def get_testrun_link(testrun_id):
    """
    This returns a link to testrun results
    TODO: Change so that multiple links and descriptions can be returned
    """
    db_testrun = Testrun.objects.get(id=testrun_id)
    stored_links = db_testrun.link_set.all()
    # Return only the first link for now...
    try:
        ret_val = stored_links[0].url
    except IndexError:
        ret_val = ""
    return ret_val



def add_testrun_link(testrun_id, url, description):
    """
    Store a testrun related link to DB
    """

    link = Link(testrun = Testrun.objects.get(id = testrun_id),
                url = url,
                description = description)
    link.save()
