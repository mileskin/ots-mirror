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
      name="ots.plugin.logger",
      author="teemu.vainio@ixonos.com",
      namespace_packages=["ots", "ots.plugin", "ots.plugin.logger"],
      version=get_spec_version(),
      include_package_data=True,
      packages=find_packages(),
      install_requires=['ots.server'],
      entry_points={"ots.publisher_plugin":
                    ["publisher_klass = "\
                     "ots.plugin.logger.logger_plugin:LoggerPlugin"]},
      
      data_files=[('/usr/share/ots/plugin/logger', ['ots/plugin/logger/django_logger/templates/ots.wsgi']),
                  ('/usr/share/ots/plugin/logger/media', ['ots/plugin/logger/django_logger/templates/media/logo.png']),
                  ('/usr/share/ots/plugin/logger/styles', ['ots/plugin/logger/django_logger/templates/styles/custom.css']),
                  ('/usr/share/ots/plugin/logger/logger', ['ots/plugin/logger/django_logger/templates/logger/index.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/workers_view.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/filter_message_view.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/basic_testrun_view.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/advanced_message_view.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/logger_base.html',
                                                           'ots/plugin/logger/django_logger/templates/logger/message_details_view.html',]),
                 ]
      )
