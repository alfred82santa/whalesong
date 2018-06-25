from base64 import b64decode, b64encode
from dirty_models import BaseModel as DirtyBaseModel, StringIdField
from dirty_models.fields import BytesField
from dirty_models.models import CamelCaseMeta
from dirty_models.utils import JSONEncoder as BaseJSONEncoder, ModelFormatterIter as BaseModelFormatterIter


class Base64Field(BytesField):

    def convert_value(self, value):
        if isinstance(value, str):
            return b64decode(value.encode())
        return super(Base64Field, self).convert_value(value)


class BaseModel(DirtyBaseModel, metaclass=CamelCaseMeta):
    id = StringIdField(read_only=True)


class ModelFormatterIter(BaseModelFormatterIter):

    def format_field(self, field, value):
        if isinstance(value, (bytes, bytearray)):
            return b64encode(value).decode()

        return super(ModelFormatterIter, self).format_field(field, value)


class JSONEncoder(BaseJSONEncoder):
    default_model_iter = ModelFormatterIter
