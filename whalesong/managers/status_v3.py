from typing import Any, Dict, List, Optional
from dirty_models import ModelField, HashMapField, ArrayField, IntegerField, StringIdField

from . import BaseModelManager, BaseCollectionManager
from .contact import Contact, ContactManager
from ..models import BaseModel, DateTimeField
from ..driver import BaseWhalesongDriver
from ..results import Result, IteratorResult


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

    read_keys = HashMapField(field_type=StringIdField())


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
                                                             manager_path=self._build_command('msgs')))

        self.add_submanager('contact', ContactManager(driver=self._driver,
                                                      manager_path=self._build_command('contact')))

    def send_read_status(self, message_id: str) -> Result[bool]:
        """
        Mark a statusV3 as read.

        :param message_id: Message serialized ID to be marked
        """
        params = {
            'messageId': message_id,
        }

        return self._execute_command('sendReadStatus', params)


class StatusV3CollectionManager(BaseCollectionManager):
    """
    Manage a collection of StatusV3.
    """
    MODEL_MANAGER_CLASS = StatusV3Manager

    def get_unexpired(self, unread: bool = True) -> IteratorResult[StatusV3]:
        """
        Get the read or unread StatusV3 collection

        :param unread: List read or unread statuses
        :return: List of StatusV3
        """
        params = {
            'unread': unread
        }

        return self._execute_command('getUnexpired', params, result_class=self.get_iterator_result_class())

    def sync(self) -> Result[None]:
        """
        Sync Statuses

        :return: None
        """
        return self._execute_command('sync')

    def get_my_status(self) -> Result[StatusV3]:
        """
        Get the own user StatusV3

        :return: StatusV3 object
        """
        return self._execute_command('getMyStatus', result_class=self.get_item_result_class())
