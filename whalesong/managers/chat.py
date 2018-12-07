from typing import Any, Dict, List, Optional

from base64 import b64encode
from dirty_models import BooleanField, DateTimeField, IntegerField, ModelField, StringIdField
from io import BytesIO

from . import BaseCollectionManager, BaseModelManager
from .contact import Contact, ContactManager
from .group_metadata import GroupMetadata, GroupMetadataManager
from .mute import Mute, MuteManager
from .presence import PresenceManager
from ..driver import BaseWhalesongDriver
from ..models import BaseModel
from ..results import Result


class Chat(BaseModel):
    """
    Chat model.
    """

    name = StringIdField()
    """
    Chat title.
    """

    last_message_ts = DateTimeField(alias=['t'])
    """
    Last message timestamp.
    """

    pin = IntegerField()
    """
    Pin type (¿?)
    """

    unread_count = IntegerField()
    """
    Unread message count.
    """

    archive = BooleanField(default=False)
    """
    Whether chat is archived or not.
    """

    change_number_new_jid = StringIdField()
    """
    Information about peer's new jabber id (user identifier). 
    It happens when a peer change its phone number.
    """

    change_number_old_jid = StringIdField()
    """
    Information about peer's old phone numberjabber id (user identifier). 
    It happens when a peer change its phone number.
    """

    contact = ModelField(model_class=Contact)
    """
    Contact object.
    """

    group_metadata = ModelField(model_class=GroupMetadata)
    """
    Group metadata object.
    """

    is_announce_grp_restrict = BooleanField(default=False)
    """
    ¿?
    """

    is_group = BooleanField(default=False)
    """
    Whether chat is group or not.
    """

    is_read_only = BooleanField(default=False)
    """
    Whether chat is read only or not.
    """

    kind = StringIdField()
    """
    ¿?
    """

    last_received_key = StringIdField()
    """
    Last encryption key received (¿?).
    """

    modify_tag = StringIdField()
    """
    ¿?
    """

    mute_expiration = IntegerField()
    """
    Seconds to mute expiration.
    """

    not_spam = BooleanField(default=False)
    """
    Whether it was notified as spam chat.
    """

    mute = ModelField(model_class=Mute)
    """
    Mute information.
    """


class MsgLoadState(BaseModel):
    context_loaded = BooleanField(default=False)
    """
    Whether context was loaded (¿?).
    """

    is_loading_around_msgs = BooleanField(default=False)
    """
    Whether it is loading messages (¿?).
    """

    is_loading_earlier_msgs = BooleanField(default=False)
    """
    Whether it is loading earlier messages.
    """

    is_loading_recent_msgs = BooleanField(default=False)
    """
    Whether it is loading recent messages.
    """

    no_earlier_msgs = BooleanField(default=False)
    """
    Whether it all message have been loaded.
    """


class MsgLoadStateManager(BaseModelManager[MsgLoadState]):
    """
    Message load state manager
    """

    MODEL_CLASS = MsgLoadState


class ChatManager(BaseModelManager[Chat]):
    """
    Chat manager. It allows manage a chat.

    .. attribute:: msgs

        :class:`~whalesong.managers.message.MessageCollectionManager`

        Chat's message collection manager.

    .. attribute:: msg_load_state

        :class:`~MsgLoadStateManager`

        Chat's message load state manager.

    .. attribute:: metadata:

        :class:`~GroupMetadataManager`

        Chat's group metadata manager.

    .. attribute:: contact

        :class:`~whalesong.managers.contact.ContactManager`

        Chat's contact manager.

    .. attribute:: live_location

        :class:`~whalesong.managers.live_location.LiveLocationManager`

        Live location manager. You should call to :meth:`~whalesong.managers.chat.ChatManager.find_live_location`
        before use it.

    """
    MODEL_CLASS = Chat

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(ChatManager, self).__init__(driver=driver, manager_path=manager_path)

        from .message import MessageCollectionManager
        self.add_submanager('msgs', MessageCollectionManager(driver=self._driver,
                                                             manager_path=self._build_command('msgs')))

        self.add_submanager('msg_load_state', MsgLoadStateManager(driver=self._driver,
                                                                  manager_path=self._build_command('msgLoadState')))

        self.add_submanager('metadata', GroupMetadataManager(driver=self._driver,
                                                             manager_path=self._build_command('metadata')))

        self.add_submanager('presence', PresenceManager(driver=self._driver,
                                                        manager_path=self._build_command('presence')))

        self.add_submanager('contact', ContactManager(driver=self._driver,
                                                      manager_path=self._build_command('contact')))

        from .live_location import LiveLocationManager
        self.add_submanager('live_location', LiveLocationManager(driver=self._driver,
                                                                 manager_path=self._build_command('liveLocation')))

        self.add_submanager('mute', MuteManager(driver=self._driver,
                                                manager_path=self._build_command('mute')))

    def send_text(self, text: str,
                  quoted_msg_id: Optional[str] = None,
                  mentions: Optional[List[str]] = None,
                  link_desc=None) -> Result[str]:
        """
        Send text message to current chat.

        :param text: Message to send.
        :param quoted_msg_id: Quoted message's identifier.
        :param mentions: List of user ids mentioned.
        :param link_desc: Link description.
        :return: New message's identifier
        """
        params: Dict[str, Any] = {'text': text}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        if link_desc:
            params['linkDesc'] = link_desc

        return self._execute_command('sendText', params)

    def send_contact(self, contact_id: str, quoted_msg_id: Optional[str] = None) -> Result[str]:
        """
        Send contact to current chat.

        :param contact_id: Contact identifier to send.
        :param quoted_msg_id: Quoted message's identifier.
        :return: New message's identifier
        """
        params: Dict[str, Any] = {'contactId': contact_id}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendContact', params)

    def send_contact_phone(self, contact_name: str,
                           phone_number: str,
                           quoted_msg_id: Optional[str] = None) -> Result[str]:
        """
        Send contact to current chat using contact name and phone number.

        :param contact_name: Contact's name.
        :param phone_number: Contact's phone number.
        :param quoted_msg_id: Quoted message's identifier.
        :return: New message's identifier
        """
        params: Dict[str, Any] = {'contactName': contact_name,
                                  'phoneNumber': phone_number}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendContactPhone', params)

    def send_media(self, media_data: BytesIO,
                   content_type: Optional[str] = None, filename: Optional[str] = None,
                   caption: Optional[str] = None,
                   quoted_msg_id: Optional[str] = None, mentions: Optional[List[str]] = None) -> Result[str]:
        """
        Send media file to current chat.

        :param media_data: io.ByteIO
        :param content_type: File content type. It is used by Whatsapp to known how to render it.
        :param filename: File name.
        :param caption: Media caption.
        :param quoted_msg_id: Quoted message's identifier.
        :param mentions: List of user ids mentioned.
        :return: New message's identifier
        """

        params: Dict[str, Any] = {'mediaData': b64encode(media_data.read()).decode()}

        if content_type:
            params['contentType'] = content_type

        if filename:
            params['filename'] = filename

        if caption:
            params['caption'] = caption

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        return self._execute_command('sendMedia', params)

    def leave_group(self) -> Result[None]:
        """
        Leave current chat group.

        .. warning:: Only available on group chats.

        """
        return self._execute_command('leaveGroup')

    def delete_chat(self) -> Result[None]:
        """
        Delete chat.
        """
        return self._execute_command('deleteChat')

    def send_seen(self) -> Result[None]:
        """
        Mark chat as seen.
        """
        return self._execute_command('sendSeen')

    def load_earlier_messages(self) -> Result[None]:
        """
        Load earlier messages.

        .. tip::

            You should monitor chat messages in order to get new messages loaded.

            .. code-block:: python3

                async for msg in driver.chat[chat_id].msgs.monitor_add():
                    print(msg)


        """
        return self._execute_command('loadEarlierMessages')

    def load_all_earlier_messages(self) -> Result[None]:
        """
        Load ALL earlier messages.

        .. tip::

            You should monitor chat messages in order to get new messages loaded.
            And perhaps you should remove them after process in order to save memory.

            .. code-block:: python3

                async for msg in driver.chat[chat_id].msgs.monitor_add():
                    print(msg)
                    await driver.chat[chat_id].msgs.remove_item_by_id(item.id)


        """
        return self._execute_command('loadAllEarlierMessages')

    def set_subject(self, subject: str) -> Result[None]:
        """
        Set group subject/title.

        :param subject: New group subject/title string
        :return: None
        """

        return self._execute_command('setSubject', {'subject': subject})

    def mark_composing(self) -> Result[None]:
        """
        Set "typing..." message for 2.5 seconds.

        :return: None
        """

        return self._execute_command('markComposing')

    def mark_recording(self) -> Result[None]:
        """
        Set "recording audio..." message.

        :return: None
        """

        return self._execute_command('markRecording')

    def mark_paused(self) -> Result[None]:
        """
        Unset "typing..." or "recording audio..." message.

        :return: None
        """

        return self._execute_command('markPaused')

    def can_archive(self) -> Result[bool]:
        """
        Check whether chat could be archived.

        :return: Whether chat could be archived.
        """

        return self._execute_command('canArchive')

    def can_send(self) -> Result[bool]:
        """
        Check whether current user could send message in chat.

        :return: Whether current user could send message in chat.
        """

        return self._execute_command('canSend')

    def can_pin(self) -> Result[bool]:
        """
        Check whether chat could be pinned.

        :return: Whether chat could be pinned.
        """

        return self._execute_command('canPin')

    def archive(self) -> Result[bool]:
        """
        Archive chat.

        :return: Operation result.
        """

        return self._execute_command('setArchive', {'archive': True})

    def unarchive(self) -> Result[bool]:
        """
        Unarchive chat.

        :return: Operation result.
        """

        return self._execute_command('setArchive', {'archive': False})

    def pin(self) -> Result[bool]:
        """
        Pin chat.

        :return: Operation result.
        """

        return self._execute_command('setPin', {'pin': True})

    def unpin(self) -> Result[bool]:
        """
        Unpin chat.

        :return: Operation result.
        """

        return self._execute_command('setPin', {'pin': False})

    def set_group_description(self, description) -> Result[bool]:
        """
        Set group description.

        :return: Operation result.
        """

        return self._execute_command('setGroupDesc', {'description': description})

    def star_messages(self, message_ids) -> Result[bool]:
        """
        Star messages.

        :return: Operation result.
        """

        return self._execute_command('sendStarMsgs', {'messageIds': message_ids})

    def unstar_messages(self, message_ids) -> Result[bool]:
        """
        Unstar messages.

        :return: Operation result.
        """

        return self._execute_command('sendUnstarMsgs', {'messageIds': message_ids})

    def send_not_spam(self) -> Result[bool]:
        """
        Send not spam report.

        :return: Operation result.
        """

        return self._execute_command('sendNotSpam')

    def send_spam_report(self) -> Result[bool]:
        """
        Send spam report.

        :return: Operation result.
        """

        return self._execute_command('sendSpamReport')

    from .live_location import LiveLocation

    def find_live_location(self) -> Result[LiveLocation]:
        """
        It find chat's live location. If it does not exist it will be created.

        :return: Live location.
        """
        from .live_location import LiveLocationManager
        return self._execute_command('findLiveLocation',
                                     result_class=LiveLocationManager.get_model_result_class())


class ChatCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = ChatManager

    def get_active(self) -> Result[Chat]:
        """
        Returns chat selected.

        :return: Chat object
        """
        return self._execute_command('getActive',
                                     result_class=self.get_item_result_class())

    def resync_messages(self) -> Result[None]:
        """
        Resynchronize messages.
        """
        return self._execute_command('resyncMessages')

    def ensure_chat_with_contact(self, contact_id: str) -> Result[Chat]:
        """
        Ensure there is a chat with a given contact. If it does not exist it will be created.

        :param contact_id: Contact's identifier.
        :return: Chat object
        """

        return self._execute_command('ensureChatWithContact',
                                     {'contactId': contact_id},
                                     result_class=self.get_item_result_class())

    def create_group(self, name: str, contact_ids: List[str],
                     picture: BytesIO = None, picture_preview: BytesIO = None) -> Result[Chat]:
        """
        Create a new chat group.

        :param name: Group's name
        :param contact_ids: List of contact identifier to invite.
        :param picture: JPG image.
        :return: Chat object.
        """
        params = {'name': name,
                  'contactIds': contact_ids}

        if picture:
            params['picture'] = b64encode(picture.read()).decode()

            if picture_preview:
                params['picturePreview'] = b64encode(picture_preview.read()).decode()

        return self._execute_command('createGroup', params)

    def forward_messages_to_chats(self, message_ids, chat_ids) -> Result[dict]:
        """
        Forward messages.

        :return: Operation result.
        """

        return self._execute_command('forwardMessagesToChats', {'messageIds': message_ids, 'chatIds': chat_ids})
