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

import os

class PluginException(Exception):
    pass

class PluginBase(object):

    DEFAULT_CONFIG_FILEPATH = "/etc/"
    application_id = None

    def _config_filename(self):
        """
        @rtype: C{str}
        @rparam the config file path.

        Tries /etc/APPLICATION_NAME.ini first.
        If that does not work,
        tries config.ini from ots.common directory
        """
        if self.application_id is not None:
            name = "%s.ini" % (self.application_id)
        else:
            name = "config.ini"
        default = os.path.join(self.DEFAULT_CONFIG_FILEPATH, name)
        if os.path.exists(default):
            config_filename = default
        else:
            common_dirname = os.path.split(os.path.dirname(
                               os.path.abspath(__file__)))[0]
            config_filename = os.path.join(common_dirname, name)
            if not os.path.exists(config_filename):
                raise PluginException("%s not found"%(config_filename))
        return config_filename
