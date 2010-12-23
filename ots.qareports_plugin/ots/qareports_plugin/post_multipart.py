# Based on http://code.activestate.com/recipes/146306/ By Wade Leftwich
"""
functions for multipart POST file sending
"""

import httplib, mimetypes

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files
    Return the server's response page.
    """
    content_type, body = _encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def _encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    crlf = '\r\n'
    content_list = []
    for (key, value) in fields:
        content_list.append('--' + boundary)
        content_list.append('Content-Disposition: form-data; name="%s"' % key)
        content_list.append('')
        content_list.append(value)
    for (key, filename, value) in files:
        content_list.append('--' + boundary)
        content_list.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        content_list.append('Content-Type: %s' % _get_content_type(filename))
        content_list.append('')
        content_list.append(value)
    content_list.append('--' + boundary + '--')
    content_list.append('')
    body = crlf.join(content_list)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body

def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
