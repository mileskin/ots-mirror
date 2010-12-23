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

import configobj
import os
DEFAULT_CONFIG_FILE = "/etc/ots_qareports_plugin.conf"

def send_files(result_xmls, attachments):
    """
    Sends files to reporting tool

    @type result_xmls: C{list} of C{tuple}s consisting of 2 C{string}s
    @param result_xmls: Result xmls in format ("filename", "file content")

    @type attachments: C{list} of C{tuple}s consisting of 2 C{string}s
    @param attachments: Attachment files in format ("filename", "file content")
    """
    config = configobj.ConfigObj(_config_filename()).get("ots.qareports_plugin")

    host = config["host"]
    selector = config["url"]
    fields = [("auth_token", config("auth_token")),
              ("release_version", config("release_version")),
              ("target", config("target")),
              ("testtype", config("testtype")),
              ("hwproduct", config("hwproduct"))]


    files = [("report.1","tatam_xml_testrunner_results_for_test-definition-tests.xml", report1), ("attachment.1", "tests.xml", attachment1)]
    
    response = post_multipart(host, selector, fields, files)
    print response

def _generate_form_data(result_xmls, attachments = []):
    """
    Generates a form_data list from input files
    """
    if not result_xmls:
        raise ValueError("No Result xmls.")
    files =[]
    index = 0
    for result in result_xmls:
        index += 1
        files.append(("report.%s" % index, result[0], result[1]))
    index = 0
    for attachment in attachments:
        index += 1
        files.append(("attachment.%s" % index, attachment[0], attachment[1]))
    return files
#    files = [("report.1,tion-tests.xml", report1), ("attachment.1", "tests.xml", attachment1)]


def _config_filename():
    """
    Returns the config file path.

    Tries /etc/ots_qareports_plugin.conf first. If that does not work, tries
    from ots.qareports_plugin directory
    """
    if os.path.exists(DEFAULT_CONFIG_FILE):
        return DEFAULT_CONFIG_FILE

    distributor_dirname = os.path.dirname(os.path.abspath(__file__))
    distributor_config_filename = os.path.join(distributor_dirname,
                                               "ots_qareports_plugin.conf")
    if not os.path.exists(distributor_config_filename):
        raise Exception("%s not found"%(distributor_config_filename))
    return distributor_config_filename

