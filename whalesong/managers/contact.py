from dirty_models import ArrayField, BooleanField, ModelField, StringIdField
from vobject import vCard

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel


class ProfilePicture(BaseModel):
    id = StringIdField()
    eurl = StringIdField()
    raw = StringIdField()
    tag = StringIdField()


class Contact(BaseModel):
    name = StringIdField()
    formatted_name = StringIdField()
    pushname = StringIdField()
    short_name = StringIdField()
    type = StringIdField()
    userhash = StringIdField()
    userid = StringIdField()
    verified_level = StringIdField()
    verified_name = StringIdField()

    profile_pic_thumb_obj = ModelField(model_class=ProfilePicture)

    is_user = BooleanField(default=True)
    is_business = BooleanField(default=False)
    is_contact_blocked = BooleanField(default=False)
    is_enterprise = BooleanField(default=False)
    is_high_level_verified = BooleanField(default=False)
    is_me = BooleanField(default=False)
    is_my_contact = BooleanField(default=True)
    is_psa = BooleanField(default=False, name='isPSA')
    is_verified = BooleanField(default=False)
    is_wa_contact = BooleanField(default=True, name='isWAContact')
    plaintext_disabled = BooleanField(default=False)
    status_mute = BooleanField(default=False)

    section_header = StringIdField()

    labels = ArrayField(field_type=StringIdField(), default=[])

    def to_vcard(self):
        vc = vCard()
        o = vc.add('fn')
        o.value = self.formatted_name

        o = vc.add('tel')
        o.type_param = "cell"
        o.value = '+' + self.id[:self.id.index('@')]

        return vc


class ContactManager(BaseModelManager):
    MODEL_CLASS = Contact


class ContactCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = ContactManager

    def resync_contacts(self):
        return self._execute_command('resyncContacts')

    def get_me(self):
        return self._execute_command('getMe')
