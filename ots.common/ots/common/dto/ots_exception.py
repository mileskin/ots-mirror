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
The Base Class for Exceptions.

- Allows for transfer across the wire 
- Has an errno
"""

class OTSException(Exception):
    """
    OTS Exception 

    Also need to support Picklable behaviour
    """
    errno = ''
    strerror = ''

    def __init__(self, *args):
        """
        Mimics API of Python's Environment Error i.e.:
        
        When exceptions of this type are created with a 2-tuple,
        the first item is available on the instances errno attribute
        (it is assumed to be an error number),
        and the second item is available on the strerror attribute
        """
        Exception.__init__(self, *args)
        if len(args) == 2:
            self.errno = args[0]
            self.strerror = args[1]

    def __setstate__(self, state):
        self.errno, self.strerror = state

    def __getstate__(self):
        return self.errno, self.strerror 

    def __reduce__(self):
        """
        Need to help pickle along
        see: http://bugs.python.org/issue1692335
        """
        return (self.__class__, self.__getstate__())

    def __str__(self):
        return "Error: %s, Error code: %s " % (self.strerror, self.errno)
