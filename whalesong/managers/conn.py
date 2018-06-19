from dirty_models import FastDynamicModel

from . import BaseModelManager
# from ..models import BaseModel


class Conn(FastDynamicModel):
    pass


class ConnManager(BaseModelManager):
    MODEL_CLASS = Conn
