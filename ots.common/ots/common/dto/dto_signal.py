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
The Signal for a DTO
"""

###################

#Django has forked PyDispatcher
#We will probably need the Django Signals 
#But to avoid making ots.server.distributor a 
#Django project use a MonkeyPatch for now

try:
    from django.conf import settings
    settings.DEBUG
except ImportError:
    import types
    class SettingsStub(object):
        """Stubs out django settings object"""
        DEBUG = False
    conf_stub = types.ModuleType("django.conf")
    conf_stub.settings = SettingsStub()
    sys.modules["django.conf"] = conf_stub
    LOGGER.debug("Monkey patching django.conf")

from django.dispatch.dispatcher import Signal

####################
# Signal
####################


DTO_SIGNAL = Signal()

