from functools import partial

from ..driver import WhalesongDriver
from ..errors import ManagerNotFound
from ..models import BaseModel
from ..results import IteratorResult, MonitorResult, Result

COMMAND_SEPARATOR = '|'


class BaseManager:
    """
    Base manager.
    """

    def __init__(self, driver: WhalesongDriver, manager_path: str = ''):
        """

        :param driver: Whalesong driver
        :param manager_path: Manager prefix path.
        """
        self._driver = driver
        self._manager_path = manager_path
        self._submanagers = {}

    def _build_command(self, command):
        if self._manager_path:
            return COMMAND_SEPARATOR.join([self._manager_path, command])
        return command

    def _execute_command(self, command, *args, **kwargs):
        return self._driver.execute_command(self._build_command(command), *args, **kwargs)

    def get_commands(self) -> Result:
        """
        Get manager available static commands.

        :return: Manager static commands.
        """
        return self._execute_command('getCommands')

    def add_submanager(self, name: str, submanager: 'BaseManager'):
        """
        Add a submanager.

        :param name: Field where manager will be stored.
        :param submanager: Submanager
        """
        self._submanagers[name] = submanager

    def remove_submanager(self, name: str) -> Result:
        """
        Remove a submanager.

        :param name: Field where submanager was stored.
        """
        try:
            del self._submanagers[name]
        except KeyError:
            pass
        return self._execute_command('removeSubmanager', {'name': name})

    def get_submanager(self, name):
        """
        Get a submanager.

        :param name: Field where submanager was stored.
        """
        try:
            return self._submanagers[name]
        except KeyError:
            raise ManagerNotFound('Manager {} not found'.format(name))

    def __getattr__(self, item):
        return self.get_submanager(item)

    def __getitem__(self, item):
        return self.get_submanager(item)


class BaseModelManager(BaseManager):
    """
    Base model manager.
    """

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

    async def get_model(self) -> Result:
        """
        Get model object

        :return: Model object
        """
        return self.MODEL_CLASS(await self._execute_command('getModel'))

    def monitor_model(self) -> MonitorResult:
        """
        Monitor any change on model.

        :return: Model monitor
        """
        return self._execute_command('monitorModel',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field: str) -> MonitorResult:
        """
        Monitor any change on a model's field.

        :param field: Field to monitor.
        :return: Model monitor
        """
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=MonitorResult)


class BaseCollectionManager(BaseManager):
    """
    Base collection manager.
    """

    MODEL_MANAGER_CLASS = BaseModelManager

    def get_items(self) -> IteratorResult:
        """
        Get all items on collection.

        :return: Async iterator
        """
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

    def get_length(self) -> Result:
        """
        Get collection items count.

        :return: Items count
        """
        return self._execute_command('getLength')

    def get_item_by_id(self, item_id: str) -> Result:
        """
        Get model by identifier.

        :param item_id: Model identifier.
        :return: Model object.
        """
        return self._execute_command('getItemById',
                                     {'id': item_id},
                                     result_class=self.get_item_result_class())

    def remove_item_by_id(self, item_id: str) -> Result:
        """
        Remove item by identifier.

        :param item_id: Model identifier.
        """
        return self._execute_command('removeItemById',
                                     {'id': item_id})

    def get_first(self) -> Result:
        """
        Get first item in collection.

        :return: Model object.
        """
        return self._execute_command('getFirst',
                                     result_class=self.get_item_result_class())

    def get_last(self) -> Result:
        """
        Get last item in collection.

        :return: Model object.
        """
        return self._execute_command('getLast',
                                     result_class=self.get_item_result_class())

    def monitor_add(self) -> MonitorResult:
        """
        Monitor add item collection. Iterate each time a item is added to collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorAdd',
                                     result_class=self.get_monitor_result_class())

    def monitor_remove(self) -> MonitorResult:
        """
        Monitor remove item collection. Iterate each time a item is removed from collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorRemove',
                                     result_class=self.get_monitor_result_class())

    def monitor_change(self) -> MonitorResult:
        """
        Monitor change item collection. Iterate each time a item change in collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorChange',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field) -> MonitorResult:
        """
        Monitor item's field change. Iterate each time a field changed in any item of collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=MonitorResult)

    def get_submanager(self, name) -> BaseManager:
        try:
            return super(BaseCollectionManager, self).get_submanager(name)
        except ManagerNotFound:
            return self.MODEL_MANAGER_CLASS(driver=self._driver,
                                            manager_path=self._build_command(name))
