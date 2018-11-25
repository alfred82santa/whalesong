from dirty_models import BooleanField, EnumField, IntegerField, StringIdField
from enum import Enum

from . import BaseModelManager
from ..models import BaseModel, DateTimeField
from ..results import Result


class Stream(BaseModel):
    class State(Enum):
        OPENING = 'OPENING'
        PAIRING = 'PAIRING'
        UNPAIRED = 'UNPAIRED'
        UNPAIRED_IDLE = 'UNPAIRED_IDLE'
        CONNECTED = 'CONNECTED'
        TIMEOUT = 'TIMEOUT'
        CONFLICT = 'CONFLICT'
        UNLAUNCHED = 'UNLAUNCHED'
        PROXYBLOCK = 'PROXYBLOCK'
        TOS_BLOCK = 'TOS_BLOCK'
        SMB_TOS_BLOCK = 'SMB_TOS_BLOCK'

    class Stream(Enum):
        DISCONNECTED = 'DISCONNECTED'
        SYNCING = 'SYNCING'
        RESUMING = 'RESUMING'
        CONNECTED = 'CONNECTED'

    backoff_generation = IntegerField()
    can_send = BooleanField()
    has_synced = BooleanField()
    is_incognito = BooleanField()

    launch_generation: IntegerField()
    launched = BooleanField()

    retry_timestamp = DateTimeField()
    state = EnumField(enum_class=State)
    stream = EnumField(enum_class=Stream)
    sync_tag = StringIdField()


class StreamManager(BaseModelManager[Stream]):
    MODEL_CLASS = Stream

    def poke(self) -> Result[None]:
        return self._execute_command('poke')

    def takeover(self) -> Result[None]:
        return self._execute_command('takeover')
