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


class OTSException(Exception):
    """
    OTS Exception has error code

    Also need to support Picklable behaviour
    see: http://bugs.python.org/issue1692335
    """
    def __init__(self, message, error_code):
        Exception.__init__(self, message)
        self.error_code = error_code
        self.message = message

    def __getstate__(self):
        return self.message, self.error_code

    def __reduce__(self):
        return (self.__class__, self.__getstate__())
