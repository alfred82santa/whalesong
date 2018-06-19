from dirty_models import FastDynamicModel

from . import BaseModelManager
# from ..models import BaseModel


class Stream(FastDynamicModel):
    pass


class StreamManager(BaseModelManager):
    MODEL_CLASS = Stream

    def poke(self):
        return self._execute_command('poke')

    def takeover(self):
        return self._execute_command('takeover')
