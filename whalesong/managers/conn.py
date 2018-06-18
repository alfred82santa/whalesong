from . import BaseModelManager
from ..models import BaseModel


class Conn(BaseModel):
    pass


class ConnManager(BaseModelManager):
    MODEL_CLASS = Conn
