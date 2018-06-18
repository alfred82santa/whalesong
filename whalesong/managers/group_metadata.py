from dirty_models import ArrayField, BooleanField, DateTimeField, ModelField, StringField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel


class Membership(BaseModel):
    is_admin = BooleanField(default=False)


class GroupMetadata(BaseModel):
    announce = StringIdField()
    creation = DateTimeField()
    desc = StringField()
    desc_owner = StringIdField()
    desc_time = DateTimeField()

    owner = StringIdField()
    participants = ArrayField(field_type=ModelField(model_class=Membership))
    restrict = StringIdField()


class GroupMetadataManager(BaseModelManager):
    MODEL_CLASS = GroupMetadata


class GroupMetadataCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = GroupMetadataManager
