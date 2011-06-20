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


#!/usr/bin/env python
"""A command line tool for triggering a test run via OTS XML-RPC interface"""

from optparse import OptionParser
import logging
import xmlrpclib
import sys
import os


def read_test_plan(filepath):
    """
    Reads given test plan and returns the file data.
    """
    testplan_data = None
    if os.path.exists(filepath):
        testplan_fb = open(filepath, 'r')
        testplan_data = testplan_fb.read(-1)
        testplan_fb.close()

    return testplan_data


def ots_trigger(options):
    """
    Executes ots testrun over xml-rpc.
    """
    build_id = options.id
    ots_options = dict()
    if options.device:
        ots_options['device'] = options.device
    sw_product = options.sw_product
    email_list = options.email.split(',')

    try:
        for option in options.options.split(" "):
            key, value = option.split(":")
            ots_options[key] = value
    except AttributeError:
        pass

    if options.image:
        ots_options['image'] = options.image
    if options.testpackages:
        ots_options['packages'] = options.testpackages
    if options.filter:
        ots_options['testfilter'] = options.filter
    if options.input_plugin:
        ots_options['input_plugin'] = options.input_plugin
    if options.hosttest:
        ots_options['hosttest'] = options.hosttest
    if options.timeout:
        ots_options['timeout'] = options.timeout
    if options.distribution:
        ots_options['distribution_model'] = options.distribution
    if options.deviceplan:
        testplans = list()
        for testplan in options.deviceplan:
            testplan_data = read_test_plan(testplan)
            testplans.append((os.path.basename(testplan), testplan_data))
        ots_options['hw_testplans'] = testplans
    if options.hostplan:
        testplans = list()
        for testplan in options.hostplan:
            testplan_data = read_test_plan(testplan)
            testplans.append((os.path.basename(testplan), testplan_data))
        ots_options['host_testplans'] = testplans
    if options.rootstrap:
        ots_options['rootstrap'] = options.rootstrap
    if options.chroottest:
        ots_options['chroottest'] = options.chroottest
    if options.use_libssh2:
        ots_options['use_libssh2'] = options.use_libssh2

    ots_interface = xmlrpclib.Server("http://%s/" % options.server)
    return ots_interface.request_sync(sw_product,
                                      build_id,
                                      email_list,
                                      ots_options)


def parse_commandline_arguments():
    """
    Parses command line parameters. Makes sure that enough parameters are given.

    Returns OptionParser options object.
    """

    usage = "usage: %prog [options] \n" + \
            "example: " + \
            "%prog -i image_url"
                
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--server", dest="server", action="store",
                      type="string", help="OTS server URL (mandatory)",
                      metavar="SERVER")

    parser.add_option("-b", "--build_id", dest="id", action="store",
                      type="string", help="build request ID (mandatory)",
                      metavar="ID")

    parser.add_option("-i", "--image", dest="image", action="store",
                      type="string", help="URL to image file (mandatory)",
                      metavar="IMAGE", default="")

    parser.add_option("-p", "--sw_product", dest="sw_product", action="store",
                      type="string",
                      help="software product (mandatory)",
                      metavar="SWPRODUCT")

    parser.add_option("-e", "--email", dest="email", action="store",
                      type="string",
                      help="email addresses as a comma separated " \
                        "list (mandatory)",
                      metavar="EMAIL", default="")

    parser.add_option("-d", "--device", dest="device", action="store",
                      type="string", help="device properties", metavar="DEVICE",
                      default="")

    parser.add_option("-t", "--testpackages", dest="testpackages",
                      action="store", type="string",
                      help="list of test packages separated with comma",
                      metavar="TESTPACKAGES", default="")

    parser.add_option("-o", "--hostpackages", dest="hosttest", action="store",
                      type="string",
                      help="list of host test packages separated with space",
                      metavar="HOSTTEST", default="")

    parser.add_option("-C", "--chrootpackages", dest="chroottest",
                      action="store", type="string",
                      help="list of test packages separated with space",
                      metavar="CHROOTTEST", default="")

    parser.add_option("-m", "--timeout", dest="timeout", action="store",
                      type="int", help="global timeout (minutes)",
                      metavar="TIMEOUT", default=0)

    parser.add_option("-f", "--filter", dest="filter", action="store",
                      type="string", help="test filter string",
                      metavar="FILTER", default="")

    parser.add_option("-n", "--input_plugin", dest="input_plugin",
                      action="store",
                      type="string", help="input plugin to use",
                      metavar="PLUGIN", default="")

    parser.add_option("-c", "--distribution",
                      dest="distribution",
                      action="store",
                      type="string",
                      help="task distribution model (for example 'perpackage')",
                      metavar="DISTMODEL")

    parser.add_option("-r", "--rootstrap",
                      dest="rootstrap",
                      action="store",
                      type="string",
                      help="URL to rootstrap file",
                      metavar="ROOTSTRAP")

    parser.add_option("-T", "--deviceplan",
                      dest="deviceplan",
                      action="append",
                      type="string",
                      help="test plan for device based execution",
                      metavar="FILE")
    
    parser.add_option("-O", "--hostplan",
                      dest="hostplan",
                      action="append",
                      type="string",
                      help="test plan for host based execution",
                      metavar="FILE")

    parser.add_option("-S", "--libssh2",
                      dest="use_libssh2",
                      action="store_true",
                      help="use testrunner-lite libssh2 support",
                      default=False,
                      metavar="BOOL")

    parser.add_option("-x", "--options",
                      dest="options",
                      action="store",
                      type="string",
                      help="options in form 'key:value key:value'",
                      metavar="OPTIONS")

    # parser returns options and args even though we only need options
    # Disabling pylint complain about unused variable
    # pylint: disable=W0612
    (options, args) = parser.parse_args()
        
    
    if  not (options.server and options.id and options.sw_product and \
                 options.email and options.image):
        parser.print_help()
        print "\nError: Some of mandatory parameters were missing!"
        sys.exit(-1)
    elif not bool(options.rootstrap) == bool(options.chroottest):
        parser.print_help()
        print "\nError: Both rootstrap and chrootpackages needs to be defined" \
            " if using one of them."
        sys.exit(-1)

    return options


def main():
    """Main function"""
    options = parse_commandline_arguments()

    log_format = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        stream=sys.stdout)

    log = logging.getLogger(__name__)
    log.info("Calling OTS XML-RPC with options:\n %s" % str(options))
    result = ots_trigger(options)
    log.info("Result: %s" % result)


if __name__ == '__main__':
    main()

