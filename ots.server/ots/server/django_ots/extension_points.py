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
Extension point example for Django OTS server
"""

from ots.server.testrun_db import interface



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

def create_testrun_id(swproduct, request, options):
    """
    Creates a new testrun into DB and returns an unique testrun ID.
    
    @param swproduct: Name of the sw product this testrun belongs to
    @type swproduct: C{string}

    @param request: Build request ID
    @type request: C{string}

    @param swproduct: Testrun options
    @type swproduct: C{dict}

    @return: Testrun id
    @rtype: C{int}
    """
    return interface.init_new_testrun(swproduct)


def update_testrun_in_db(testrun, testrun_id):
    """
    This is called when testrun data in db needs updating
    """
    return interface.update_testrun(testrun, testrun_id)

def get_testrun_link(testrun_id):
    """
    This returns a link to testrun results
    """
    return interface.get_testrun_link(testrun_id)


def get_custom_distribution_models(testrun):
    """
    @rtype: c{list} of c{tuples}
    @return: List of custom distribution models. Each model should be tuple
    consisting of (distribution_model_name, a callable)
    """
    return []
