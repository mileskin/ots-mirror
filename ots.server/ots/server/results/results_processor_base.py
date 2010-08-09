
def _set_attrs(klass):
    #FIXME set from XSD
    tags = ["testresults", "suite", "set", 
            "case", "step", "expected_result",
            "return_code", "start", "end"]
    def _base_method(self, node):
        pass 
        #print "doing nothing in base method", node.tag
    for tag in tags:
        if not hasattr(klass, klass._pre_tag_method_name(tag)):
            setattr(klass, klass._pre_tag_method_name(tag), _base_method)
        if not hasattr(klass, klass._post_tag_method_name(tag)):
            setattr(klass, klass._post_tag_method_name(tag), _base_method)


class ResultsProcessorMeta(type):
    
    def __new__(cls, name, bases, dct):
        new = type.__new__(cls, name, bases, dct)
        _set_attrs(new)
        return new

    def __init__(cls, name, bases, dct):
        super(ResultsProcessorMeta, cls).__init__(name, bases, dct)
    
class ResultsProcessorBase(object):

    __metaclass__ = ResultsProcessorMeta

    @staticmethod
    def _pre_tag_method_name(tag):
        return "_preproc_%s"%(tag)

    @staticmethod
    def _post_tag_method_name(tag):
        return "_postproc_%s"%(tag)

    def _process(self, method_name, node):
        if hasattr(self, method_name):
            fn = getattr(self, method_name)
            fn(node)
        else:
            msg = "Unexpected tag: '%s'"%(node.tag)
            raise ResultProcessorException(msg)

    def pre_process(self, node):
        method_name = self._pre_tag_method_name(node.tag)
        self._process(method_name, node)

    def post_process(self, node):
        method_name = self._pre_tag_method_name(node.tag)
        self._process(method_name, node)
