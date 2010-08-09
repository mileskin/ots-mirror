
from ots.server.results.results_processor_base import ResultsProcessorBase
from ots.server.results.package_results import PackageResults
from ots.server.results.schema import Tags, Values
from ots.server.results.testrun_result import TestrunResult

class PackageResultsProcessor(ResultsProcessorBase):

    def __init__(self,  test_package, environment):
        ResultsProcessorBase.__init__(self)
        self.package_results = PackageResults(test_package, 
                                              environment)
 
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
            self.package_results.significant_results.append(result)
        else:
            self.package_results.insignificant_results.append(result)
