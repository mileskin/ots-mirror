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
Convert recognised string patterns
to Python types
""" 

import re

def string_2_list(string):
    """
    Converts a spaced string to an array
    
    @param string: The string for conversion
    @type string: C{str}
    
    @rtype: C{list} consisting of C{str}
    @return: The converted string
    """
    
    if type(string) is list:
        return string
    
    if string:
        spaces = re.compile(r'\s+')
        return spaces.split(string.strip())
    else:
        return []

def string_2_dict(string):
    """
    Converts a spaced string of form 'foo:1 bar:2 baz:3'
    to a dictionary
    
    @param string: The string for conversion
    @type string: C{str}
    
    @rtype: C{dict} consisting of C{str}
    @return: The converted string
    """
    spaces = re.compile(r'\s+')
    return dict([ pair.split(':', 1) for pair \
                      in spaces.split(string) if ':' in pair ])
