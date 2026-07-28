"""
Support for reading tracking event logs.

Taken entirely from edx-analytics-pipeline.
"""
import json
import logging
import re
from json.decoder import JSONDecodeError

log = logging.getLogger(__name__)

PATTERN_JSON = re.compile(r'^.*?(\{.*\})\s*$')


def parse_json_event(line):
    """
    Parse a tracking log input line as JSON to create a dict representation.

    Arguments:
    * line:  the eventlog text
    """
    try:
        json_match = PATTERN_JSON.match(line)
        parsed = json.loads(json_match.group(1))

        # The representation of an event that event-routing-backends receives
        # from the async sender if significantly different from the one that
        # are saved to tracking log files for reasons lost to history.
        # This section of code attempts to format the event line to match the
        # async version.

        try:
            # The async version uses "data" for what the log file calls "event".
            # Sometimes "event" is a nested string of JSON that needs to be parsed.
            parsed["data"] = json.loads(parsed["event"])
        except (TypeError, JSONDecodeError):
            # If it's a TypeError then the "event" was not a string to be parsed,
            # so probably already a dict. If it's a JSONDecodeError that means the
            # "event" was a string, but not JSON. Either way we just pass the value
            # back, since all of those are valid.
            parsed["data"] = parsed["event"]

        # The async version of tracking logs seems to use "timestamp" for this key,
        # while the log file uses "time". We normalize it here.
        if "timestamp" not in parsed and "time" in parsed:
            parsed["timestamp"] = parsed["time"]

        return parsed
    except (AttributeError, JSONDecodeError, KeyError) as e:
        log.error("EXCEPTION!!!")
        log.error(type(e))
        log.error(e)
        log.error(line)

        return None
