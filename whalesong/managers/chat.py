from base64 import b64encode
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


class MsgLoadState(BaseModel):
    context_loaded = BooleanField(default=False)
    is_loading_around_msgs = BooleanField(default=False)
    is_loading_earlier_msgs = BooleanField(default=False)
    is_loading_recent_msgs = BooleanField(default=False)
    no_earlier_msgs = BooleanField(default=False)


class MsgLoadStateManager(BaseModelManager):
    MODEL_CLASS = MsgLoadState


class ChatManager(BaseModelManager):
    MODEL_CLASS = Chat

    def __init__(self, driver, manager_path=''):
        super(ChatManager, self).__init__(driver=driver, manager_path=manager_path)

        from .message import MessageCollectionManager
        self.add_submanager('msgs', MessageCollectionManager(driver=self._driver,
                                                             manager_path=self._build_command('msgs')))

        self.add_submanager('msg_load_state', MsgLoadStateManager(driver=self._driver,
                                                                  manager_path=self._build_command('msgLoadState')))

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
                  'vcard': vcard.serialize()}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendVCard', params)

    def send_media(self, media_data, content_type=None, filename=None, caption=None,
                   quoted_msg_id=None, mentions=None):
        params = {'mediaData': b64encode(media_data.read()).decode()}

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

    def send_seen(self):
        return self._execute_command('sendSeen')

    def load_earlier_messages(self):
        return self._execute_command('loadEarlierMessages')

    def load_all_earlier_messages(self):
        return self._execute_command('loadAllEarlierMessages')


class ChatCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = ChatManager

    def get_active(self):
        return self._execute_command('getActive')

    def resync_messages(self):
        return self._execute_command('resyncMessages')
