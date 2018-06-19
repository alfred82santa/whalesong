from dirty_models import BooleanField, DateTimeField, IntegerField, ModelField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from .contact import Contact
from .group_metadata import GroupMetadata
from ..models import BaseModel


class Chat(BaseModel):
    name = StringIdField()
    last_message_ts = DateTimeField(name='t')
    pin = IntegerField()
    unread_count = IntegerField()

    archive = BooleanField(default=False)
    change_number_new_jid = StringIdField()
    change_number_old_jid = StringIdField()
    contact = ModelField(model_class=Contact)
    group_metadata = ModelField(model_class=GroupMetadata)
    is_announce_grp_restrict = BooleanField(default=False)
    is_group = BooleanField(default=False)
    is_read_only = BooleanField(default=False)
    kind = StringIdField()

    last_received_key = StringIdField()
    modify_tag = StringIdField()
    mute_expiration = IntegerField()
    not_spam = BooleanField(default=False)


class ChatManager(BaseModelManager):

    MODEL_CLASS = Chat

    def get_messages(self):
        from .message import MessageCollectionManager
        return self._execute_command('getMessages',
                                     result_class=MessageCollectionManager.get_iterator_result_class())

    def send_text(self, text, quoted_msg_id=None, mentions=None, link_desc=None):
        params = {'text': text}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        if link_desc:
            params['linkDesc'] = link_desc

        return self._execute_command('sendText', params)

    def send_vcard(self, contact_name, vcard, quoted_msg_id=None):
        params = {'contactName': contact_name,
                  'vcard': vcard}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendVCardt', params)

    def send_media(self, media_data, caption=None, quoted_msg_id=None, mentions=None):
        params = {'mediaData': media_data}

        if caption:
            params['caption'] = caption

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        return self._execute_command('sendMedia', params)


class ChatCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = ChatManager

    def get_active(self):
        return self._execute_command('getActive')

    def resync_messages(self):
        return self._execute_command('resyncMessages')

    def get_chat_messages(self, chat_id):
        from .message import MessageCollectionManager
        return self._execute_command('getChatMessages',
                                     {'id': chat_id},
                                     result_class=MessageCollectionManager.get_iterator_result_class())

    def send_text_to_chat(self, chat_id, text, quoted_msg_id=None, mentions=None, link_desc=None):
        params = {'chatId': chat_id,
                  'text': text}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        if link_desc:
            params['linkDesc'] = link_desc

        return self._execute_command('sendTextToChat', params)

    def send_vcard_to_chat(self, chat_id, contact_name, vcard, quoted_msg_id=None):
        params = {'chatId': chat_id,
                  'contactName': contact_name,
                  'vcard': vcard}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendVCardToChat', params)

    def send_media_to_chat(self, chat_id, media_data, caption=None, quoted_msg_id=None, mentions=None):
        params = {'chatId': chat_id,
                  'mediaData': media_data}

        if caption:
            params['caption'] = caption

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        if mentions:
            params['mentions'] = mentions

        return self._execute_command('sendMediaToChat', params)
