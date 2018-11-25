from dirty_models import BooleanField, EnumField, IntegerField, StringIdField
from enum import Enum

from . import BaseModelManager
from ..models import BaseModel, DateTimeField
from ..results import Result


class Stream(BaseModel):
    """
    Connection stream model.
    """

    class State(Enum):
        """
        Connection states.
        """

        OPENING = 'OPENING'
        """
        Opening stream.
        """

        PAIRING = 'PAIRING'
        """
        Pairing WhatsappWeb with a phone.
        """

        UNPAIRED = 'UNPAIRED'
        """
        Unpaired WhatsappWeb with a phone. QR is available.
        """

        UNPAIRED_IDLE = 'UNPAIRED_IDLE'
        """
        Unpaired WhatsappWeb with a phone. QR is not available.
        """

        CONNECTED = 'CONNECTED'
        """
        WhatsappWeb is connected to a phone.
        """

        TIMEOUT = 'TIMEOUT'
        """
        WhatsappWeb connection to a phone is timeout.
        """

        CONFLICT = 'CONFLICT'
        """
        Other browser has initiated WhatsappWeb with same phone.
        """

        UNLAUNCHED = 'UNLAUNCHED'
        """
        WhatsappWeb application has not been launched.
        """

        PROXYBLOCK = 'PROXYBLOCK'
        """
        Proxy is blocking connection.
        """

        TOS_BLOCK = 'TOS_BLOCK'
        """
        ¿?
        """

        SMB_TOS_BLOCK = 'SMB_TOS_BLOCK'
        """
        ¿?
        """

    class Stream(Enum):
        DISCONNECTED = 'DISCONNECTED'
        """
        Stream disconnected.
        """

        SYNCING = 'SYNCING'
        """
        Synchronizing data with phone.
        """

        RESUMING = 'RESUMING'
        """
        Resuming connection with phone.
        """

        CONNECTED = 'CONNECTED'
        """
        Connected to phone.
        """

    backoff_generation = IntegerField()
    """
    ¿?
    """

    can_send = BooleanField()
    """
    Whether it is able to send messages to phone.
    """

    has_synced = BooleanField()
    """
    Whether it is synchronized with phone.
    """

    is_incognito = BooleanField()
    """
    Whether it running in a incognito tab.
    """

    launch_generation: IntegerField()
    """
    ¿?
    """

    launched = BooleanField()
    """
    Whether it has been launched.
    """

    retry_timestamp = DateTimeField()
    """
    ¿?
    """

    state = EnumField(enum_class=State)
    """
    Current stream connection state.
    """

    stream = EnumField(enum_class=Stream)
    """
    Current stream state
    """

    sync_tag = StringIdField()
    """
    Last synchronizing tag.
    """


class StreamManager(BaseModelManager[Stream]):
    MODEL_CLASS = Stream

    def poke(self) -> Result[None]:
        """
        Refresh ref field. It is used to refresh QR image when it expires.
        """

        return self._execute_command('poke')

    def takeover(self) -> Result[None]:
        """
        Refresh login. It is used to take session again when other browser has been started session.
        """

        return self._execute_command('takeover')
