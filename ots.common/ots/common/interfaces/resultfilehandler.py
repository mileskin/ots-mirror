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


"""Abstract base class for ots result file handlers"""
#from ots.common.resultobject import ResultObject
#from ots.common.testrun import Testrun

class ResultFileHandler(object):
    """
    Abstract base class for ots result file handlers.

    """
        
    def name(self):
        """ This method returns the name of the plugin as a string

            @rtype: C{string}
            @return: Name of the plugin
        """
        raise NotImplementedError

    def save_results(self, testrun_object):
        """ This method is called in the end of the testrun. It should save all
            the results.

            @type testrun_object: L{testrun}
            @param testrun_object: The testrun to be executed

            @rtype: C{List}
            @return: A list of error messages

        """
        raise NotImplementedError    

    def add_result_object(self, result_object):
        """ This method stores a ResultObject. It is called every time a result
            object is stored into the testrun.

            @type result_object: L{ResultObject}
            @param result_object: The ResultObject to be stored

            @rtype: C{None}
            @return: Nothing

        """
        raise NotImplementedError
