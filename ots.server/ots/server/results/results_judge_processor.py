
from ots.server.results.results_processor_base import ResultsProcessorBase
from ots.server.results.package import Package


########################################
# XSD
########################################

#FIXME. Get these from the XSD

class Tags:

    INSIGNIFICANT = "insignificant"
    RESULTS = "results"
    NO_CASES = "NO_CASES"
    RESULT = "result"

class Values: 

    ERROR = "ERROR"
    TRUE = "TRUE"
    PASS = "PASS"
    FAIL = "FAIL"


class ResultsJudgeException(Exception):
    pass

####################################
# Result Judge Processor
####################################

class ResultsJudgeProcessor(ResultsProcessorBase):

    def __init__(self):
        ResultsProcessorBase.__init__(self)
        self._packages = []
        self._active_package = None

    def set_active_package(self, 
                           test_package, 
                           environment,
                           insignificant_tests_matter = False):
        #FIXME check that package exists
        package = Package(test_package, 
                          environment, 
                          insignificant_tests_matter)
        self._packages.append(package)
        self._active_package = package
 
    @staticmethod
    def _is_significant(element):
        is_significant = True
        items_dict = dict(element.items())
        if items_dict.has_key(Tags.INSIGNIFICANT):
            insignificant = items_dict[Tags.INSIGNIFICANT].lower()
            return not (insignificant ==  Values.TRUE)
        
    #############################################
    # Node Processing 
    #############################################
        
    def _preproc_case(self, element): 
        is_significant = self._is_significant(element)
        items_dict = dict(element.items())
        result = items_dict[Tags.RESULT]
        if is_significant:
            self._active_package.significant_results.append(result)
        else:
            self._active_package.insignificant_results.append(result)
       
        for pkg in self._packages:
            print "sig", pkg.significant_results
            print "insig", pkg.insignificant_results

