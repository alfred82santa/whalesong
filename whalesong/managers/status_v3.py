from typing import Any, Dict, List, Optional
from dirty_models import ModelField, IntegerField, StringIdField

from . import BaseModelManager, BaseCollectionManager
from .contact import Contact, ContactManager
from ..models import BaseModel, DateTimeField
from ..driver import BaseWhalesongDriver
from ..results import Result


class StatusV3(BaseModel):
    """
    StatusV3 model
    """

    unread_count = IntegerField()
    """
    Unread statuses
    """

    expire_ts = DateTimeField()
    """
    Status expiration date
    """

    contact = ModelField(model_class=Contact)
    """
    Contact object
    """

    last_received_key = StringIdField()
    """
    Last encryption key received (¿?).
    """


class StatusV3Manager(BaseModelManager[StatusV3]):
    """
    StatusV3 manager. Allow to manage a WhatsApp status.

    .. attribute:: msgs
        :class: `~whalesong.managers.message.MessageCollectionManager`
        StatusV3 message collection manager.

    .. attribute:: contact
        :class: `~whalesong.managers.contact.ContactManager`
        StatusV3 contact manager.
    """
    MODEL_CLASS = StatusV3
    
    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(StatusV3Manager, self).__init__(driver=driver, manager_path=manager_path)

        from .message import MessageCollectionManager
        self.add_submanager('msgs', MessageCollectionManager(driver=self._driver,
                                                             manager_path=self._build_command('args')))

        self.add_submanager('contact', ContactManager(driver=self._driver,
                                                      manager_path=self._build_command('contact')))

    def send_read_status(self, status_serialized_id, user_serialized_id) -> Result[bool]:
        """
        Mark a statusV3 as read.

        :param status_serialized_id: StatusV3 serialized ID to be marked
        :param user_serialized_id: User that owns the statusV3
        """
        serialized_remote = status_serialized_id.split('_')[len(status_serialized_id.split('_')) - 2]
        params: Dict[str, Any] = {
            'readMessage': {
                'fromMe': False,
                'id': status_serialized_id.split('_')[len(status_serialized_id.split('_')) - 1],
                'remote': {
                    'server': serialized_remote.split('@')[1],
                    'user': serialized_remote.split('@')[0],
                    '_serialized': serialized_remote
                },
                '_serialized': status_serialized_id
            },
            'fromUser': {
                'server': user_serialized_id.split('@')[1],
                'user': user_serialized_id.split('@')[0],
                '_serialized': user_serialized_id
            }
        }

        return self._execute_command('sendReadStatus', params)

    def load_more(self):
        """
        When you are seeing one statusV3 and want to load the next. (Not obligatory)
        """
        return self._execute_command('loadMore')


class StatusV3CollectionManager(BaseCollectionManager):
    """
    Manage a collection of StatusV3.
    """
    MODEL_MANAGER_CLASS = StatusV3Manager

    def get_statuses(self, read_status) -> Result[List[StatusV3]]:
        """
        Get the read or unread StatusV3 collection

        :param read_status: List read or unread statuses
        :return: List of StatusV3
        """
        params = {
            'unread': read_status
        }

        return self._execute_command('getStatus', params)

    def sync(self) -> Result[List[StatusV3]]:
        """
        Sync Statuses and return all

        :return: List of StatusV3
        """
        return self._execute_command('sync')

    def get_my_status(self) -> Result[StatusV3]:
        """
        Get the own user StatusV3

        :return: StatusV3 object
        """
        return self._execute_command('getMyStatus')
