"""
xAPI statement classes
"""
from tincan import Activity


class GroupActivity(Activity):
    """
    Subclass of tincan.Activity which reports object_type="GroupActivity"

    For use with Activites that contain one or more child Activities, like Problems that contain multiple Questions.
    """
    @Activity.object_type.setter
    def object_type(self, _):
        self._object_type = 'GroupActivity'
