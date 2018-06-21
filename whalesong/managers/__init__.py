from functools import partial

from ..driver import WhalesongDriver
from ..errors import ManagerNotFound
from ..models import BaseModel
from ..results import IteratorResult, MonitorResult, Result

COMMAND_SEPARATOR = '|'


class BaseManager:

    def __init__(self, driver: WhalesongDriver, manager_path=''):
        self._driver = driver
        self._manager_path = manager_path
        self._submanagers = {}

    def _build_command(self, command):
        if self._manager_path:
            return COMMAND_SEPARATOR.join([self._manager_path, command])
        return command

    def _execute_command(self, command, *args, **kwargs):
        return self._driver.execute_command(self._build_command(command), *args, **kwargs)

    def get_commands(self):
        return self._execute_command('getCommands')

    def add_submanager(self, name, submanager):
        self._submanagers[name] = submanager

    def remove_submanager(self, name):
        try:
            del self._submanagers[name]
        except KeyError:
            pass
        return self._execute_command('removeSubmanager', {'name': name})

    def get_submanager(self, name):
        try:
            return self._submanagers[name]
        except KeyError:
            raise ManagerNotFound('Manager {} not found'.format(name))

    def __getattr__(self, item):
        return self.get_submanager(item)

    def __getitem__(self, item):
        return self.get_submanager(item)


class BaseModelManager(BaseManager):
    MODEL_CLASS = BaseModel

    @classmethod
    def map_model(cls, data):
        return cls.MODEL_CLASS(data)

    @classmethod
    def get_model_result_class(cls):
        return partial(Result, fn_map=cls.map_model)

    @classmethod
    def get_monitor_result_class(cls):
        return partial(MonitorResult, fn_map=cls.map_model)

    async def get_model(self):
        return self.MODEL_CLASS(await self._execute_command('getModel'))

    def monitor_model(self):
        return self._execute_command('monitorModel',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field):
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=MonitorResult)


class BaseCollectionManager(BaseManager):
    MODEL_MANAGER_CLASS = BaseModelManager

    def get_items(self):
        return self._execute_command('getItems', result_class=self.get_iterator_result_class())

    @classmethod
    def get_monitor_result_class(cls):
        return partial(MonitorResult, fn_map=lambda evt: cls.MODEL_MANAGER_CLASS.map_model(evt['item']))

    @classmethod
    def get_iterator_result_class(cls):
        return partial(IteratorResult, fn_map=cls.MODEL_MANAGER_CLASS.map_model)

    @classmethod
    def get_item_result_class(cls):
        return cls.MODEL_MANAGER_CLASS.get_model_result_class()

    def get_length(self):
        return self._execute_command('getLength')

    def get_item_by_id(self, item_id):
        return self._execute_command('getItemById',
                                     {'id': item_id},
                                     result_class=self.get_item_result_class())

    def remove_item_by_id(self, item_id):
        return self._execute_command('removeItemById',
                                     {'id': item_id})

    def get_first(self):
        return self._execute_command('getFirst',
                                     result_class=self.get_item_result_class())

    def get_last(self):
        return self._execute_command('getLast',
                                     result_class=self.get_item_result_class())

    def monitor_add(self):
        return self._execute_command('monitorAdd',
                                     result_class=self.get_monitor_result_class())

    def monitor_remove(self):
        return self._execute_command('monitorRemove',
                                     result_class=self.get_monitor_result_class())

    def monitor_change(self):
        return self._execute_command('monitorChange',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field):
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=MonitorResult)

    def get_submanager(self, name):
        try:
            return super(BaseCollectionManager, self).get_submanager(name)
        except ManagerNotFound:
            return self.MODEL_MANAGER_CLASS(driver=self._driver,
                                            manager_path=self._build_command(name))
