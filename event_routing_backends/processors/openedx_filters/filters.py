"""
Processors filters, this file aims to contain all the filters that could modify the
standard transformer results by implementing external pipeline steps.
"""
from openedx_filters.tooling import OpenEdxPublicFilter

from event_routing_backends.processors.openedx_filters.exceptions import InvalidFilterType


class ProcessorBaseFilter(OpenEdxPublicFilter):
    """
    This is a general filter class that applies the open edx filter in multiple
    scenarios, its functionality is limited to one input one output therefore this
    only can be applied in method that returns a unique value.
    """

    @classmethod
    def generate_dynamic_filter(cls, filter_type):
        """This generates a sub class of ProcessorBaseFilter with the filter_type attribute.

        Arguments:
            filter_type: String the defines the filter key on the OPEN_EDX_FILTERS_CONFIG
                section

        Returns:
            ProcessorBaseFilter sub-class: This new class includes the filter_type attribute.
        """
        return type("DynamicFilter", (cls,), {"filter_type": filter_type})

    @classmethod
    def run_filter(cls, transformer, result):
        """
        Executes a filter after validating the right class configuration.

        Arguments:
            transformer: XApiTransformer instance.
            result: Result to be modified or extended.

        Returns:
            result: This value comes from the dictionary returned by run_pipeline and will vary
                depends on the implemented pipelines.

        Raises:
            InvalidFilterType: if the ProcessorBaseFilter is used instead of a dynamic filter.
        """
        if not cls.filter_type:
            raise InvalidFilterType("Parameter filter_type has not been set.")

        data = super().run_pipeline(transformer=transformer, result=result)

        return data.get("result", result)
