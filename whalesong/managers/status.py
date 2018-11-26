from dirty_models import StringIdField

from . import BaseCollectionManager, BaseModelManager
from ..models import BaseModel
from ..results import Result


class Status(BaseModel):
    status = StringIdField()
    """
    Contact status.
    """


class StatusManager(BaseModelManager[Status]):
    """
    Status manager.
    """

    MODEL_CLASS = Status


class StatusCollectionManager(BaseCollectionManager[StatusManager]):
    """
    Status collection manager.
    """

    MODEL_MANAGER_CLASS = StatusManager

    def set_my_status(self, new_status: str = None) -> Result[bool]:
        """
        Set current user status.

        :return: Operation result.
        """

        return self._execute_command('setMyStatus', {'status': new_status or ''})
