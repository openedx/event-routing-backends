"""
Custom django model fields.
"""
from fernet_fields import EncryptedField
from jsonfield.fields import JSONField


class EncryptedJSONField(EncryptedField, JSONField):
    description = 'Field to store encrypted JSON data.'
