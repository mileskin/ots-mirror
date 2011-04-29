# Based on http://code.activestate.com/recipes/146306/ By Wade Leftwich
"""
functions for multipart POST file sending
"""

import mimetypes, mimetools, urllib2

def post_multipart(host, selector, fields, files,
                   protocol="http",
                   user="",
                   password="",
                   realm="",
                   proxy = ""):
    """
    Post fields and files to an http host as multipart/form-data.
    
    @type host: C{str}
    @param host: receiving host
    
    @type selector: C{str}
    @param selector: selector part of url
    
    @type fields: C{list} of (C{str}, ?) C{tuple}s
    @param fields: sequence of (name, value) elements for regular form fields.
    
    @type files: C{list} of (C{str}, C{str}, ?) C{tuple}s
    @param files: sequence of (name, filename, value) elements for data to be
                  uploaded as files
    
    @type protocol: C{str}
    @param protocol: protocol to be used. defaults to http
    
    @type user: C{str}
    @param user: user name to be used in authentication
    
    @type password: C{str}
    @param password: password to be used in authentication
    
    @type realm: C{str}
    @param realm: realm to be associate with
    
    @rtype: C{file}
    @return: the server's response page.
    """
    if (user and password and realm):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm, host, user, password)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

    content_type, body = encode_multipart_formdata(fields, files)
    headers = {'Content-Type': content_type,
               'Content-Length': str(len(body))}
    request = urllib2.Request("%s://%s/%s" % (protocol, host, selector),
                        body, headers)
    if proxy:
        request.set_proxy(proxy, "http")
    return urllib2.urlopen(request).read()

def encode_multipart_formdata(fields, files):
    """
    @type fields: C{list} of ({C{str}, ?) C{tuple}s
    @param fields: sequence of (name, value) elements for regular form fields.
    
    @type files: C{list} of (C{str},C{str},?) C{tuple}s
    @param files: sequence of (name, filename, value) elements for data to be
                  uploaded as files
    
    @rtype: (C{str},C{str}) C{tuple}
    @return: tuple of content type and encoded body 
    """
    unique_boundary = mimetools.choose_boundary()
    crlf = '\r\n'
    lines = []
    for (key, value) in fields:
        lines.append('--' + unique_boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)
    for (key, filename, value) in files:
        lines.append('--' + unique_boundary)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"'\
                     % (key, filename))
        lines.append('Content-Type: %s' % get_content_type(filename))
        lines.append('')
        lines.append(value)
    lines.append('--' + unique_boundary + '--')
    lines.append('')
    body = crlf.join(lines)
    content_type = 'multipart/form-data; boundary=%s' % unique_boundary
    return content_type, body

def get_content_type(filename):
    """
    Get content type
    """
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

