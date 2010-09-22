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

"""Default config file for the OTS system"""
from socket import gethostname
##################
# General config #
##################

#
# Disables input plugin calls (adding links and storing files) and emails
#
debug_mode = False 


#
# Link URLs
#
link_urls = dict()
link_urls['buildURL'] = "http://localhost/build/%s/"
link_urls['resultURL1'] = "http://"+gethostname()+"%s"
link_urls['logURL'] =  "http://"+gethostname()+"/logger/view/ots/%s/"
link_urls['resultURL2'] = "https://anotherresultserver%s"

link_text = dict()
link_text['resultURL1'] = "Testrun %s (%s) results in primary server"
link_text['resultURL2'] = "Testrun %s results in secondary server"

#
# Email settings
#
email_settings = dict()
email_settings['fromAddress'] = "ots@localhost"
email_settings['smtpServer'] = "your_mail_server_here"

email_settings['message_body'] = \
"SW Product     : %s\n"\
"BUILD Request ID: %s\n"\
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

email_settings['message_subject'] = "[OTS] [%s] Req#%s: %s"



#
# Config for result handling
#
results_storage_config = dict()
# (In current setup the service runs on same machine)

results_storage_config['host'] = gethostname()
results_storage_config['port'] = 1982

# String in filename that identifies a result file to be testrunner 
# output xml: 
xml_file_name_pattern = "tatam_xml_testrunner"

# Whether the result of "insignificant" test cases can affect testrun result
insignificant_tests_matter = False

###########################
# Testrun default options #
###########################
default_options = dict()

#
# Global defaults for all sw configurations
#
global_defaults = dict()
global_defaults['device'] = {'devicegroup':'default'}
global_defaults['emmc'] = ""
global_defaults['timeout'] = 30
global_defaults['hosttest'] = []
global_defaults['engine'] = ["ots"]
global_defaults['input_plugin'] = "default"
global_defaults['distribution_model'] = "default"
global_defaults['email-attachments'] = False

#
# Defaults for example_sw_product
#
default_options["example_sw_product"] = global_defaults.copy()
default_options["example_sw_product"]['input_plugin'] = "default"
default_options["example_sw_product"]['device'] = {'devicegroup':'examplegroup'}
