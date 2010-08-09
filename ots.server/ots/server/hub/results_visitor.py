
import xml.etree.cElementTree as ET

def visit_results(results_xml):
    visitor = ResultsVisitor()
    result_judge_processor = ResultJudgeProcessor()
    result_judge_processor.set_active_package("foo", "bar")
    visitor.add_processor(result_judge_processor)
    root = ET.fromstring(results_xml)
    visitor.visit(root)

class ResultsVisitor(object):
    """
    Extrinsic Visitor 
    """

    _processors = []

    def add_processor(self, processor):
        self._processors.append(processor)

    def visit(self, node):
        for processor in self._processors:
            processor.pre_process(node)
        for n in node.getchildren():
            self.visit(n)
        for processor in self._processors:
            processor.post_process(node)

class ResultProcessorException(Exception):
    pass

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

class ResultProcessorMeta(type):
    
    def __new__(cls, name, bases, dct):
        new = type.__new__(cls, name, bases, dct)
        _set_attrs(new)
        return new

    def __init__(cls, name, bases, dct):
        super(ResultProcessorMeta, cls).__init__(name, bases, dct)
    
class ResultProcessorBase(object):

    __metaclass__ = ResultProcessorMeta

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

class Package(object):
    """
    Container for the Package results
    """

    def __init__(self, 
                 testpackage, 
                 environment,
                 insignificant_tests_matter):
        self.testpackage = testpackage
        self.environment = environment
        self.insignificant_tests_matter = insignificant_tests_matter
        self.significant_results = []
        self.insignificant_results = []

#Fixme. Can we get these from the XSD?

INSIGNIFICANT = "insignificant"
RESULTS = "results"

class ResultsJudgeException(Exception):
    pass

class ResultJudgeProcessor(ResultProcessorBase):

    def __init__(self):
        ResultProcessorBase.__init__(self)
        self._packages = []
        self._active_package = None

    def set_active_package(self, 
                           test_package, 
                           environment,
                           insignificant_tests_matter = False):
        #FIXME check that package exists
        package = Package(test_package, environment, insignificant_tests_matter)
        self._packages.append(package)
        self._active_package = package
 
    @staticmethod
    def _is_significant(element):
        is_significant = True
        items_dict = dict(element.items())
        if items_dict.has_key(INSIGNIFICANT):
            insignificant = items_dict[INSIGNIFICANT].lower()
            if insignificant == "true" or insignificant == "false":
                is_significant = not (insignificant ==  "true")
            else:
                msg = "insignificant attribute must be 'false' or 'true'"\
                    " but it was %s" % insignificant
                raise ResultsJudgeException(msg)
        return is_significant
        
    #############################################
    # Node Processing 
    #############################################
        
    def _preproc_testresults(self, node):
        print "doing something in concrete method prepoc", node

    def _postproc_testresults(self, node):
        print "doing something in concrete method postproc", node

    def _preproc_case(self, element): 
        is_significant = self._is_significant(element)
        items_dict = dict(element.items())
        result = items_dict["result"]
        if is_significant:
            self._active_package.significant_results.append(result)
        else:
            self._active_package.insignificant_results.append(result)
       
        for pkg in self._packages:
            print "sig", pkg.significant_results
            print "insig", pkg.insignificant_results
