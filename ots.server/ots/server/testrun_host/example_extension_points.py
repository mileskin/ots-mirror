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
Extension point example for adding additional plugins to OTS server
"""

import uuid


def get_inputplugin(testrun):
    """Returns custom input plugin"""
    return None

def get_postprocessplugins(testrun):
    """Returns custom PostProcessPlugins as a list"""
    return []

def get_resultfilehandlers(testrun):
    """Returns custom ResultFileHandlers as a list"""
    return []

def get_resultbackends(testrun):
    """Returns custom ResultBackends as a list"""
    return []

#
# DB related functions
#

def init_new_testrun(swproduct, testplan_id=None, testplan_name="",
                    gate=None, label=None):
    """
    Creates a new testrun into DB and returns an unique testrun ID. Default
    implementation only generates an unique testrun id.
    
    @param swproduct: Name of the sw product this testrun belongs to
    @type swproduct: C{string}

    @return: Testrun id
    @rtype: C{int}
    """
    return uuid.uuid1().int


def update_testrun_in_db(testrun, testrun_id):
    """
    This is called when testrun data in db needs updating
    """
    pass

def get_testrun_link(testrun_id):
    """
    This returns a link to testrun results
    """
    return "n/a"
