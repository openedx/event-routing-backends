"""
Decorators that helps to implement the Processor filter functionality.
"""
import functools

from event_routing_backends.processors.openedx_filters.filters import ProcessorBaseFilter


def openedx_filter(filter_type):
    """
    This decorator allows to implement the ProcessorBaseFilter on multiple class methods
    and intends to modify the returned value from methods like get_actor or get_objects
    in cases where the standard output doesn't satisfy the implementation requirements.

    Arguments:
        filter_type: String that defines the filter_type attribute of ProcessorBaseFilter,
            this allows to identify the configuration setting.

    Example:

        1. Decorate your method:

            @openedx_filter(filter_type="this.will.be.the.filter.key")
            def get_object(self):
                ...

        2. Set the openedx filter config in your environment variables.

            OPEN_EDX_FILTERS_CONFIG = {
                "this.will.be.the.filter.key": {
                    "pipeline": ["path.to.an.external.pipeline.step"],
                    "fail_silently": False,
                }
            }

        3. More details about filters https://github.com/openedx/openedx-filters/
    """
    def wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            dynamic_filter = ProcessorBaseFilter.generate_dynamic_filter(filter_type=filter_type)

            return dynamic_filter.run_filter(
                transformer=args[0],
                result=func(*args, **kwargs),
            )

        return inner_wrapper

    return wrapper
