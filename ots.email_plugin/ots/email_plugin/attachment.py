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

from zipfile import ZipFile
from zipfile import ZipInfo
from zipfile import ZIP_DEFLATED

from tempfile import gettempdir

def attach_as_zip_file(msg, result_files, unique_id):
    """
    Create a zip file containing result_files and attach it to msg.
    msg must be MIMEMultipart object.
    """

    #create temp file for ZipFile.
    zipname = 'OTS_testrun_%s.zip' % unique_id
    tmp_file = os.path.join(gettempdir(), "tmp_file_%s" % zipname)

    zipped = ZipFile(tmp_file, 'w')

    LOG.debug("Created temporary file: %s" % tmp_file)

    #add results files to zip file
    for resultfile in result_files:
        filename = "%s-%s" % (resultfile.environment, resultfile.filename)
        info = ZipInfo(filename)
        info.date_time = time.localtime(time.time())[:6] #now
        info.external_attr = 0666 << 16L # read-write access to everyone
        info.compress_type = ZIP_DEFLATED
        zipped.writestr(info, resultfile.content)

    #calling close is required to finalize zip file. Closes tmp_file.
    #This is why we cannot use usual tempfiles - they are removed automatically 
    #when closed.
    zipped.close()

    zipped_content = open(tmp_file).read()

    ctype = 'application/zip'
    maintype, subtype = ctype.split('/', 1)
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(zipped_content)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', 
                          filename = zipname )

    #attach to message
    msg.attach(attachment)

    LOG.debug("Attached file %s containing %s files" \
              % (zipname, len(result_files)))

    #delete temp file
    os.unlink(tmp_file)
    LOG.debug("Deleted temporary file: %s" % tmp_file)

