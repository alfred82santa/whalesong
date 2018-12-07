import binascii
from typing import Dict, Type, cast

from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dirty_models import ArrayField, BooleanField, DateTimeField, EnumField, FloatField, IntegerField, ModelField, \
    StringIdField, TimedeltaField
from dirty_models.models import CamelCaseMeta
from enum import Enum
from io import BytesIO

from . import BaseCollectionManager, BaseModelManager
from .chat import Chat
from .contact import Contact
from ..driver import BaseWhalesongDriver
from ..models import Base64Field, BaseModel
from ..results import MonitorResult, Result


class MessageTypes(Enum):
    NOTIFICATION_TEMPLATE = 'notification_template'
    GROUP_NOTIFICATION = 'group_notification'
    GP2 = 'gp2'
    BROADCAST_NOTIFICATION = 'broadcast_notification'
    E2E_NOTIFICATION = 'e2e_notification'
    CALL_LOG = 'call_log'
    PROTOCOL = 'protocol'
    CIPHERTEXT = 'ciphertext'
    REVOKED = 'revoked'
    UNKNOWN = 'unknown'

    CHAT = 'chat'  # thumbnail
    IMAGE = 'image'  # body as thumbnail
    VCARD = 'vcard'
    MULTI_VCARD = 'multi_vcard'
    LOCATION = 'location'  # body as thumbnail
    PAYMENT = 'payment'
    DOCUMENT = 'document'  # body as thumbnail
    AUDIO = 'audio'
    PTT = 'ptt'
    VIDEO = 'video'  # body as thumbnail
    STICKER = 'sticker'


class Ack(Enum):
    ERROR = -1
    PENDING = 0
    SERVER = 1
    DEVICE = 2
    READ = 3
    PLAYED = 4


class VCardItem(BaseModel):
    """
    vCard item.
    """

    display_name = StringIdField()
    """
    Contact's name.
    """

    vcard = StringIdField()
    """
    Serialized vCard object.
    """


class MessageMetaclass(CamelCaseMeta):
    """
    Message metaclass. It will build message model according to type.
    """

    __message_classes__: Dict[str, Type['BaseMessage']] = {}

    def __init__(cls, name, bases, classdict):
        super(MessageMetaclass, cls).__init__(name, bases, classdict)

        try:
            cls.__message_classes__[cls.__default_data__['type']] = cls
        except KeyError:
            pass

    def __call__(cls, data=None, *args, **kwargs):
        if 'type' in cls.__default_data__:
            return super(MessageMetaclass, cls).__call__(data=data, *args, **kwargs)

        try:
            t = data['type']
        except (TypeError, KeyError):
            try:
                t = kwargs['type']
            except KeyError:
                raise RuntimeError('Message with no type')

        try:
            return cls.__message_classes__[t](data=data, *args, **kwargs)
        except KeyError:
            try:
                return cls.__message_classes__[MessageTypes(t)](data=data, *args, **kwargs)
            except KeyError:
                return super(MessageMetaclass, cls).__call__(data=data, *args, **kwargs)


class BaseMessage(BaseModel, metaclass=MessageMetaclass):
    """
    Base message model.
    """

    type = EnumField(enum_class=MessageTypes, read_only=True)
    """
    Message type.
    """

    subtype = StringIdField()
    """
    Message subtype.
    """

    body = StringIdField()
    """
    Message content.
    """

    timestamp = DateTimeField(alias=['t'])
    """
    Message timestamp.
    """

    notify_name = StringIdField()
    """
    ¿?
    """

    from_ = StringIdField(name='from')
    """
    ¿?
    """

    to = StringIdField()
    """
    ¿?
    """

    author = StringIdField()
    """
    ¿?
    """

    sender = StringIdField()
    """
    Sender's contact identifier.
    """

    sender_obj = ModelField(model_class=Contact)
    """
    Sender's contact object.
    """

    self = StringIdField(default='in')
    """
    ¿?
    """

    ack = EnumField(enum_class=Ack)
    """
    Acknowledge state.
    """

    invis = BooleanField(default=False)
    """
    ¿?
    """

    is_new_msg = BooleanField(default=False)
    """
    Whether it is a new message or not.
    """

    star = BooleanField(default=False)
    """
    Whether it is starred or not.
    """

    is_forwarded = BooleanField(default=False)
    """
    Whether it is forwarded or not.
    """

    links = ArrayField(field_type=StringIdField())
    """
    List of links of message.
    """

    chat = ModelField(model_class=Chat)
    """
    Chat object where message was sent.
    """

    is_group_msg = BooleanField(default=False)
    """
    Whether it is a group message or not.
    """

    is_status_v3 = BooleanField(default=False)
    """
    ¿?
    """

    is_psa = BooleanField(default=False, name='isPSA')
    """
    ¿?
    """

    status_v3_text_bg = StringIdField()
    """
    ¿?
    """

    is_sent_by_me = BooleanField(default=False)
    """
    Whether it is was sent by current user.
    """

    is_notification = BooleanField(default=False)
    """
    Whether it is a notification or not.
    """

    is_group_notification = BooleanField(default=False)
    """
    Whether it is a group notification or not.
    """

    is_biz_notification = BooleanField(default=False)
    """
    ¿?
    """

    is_media = BooleanField(default=False)
    """
    Whether it is a media message or not.
    """

    is_link = BooleanField(default=False)
    """
    Whether it is a link message or not.
    """

    has_link = BooleanField(default=False)
    """
    Whether message's content has links or not.
    """

    is_doc = BooleanField(default=False)
    """
    Whether it is a document message (pdf) or not.
    """

    is_mms = BooleanField(default=False)
    """
    Whether it is a multimedia message or not.
    """

    is_revoked = BooleanField(default=False)
    """
    Whether it is revoked (deleted?) or not.
    """

    show_forwarded = BooleanField(default=False)
    """
    Whether forwarded label must be shown or not.
    """

    contains_emoji = BooleanField(default=False)
    """
    Whether message's content contains emojis or not.
    """

    is_failed = BooleanField(default=False)
    """
    Whether message sending failed or not.
    """

    dir = StringIdField()
    """
    ¿?
    """

    rtl = BooleanField(default=False)
    """
    Whether message's content is a right to left text.
    """

    is_persistent = BooleanField(default=False)
    """
    Whether it is persistent (¿?) or not.
    """

    is_user_created_type = BooleanField(default=False)
    """
    Whether it is a user created type message (¿?) or not.
    """

    has_promises = BooleanField(default=False)
    """
    Whether message still processing or not.
    """


class QuotedMessageMixin(BaseModel):
    quoted_msg_obj = ModelField(model_class=BaseMessage)
    """
    Original message object quoted.
    """

    quoted_stanza_id = StringIdField(name='quotedStanzaID')
    """
    Original message identifier quoted.
    """

    quoted_participant = StringIdField()
    """
    Sender identifier.
    """

    quoted_remote_jid = StringIdField()
    """
    Sender identifier. ¿?
    """


class MentionsMixin(BaseModel):
    mentioned_jid_list = ArrayField(field_type=StringIdField())
    """
    List of contact ids mentioned.
    """


class LinkContentMixin(BaseModel):
    matched_text = StringIdField()
    """
    Piece of text which match with link.
    """

    canonical_url = StringIdField()
    """
    Canonical url.
    """

    description = StringIdField()
    """
    Page description.
    """

    title = StringIdField()
    """
    Page title.
    """

    thumbnail = Base64Field()
    """
    Page thumbnail.
    """

    link_preview = BooleanField(default=False)
    """
    Whether there is a thumbnail or not.
    """

    links = ArrayField(field_type=StringIdField())
    """
    List of links. ¿?
    """


class MediaMixin(BaseModel):
    type = EnumField(enum_class=MessageTypes, read_only=True)

    client_url = StringIdField()
    direct_path = StringIdField()
    mimetype = StringIdField()
    caption = StringIdField()
    filehash = StringIdField()
    size = IntegerField()
    media_key = StringIdField()

    is_unsent_media = BooleanField(default=False)


class MediaFrameMixin(BaseModel):
    body = Base64Field()
    height = IntegerField()
    width = IntegerField()


class AuthorMixin(BaseModel):
    author = StringIdField()


class MediaStreamMixin(BaseModel):
    streamable = BooleanField(default=False)
    durantion = IntegerField()

    is_gif = BooleanField(default=False)
    gif_attribution = BooleanField(default=False)


class TextMessage(QuotedMessageMixin, LinkContentMixin, MentionsMixin, BaseMessage):
    """
    Text message.
    """

    __default_data__ = {'type': MessageTypes.CHAT}

    text_color = StringIdField()
    background_color = StringIdField()
    font = StringIdField()

    contains_emoji = BooleanField(default=False)


class ImageMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaFrameMixin, BaseMessage):
    """
    Image message.
    """

    __default_data__ = {'type': MessageTypes.IMAGE}


class VideoMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaFrameMixin, MediaStreamMixin, BaseMessage):
    """
    Video message.
    """

    __default_data__ = {'type': MessageTypes.VIDEO}


class AudioMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaStreamMixin, BaseMessage):
    """
    Audio message.
    """

    __default_data__ = {'type': MessageTypes.AUDIO}


class PTTMessage(AudioMessage):
    """
    Push to talk message.
    """

    __default_data__ = {'type': MessageTypes.PTT}


class DocumentMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, BaseMessage):
    """
    Document message.
    """
    __default_data__ = {'type': MessageTypes.DOCUMENT}

    body = Base64Field()
    page_count = IntegerField()


class VCardMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    """
    vCard message.
    """

    __default_data__ = {'type': MessageTypes.VCARD}


class MultiVCardMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    """
    Multi vCard message.
    """

    __default_data__ = {'type': MessageTypes.MULTI_VCARD}

    vcard_list = ArrayField(field_type=ModelField(model_class=VCardItem))


class LocationMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    """
    Location message.
    """

    __default_data__ = {'type': MessageTypes.LOCATION}

    body = Base64Field()

    is_live = BooleanField(default=False)

    lat = FloatField()
    lng = FloatField()

    loc = StringIdField()
    accuracy = IntegerField()
    speed = IntegerField()
    degrees = FloatField()
    comment = StringIdField()
    sequence = DateTimeField()
    share_duration = TimedeltaField()
    duration = TimedeltaField()

    text = StringIdField()

    final_thumbnail = Base64Field()
    final_lat = FloatField()
    final_lng = FloatField()
    final_accuracy = IntegerField()
    final_speed = IntegerField()
    final_degrees = FloatField()
    final_time_offset = TimedeltaField()


class PaymentMessage(BaseMessage):
    """
    Payment message.
    """
    __default_data__ = {'type': MessageTypes.PAYMENT}


class GroupNotificationMessage(BaseMessage):
    """
    Notification message.
    """
    __default_data__ = {'type': MessageTypes.GROUP_NOTIFICATION}

    # group notifications
    recipients = ArrayField(field_type=StringIdField())
    broadcast = BooleanField(default=False)
    multicast = BooleanField(default=False)

    url_text = StringIdField()
    url_number = IntegerField()


class StickerMessage(ImageMessage):
    """
    Sticker message.
    """

    __default_data__ = {'type': MessageTypes.STICKER}


CRYPT_KEYS = {MessageTypes.DOCUMENT: '576861747341707020446f63756d656e74204b657973',
              MessageTypes.IMAGE: '576861747341707020496d616765204b657973',
              MessageTypes.VIDEO: '576861747341707020566964656f204b657973',
              MessageTypes.PTT: '576861747341707020417564696f204b657973',
              MessageTypes.AUDIO: '576861747341707020417564696f204b657973',
              MessageTypes.STICKER: '576861747341707020496d616765204b657973'}


class MessageAck(BaseModel):
    """
    Message acknowledgement.
    """

    timestamp = DateTimeField(alias=['t'])
    """
    Ack timestamp.
    """


class MessageInfo(BaseModel):
    """
    Message information.
    """

    delivery = ArrayField(field_type=ModelField(model_class=MessageAck))
    """
    Delivery message acknowledgement list.
    """

    delivery_remaining = IntegerField(default=0)
    """
    Remaining delivery count.
    """

    is_ptt = BooleanField(default=False)
    """
    Whether it was a push to talk message.
    """

    played = ArrayField(field_type=ModelField(model_class=MessageAck))
    """
    Played message acknowledgement list.
    """

    played_remaining = IntegerField(default=0)
    """
    Remaining played count.
    """

    read = ArrayField(field_type=ModelField(model_class=MessageAck))
    """
    Read message acknowledgement list.
    """

    read_remaining = IntegerField(default=0)
    """
    Remaining read count.
    """


class MessageAckManager(BaseModelManager[MessageAck]):
    """
    Message acknowledgement object manager.
    """

    MODEL_CLASS = MessageAck


class MessageAckCollectionManager(BaseCollectionManager[MessageAckManager]):
    """
    Message acknowledgement collection manager.
    """

    MODEL_MANAGER_CLASS = MessageAckManager


class MessageInfoManager(BaseModelManager[MessageInfo]):
    """
    Message information object manager.

    .. attribute:: delivery

        :class:`~whalesong.managers.message.MessageAckCollectionManager`

        Message delivery acknowledgement collection manager.

    .. attribute:: read

        :class:`~whalesong.managers.message.MessageAckCollectionManager`

        Message read acknowledgement collection manager.

    .. attribute:: played

        :class:`~whalesong.managers.message.MessageAckCollectionManager`

        Message played acknowledgement collection manager.
    """

    MODEL_CLASS = MessageInfo

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(MessageInfoManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('delivery', MessageAckCollectionManager(driver=self._driver,
                                                                    manager_path=self._build_command('delivery')))

        self.add_submanager('read', MessageAckCollectionManager(driver=self._driver,
                                                                manager_path=self._build_command('read')))

        self.add_submanager('played', MessageAckCollectionManager(driver=self._driver,
                                                                  manager_path=self._build_command('played')))


class MessageManager(BaseModelManager[BaseMessage]):
    """
    Message object manager.

    .. attribute:: info

        :class:`~whalesong.managers.message.MessageInfoManager`

        Message information manager.
    """

    MODEL_CLASS = BaseMessage

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(MessageManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('info', MessageInfoManager(driver=self._driver,
                                                       manager_path=self._build_command('msgInfo')))

    async def download_media(self) -> BytesIO:
        """
        Download message's attached media file. It will decrypt media file using key on message object.

        :return: Media stream.
        """
        model = await self.get_model()

        return await download_media(self._driver, cast(MediaMixin, model))

    def fetch_info(self) -> Result[MessageInfo]:
        """
        Fetch message information. It must fetch before try to use message information manager.

        :return: Message information (:class:`~whalesong.managers.message.MessageInfo`)
        """
        return self._execute_command('fetchInfo', result_class=MessageInfoManager.get_model_result_class())

    def can_star(self) -> Result[bool]:
        """
        Check whether message could be starred.

        :return: Whether message could be starred.
        """
        return self._execute_command('canStar')

    def star(self) -> Result[bool]:
        """
        Star message.
        """
        return self._execute_command('star')

    def unstar(self) -> Result[bool]:
        """
        Unstar message.
        """
        return self._execute_command('unstar')

    def can_revoke(self) -> Result[bool]:
        """
        Check whether message could be revoked (deleted for other).

        :return: Whether message could be revoked.
        """
        return self._execute_command('canRevoke')

    def revoke(self, clear_media: bool = True) -> Result[str]:
        """
        Revoke message.
        """
        return self._execute_command('revoke', {'clearMedia': clear_media})


class MessageCollectionManager(BaseCollectionManager[MessageManager]):
    """
    Message collection manager.
    """

    MODEL_MANAGER_CLASS = MessageManager

    def monitor_new(self) -> MonitorResult[BaseMessage]:
        """
        Monitor new messages.

        :return: New message monitor.
        """

        return self._execute_command('monitorNew', result_class=self.get_monitor_result_class())

    async def download_media(self, model: MediaMixin) -> BytesIO:
        """
        Download message's attached media file. It will decrypt media file using key on message object.

        :param model: MediaMixin
        :return: Media stream.
        """
        return await download_media(self._driver, model)


async def download_media(driver: BaseWhalesongDriver, model: MediaMixin) -> BytesIO:
    """
    Download message's attached media file. It will decrypt media file using key on message object.

    :param driver:
    :param model: MediaMixin
    :return: Media stream.
    """
    file_data = (await driver.download_file(model.client_url)).read()

    try:
        media_key = b64decode(model.media_key)
    except Exception:
        media_key = b64decode(model.media_key + ('=' * (len(model.media_key) % 3)))

    try:
        derivative = HKDFv3().deriveSecrets(media_key,
                                            binascii.unhexlify(CRYPT_KEYS[model.type]),
                                            112)
    except KeyError:
        raise ValueError('Invalid message type')

    parts = ByteUtil.split(derivative, 16, 32)
    iv = parts[0]
    cipher_key = parts[1]
    e_file = file_data[:-10]

    cr_obj = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
    decryptor = cr_obj.decryptor()
    return BytesIO(decryptor.update(e_file) + decryptor.finalize())
