# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: meego-qa@lists.meego.com
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
OTS 0.8 compatible publisher plugin for qa-reports tool
"""
from ots.common.framework.api import PublisherPluginBase
from ots.plugin.qareports.qareports_client import send_files

class QAReportsPlugin(PublisherPluginBase):
    """
    OTS 0.8 compatible publisher plugin for qa-reports tool
    """

    def __init__(self,
                 request_id,
                 testrun_uuid,
                 sw_product,
                 image,
                 qa_hwproduct=None,
                 qa_testtype=None,
                 qa_target=None,
                 qa_release_version = None,
                 qa_reporting_disabled = False,
                 **kwargs):
        """
        @type qa_hwproduct: C{str}
        @param qa_hwproduct: HW product used in the report

        @type qa_testtype: C{str}
        @param qa_testtype: Test Type used in the report

        @type qa_target: C{str}
        @param qa_target: Target used in the report
        
        @type qa_release_version: C{str}
        @param qa_release_version: Release_Version used in the report

        @type qa_reporting_disabled: C{str}
        @param qa_reporting_disabled: Disables report sending if True
        """
        self.result_xmls = []
        self.attachments = []
        self.hwproduct = qa_hwproduct
        self.testtype = qa_testtype
        self.target = qa_target
        self.release_version = qa_release_version
        self.disabled = qa_reporting_disabled
        
    def set_results(self, results):
        """
        @type results : C{list} of C{ots.common.dto.results}
        @param results : The Results
        """

        for result in results:
            if result.is_result_xml:
                self.result_xmls.append((result.name, result.content))
                continue
            self.attachments.append((result.name, result.content))

    def publish(self):
        """
        Send files to qa-reports
        """
        if not self.disabled:
            send_files(self.result_xmls,
                       self.attachments,
                       hwproduct=self.hwproduct,
                       testtype=self.testtype,
                       target=self.target,
                       release_version = self.release_version)
            
