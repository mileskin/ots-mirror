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
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

###########################
# DEFAULT TEMPLATES 
###########################

DEFAULT_MESSAGE_BODY = \
"SW Product     : %s\n"\
"Build ID: %s\n"\
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

DEFAULT_MESSAGE_SUBJECT = "[OTS] [%s] Req#%s: %s"

#########################
# Helpers
#########################

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


#########################
# Type Formatting
#########################
    
def format_result(result, exception, verbose = False):
    """
    Test result string for mail message body

    @type result: C{ots.results.testrun_result}
    @param result: The testrun result

    @type exception: C{ots.common.dto.OTSException} or None
    @param exception: The exception raised

    @rtype: C{str}
    @rparam: The formatted result 
    """
    if exception is not None:
        return "%s (%s)" % (result, exception.strerror)
    #FIXME: verbose code
    return str(result)

def format_links(links):
    """ 
    @type links: C{list} of C{tuple} of C{str},C{str}
    @param links: The links to the results

    @rtype: C{str}
    @rparam: The formatted result 
    """
    return "\n".join(["%s: %s"%(text, url) for text,url in links])


def format_packages(packages):
    """
    @type expected_packages: C{ots.common.dto.packages}
    @param expected_packages: The packages that should be 
                              executed in the run
    """
   
    if not packages:
        return "(none)\n"
    packages_str = ""
    for (environment, pkg_list) in packages.items():
        pkgs = " ".join([pkg for pkg in pkg_list])
        packages_str += "  " + environment + ": " + pkgs + "\n"
    return packages_str
    


################################
# MailMessage
################################


class MailMessage(object):

    def __init__(self, from_address,
                       message_template = None, 
                       subject_template = None):
        self.from_address = from_address
        self.message_template = message_template
        if not self.message_template:
            self.message_template = DEFAULT_MESSAGE_BODY
        self.subject_template = subject_template
        if not self.subject_template:
            self.subject_template = DEFAULT_MESSAGE_SUBJECT

    def _body(self, sw_product, request_id, testrun_uuid,
                    tested_packages, result, exception, 
                    links, build_url):
        """
        """
        #FIXME epydoc
        build_link = build_url % request_id


        
        return self.message_template % (sw_product, 
                                        request_id, 
                                        testrun_uuid,
                                        format_packages(tested_packages), 
                                        format_result(result, exception), 
                                        format_links(links), 
                                        build_link)

    def _subject(self, sw_product, request_id, result):
        """
        """
        #FIXME epydoc
        return self.subject_template % (sw_product, 
                                        request_id, 
                                        result)
      
    def message(self, result, result_files, exception, 
                      tested_packages, sw_product, 
                      request_id, testrun_uuid, source_uris,
                      notify_list, email_attachments,
                      build_url):
        """
        
        """
        #FIXME epydoc

        msg = MIMEMultipart()

        #Body
        body = self._body(sw_product, request_id, testrun_uuid,
                          tested_packages, result, exception, 
                          source_uris, build_url)
        bodypart = MIMEText(body)
        msg.attach(bodypart)

        #Attachments
        if result_files and email_attachments:
            try:
                attach_as_zip_file(msg, result_files, testrun_uuid)
            except:
                LOG.error("Error creating email attachement:",
                      exc_info = True)

        #Headers
        msg["Subject"] = self._subject(sw_product, request_id, result)
        msg["From"] = self.from_address
        msg["To"] = ", ".join(notify_list)
        return msg
