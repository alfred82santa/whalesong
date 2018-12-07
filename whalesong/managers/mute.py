from datetime import datetime
from typing import List

from dirty_models import ArrayField, BooleanField, DateTimeField, ModelField, StringField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel
from ..results import Result


class Mute(BaseModel):
    """
    Mute model.
    """

    expiration = DateTimeField()
    """
    Expiration date time.
    """

    is_muted = BooleanField()
    """
    Whether it is already muted or not.
    """

    is_state = BooleanField()
    """
    ¿?
    """


class MuteManager(BaseModelManager[Mute]):
    """
    Mute manager. It allows manage chat mute.
    """

    MODEL_CLASS = Mute

    def mute(self, expiration: datetime) -> Result[None]:
        return self._execute_command('mute', {'expiration': int(expiration.timestamp())})

    def can_mute(self) -> Result[bool]:
        return self._execute_command('canMute')

    def unmute(self) -> Result[None]:
        return self._execute_command('unmute')


class MuteCollectionManager(BaseCollectionManager[MuteManager]):
    """
    Mutes collection manager. It allows manage global mute as well.
    """

    MODEL_MANAGER_CLASS = MuteManager

    def get_global_notifications(self) -> Result[bool]:
        return self._execute_command('getGlobalNotifications')

    def set_global_notifications(self, state: bool) -> Result[None]:
        return self._execute_command('setGlobalNotifications', {'state': state})

    def get_global_sounds(self) -> Result[bool]:
        return self._execute_command('getGlobalSounds')

    def set_global_sounds(self, state: bool) -> Result[None]:
        return self._execute_command('setGlobalSounds', {'state': state})

    def get_global_previews(self) -> Result[bool]:
        return self._execute_command('getGlobalPreviews')

    def set_global_previews(self, state: bool) -> Result[None]:
        return self._execute_command('setGlobalPreviews', {'state': state})
