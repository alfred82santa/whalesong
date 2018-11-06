from typing import Union

from . import BaseManager
from ..results import MonitorResult, Result


class StorageManager(BaseManager):
    """
    Local storage manager. It allows manage browser local storage.
    """

    def get_storage(self) -> Result:
        return self._execute_command('getStorage')

    def get_item(self, key: str) -> Result:
        return self._execute_command('getItem', {'key': key})

    def set_item(self, key: str, value: Union[str, int, float]) -> Result:
        return self._execute_command('setItem', {'key': key, 'value': value})

    def set_storage(self, data: dict) -> Result:
        return self._execute_command('setStorage', {'data': data})

    def monitor_storage(self) -> Result:
        return self._execute_command('monitorStorage', result_class=MonitorResult)

    def monitor_item_storage(self):
        return self._execute_command('monitorItemStorage', result_class=MonitorResult)
