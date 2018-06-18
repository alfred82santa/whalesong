from dirty_models import BaseModel as DirtyBaseModel, StringIdField
from dirty_models.models import CamelCaseMeta


class BaseModel(DirtyBaseModel, metaclass=CamelCaseMeta):

    id = StringIdField(read_only=True)
