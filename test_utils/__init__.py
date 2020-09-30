"""
Test utilities.

Since pytest discourages putting __init__.py into testdirectory
(i.e. making tests a package) one cannot import from anywhere
under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes).

So this package is the place to put them.
"""
import sys

import mock


def _mock_third_party_modules():
    """
    Mock third party modules used in the app.
    """
    student_module = mock.MagicMock()
    student_module.anonymous_id_for_user.return_value = 'anonymous_id'
    sys.modules['student.models'] = student_module
