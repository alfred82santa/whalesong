from datetime import datetime

from base64 import b64decode, b64encode
from dirty_models import BaseModel as DirtyBaseModel, StringIdField
from dirty_models.fields import BytesField, DateTimeField as BaseDateTimeField
from dirty_models.models import CamelCaseMeta
from dirty_models.utils import JSONEncoder as BaseJSONEncoder, ModelFormatterIter as BaseModelFormatterIter


class Base64Field(BytesField):
    """
    Byte field which allows to set base64 string data.
    """

    def convert_value(self, value):
        if isinstance(value, str):
            return b64decode(value.encode())
        return super(Base64Field, self).convert_value(value)


class DateTimeField(BaseDateTimeField):
    """
    Date time field that allow timestamps in microseconds.
    """

    def convert_value(self, value):
        try:
            return super(DateTimeField, self).convert_value(value)
        except Exception as ex:
            try:
                return super(DateTimeField, self).convert_value(value / 1000)
            except Exception:
                raise ex


class BaseModel(DirtyBaseModel, metaclass=CamelCaseMeta):
    """
    Base model which convert field name from underscore-style to camelCase-style automatically.
    """

    #: Unique identifier.
    id = StringIdField(read_only=True)


class ModelFormatterIter(BaseModelFormatterIter):

    def format_field(self, field, value):
        if isinstance(value, (bytes, bytearray)):
            return b64encode(value).decode()

        return super(ModelFormatterIter, self).format_field(field, value)


class JSONEncoder(BaseJSONEncoder):
    default_model_iter = ModelFormatterIter
