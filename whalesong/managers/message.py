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

from . import BaseCollectionManager, BaseModelManager
from .chat import Chat
from .contact import Contact
from ..models import BaseModel


class MessageTypes(Enum):
    CHAT = 'chat'
    IMAGE = 'image'
    VCARD = 'vcard'
    MULTI_VCARD = 'multi_vcard'
    LOCATION = 'location'
    PAYMENT = 'payment'
    DOCUMENT = 'document'
    AUDIO = 'audio'
    PTT = 'ptt'
    VIDEO = 'video'


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

    client_url = StringIdField()
    direct_path = StringIdField()
    mimetype = StringIdField()
    caption = StringIdField()
    filehash = StringIdField()
    size = IntegerField()
    height = IntegerField()
    width = IntegerField()
    media_key = StringIdField()

    vcard_list = ArrayField(field_type=ModelField(model_class=VCardItem))

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

    matched_text = StringIdField()
    canonical_url = StringIdField()
    description = StringIdField()
    title = StringIdField()
    thumbnail = StringIdField()
    text_color = StringIdField()
    background_color = StringIdField()
    font = StringIdField()

    page_count = IntegerField()

    streaming_sidecar = BooleanField(default=False)
    streamable = BooleanField(default=False)
    durantion = IntegerField()

    is_gif = BooleanField(default=False)
    gif_attribution = BooleanField(default=False)

    quoted_msg_obj = ModelField()

    quoted_stanza_id = StringIdField(name='quotedStanzaID')
    quoted_participant = StringIdField()
    quoted_remote_jid = StringIdField()
    mentioned_jid_list = ArrayField(field_type=StringIdField())

    is_forwarded = BooleanField(default=False)

    recipients = ArrayField(field_type=StringIdField())
    broadcast = BooleanField(default=False)
    multicast = BooleanField(default=False)

    url_text = StringIdField()
    url_number = IntegerField()

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

    vcard = ModelField(model_class=VCardItem)

    is_unsent_media = BooleanField(default=False)
    dir = StringIdField()
    rtl = BooleanField(default=False)

    link_preview = BooleanField(default=False)
    is_persistent = BooleanField(default=False)
    is_user_created_type = BooleanField(default=False)


CRYPT_KEYS = {'document': '576861747341707020446f63756d656e74204b657973',
              'image': '576861747341707020496d616765204b657973',
              'video': '576861747341707020566964656f204b657973',
              'ptt': '576861747341707020417564696f204b657973',
              'audio': '576861747341707020417564696f204b657973'}


class MessageManager(BaseModelManager):
    MODEL_CLASS = BaseMessage


class MessageCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = MessageManager

    def monitor_new(self):
        return self._execute_command('monitorNew', result_class=self.get_monitor_result_class())

    async def download_media(self, media_msg, force_download=False):
        if not force_download:
            try:
                if media_msg.content:
                    return BytesIO(b64decode(media_msg.body))
            except AttributeError:
                pass

        file_data = await self._driver.download_file(media_msg.client_url)

        media_key = b64decode(media_msg.media_key)
        derivative = HKDFv3().deriveSecrets(media_key,
                                            binascii.unhexlify(CRYPT_KEYS[media_msg.type]),
                                            112)

        parts = ByteUtil.split(derivative, 16, 32)
        iv = parts[0]
        cipher_key = parts[1]
        e_file = file_data[:-10]

        cr_obj = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
        decryptor = cr_obj.decryptor()
        return BytesIO(decryptor.update(e_file) + decryptor.finalize())
