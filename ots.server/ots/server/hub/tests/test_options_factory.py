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

import unittest

from ots.server.hub.options_factory import OptionsFactory

class TestOptionsFactory(unittest.TestCase):

    def test_default_options_dict(self):
        options_factory = OptionsFactory("example_sw_product", {})
        expected = {'devicegroup' : 'examplegroup'}
        d = options_factory._default_options_dict("example_sw_product")
        self.assertEquals(expected, d["device"])

    def test_core_options_names(self):
        names = OptionsFactory("example_sw_product", {}).core_options_names
        expected = ('self', 'image', 'packages', 'plan', 'hosttest', 
                    'device', 'emmc', 'distribution_model', 'flasher', 
                    'testfilter', 'timeout', 'chroottest', 'rootstrap')
        self.assertEquals(expected, names)

    def test_extended_options_dict(self):
        d = {'image' : 'image', 'packages' : 'packages', 
             'plan' : 'plan', 'hosttest' : 'hosttest', 
             'device' : 'device', 'emmc' : 'emmc', 
             'distribution_model' : 'distribution_model', 
             'flasher' : 'flasher', 'testfilter' : 'testfilter',
             'foo' : 'foo', 'bar' : 'bar', 'baz' : 'baz'}
        ext_opts = OptionsFactory("example_sw_product", d).extended_options_dict
        expected = {'foo': 'foo',
                    'bar': 'bar',
                    'email_attachments': 'off',
                    'baz': 'baz',
                    'email': 'on'
                    }
        self.assertEquals(ext_opts, expected)

    def test_chroot_parameters(self):
        d = {'image' : 'image', 'packages' : 'packages-tests', 
             'plan' : 'plan', 'hosttest' : 'hosttest-tests', 
             'device' : 'device', 'emmc' : 'emmc', 
             'distribution_model' : 'distribution_model', 
             'flasher' : 'flasher', 'testfilter' : 'testfilter',
             'foo' : 'foo', 'bar' : 'bar', 'baz' : 'baz',
             "chroottest": "some-tests"}
        self.assertRaises(ValueError, OptionsFactory("example_sw_product", d))

    def test_extended_options_dict_overridden(self):
        d = {'image' : 'image', 'packages' : 'packages', 
             'plan' : 'plan', 'hosttest' : 'hosttest', 
             'device' : 'device', 'emmc' : 'emmc', 
             'distribution_model' : 'distribution_model', 
             'flasher' : 'flasher', 'testfilter' : 'testfilter',
             'email_attachments' : 'off', 'email' : 'on'}
        ext_opts = OptionsFactory("example_sw_product", d).extended_options_dict
        expected = {'email_attachments': 'off',
                    'email': 'on'}
        self.assertEquals(ext_opts, expected)

    def test_device_option_handling(self):
        user_options = {"device": "devicename:name", "image": "foo"}
        options_factory = OptionsFactory("example_sw_product", user_options)
        properties = options_factory().device_properties
        expected = {'devicegroup' : 'examplegroup', "devicename":"name"}
        self.assertEquals(properties, expected)

if __name__ == "__main__":
    unittest.main()
