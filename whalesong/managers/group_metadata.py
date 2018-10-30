from dirty_models import ArrayField, BooleanField, DateTimeField, ModelField, StringField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel


class Participant(BaseModel):
    is_admin = BooleanField(default=False)
    is_super_admin = BooleanField()


class GroupMetadata(BaseModel):
    announce = StringIdField()
    creation = DateTimeField()
    desc = StringField()
    desc_owner = StringIdField()
    desc_time = DateTimeField()

    owner = StringIdField()
    participants = ArrayField(field_type=ModelField(model_class=Participant))
    restrict = StringIdField()

    group_invite_link = StringIdField()
    invite_code = StringIdField()


class ParticipantManager(BaseModelManager):
    MODEL_CLASS = Participant


class ParticipantCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = ParticipantManager

    def add_participants(self, contact_ids):
        return self._execute_command('addParticipants', {'contactIds': contact_ids})

    def can_add(self, contact_id):
        return self._execute_command('canAdd', {'contactId': contact_id})

    def remove_participants(self, contact_ids):
        return self._execute_command('removeParticipants', {'contactIds': contact_ids})

    def can_remove(self, contact_id):
        return self._execute_command('canRemove', {'contactId': contact_id})

    def promote_participants(self, contact_ids):
        return self._execute_command('promoteParticipants', {'contactIds': contact_ids})

    def can_promote(self, contact_id):
        return self._execute_command('canPromote', {'contactId': contact_id})

    def demote_participants(self, contact_ids):
        return self._execute_command('demoteParticipants', {'contactIds': contact_ids})

    def can_demote(self, contact_id):
        return self._execute_command('canDemote', {'contactId': contact_id})


class GroupMetadataManager(BaseModelManager):
    MODEL_CLASS = GroupMetadata

    def __init__(self, driver, manager_path=''):
        super(GroupMetadataManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('participants', ParticipantCollectionManager(
            driver=self._driver,
            manager_path=self._build_command('participants')
        ))

    def group_invite_code(self):
        return self._execute_command('groupInviteCode')

    def revoke_group_invite(self):
        return self._execute_command('revokeGroupInvite')


class GroupMetadataCollectionManager(BaseCollectionManager):
    MODEL_MANAGER_CLASS = GroupMetadataManager
