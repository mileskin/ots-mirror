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
The EmailPlugin
"""

#WIP

import logging
import datetime

from ots.common.framework.api import PluginBase
from ots.results.api import TestrunResult


LOG = logging.getLogger(__name__)

from ots.email_plugin.mail_message import MailMessage 

############################
# Configuration 
############################

#FIXME

def get_from_address():
    pass

def get_message_body():
    pass

def get_message_subject():
    pass

def get_link_text():
    pass

def get_link_urls():
    pass

##############################
# EmailPlugin
##############################

class EmailPlugin(PluginBase):

    def __init__(self, request_id, sw_product, image, expected_packages):
        self.request_id = request_id
        self.sw_product = sw_product 
        self.target_packages = target_packages
        self.mail_message = MailMessage(get_from_address(),
                                        get_message_body(),
                                        get_message_subject())
        
        #Hmmm tricky to abstract
        #FIXME
        self.email_attachments = None

    ###################################
    # FIXME
    ###################################

    def set_source_uris(self, uris):
        """
        @type: C{list} of C{str}
        @param: Uris of other reporting tools 
        """
        self._source_uris = source_uris
        
    def set_target_uris(self, uris):
        """
        @type: C{list} of C{str}
        @param: Uris of other reporting tools 
        """
        self._target_uris = uri
        
    #####################################
    # Setters
    #####################################
       
    def set_testrun_result(self, testrun_result):
        """
        @type: C{ots.common.testrun_result}
        @param: The testrun result
        """
        self._testrun_result = testrun_result

    def set_result_xmls(self, result_xmls):
        """
        @type: C{list} of C{file type objects}
        @param: The result xmls
        """
        self._result_xmls = result_xmls

    def set_exception(self, exception):
        """
        @type: C{Exception}
        @param: The Exception
        """
        self._exception = exception

    def set_tested_packages(self, tested_packages):
        """
        @type: C{tested_packages}
        @param: The TestedPackages
        """
        self._tested_packages = tested_packages

    def publish():
        """
        Sends the email
        """
        to_address_list = self.email_list()
        if not to_address_list:
            raise EmailPublisherException("No address list")

        message = self.mail_message.message(self.result, 
                                  self._results_xmls, 
                                  self._exception, 
                                  self._tested_packages, 
                                  self._sw_product, 
                                  self._request_id, 
                                  self._testrun_uuid, 
                                  self._source_uris,
                                  self._target_uris, 
                                  self._email_attachments):
        
        failed_addresses = mailer.sendmail(from_address, 
                                           to_address_list, 
                                           message)
        LOG.error("Error in sending mail to following addresses:")
        LOG.error(str(failed_addresses))    
