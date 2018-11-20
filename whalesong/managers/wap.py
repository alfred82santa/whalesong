from dirty_models import FastDynamicModel

from . import BaseModelManager
from ..results import Result


# from ..models import BaseModel


class Wap(FastDynamicModel):
    pass


class WapManager(BaseModelManager[Wap]):
    """
    Entry point to request data to phone.
    """

    MODEL_CLASS = Wap

    def query_exist(self, contact_id: str) -> Result[bool]:
        """
        Check whether a contact identifier exists on Whatsapp or not.

        :param contact_id: Contact identifier
        :return: Bool
        """
        return self._execute_command('queryExist', {'contactId': contact_id})
