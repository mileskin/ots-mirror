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

"""Resultplugin that sends result files with the input plugin"""
from ots.common.interfaces.resultfilehandler import ResultFileHandler
import logging

class InputResultsPlugin(ResultFileHandler):
    """Resultplugin that sends result files with the input plugin"""
        
    def __init__(self, input_plugin):
        """
        @type input_plugin: L{InputPlugin}
        @param input_plugin: Input plugin to be used for storing files
        """

        self.log = logging.getLogger(__name__)
        self.result_objects = []
        self.input_plugin = input_plugin
        
    def name(self):
        """Returns name of the results plugin"""
        return "InputResultsPlugin"

    def save_results(self, testrun):
        """
        Stores result files with the input_plugin

        @type testrun: L{testrun}
        @param testrun: Testrun object the results are related to.


        """
        for result in self.result_objects:
            # add timestamp to filename
            timestamp = str(testrun.get_start_time())
            shor_timestamp = timestamp
            shor_timestamp = shor_timestamp.replace(" ", "_")
            shor_timestamp = shor_timestamp.replace(":", "")
            shor_timestamp = shor_timestamp.replace("-", "")
            # refine the shown time to seconds
            index = shor_timestamp.find('.')
            shor_timestamp = shor_timestamp[:index]

            # If environment is set, add it to filename
            if result.get_environment():
                environment_string = result.get_environment()+"-"
            else:
                environment_string = ""
            
            filename = shor_timestamp+"-"+environment_string+result.name()
            
            # refine the shown time to seconds but keep the format intact
            index1 = timestamp.find(".")
            timestamp = timestamp[:index1]
            label = "From testrun started at: "+timestamp
            self.input_plugin.store_file(result.get_content(),
                                         filename,
                                         filename,
                                         label)
    
    
    def add_result_object(self, result_object):
        """
        Stores a result object

        @type result_object: L{ResultObject}
        @param result_object: Results object containing the results

        """
        self.result_objects.append(result_object) 
    
