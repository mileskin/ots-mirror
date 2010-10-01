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


"""Email Backend"""

import smtplib
import logging
from ots.common.results.result_backend import ResultBackend

from ots.server.email_backend import mailmessage


class EmailBackend(ResultBackend):
    """
    This backend sends test results by mail. 
    Mailer argument can be used to specify a special mailer (typically a mailer 
    stub for testing).
    If mailer == "LOG_ONLY", mail is not sent but it is written to log instead.
    """

    def __init__(self, testrun, link_urls, email_settings, 
                 mailer = "DEFAULT"):

        if mailer == "DEFAULT": 
            mailer = DefaultMailer(email_settings['smtpServer'])
        if mailer == "LOG_ONLY": 
            mailer = LogMailer()

        self.testrun = testrun
        self.log = logging.getLogger(__name__)
        self.build_url = link_urls['buildURL']
        self.from_address = email_settings['fromAddress']
        self.mailer = mailer
        self.result_files = []
        self.message_body = email_settings['message_body']
        self.message_subject = email_settings['message_subject']

    def name(self):
        """Returns the name of the backend plugin"""
        return "EmailBackend"

    def saveRawFiles(self, files):
        """Does nothing. Mandatory interface method."""
        pass

    def save(self, suites=None, summary=None):
        """Does nothing. Mandatory interface method."""
        pass

    def finished_processing(self):
        """
        This method makes the plugin compatible with the new backend 
        plugin interface. It is called after all files have been processed.
        """
        self.save()

    def process_raw_file(self, result_object, testrun_object):
        """Store file to be later attached to e-mail."""
        self.result_files.append(result_object)

    def send_mail(self): #TODO Redesign needed. Design publishing backend?
        """Sends test results by email"""

        to_address_list = self.testrun.get_email_list()

        #check parameters
        if not to_address_list or not self.testrun.get_request_id():
            return
        if not (type(to_address_list) == type(list()) \
                or type(to_address_list) == type("")):
            self.log.error("Error in sending mail: expected list or string in "\
                           "to_address_list: %s " % str(to_address_list))
            return

        self.log.info("Sending email about testrun results")

        message = mailmessage.create(self.testrun, 
                                     self.from_address, 
                                     to_address_list, 
                                     self.build_url, 
                                     self.result_files,
                                     self.message_body,
                                     self.message_subject)

        self.mailer.new()
        failed_addresses = dict()
        try:
            failed_addresses = self.mailer.sendmail(self.from_address, 
                                              to_address_list, 
                                              message)
        finally:
            self.mailer.quit()
        
        self._log_failed_addresses(failed_addresses)


    def _log_failed_addresses(self, failed_addresses):
        """Write given list of failed addresses to log if list is non empty."""
        if failed_addresses:
            self.log.error("Error in sending mail to following addresses:")
            self.log.error(str(failed_addresses)) 
            #key=address,entry=(errCode, errMsg)


class DefaultMailer():
    """Wrapper for smtplib commands to send mail"""

    def __init__(self, smtp_server):
        self._smtp_server = smtp_server
        self._conn = None
    def get_smtp_server(self):
        """Return smtp server"""
        return self._smtp_server
    def new(self):
        """Connect to smtp server"""
        self._conn = smtplib.SMTP(self._smtp_server)
    def sendmail(self, from_address, to_address_list, message):
        """
        Sends e-mail. 
        Returns None or dictionary of addresses to which sending failed.
        """
        return self._conn.sendmail(from_address, to_address_list, message)
    def quit(self):
        """Disconnect from smtp server"""
        self._conn.quit()


class LogMailer():
    """Write mail to log instead of sending mail"""

    def __init__(self):
        self._log = logging.getLogger(__name__)
    def new(self):
        """Do nothing"""
        pass
    def sendmail(self, from_address, to_address_list, message):
        """Write mail to log instead of sending mail"""
        self._log.debug("Mail to be sent:")
        self._log.debug(message)
        return None
    def quit(self):
        """Do nothing"""
        pass
