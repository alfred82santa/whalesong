from dirty_models import ArrayField, BooleanField, DateTimeField, EnumField, ModelField
from enum import Enum

from . import BaseCollectionManager, BaseModelManager
from ..driver import BaseWhalesongDriver
from ..models import BaseModel
from ..results import Result


class ChatState(BaseModel):
    class Type(Enum):
        AVAILABLE = 'available'
        UNAVAILABLE = 'unavailable'
        COMPOSING = 'composing'
        RECORDING = 'recording'

    deny = BooleanField()
    is_state = BooleanField()
    timestamp = DateTimeField(alias=['t'])
    update_time = DateTimeField()
    type = EnumField(enum_class=Type)


class Presence(BaseModel):
    """
    Presence model.
    """

    chat_active = BooleanField()

    chat_state = ModelField(model_class=ChatState)

    chat_states = ArrayField(field_type=ModelField(model_class=ChatState), alias=['chatstates'])

    has_data = BooleanField()

    is_group = BooleanField()

    is_user = BooleanField()

    is_online = BooleanField()

    is_subscribed = BooleanField()


class ChatStateManager(BaseModelManager[ChatState]):
    """
    Chat state manager.
    """

    MODEL_CLASS = ChatState


class ChatStateCollectionManager(BaseCollectionManager[ChatStateManager]):
    """
    Chat state collection manager.
    """

    MODEL_MANAGER_CLASS = ChatStateManager


class PresenceManager(BaseModelManager[Presence]):
    """
    Presence manager.
    """

    MODEL_CLASS = Presence

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(PresenceManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('chat_states', ChatStateCollectionManager(driver=self._driver,
                                                                      manager_path=self._build_command('chatStates')))
        self.add_submanager('chat_state', ChatStateManager(driver=self._driver,
                                                           manager_path=self._build_command('chatState')))

    def update(self) -> Result[Presence]:
        return self._execute_command('update',
                                     result_class=self.get_model_result_class())


class PresenceCollectionManager(BaseCollectionManager[PresenceManager]):
    """
    Presence collection manager.
    """

    MODEL_MANAGER_CLASS = PresenceManager
