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
      name = "ots.tools",
      description="Various helper tools for OTS",
      author = "teemu.vainio@ixonos.com",
      version = "0.1.2",
      include_package_data = True,
      namespace_packages = ['ots'],
      packages = find_packages(),
      zip_safe = False,

      entry_points={
        "console_scripts":
            ["ots_trigger = ots.tools.trigger.ots_trigger:main",
             "ots_empty_queue = ots.tools.queue_management.empty_queue:main",
             "ots_delete_queue = ots.tools.queue_management.delete_queue:main",
             ],},
      )
