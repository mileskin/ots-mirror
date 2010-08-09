
from ots.server.results.results_processor_base import ResultsProcessorBase
from ots.server.results.package import Package
from ots.server.results.required_packages import required_packages
from ots.server.results.schema import Tags, Values
from ots.server.results.testrun_result import TestrunResult

class ResultsJudgeException(Exception):
    pass

class ResultsJudgeProcessor(ResultsProcessorBase):

    def __init__(self, insignificant_tests_matter = False):
        ResultsProcessorBase.__init__(self)
        self._packages = []
        self._active_package = None
        self.insignificant_tests_matter =  insignificant_tests_matter
 
    @staticmethod
    def _is_significant(element):
        is_significant = True
        items_dict = dict(element.items())
        if items_dict.has_key(Tags.INSIGNIFICANT):
            insignificant = items_dict[Tags.INSIGNIFICANT].lower()
            return not (insignificant ==  Values.TRUE)

    def _check_run_validity(self):
        #FIXME
        required_packages = required_packages()
        if not required_packages:
            raise ResultsJudgeException("No test packages defined nor found.")

        missing = False  #FIXME set difference here
        if missing: 
            missing = ", ".join(missing)
            raise ResultsJudgeException("Missing from: %s"%(missing)) 

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
       
    #########################################
    # PUBLIC METHODS
    #########################################
            
    def set_active_package(self, 
                           test_package, 
                           environment):
        #FIXME check that package exists
        package = Package(test_package, 
                          environment)
        self._packages.append(package)
        self._active_package = package

    def result(self):
        ret_val = TestResult.NO_CASES
        self._check_run_validity() 
        results = []
        for package in self._packages:
            results.extend(package.significant_results)
            if self.insignificant_tests_matter:
                results.extend(package.insignificant_results)
        if results:
            if results.count(TestrunResult.PASS) == len(results):
                ret_val = TestrunResult.PASS
            else:
                ret_val = TestrunResult.FAIL
        return ret_val
