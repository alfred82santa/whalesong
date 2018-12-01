from asyncio import CancelledError, Future, Task, ensure_future, sleep
from datetime import datetime

from dirty_models import BooleanField, EnumField, IntegerField
from enum import Enum

from whalesong import BaseWhalesongDriver
from . import BaseModelManager
from ..models import BaseModel
from ..results import Result


class DisplayInfo(BaseModel):
    """
    Connection stream model.
    """

    class StreamInfo(Enum):
        """
        Stream information.
        """

        OFFLINE = 'OFFLINE'
        """
        Offline.
        """

        OPENING = 'OPENING'
        """
        Opening connection.
        """

        PAIRING = 'PAIRING'
        """
        Pairing phone.
        """

        SYNCING = 'SYNCING'
        """
        Synchronizing data.
        """

        RESUMING = 'RESUMING'
        """
        Resuming connection.
        """

        CONNECTING = 'CONNECTING'
        """
        Connecting.
        """

        NORMAL = 'NORMAL'
        """
        Normal.
        """

        TIMEOUT = 'TIMEOUT'
        """
        Connection timeout.
        """

    class StreamMode(Enum):
        """
        Stream mode.
        """

        QR = 'QR'
        """
        Wait for QR scan.
        """

        MAIN = 'MAIN'
        """
        Main.
        """

        SYNCING = 'SYNCING'
        """
        Synchronizing data.
        """

        OFFLINE = 'OFFLINE'
        """
        Not connected.
        """

        CONFLICT = 'CONFLICT'
        """
        Other browser has opened session.
        """

        PROXYBLOCK = 'PROXYBLOCK'
        """
        Proxy blocks connection.
        """

        TOS_BLOCK = 'TOS_BLOCK'
        """
        ¿?
        """

        SMB_TOS_BLOCK = 'SMB_TOS_BLOCK'
        """
        ¿?
        """

        DEPRECATED_VERSION = 'DEPRECATED_VERSION'
        """
        Using a deprecated version.
        """

    class DisplayState(Enum):
        """
        Display state.
        """

        SHOW = 'SHOW'
        """
        Display showing.
        """

        OBSCURE = 'OBSCURE'
        """
        Display obscured.
        """

        HIDE = 'HIDE'
        """
        Display hidden.
        """

    available = BooleanField(default=False)
    """
    Whether current user is available.
    """

    client_expired = BooleanField()
    """
    Whether client session has expired.
    """

    could_force = BooleanField()
    """
    ¿?
    """

    display_info = EnumField(enum_class=StreamInfo)
    """
    Stream state.
    """

    hard_expired: BooleanField()
    """
    ¿?
    """

    info = EnumField(enum_class=StreamInfo)
    """
    Same than display info?
    """

    is_state = BooleanField()
    """
    ¿?
    """

    obscurity = EnumField(enum_class=DisplayState)
    """
    Current display state.
    """

    mode = EnumField(enum_class=StreamMode)
    """
    Stream mode.
    """

    phone_authed = BooleanField()
    """
    Whether phone authorized.
    """

    ui_active = BooleanField()
    """
    Whether UI is active.
    """

    resume_count = IntegerField()
    """
    Count how many time connection was resumed.
    """


class DisplayInfoManager(BaseModelManager[DisplayInfo]):
    """
    Manage display information.
    """

    MODEL_CLASS = DisplayInfo

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        """

        :param driver: Whalesong driver
        :param manager_path: Manager prefix path.
        """
        super(DisplayInfoManager, self).__init__(driver=driver, manager_path=manager_path)

        self._fut_available: Future = None

    def mark_available(self) -> Result[None]:
        """
        Mark current user as available. It is need to get presence from other users.
        """

        return self._execute_command('markAvailable')

    def mark_unavailable(self) -> Result[None]:
        """
        Mark current user as unavailable.
        """

        return self._execute_command('markUnavailable')

    def unobscure(self) -> Result[None]:
        """
        Unobscure display.
        """

        return self._execute_command('unobscure')

    def set_available_permanent(self):
        """
        Set user available permanently. It starts a loop in order to set availability each 30 seconds.
        """
        if self.is_available_permanent():
            return

        self._fut_available = ensure_future(self._available_permanent())

    def unset_available_permanent(self):
        """
        Unset user available permanently. It stops permanent availability loop.
        """
        if self._fut_available is None:
            return

        if not self._fut_available.done():
            self._fut_available.cancel()
        self._fut_available = None

    def is_available_permanent(self):
        """
        Checks whether permanent availability loop is running.

        :return: Permanent availability loop state.
        """
        if self._fut_available is not None:
            if not self._fut_available.done():
                return True
            self._fut_available = None

        return False

    async def _available_permanent(self):
        try:
            while not Task.current_task().cancelled():
                self.mark_available()
                await sleep(30)
        except CancelledError:
            pass
