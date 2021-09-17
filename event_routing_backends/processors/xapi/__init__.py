"""
xAPI processors and spec implementation.
"""


from edx_toggles.toggles import SettingToggle

# .. toggle_name: XAPI_EVENTS_ENABLED
# .. toggle_implementation: SettingToggle
# .. toggle_default: True
# .. toggle_description: Allow sending events to external servers via xAPI.
#   Toggle intended both for gating initial release and for shutting off all
#   xAPI events in case of emergency.
# .. toggle_warnings: Do not enable sending of xAPI events until there has
#   been a thorough review of PII implications and safeguards put in place to
#   prevent accidental leakage of novel event fields to third parties. See
#   ARCHBOM-1655 for details.
# .. toggle_use_cases: circuit_breaker
# .. toggle_creation_date: 2021-01-01
# .. toggle_tickets: https://openedx.atlassian.net/browse/ARCHBOM-1658
XAPI_EVENTS_ENABLED = SettingToggle("XAPI_EVENTS_ENABLED", default=False)
