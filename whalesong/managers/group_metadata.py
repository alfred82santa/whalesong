from typing import List

from dirty_models import ArrayField, BooleanField, DateTimeField, ModelField, StringField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel
from ..results import Result


class Participant(BaseModel):
    is_admin = BooleanField(default=False)
    """
    Whether the participant is a group administrator or not.
    """

    is_super_admin = BooleanField()
    """
    Whether the participant is a group super administrator or not. ¿?
    """


class GroupMetadata(BaseModel):
    """
    Group metadata model.
    """

    announce = StringIdField()
    """
    ¿?
    """

    creation = DateTimeField()
    """
    Group creation timestamp.
    """

    desc = StringField()
    """
    Group description.
    """

    desc_owner = StringIdField()
    """
    Who change last group description.
    """

    desc_time = DateTimeField()
    """
    When last group description was changed.
    """

    owner = StringIdField()
    """
    Who made group.
    """

    participants = ArrayField(field_type=ModelField(model_class=Participant))
    """
    List of participants.
    """

    restrict = StringIdField()
    """
    ¿?
    """

    group_invite_link = StringIdField()
    """
    Group link to invite people.
    """

    invite_code = StringIdField()
    """
    Group code to invite people.
    """


class ParticipantManager(BaseModelManager[Participant]):
    """
    Participant manager.
    """

    MODEL_CLASS = Participant


class ParticipantCollectionManager(BaseCollectionManager[ParticipantManager]):
    """
    Participant collection manager. It allows manage group participants.
    """

    MODEL_MANAGER_CLASS = ParticipantManager

    def add_participants(self, contact_ids: List[str]) -> Result[None]:
        return self._execute_command('addParticipants', {'contactIds': contact_ids})

    def can_add(self, contact_id: str) -> Result[bool]:
        return self._execute_command('canAdd', {'contactId': contact_id})

    def remove_participants(self, contact_ids: List[str]) -> Result[None]:
        return self._execute_command('removeParticipants', {'contactIds': contact_ids})

    def can_remove(self, contact_id: str) -> Result[bool]:
        return self._execute_command('canRemove', {'contactId': contact_id})

    def promote_participants(self, contact_ids: List[str]) -> Result[None]:
        return self._execute_command('promoteParticipants', {'contactIds': contact_ids})

    def can_promote(self, contact_id: str) -> Result[bool]:
        return self._execute_command('canPromote', {'contactId': contact_id})

    def demote_participants(self, contact_ids: List[str]) -> Result[None]:
        return self._execute_command('demoteParticipants', {'contactIds': contact_ids})

    def can_demote(self, contact_id: str) -> Result[bool]:
        return self._execute_command('canDemote', {'contactId': contact_id})


class GroupMetadataManager(BaseModelManager[GroupMetadata]):
    """
    Group metadata manager. It allows manage groups, further than a chat.

    .. attribute:: participants

        :class:`~whalesong.managers.group_metadata.ParticipantCollectionManager`

        Group's participants collection manager.
    """

    MODEL_CLASS = GroupMetadata

    def __init__(self, driver, manager_path=''):
        super(GroupMetadataManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('participants', ParticipantCollectionManager(
            driver=self._driver,
            manager_path=self._build_command('participants')
        ))

    def group_invite_code(self) -> Result[None]:
        return self._execute_command('groupInviteCode')

    def revoke_group_invite(self) -> Result[None]:
        return self._execute_command('revokeGroupInvite')


class GroupMetadataCollectionManager(BaseCollectionManager[GroupMetadataManager]):
    MODEL_MANAGER_CLASS = GroupMetadataManager
