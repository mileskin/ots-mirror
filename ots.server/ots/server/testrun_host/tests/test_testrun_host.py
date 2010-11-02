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

import unittest
import datetime
from ots.server.testrun_host.testrun_host import TestrunHost

class testTestrunHost(unittest.TestCase):
    
    
    def setUp(self):

        self.host = TestrunHost()
        
            
    def tearDown(self):
        
        pass
        
    def test_publish_log_link(self):
        input_plugin_mock = InputPluginMock()
        testrun_mock = Testrun_mock()
        self.host.input_plugin = input_plugin_mock
        self.host.testrun = testrun_mock
        expected_text = "Log for testrun %s" % testrun_mock.get_testrun_id()

        self.host._publish_log_link()
        self.assertTrue(input_plugin_mock.url)
        self.assertEquals(expected_text, input_plugin_mock.text)


# Mock helpers#####
    def init_assetplugin_mock(self):
        pass
###
    def load_mock_options(self, sw_product):
        mock_options = dict()
        mock_options["default_option"] = "default_value"
        mock_options["distribution_model"] = "default"
        return mock_options


    def test_init_testrun(self):

        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["set_option"] = "something"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests"]
        image_url = "url/image.bin"
        rootstrap_url = None
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        returned_id = self.host.init_testrun(build_id,
                                             testrun_id,
                                             sw_product,
                                             ots_options,
                                             email_list,
                                             test_packages,
                                             image_url,
                                             rootstrap_url)
        self.assertEquals(returned_id, testrun_id)
        self.assertEquals(self.host.testrun.get_option("set_option"),
                          ots_options["set_option"])

        self.assertEquals(self.host.testrun.get_option("default_option"),
                          "default_value")

        self.assertEquals(self.host.testrun.get_email_list(),
                          email_list)

        self.assertEquals(self.host.testrun.get_image_url(),
                          image_url)

        self.assertEquals(self.host.testrun.get_testpackages(),
                          test_packages)

        self.assertEquals(self.host.testrun.get_option("distribution_model"),
                          "default")



    def _mock_targetpackages(self, build_id):
        return []

    def test_init_testrun_no_image(self):

        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["set_option"] = "something"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests"]
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        self.assertRaises(ValueError,
                          self.host.init_testrun,
                          build_id,
                          testrun_id,
                          sw_product,
                          ots_options,
                          email_list,
                          test_packages)
        self.assertEquals(self.host.testrun.get_error_info(),
                          "No image url or rootstrap url defined.")


    def test_init_testrun_bad_packages(self):

        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["set_option"] = "something"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests-invalid"]
        image_url = "url/image.bin"
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        self.assertRaises(ValueError,
                          self.host.init_testrun,
                          build_id,
                          testrun_id,
                          sw_product,
                          ots_options,
                          email_list,
                          test_packages,
                          image_url)
        self.assertEquals(self.host.testrun.get_error_info(),
                          "Invalid testpackage(s): ['dummy-tests-invalid']")

    def test_validate_custom_distribution_model(self):
        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["distribution_model"] = "custom_distribution"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests"]
        image_url = "url/image.bin"
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        self.host.init_testrun(build_id,
                               testrun_id,
                               sw_product,
                               ots_options,
                               email_list,
                               test_packages,
                               image_url)
        self.host._validate_distribution_model(["custom_distribution"])

    def test_validate_bad_custom_distribution_model(self):
        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["distribution_model"] = "unsupported_custom_distribution"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests"]
        image_url = "url/image.bin"
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        self.host.init_testrun(build_id,
                               testrun_id,
                               sw_product,
                               ots_options,
                               email_list,
                               test_packages,
                               image_url)
        self.assertRaises(ValueError,
                          self.host._validate_distribution_model,
                          ["custom_distribution"])



    def test_init_testrun_bad_distribution_model(self):

        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["distribution_model"] = "unsupported-value"
        email_list = ["dummy@localhost"]
        test_packages = ["dummy-tests"]
        image_url = "url/image.bin"
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock
        self.host.init_testrun(build_id,
                               testrun_id,
                               sw_product,
                               ots_options,
                               email_list,
                               test_packages,
                               image_url)
        self.assertRaises(ValueError, self.host.register_ta_plugins)
        self.assertEquals(self.host.testrun.get_error_info(),
                          "Invalid distribution model: unsupported-value")

    def test_init_testrun_perpackage_distribution_model_without_packages(self):

        build_id = 666
        testrun_id = 1234
        sw_product = "swproduct1"
        ots_options = dict()
        ots_options["distribution_model"] = "perpackage"
        email_list = ["dummy@localhost"]
        test_packages = []
        image_url = "url/image.bin"
        self.host._load_default_options = self.load_mock_options
        self.host._init_assetplugin = self.init_assetplugin_mock

        self.host.init_testrun(build_id,
                               testrun_id,
                               sw_product,
                               ots_options,
                               email_list,
                               test_packages,
                               image_url)
        self.assertRaises(ValueError, self.host.register_ta_plugins)
        self.assertEquals(self.host.testrun.get_error_info(),
            "Test packages must be defined for specified distribution model 'perpackage'")


    def test_register_ta_plugins(self):
        mock = Testrun_mock()
        self.host.testrun = mock
        self.host.register_ta_plugins()
        self.assertTrue(self.host.test_engines)




    def test_testrun_result(self):
        self.host.testrun = Testrun_mock()
        expected_result = "PASS"
        self.assertEquals(self.host.testrun_result(), expected_result)


class Testrun_mock(object):
    def __init__(self, testrun_id = "666"):
        self.engine = None
        self.resultsplugins = []
        self.testrun_id = testrun_id
        self.save_results_called = False
        self.target_packages = []
        self.n = 1

    def get_target_packages(self):
        pkgs = self.target_packages
        self.target_packages.append("pkg%s" % self.n)
        ++self.n
        return pkgs

    def get_option(self, option):
        if option == "distribution_model":
            return "default"
        return ""

    def set_state(self, state, status_info):
        pass
    def set_error_info(self, error):
        pass

    def set_result(self, result):
        pass

    def get_result_objects(self):
        return []

    def get_result_links(self):
        return [("text", "url")]

    def get_state(self):
        return ("Flashing", "Flashing")

    def get_image_name(self):
        return "asdf"
    
    def get_start_time(self):
        return datetime.datetime.now()

    def get_end_time(self):
        return datetime.datetime.now()

    def get_result(self):
        return "PASS"

    def add_result_link(self, text, link):
        self.link = link
        self.text = text

    def get_error_code(self):
        return "444"

    def get_error_info(self):
        return "444"


    def get_sw_version(self):
        return "asdf"

    def get_cmt_version(self):
        return "asdf"

    def get_image_url(self):
        return "asdf/asdf"

    def get_testrun_id(self):
        return self.testrun_id

    def email_enabled(self):
        return True

    def get_request_id(self):
        return "666"

    def registerResultsPlugin(self, plugin):
        self.resultsplugins.append(plugin)

    def save_results(self):
        self.save_results_called = True

class InputPluginMock(object):

    def __init__(self):
        self.request = None
        self.url = None
        self.text = None

    def store_url(self, url, text):
        self.url = url
        self.text = text


if __name__ == '__main__':
    unittest.main()
