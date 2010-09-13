
def store_url(url, text):
    """
    Method for storing result urls

    @type url: C{string}
    @param url: Url string

    @type text: C{string}
    @param text: Description text for the url

    """
    pass

def get_target_packages(build_id):
    """
    Method for storing result urls

    @type build_id: C{int}
    @param build_id: Build request number

    @type text: C{string}
    @param text: Description text for the url

    @rtype: C{list} consisting of C{string}
    @return: List of changed packages

    """
    raise NotImplementedError



def store_file(file_content,
               filename,
               label,
               description):
    """
    Method for storing result files

    @type file_content: C{string}
    @param file_content: File content as a string

    @type filename: C{string}
    @param filename: File name

    @type label: C{string}
    @param label: Label of the file

    @type description: C{string}
    @param description: Description of the file


    """
    pass
