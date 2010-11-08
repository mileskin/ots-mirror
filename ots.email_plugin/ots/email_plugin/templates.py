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
Default Templates
"""

DEFAULT_MESSAGE_BODY = \
"SW Product     : %s\n"\
"Build ID: %s\n"\
"OTS testrun ID: %s\n"\
"\n"\
"Test packages:\n"\
"%s"\
"\n"\
"Test result: %s\n"\
"\n"\
"Test result details:\n"\
"\n"\
"%s\n"\
"\n"\
"Build request:\n"\
"%s\n"

DEFAULT_MESSAGE_SUBJECT = "[OTS] [%s] Req#%s: %s"

