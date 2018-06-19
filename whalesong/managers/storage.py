from . import BaseManager
from ..results import MonitorResult


class StorageManager(BaseManager):

    def get_storage(self):
        return self._execute_command('getStorage')

    def get_item(self, key):
        return self._execute_command('getItem', {'key': key})

    def set_item(self, key, value):
        return self._execute_command('setItem', {'key': key, 'value': value})

    def set_storage(self, data):
        return self._execute_command('setStorage', {'data': data})

    def monitor_storage(self):
        return self._execute_command('monitorStorage', result_class=MonitorResult)

    def monitor_item_storage(self):
        return self._execute_command('monitorItemStorage', result_class=MonitorResult)
