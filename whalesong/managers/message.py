import binascii

from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dirty_models import ArrayField, BooleanField, DateTimeField, EnumField, FloatField, IntegerField, ModelField, \
    StringIdField
from enum import Enum
from io import BytesIO

from whalesong.models import Base64Field
from . import BaseCollectionManager, BaseModelManager
from .chat import Chat
from .contact import Contact
from ..models import BaseModel


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


class Ack(Enum):
    ERROR = -1
    PENDING = 0
    SERVER = 1
    DEVICE = 2
    READ = 3
    PLAYED = 4


class VCardItem(BaseModel):
    display_name = StringIdField()
    vcard = StringIdField()


class QuotedMessageMixin(BaseModel):
    quoted_msg_obj = ModelField()
    quoted_stanza_id = StringIdField(name='quotedStanzaID')
    quoted_participant = StringIdField()
    quoted_remote_jid = StringIdField()


class MentionsMixin(BaseModel):
    mentioned_jid_list = ArrayField(field_type=StringIdField())


class LinkContentMixin(BaseModel):
    matched_text = StringIdField()
    canonical_url = StringIdField()
    description = StringIdField()
    title = StringIdField()
    thumbnail = Base64Field()
    link_preview = BooleanField(default=False)

    links = ArrayField(field_type=StringIdField())


class MediaMixin(BaseModel):
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


class BaseMessage(BaseModel):
    type = EnumField(enum_class=MessageTypes)
    subtype = StringIdField()

    body = StringIdField()

    timestamp = DateTimeField(name='t')

    notify_name = StringIdField()
    from_ = StringIdField(name='from')
    to = StringIdField()
    author = StringIdField()
    sender = StringIdField()
    sender_obj = ModelField(model_class=Contact)

    self = StringIdField(default='in')
    ack = EnumField(enum_class=Ack)
    invis = BooleanField(default=False)
    is_new_msg = BooleanField(default=False)
    star = BooleanField(default=False)

    is_forwarded = BooleanField(default=False)

    links = ArrayField(field_type=StringIdField())

    chat = ModelField(model_class=Chat)

    is_group_msg = BooleanField(default=False)
    is_status_v3 = BooleanField(default=False)
    is_psa = BooleanField(default=False, name='isPSA')
    status_v3_text_bg = StringIdField()
    is_sent_by_me = BooleanField(default=False)
    is_notification = BooleanField(default=False)
    is_group_notification = BooleanField(default=False)
    is_biz_notification = BooleanField(default=False)
    is_media = BooleanField(default=False)
    is_link = BooleanField(default=False)
    has_link = BooleanField(default=False)
    is_doc = BooleanField(default=False)
    is_mms = BooleanField(default=False)
    is_revoked = BooleanField(default=False)
    show_forwarded = BooleanField(default=False)

    contains_emoji = BooleanField(default=False)
    is_failed = BooleanField(default=False)

    dir = StringIdField()
    rtl = BooleanField(default=False)

    is_persistent = BooleanField(default=False)
    is_user_created_type = BooleanField(default=False)


class TextMessage(QuotedMessageMixin, LinkContentMixin, MentionsMixin, BaseMessage):
    text_color = StringIdField()
    background_color = StringIdField()
    font = StringIdField()

    contains_emoji = BooleanField(default=False)


class ImageMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaFrameMixin, BaseMessage):
    pass


class VideoMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaFrameMixin, MediaStreamMixin, BaseMessage):
    pass


class AudioMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, MediaStreamMixin, BaseMessage):
    pass


class DocumentMessage(QuotedMessageMixin, MentionsMixin, MediaMixin, BaseMessage):
    body = Base64Field()
    page_count = IntegerField()


class VCardMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    pass


class MultiVCardMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    vcard_list = ArrayField(field_type=ModelField(model_class=VCardItem))


class LocationMessage(QuotedMessageMixin, MentionsMixin, BaseMessage):
    body = Base64Field()

    lat = FloatField()
    lng = FloatField()
    loc = StringIdField()
    is_live = BooleanField(default=False)
    accuracy = IntegerField()
    speed = IntegerField()
    degrees = FloatField()
    comment = StringIdField()
    sequence = IntegerField()
    share_duration = IntegerField()


class PaymentMessage(BaseMessage):
    pass


class NotificationMessage(BaseMessage):
    # group notifications
    recipients = ArrayField(field_type=StringIdField())
    broadcast = BooleanField(default=False)
    multicast = BooleanField(default=False)

    url_text = StringIdField()
    url_number = IntegerField()


CRYPT_KEYS = {MessageTypes.DOCUMENT: '576861747341707020446f63756d656e74204b657973',
              MessageTypes.IMAGE: '576861747341707020496d616765204b657973',
              MessageTypes.VIDEO: '576861747341707020566964656f204b657973',
              MessageTypes.PTT: '576861747341707020417564696f204b657973',
              MessageTypes.AUDIO: '576861747341707020417564696f204b657973'}


def message_factory(data):
    if data['type'] == MessageTypes.CHAT.value:
        return TextMessage(data)
    elif data['type'] in (MessageTypes.AUDIO.value, MessageTypes.PTT.value):
        return AudioMessage(data)
    elif data['type'] == MessageTypes.IMAGE.value:
        return ImageMessage(data)
    elif data['type'] == MessageTypes.VIDEO.value:
        return VideoMessage(data)
    elif data['type'] == MessageTypes.VCARD.value:
        return VCardMessage(data)
    elif data['type'] == MessageTypes.MULTI_VCARD.value:
        return MultiVCardMessage(data)
    elif data['type'] == MessageTypes.LOCATION.value:
        return LocationMessage(data)
    elif data['type'] == MessageTypes.DOCUMENT.value:
        return DocumentMessage(data)
    elif data['type'] == MessageTypes.PAYMENT.value:
        return PaymentMessage(data)
    else:
        return NotificationMessage(data)


class MessageManager(BaseModelManager):
    MODEL_CLASS = message_factory

    async def download_media(self):
        model = await self.get_model()

        return await download_media(self._driver, model)


class MessageCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = MessageManager

    def monitor_new(self):
        return self._execute_command('monitorNew', result_class=self.get_monitor_result_class())

    async def download_media(self, media_msg):
        return await download_media(self._driver, media_msg)


async def download_media(driver, model):
    file_data = (await driver.download_file(model.client_url)).read()

    media_key = b64decode(model.media_key)
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
