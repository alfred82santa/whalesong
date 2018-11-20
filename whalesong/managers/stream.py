from dirty_models import FastDynamicModel

from . import BaseModelManager
from ..results import Result


# from ..models import BaseModel


class Stream(FastDynamicModel):
    pass


class StreamManager(BaseModelManager[Stream]):
    MODEL_CLASS = Stream

    def poke(self) -> Result[None]:
        return self._execute_command('poke')

    def takeover(self) -> Result[None]:
        return self._execute_command('takeover')
