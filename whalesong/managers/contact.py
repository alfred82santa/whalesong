from dirty_models import ArrayField, BooleanField, ModelField, StringIdField
from vobject import vCard

from . import BaseCollectionManager, BaseModelManager
from .profile_pic_thumb import ProfilePicture, ProfilePictureManager
from .status import Status
from .. import BaseWhalesongDriver
from ..models import BaseModel
from ..results import Result


class Contact(BaseModel):
    name = StringIdField()
    """
    Contact name. It will be name on phone contact list.
    """

    formatted_name = StringIdField()
    """
    Contact's formatted name.
    """

    pushname = StringIdField()
    """
    Contact defined name. It is set by contact on its whatsapp application. 
    """

    short_name = StringIdField()
    """
    Short form of contact's name.
    """

    type = StringIdField()
    """
    ¿?
    """

    userhash = StringIdField()
    """
    ¿?
    """

    userid = StringIdField()
    """
    User identifier. It used to be the phone number.
    """

    verified_level = StringIdField()
    """
    Something about business accounts.
    """

    verified_name = StringIdField()
    """
    Verified contact's name for business.
    """

    profile_pic_thumb_obj = ModelField(model_class=ProfilePicture)
    """
    Contact picture.
    """

    status = ModelField(model_class=Status)
    """
    Contact status.
    """

    is_user = BooleanField(default=True)
    """
    Whether contact is a user or not.
    """

    is_business = BooleanField(default=False)
    """
    Whether contact is a business or not.
    """

    is_contact_blocked = BooleanField(default=False)
    """
    Whether contact has been blocked or not.
    """

    is_enterprise = BooleanField(default=False)
    """
    Whether contact is an enterprise or not.
    """

    is_high_level_verified = BooleanField(default=False)
    """
    Whether contact is verified as enterprise or not.
    """

    is_me = BooleanField(default=False)
    """
    Whether contact is the current user or not.
    """

    is_my_contact = BooleanField(default=True)
    """
    Whether contact is in phone's contact list or not.
    """

    is_psa = BooleanField(default=False, name='isPSA')
    """
    ¿?
    """

    is_verified = BooleanField(default=False)
    """
    Whether contact is verified or not.
    """

    is_wa_contact = BooleanField(default=True, name='isWAContact')
    """
    Whether contact is a whatsapp user or not.
    """

    plaintext_disabled = BooleanField(default=False)
    """
    Whether contact has disabled plain text or not.
    """

    status_mute = BooleanField(default=False)
    """
    Whether contact is muted or not.
    """

    section_header = StringIdField()
    """
    ¿?
    """

    labels = ArrayField(field_type=StringIdField(), default=[])
    """
    List of contact labels ¿?
    """

    def to_vcard(self) -> vCard:
        """
        Build vCard from contact.

        :return: vCard object of contact
        """
        vc = vCard()
        o = vc.add('fn')
        o.value = self.formatted_name

        o = vc.add('tel')
        o.type_param = "cell"
        o.value = '+' + self.id[:self.id.index('@')]

        return vc


class ContactManager(BaseModelManager[Contact]):
    """
    Contact manager. It allows manage a contact.

    .. attribute:: profile_pic_thumb

        :class:`~whalesong.managers.profile_pic_thumb.ProfilePictureManager`

        Contact's picture thumb manager.
    """

    MODEL_CLASS = Contact

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(ContactManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('profile_pic_thumb', ProfilePictureManager(
            driver=self._driver,
            manager_path=self._build_command('profilePicThumb')
        ))

    def block(self) -> Result[None]:
        """
        Block contact.
        """

        return self._execute_command('block')

    def unblock(self) -> Result[None]:
        """
        Unblock contact.
        """

        return self._execute_command('unblock')


class ContactCollectionManager(BaseCollectionManager[ContactManager]):
    """
    Contact collection manager. It allows manage contact collection.
    """

    MODEL_MANAGER_CLASS = ContactManager

    def resync_contacts(self) -> Result[None]:
        return self._execute_command('resyncContacts')

    def get_me(self) -> Result[Contact]:
        return self._execute_command('getMe')
