from typing import Any, ClassVar, Dict, Generic, List, Type, TypeVar, Union, cast

from functools import partial

from ..driver import BaseWhalesongDriver
from ..errors import ManagerNotFound
from ..models import BaseModel
from ..results import IteratorResult, MonitorResult, Result

COMMAND_SEPARATOR = '|'


class BaseManager:
    """
    Base manager.
    """

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        """

        :param driver: Whalesong driver
        :param manager_path: Manager prefix path.
        """
        self._driver = driver
        self._manager_path = manager_path
        self._submanagers: Dict[str, 'BaseManager'] = {}

    def _build_command(self, command):
        if self._manager_path:
            return COMMAND_SEPARATOR.join([self._manager_path, command])
        return command

    def _execute_command(self, command, *args, **kwargs):
        return self._driver.execute_command(self._build_command(command), *args, **kwargs)

    def get_commands(self) -> Result[List[str]]:
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

    def get_submanager(self, name: str) -> 'BaseManager':
        """
        Get a submanager.

        :param name: Field where submanager was stored.
        """
        try:
            return self._submanagers[name]
        except KeyError:
            raise ManagerNotFound('Manager {} not found'.format(name))

    __getattr__ = get_submanager

    __getitem__ = get_submanager


MODEL_TYPE = TypeVar('MODEL_TYPE', bound=BaseModel, covariant=True)


class BaseModelManager(BaseManager, Generic[MODEL_TYPE]):
    """
    Base model manager.
    """

    MODEL_CLASS: ClassVar[Type[BaseModel]]

    @classmethod
    def map_model(cls, data) -> MODEL_TYPE:
        return cls.MODEL_CLASS(data)

    @classmethod
    def get_model_result_class(cls) -> Result[MODEL_TYPE]:
        return cast(Result[MODEL_TYPE], partial(Result, fn_map=cls.map_model))

    @classmethod
    def get_monitor_result_class(cls) -> MonitorResult[MODEL_TYPE]:
        return cast(MonitorResult[MODEL_TYPE], partial(MonitorResult, fn_map=cls.map_model))

    @classmethod
    def get_field_monitor_result_class(cls, field) -> MonitorResult[Dict[str, Any]]:
        def map(evt):
            if evt['value'] is not None:
                field_obj = cls.MODEL_CLASS.get_field_obj(field)
                try:
                    evt['value'] = field_obj.use_value(evt['value'])
                except (ValueError, TypeError):
                    pass

            return evt

        return cast(MonitorResult[Dict[str, Any]], partial(MonitorResult, fn_map=map))

    def get_model(self) -> Result[MODEL_TYPE]:
        """
        Get model object

        :return: Model object
        """
        return self._execute_command('getModel',
                                     result_class=self.get_model_result_class())

    def monitor_model(self) -> MonitorResult[MODEL_TYPE]:
        """
        Monitor any change on model.

        :return: Model monitor
        """
        return self._execute_command('monitorModel',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field: str) -> MonitorResult[Dict[str, Any]]:
        """
        Monitor any change on a model's field.

        :param field: Field to monitor.
        :return: Model monitor
        """
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=self.get_field_monitor_result_class(field))


MODEL_MANAGER_TYPE = TypeVar('MODEL_MANAGER_TYPE', bound=BaseModelManager)


class BaseCollectionManager(BaseManager, Generic[MODEL_MANAGER_TYPE]):
    """
    Base collection manager.
    """

    MODEL_MANAGER_CLASS: ClassVar[Type[BaseModelManager]]

    @classmethod
    def get_monitor_result_class(cls) -> MonitorResult[MODEL_TYPE]:
        return cast(MonitorResult[MODEL_TYPE],
                    partial(MonitorResult[MODEL_TYPE],
                            fn_map=lambda evt: cls.MODEL_MANAGER_CLASS.map_model(evt['item'])))

    @classmethod
    def get_iterator_result_class(cls) -> IteratorResult[MODEL_TYPE]:
        return cast(IteratorResult[MODEL_TYPE],
                    partial(IteratorResult[MODEL_TYPE], fn_map=cls.MODEL_MANAGER_CLASS.map_model))

    @classmethod
    def get_item_result_class(cls) -> Result[MODEL_TYPE]:
        return cls.MODEL_MANAGER_CLASS.get_model_result_class()

    def get_items(self) -> IteratorResult[MODEL_TYPE]:
        """
        Get all items on collection.

        :return: Async iterator
        """
        return self._execute_command('getItems', result_class=self.get_iterator_result_class())

    def get_length(self) -> Result[int]:
        """
        Get collection items count.

        :return: Items count
        """
        return self._execute_command('getLength')

    def get_item_by_id(self, item_id: str) -> Result[MODEL_TYPE]:
        """
        Get model by identifier.

        :param item_id: Model identifier.
        :return: Model object.
        """
        return self._execute_command('getItemById',
                                     {'id': item_id},
                                     result_class=self.get_item_result_class())

    def find_item_by_id(self, item_id: str) -> Result[MODEL_TYPE]:
        """
        Find model by identifier. If item is not in collection it will try to load it.

        :param item_id: Model identifier.
        :return: Model object.
        """
        return self._execute_command('findItemById',
                                     {'id': item_id},
                                     result_class=self.get_item_result_class())

    def remove_item_by_id(self, item_id: str) -> Result[None]:
        """
        Remove item by identifier.

        :param item_id: Model identifier.
        """
        return self._execute_command('removeItemById',
                                     {'id': item_id})

    def get_first(self) -> Result[MODEL_TYPE]:
        """
        Get first item in collection.

        :return: Model object.
        """
        return self._execute_command('getFirst',
                                     result_class=self.get_item_result_class())

    def get_last(self) -> Result[MODEL_TYPE]:
        """
        Get last item in collection.

        :return: Model object.
        """
        return self._execute_command('getLast',
                                     result_class=self.get_item_result_class())

    def monitor_add(self) -> MonitorResult[MODEL_TYPE]:
        """
        Monitor add item collection. Iterate each time a item is added to collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorAdd',
                                     result_class=self.get_monitor_result_class())

    def monitor_remove(self) -> MonitorResult[MODEL_TYPE]:
        """
        Monitor remove item collection. Iterate each time a item is removed from collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorRemove',
                                     result_class=self.get_monitor_result_class())

    def monitor_change(self) -> MonitorResult[MODEL_TYPE]:
        """
        Monitor change item collection. Iterate each time a item change in collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorChange',
                                     result_class=self.get_monitor_result_class())

    def monitor_field(self, field: str) -> MonitorResult[Dict[str, Any]]:
        """
        Monitor item's field change. Iterate each time a field changed in any item of collection.

        :return: Model object iterator
        """
        return self._execute_command('monitorField',
                                     {'field': field},
                                     result_class=MonitorResult)

    def get_submanager(self, name: str) -> Union[BaseManager, MODEL_MANAGER_TYPE]:
        """
        Get a submanager. It could be a explicit submanager or contained model manager.

        :param name: Field where submanager was stored.
        """

        try:
            return super(BaseCollectionManager, self).get_submanager(name)
        except ManagerNotFound:
            return self.MODEL_MANAGER_CLASS(driver=self._driver,
                                            manager_path=self._build_command(name))

    __getattr__ = get_submanager

    __getitem__ = get_submanager
