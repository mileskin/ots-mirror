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

from setuptools import setup, find_packages

setup(
      name = "ots.server",
      author = "ext-teemu.a.vainio@nokia.com",
      version =  "0.1.1",
      include_package_data = True,
      namespace_packages = ['ots', "ots.server"],
      packages = find_packages(),
#      packages = ['ots.server.distributor',
#                  'ots.server.email_backend',
#                  'ots.server.input',
#                  'ots.server.logger',
#                  'ots.server.testrun_host',
#                  'ots.server.xmlrpc',
#                  'ots.server.conductorengine'],
      entry_points={"console_scripts":
                    ["ots_server = ots.server.xmlrpc.server:main",]
                    },
      zip_safe = False,
      data_files=[('/etc', ['ots-server.ini'])]
      )
