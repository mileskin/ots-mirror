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

import socket
import base64

from ots.common.framework.plugin_base import PluginBase


LOG = logging.getLogger("__name__")

dummy_config = {'peer_ca_cert' : "foo",
                 'key_and_cert' : "bar",
                 'ca_cert': "baz",
                 'xml_rpc_url' : "www.nokia.com"}

class BifhPlugin(PluginBase):

    def __init__(self, application_id, request_id):
        PluginBase.__init__(self, application_id)
        self.request_id = request_id

    def _create_proxy(self):
        #FIXME
        pass


    def store_url(self, url, text):
        """
        Method for storing result urls

        @type url: C{string}
        @param url: Url string

        @type text: C{string}
        @param text: Description text for the url
        """
        proxy =  self._create_proxy()
        try:
            for old_url in proxy.bifh.users.request.get_urls(self.request_id):
                if old_url["url"] == url:
                    self.log.debug("url %s is already in bifh." % url)
                    return
            proxy.bifh.users.request.add_url(self.request_id, text, url)
        except socket.timeout:
            self.log.exception("Bifh XMLRPC call timed out")
        LOG.debug("added url %s to bifh request page" % url)

    def get_target_packages(self, build_id):
        """
        Method for storing result urls

        @type build_id: C{int}
        @param build_id: Build request number

        @type text: C{string}
        @param text: Description text for the url

        @rtype: C{list} consisting of C{string}
        @return: List of changed packages

        """
        try:
            packages = []
            server = self._create_proxy()
            if server is not None:
                results = server.bifh.users.request.results(self.request_id)
                for package in results['packages']:
                    if not packages.count(package['binary_name']):
                        packages.append(package['binary_name'])
        except socket.timeout:
            self.log.exception("Bifh XMLRPC call timed out")
        return packages

    def store_file(self,
                   file_content,
                   filename,
                   label,
                   description):
        """
        Method for storing result files

        @type file_content: C{string}
        @param file_content: File content as a string

        @type filename: C{string}
        @param filename: File name

        @type label: C{string}
        @param label: Label of the file

        @type description: C{string}
        @param description: Description of the file

        """
        LOG.debug("adding file %s to BIFH request page" % filename)
        proxy =  self._create_proxy()
        b64content = base64.b64encode(file_content)
        try:
            proxy.bifh.users.request.add_attachment(self.request_id,
                                                    label,
                                                    filename,
                                                    description,
                                                    b64content)
        except socket.timeout:
            LOG.exception("Bifh XMLRPC call timed out")
        LOG.debug("added file %s" % filename)

