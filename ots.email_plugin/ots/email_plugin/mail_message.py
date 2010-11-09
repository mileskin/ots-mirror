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

import logging

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from ots.results.api import result_2_string

from ots.email_plugin.templates import DEFAULT_MESSAGE_BODY
from ots.email_plugin.templates import DEFAULT_MESSAGE_SUBJECT
from ots.email_plugin.attachment import attachment

LOG = logging.getLogger(__name__)

#########################
# FORMATTING HELPERS
#########################
    
def format_result(result, exception):
    """
    Test result string for mail message body

    @type result: C{ots.results.testrun_result}
    @param result: The testrun result

    @type exception: C{ots.common.dto.OTSException} or None
    @param exception: The exception raised

    @rtype: C{str}
    @rparam: The formatted result 
    """
    result = result_2_string(result)
    if exception is not None:
        return "%s (%s)" % (result, exception.strerror)
    #FIXME: verbose code
    return result

def format_source_uris(source_uris_dict):
    """ 
    @type links: C{list} of C{tuple} of C{str},C{str}
    @param links: The links to the results

    @rtype: C{str}
    @rparam: The formatted result 
    """
    return "\n".join(["%s: %s"%(text, url) 
                      for text,url in source_uris_dict.items()])


def format_packages(packages):
    """
    @type expected_packages: C{ots.common.dto.packages}
    @param expected_packages: The packages that should be 
                              executed in the run
    """
   
    if not packages:
        return "(none)\n"
    packages_str = ""
    for (env, pkg_list) in packages.items():
        pkgs = " ".join([pkg for pkg in pkg_list])
        packages_str += "  " + env.environment + ": " + pkgs + "\n"
    return packages_str
    

################################
# MailMessage
################################


class MailMessage(object):
    """
    Builds a Mime Message from the Templates
    """

    def __init__(self, from_address,
                       message_template = None, 
                       subject_template = None):
        self.from_address = from_address
        self.message_template = message_template
        if not self.message_template:
            self.message_template = DEFAULT_MESSAGE_BODY
        self.subject_template = subject_template
        if not self.subject_template:
            self.subject_template = DEFAULT_MESSAGE_SUBJECT

    #################################
    # HELPERS
    #################################

    def _body(self, request_id, testrun_uuid, sw_product,
                    result, exception, tested_packages,  
                    source_uris, build_url):
        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param The unique identifier for the testrun

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type: C{ots.common.testrun_result}
        @param: The testrun result
        
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The Results
        
        @type: C{Exception}
        @param: The Exception
        
        @type tested_packages : C{ots.common.dto.packages}
        @param tested_packages: The Test Packages that were run

        @type source_uris : C{dict} of C{str} : C{str}
        @param source_uris : Uris of other reporting tools 

        @type build_url : C{str}
        @param build_url : The build url
                
        @rtype : C{str}
        @rparam : The Body of the email message
        """
        build_link = build_url % request_id
        return self.message_template % (sw_product, 
                                        request_id, 
                                        testrun_uuid,
                                        format_packages(tested_packages), 
                                        format_result(result, exception), 
                                        format_source_uris(source_uris), 
                                        build_link)

    def _subject(self, request_id, sw_product, result):
        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type: C{ots.common.testrun_result}
        @param: The testrun result

        @rtype : C{str}
        @rtype : The subject
        """
        return self.subject_template % (sw_product, 
                                        request_id, 
                                        result)

    ######################################
    # PUBLIC
    ######################################
      
    def message(self, request_id, testrun_uuid, sw_product,
                      result, result_files, exception, 
                      tested_packages,  
                      source_uris,
                      notify_list, email_attachments,
                      build_url):

        """
        @type request_id: C{str}
        @param request_id: An identifier for the request from the client

        @type testrun_uuid: C{str}
        @param The unique identifier for the testrun

        @type sw_product: C{str}
        @param sw_product: Name of the sw product this testrun belongs to

        @type: C{ots.common.testrun_result}
        @param: The testrun result
        
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The Results
        
        @type: C{Exception}
        @param: The Exception
        
        @type tested_packages : C{ots.common.dto.packages}
        @param tested_packages: The Test Packages that were run

        @type source_uris : C{dict} of C{str} : C{str}
        @param source_uris : Uris of other reporting tools 

        @type notify_list : C{list}
        @param notify_list : The email notify list 
  
        @type email_attachments : C{bool}
        @param email_attachments : Is the email attachment switched on?
        
        @type build_url : C{str}
        @param build_url : The build url
                
        @rtype : C{MIMEMultipart}
        @rparam : Mail message
        """
        msg = MIMEMultipart()
        msg["Subject"] = self._subject(request_id, sw_product, result)
        msg["From"] = self.from_address
        msg["To"] = ", ".join(notify_list)
        msg.attach(MIMEText(self._body(request_id, sw_product, testrun_uuid,
                                       result, exception, tested_packages, 
                                       source_uris, build_url)))
        if result_files and email_attachments:
            try:
                attachment = attachment(result_files, testrun_uuid)
                msg.attach(attachment)
            except:
                LOG.error("Error creating email attachement:",
                      exc_info = True)
        return msg
