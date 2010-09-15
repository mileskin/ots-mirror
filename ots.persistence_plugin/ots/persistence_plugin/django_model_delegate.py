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
Acts as a facade onto Django Models
Based on 0.1 ndb_plugin.py
"""

#FIXME: The Django Models already provide an abstraction layer
#perhaps this should be removed as a refactoring step?

import logging

import datetime

####################################
# HELPERS
####################################

def _get_gate(gate):
    return models.NdbGateInfo.objects.get_or_create(name=gate)[0]

def _get_testplan(testplan_id):
    testplan = None
    if testplan_id:
        try:
            testplan = models.NdbTestplan.objects.get(id = testplan_id)
        except models.NdbTestplan.DoesNotExist:
            #No logger available at this point
            pass
    elif gate is not None:
        testplan = create_testplan(name = testplan_name,
                                   gate = _get_gate(gate))
    return testplan


def _get_label(label):
    if label is not None:
        label = models.NdbLabel.objects.get_or_create(name = label)[0]
    return label


def _get_sw_product(sw_product):
    return models.NdbSwproduct.objects.get(name = swproduct)


def _get_testrun(request_id, testrun_id, image, image_name, sw_version):
    """
    @param testrun_id: Testrun id in the DB.
    @type testplan_id: C{int}
    """
    testrun = models.NdbTestrun(testplan = testplan,
                                swproduct = sw_product,
                                label = label)
    testrun = models.NdbTestrun.objects.get(id = testrun_id)
    testrun.request = request_id
    testrun.imagename = image_name
    testrun.imageurl = image
    testrun.sw = sw_version
    #TODO: Does cmt need checking here?
    testrun.starttime = datetime.datetime.now()
    testrun.save()
    return testrun

def _update_target_packages(request, target_packages):
    """
    Updates target packages for a build request.

    @param request: NdbRequest model object
    @type request: L{NdbRequest}

    @param pkg_list: List of target package names
    @type pkg_list: C{list} consisting of C{string}
    """
    for pkg in pkg_list:
        package = models.NdbTargetPackage.objects.\
            get_or_create(name=pkg)[0]

        # Adding package only if it doesn't exist
        if not request.built_packages.filter(id=package.id).count():
            # if clause may not be enough if parallel processes are trying
            # to store packages simultaneously
            try:
                request.built_packages.add(package)
            except IntegrityError:
                pass

###################################
# PUBLIC
###################################

def init_testrun(request_id, testrun_id, testplan_id,
                 label, image, image_name, sw_version,
                 target_packages):
    testplan = get_testplan(testplan_id
    label = _get_label(label)
    if testplan is not None:
        sw_product = _get_sw_product(sw_product)
        testrun = _get_testrun(request_id, testrun_id,
                                   image, image_name, sw_version)
        _update_target_packages(testrun.request, target_packages)
        return testrun.id

def set_testrun_result(testrun_id, result):
    testrun = models.NdbTestrun.objects.get(id=testrun_id)
    testrun.endtime = datetime.datetime.now()
    testrun.result = result

def set_testrun_error(testrun_id,error_code, error_info):
    testrun.error_code = testrun_object.get_error_code()
    testrun.error_info = testrun_object.get_error_info()
