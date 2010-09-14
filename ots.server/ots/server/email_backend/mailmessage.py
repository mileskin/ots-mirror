# -*- coding: utf-8 -*-
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


"""OTS email. Result xml files attached as zip file."""

import os
import time
import logging
from zipfile import ZipFile
from zipfile import ZipInfo
from zipfile import ZIP_DEFLATED
from tempfile import gettempdir
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

LOG = logging.getLogger(__name__)

DEFAULT_MESSAGE_BODY = \
"SW Product     : %s\n"\
"Build ID: %s\n"\
"OTS testrun ID: %s\n"\
"\n"\
"Test packages:\n"\
"%s"\
"\n"\
"Test result: %s\n"\
"\n"\
"Test result details:\n"\
"\n"\
"%s\n"\
"\n"\
"Build request:\n"\
"%s\n"

DEFAULT_MESSAGE_SUBJECT = "[OTS] [%s] Req#%s: %s"


#NOTE: We could use django template instead!
def create(testrun,
           from_address,
           to_address_list,
           build_url,
           result_files,
           message_template = None,
           subject_template = None):
    """
    Creates MIME Multipart message. 
    If there are any result_files, files are attached to email as one zip file.
    Returns email message as a string ready to be sent for example with smtplib.
    """
    return _create(testrun, from_address, to_address_list, build_url, 
                   result_files, message_template, subject_template).as_string()


def _create(testrun, from_address, to_address_list, build_url,
            result_files, message_template = None, subject_template = None):
    """
    Creates MIME Multipart message. 
    If there are any result_files, files are attached to email as one zip file.
    Returns email message as an object instantiated from MIMEMultipart class.
    This is easier to test.
    """

    if not message_template:
        message_template = DEFAULT_MESSAGE_BODY
    if not subject_template:
        subject_template = DEFAULT_MESSAGE_SUBJECT

    def long_result_string():
        """Test result string for mail message body"""
        if testrun.get_result() == "ERROR":
            return "%s (%s)" % (testrun.get_result(), 
                                testrun.get_error_info())

        return testrun.get_result()

    def results_link():
        """Test result links for mail message body"""
        links = ""
        for text, url in testrun.get_result_links():
            links = links + text+": "+url+"\n"
        return links

    def test_packages_string():
        """Test packages string for mail message body"""
        packages = testrun.get_all_executed_packages()
        if not packages.items():
            return "(none)\n"
        packages_str = ""
        for (environment, pkg_list) in packages.items():
            pkgs = " ".join([pkg for pkg in pkg_list])
            packages_str += "  " + environment + ": " + pkgs + "\n"

        return packages_str


    #create strings
    build_link = build_url % testrun.get_request_id()
    subject = subject_template % (testrun.get_sw_product(), 
                                  testrun.get_request_id(), 
                                  testrun.get_result())
    body = message_template % (testrun.get_sw_product(), 
                               testrun.get_request_id(), 
                               testrun.get_testrun_id(),
                               test_packages_string(), 
                               long_result_string(), 
                               results_link(), 
                               build_link)

    #Create multipart message
    msg = MIMEMultipart()

    bodypart = MIMEText(body)

    msg.attach(bodypart)

    if result_files and testrun.options['email-attachments'] == True:
        unique_id = testrun.get_testrun_id()
        try:
            attach_as_zip_file(msg, result_files, unique_id)
        except:
            LOG.error("Something went wrong when creating email attachment. "\
                      "Traceback follows:", exc_info = True)

    #add message headers
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(to_address_list)

    return msg


def attach_as_zip_file(msg, result_files, unique_id):
    """
    Create a zip file containing result_files and attach it to msg.
    msg must be MIMEMultipart object.
    """

    #create temp file for ZipFile.
    zipname = 'OTS_testrun_%s.zip' % unique_id
    tmp_file = os.path.join(gettempdir(), "tmp_file_%s" % zipname)

    zipped = ZipFile(tmp_file, 'w')

    LOG.debug("Created temporary file: %s" % tmp_file)

    #add results files to zip file
    for resultfile in result_files:
        filename = "%s-%s" % (resultfile.environment, resultfile.filename)
        info = ZipInfo(filename)
        info.date_time = time.localtime(time.time())[:6] #now
        info.external_attr = 0666 << 16L # read-write access to everyone
        info.compress_type = ZIP_DEFLATED
        zipped.writestr(info, resultfile.content)

    #calling close is required to finalize zip file. Closes tmp_file.
    #This is why we cannot use usual tempfiles - they are removed automatically 
    #when closed.
    zipped.close()

    zipped_content = open(tmp_file).read()

    ctype = 'application/zip'
    maintype, subtype = ctype.split('/', 1)
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(zipped_content)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', 
                          filename = zipname )

    #attach to message
    msg.attach(attachment)

    LOG.debug("Attached file %s containing %s files" \
              % (zipname, len(result_files)))

    #delete temp file
    os.unlink(tmp_file)
    LOG.debug("Deleted temporary file: %s" % tmp_file)

