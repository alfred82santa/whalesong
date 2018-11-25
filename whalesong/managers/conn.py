from dirty_models import ArrayField, BooleanField, IntegerField, ModelField, StringIdField

from ..results import Result
from . import BaseModelManager
from ..models import BaseModel


class PhoneDescription(BaseModel):
    whatsapp_version = StringIdField(alias=['wa_version'])
    """
    Whatsapp version running on phone.
    """

    mcc = StringIdField()
    """
    ¿?
    """

    mnc = StringIdField()
    """
    ¿?
    """

    os_version = StringIdField()
    """
    Operating system version running on phone.
    """

    device_manufacturer = StringIdField()
    """
    Phone manufacturer.
    """

    device_model = StringIdField()
    """
    Phone model.
    """

    os_build_number = StringIdField()
    """
    Operating system build nummber running on phone.
    """


class Conn(BaseModel):
    ref = StringIdField()
    """
    Client token reference. Used on QR.
    """

    refTTL = IntegerField()
    """
    Ref time to live
    """

    whatsapp_id = StringIdField(alias=['wid'])
    """
    Whatsapp user identifier.
    """

    connected = BooleanField()
    """
    Whether is connected or not.
    """

    me = StringIdField()
    """
    Whatsapp user identifier.
    """

    proto_version = ArrayField(field_type=IntegerField())
    """
    Protocol version.
    """

    client_token = StringIdField()
    """
    Client token.
    """

    server_token = StringIdField()
    """
    Server token.
    """

    is_response = BooleanField()
    """
    ¿?
    """

    battery = IntegerField()
    """
    Phone battery level, in percentage. 
    """

    plugged = BooleanField()
    """
    Whether phone is plugged to charger or not.
    """

    locale = StringIdField(alias=['lc'])
    """
    Phone locale.
    """

    language = StringIdField(alias=['lg'])
    """
    Phone language.
    """

    locales = StringIdField()
    """
    Phone locale-language.
    """

    is_24h = BooleanField(alias=['is24h'])
    """
    Whether time must be in 24h format. 
    """

    platform = StringIdField()
    """
    Platform (android, iphone, wp7, etc...)
    """

    phone = ModelField(model_class=PhoneDescription)
    """
    Phone description.
    """

    tos = IntegerField()
    """
    ¿?
    """

    smb_tos = IntegerField()
    """
    ¿?
    """

    pushname = StringIdField()
    """
    Current user's push name.
    """


class ConnManager(BaseModelManager[Conn]):
    MODEL_CLASS = Conn

    def update_pushname(self, name: str) -> Result[None]:
        """
        Update user's push name.

        :param name: New push name
        """
        return self._execute_command('updatePushname', {'name': name})

    def can_update_pushname(self) -> Result[bool]:
        """
        Whether it is possible to update push name or not.

        :return: Whether it is possible to update push name or not.
        """
        return self._execute_command('canUpdatePushname')
