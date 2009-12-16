from django.db import models
import pickle, base64
from django.core import serializers

# Store for MetaData associated with Resources
# note that anything stored in this metadata object is not available for DB querying

class MetaData(object):
    # Image, audio, video
    width = None #pixels
    height = None #pixels
    duration = None #seconds
    # Book/text items
    pages = None
    chapters = None
    characters = None


class MetaDataField(models.Field):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(MetaDataField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value == '':
            return MetaData()
        if isinstance(value, MetaData):
            return value
        return pickle.loads(base64.b64decode(value))
 
    def get_db_prep_value(self, value):
        if value is None: return
        return base64.b64encode(pickle.dumps(value))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
