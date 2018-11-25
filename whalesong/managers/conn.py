from dirty_models import ArrayField, BooleanField, IntegerField, ModelField, StringIdField

from ..results import Result
from . import BaseModelManager
from ..models import BaseModel


class PhoneDescription(BaseModel):
    whatsapp_version = StringIdField(alias=['wa_version'])
    mcc = StringIdField()
    mnc = StringIdField()
    os_version = StringIdField()
    device_manufacturer = StringIdField()
    device_model = StringIdField()
    os_build_number = StringIdField()


class Conn(BaseModel):
    ref = StringIdField()
    refTTL = IntegerField()
    whatsapp_id = StringIdField(alias=['wid'])
    connected = BooleanField()
    me = StringIdField()
    proto_version = ArrayField(field_type=IntegerField())
    client_token = StringIdField()
    server_token = StringIdField()
    is_response = BooleanField()
    battery = IntegerField()
    plugged = BooleanField()
    locale = StringIdField(alias=['lc'])
    language = StringIdField(alias=['lg'])
    locales = StringIdField()
    is_24h = BooleanField(alias=['is24h'])
    platform = StringIdField()
    phone = ModelField(model_class=PhoneDescription)
    tos = IntegerField()
    smb_tos = IntegerField()
    pushname = StringIdField()


class ConnManager(BaseModelManager[Conn]):
    MODEL_CLASS = Conn

    def update_pushname(self, name: str) -> Result[None]:
        return self._execute_command('updatePushname', {'name': name})

    def can_update_pushname(self) -> Result[bool]:
        return self._execute_command('canUpdatePushname')
