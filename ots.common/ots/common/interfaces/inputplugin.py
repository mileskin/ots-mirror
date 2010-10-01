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

"""Abstract base class for input plugin."""


class InputPlugin(object):
    """Abstract base class for input plugin."""

    
    def store_url(self, url, text):
        """ 
        Method for storing result urls

        @type url: C{string}
        @param url: Url string

        @type text: C{string}
        @param text: Description text for the url

        """  
        raise NotImplementedError

    def get_changed_packages(self, build_id):
        """ 
        Method for storing result urls

        @type build_id: C{int}
        @param build_id: Build request number

        @type text: C{string}
        @param text: Description text for the url

        @rtype: C{list} consisting of C{string}
        @return: List of changed packages
 
        """  
        raise NotImplementedError



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
        raise NotImplementedError
        
