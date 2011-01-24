# ***** BEGIN LICENCE BLOCK *****
# This file is part of OTS
#
# Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#
# Contact: Ville Ilvonen <ville.p.ilvonen@nokia.com>
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
from get_spec_version import get_spec_version

setup(
      name="ots.logger_plugin",
      author="teemu.vainio@ixonos.com",
      namespace_packages=["ots", "ots.logger_plugin"],
      version=get_spec_version(),
      include_package_data=True,
      packages=find_packages(),
      install_requires=['ots.server'],
      entry_points={"ots.publisher_plugin":
                    ["publisher_klass = "\
                     "ots.logger_plugin.logger_plugin:LoggerPlugin"]},
      )
