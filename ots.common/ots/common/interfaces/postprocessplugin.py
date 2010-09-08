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
Abstract Base class (or interface) for ots testrun post processing plugins.

Post process plugins are executed after the test execution has finished but 
before result handling.
"""
           

class PostProcessPlugin(object):
    """Base class (or interface) for ots testrun post processing plugins"""

    def name(self):
        """ This method returns the name of the plugin as a string
                    
            @rtype: C{string}
            @return: Name of the plugin
        """ 
        raise NotImplementedError


        
    def process(self, testrun_object):
        """ Process the testrun with this plugin
    
            @type testrun_object: L{Testrun}
            @param testrun_object: The testrun to be executed
                    
            @rtype: C{None}
            @return: Nothing

        """ 
        raise NotImplementedError
