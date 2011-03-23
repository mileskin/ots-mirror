# -*- coding: utf-8 -*-
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

"""Test chroot environment"""

import os
import urllib
import urlparse
import tempfile
import re
import stat
import tarfile
import shutil
import logging

from ots.worker.conductor.conductorerror import ConductorError

class Chroot(object):

    def __init__(self, testrun):
        self.log = logging.getLogger("conductor")
        self.testrun = testrun
        self.path = None
        self._rootstrap = None

    def prepare(self):
        """Set up a Maemo/MeeGo rootstrap as a chroot environment."""
        if not self.testrun.is_chrooted:
            return
        self._setup_rootstrap()

    def cleanup(self):
        """Remove the rootstrap from the filesystem."""
        if not self.testrun.is_chrooted:
            return
        self._delete_rootstrap()

    # Private methods

    def _setup_rootstrap(self):
        """Download and install a rootstrap for running tests chrooted."""
        self._retrieve_rootstrap()
        self._unpack_rootstrap()
        self._prepare_chroot()

    def _retrieve_rootstrap(self):
        """Download rootstrap."""
        self._rootstrap = None

        if self.testrun.rootstrap_url:
            self.log.debug("Downloading rootstrap from '%s'" %
                self.testrun.rootstrap_url)
            try:
                # strap file extension from url
                extension = '.' + '.'.join(
                    urlparse.urlparse(self.testrun.rootstrap_url)[2] \
                        .split('/')[-1].split('.')[1:]
                )
                tmpfile = \
                    tempfile.NamedTemporaryFile(prefix='rootstrap-',
                        suffix=extension, delete=False)
                resource = urllib.urlopen(self.testrun.rootstrap_url)
                while True:
                    buf = resource.read(1024)
                    if not buf:
                        break
                    tmpfile.write(buf)
                resource.close()
                tmpfile.close()
                self._rootstrap = tmpfile.name
            except Exception, e:
                if os.path.isfile(self._rootstrap):
                    os.unlink(self._rootstrap)
                self._rootstrap = None

        # fallback to local copy
        if not self._rootstrap and self.testrun.rootstrap_path:
            self.log.debug("Using local rootstrap at '%s'" %
                self.testrun.rootstrap_path)
            self._rootstrap = self.testrun.rootstrap_path

        # handle problems
        if not self._rootstrap:
            msg = "Failed to download rootstrap and no local copy supplied."
            raise ConductorError(msg, "310")
        if not os.path.isfile(self._rootstrap):
            msg = "No rootstrap found at '%s'." % self._rootstrap
            raise ConductorError(msg, "310")

    def _unpack_rootstrap(self):
        """Unpack the rootstrap to a temporary directory."""

        ext2compr = { 'tgz': 'gz', 'gz': 'gz', 'bz2': 'bz2' }

        try:
            extension = self._rootstrap.split('.')[-1]
            try:
                compr_flag = ext2compr[extension]
            except KeyError:
                compr_flag = ''
            rootstrap = tarfile.open(self._rootstrap, "r:%s" % compr_flag)
            tmpdir = tempfile.mkdtemp(prefix='rootstrap-')
            self.log.debug("Unpacking rootstrap to '%s'" % tmpdir)
            rootstrap.extractall(tmpdir)
            self.path = tmpdir
        except Exception, e:
            msg = "Failed to unpack rootstrap: '%s'" % str(e)
            raise ConductorError(msg, "311")

    def _prepare_chroot(self):
        """Configure basic things, such as device nodes."""
        device_nodes = [
            ('console', stat.S_IFCHR | 0600, 5, 1),
            ('null',    stat.S_IFCHR | 0666, 1, 3),
            ('random',  stat.S_IFCHR | 0666, 1, 8),
            ('tty',     stat.S_IFCHR | 0666, 5, 0),
            ('urandom', stat.S_IFCHR | 0666, 1, 9)
        ]

        try:
            self.log.debug("Preparing chroot environment.")
            # create basic device nodes
            dev_path = self.path + os.sep + 'dev'
            if not os.path.exists(dev_path):
                os.mkdir(dev_path)
            umask = os.umask(0)
            for name, mode, major, minor in device_nodes:
                os.mknod(dev_path + os.sep + name, mode, os.makedev(major, minor))
            os.umask(umask)

            # copy resolv.conf from host
            etc_path = self.path + os.sep + 'etc'
            shutil.copy('/etc/resolv.conf', etc_path)

            # write /etc/hosts
            hosts = file(etc_path + os.sep + 'hosts', 'wb+')
            hosts.write("127.0.0.1       localhost.localdomain   localhost \n")
            hosts.write("%s       testdevice.localdomain  testdevice\n" \
                % self.testrun.target_ip_address)
            hosts.close()
        except Exception, e:
            msg = "Failed to setup chroot: '%s'" % str(e)
            raise ConductorError(msg, "312")

    def _delete_rootstrap(self):
        """Remove the packed and unpacked rootstrap."""
        if self._rootstrap and os.path.isfile(self._rootstrap):
            self.log.debug("Deleting rootstrap file '%s'." % self._rootstrap)
            os.unlink(self._rootstrap)
            self._rootstrap = None

        if self.path and os.path.isdir(self.path):
            self.log.debug("Deleting chroot environment below '%s'." %
                self.path)
            shutil.rmtree(self.path)
            self.path = None


class RPMChroot(Chroot):
    pass
