
from ots.server.results.results_processor_base import ResultsProcessorBase
from ots.server.results.package import Package

#Fixme. Can we get these from the XSD?
INSIGNIFICANT = "insignificant"
RESULTS = "results"

class ResultsJudgeException(Exception):
    pass

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

