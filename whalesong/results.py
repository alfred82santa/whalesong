from asyncio import Future, Queue, ensure_future
from logging import getLogger
from typing import Any, AsyncIterable, AsyncIterator, Awaitable, Callable, Dict, List, Optional, Type, TypeVar, Union, \
    cast

from abc import ABC, abstractmethod

from . import errors

logger = getLogger(__name__)

T = TypeVar('T')


class BaseResultMixin(ABC, Awaitable[T]):
    """
    Base result mixin.

    .. attribute:: result_id: str

        Result unique identifier.

    .. attribute:: fn_map: Callable[[dict], Union[BaseModel, dict]]

        Mapping function used to map result.

    """

    def __init__(self, result_id: str, *, fn_map: Optional[Callable[[dict], T]] = None):
        """

        :param result_id: Result unique identifier.
        :param fn_map: Mapping function used to map result.
        """
        self.result_id = result_id
        self.fn_map = fn_map
        super(BaseResultMixin, self).__init__()

    def map(self, data: dict) -> T:
        """
        Maps data from browser to an object if `fn_map` function is defined.

        :param data: Data from browser.
        :return: Mapped object.
        """
        if self.fn_map:
            return self.fn_map(data)
        return cast(T, data)

    async def set_final_result(self, data: dict):
        await self._set_result(self.map(data))

    async def set_error_result(self, data: dict):
        try:
            ex_class = getattr(errors, data['name'])
        except (AttributeError, KeyError):
            ex_class = errors.UnknownError

        try:
            args = [data['message'], ]
        except KeyError:
            args = []

        try:
            kwargs = data['params']
        except KeyError:
            kwargs = {}

        await self._set_exception(ex_class(*args, **kwargs))

    @abstractmethod
    async def _set_result(self, data: T):
        pass

    @abstractmethod
    async def _set_exception(self, ex: Exception):
        pass


class Result(BaseResultMixin[T], Future):
    """
    Result of command. It is a subtype of :class:`asyncio.Future`, so in order to get
    result value you must `await` it.

    .. code-block:: python3

        value = await result

    """

    def __await__(self):
        return Future.__await__(self)

    async def _set_result(self, data: T):
        self.set_result(data)

    async def _set_exception(self, ex: Exception):
        self.set_exception(ex)


class BasePartialResult(BaseResultMixin[T], AsyncIterable[T]):

    def __init__(self, result_id: str, *, fn_map: Optional[Callable[[dict], T]] = None):
        super(BasePartialResult, self).__init__(result_id, fn_map=fn_map)
        self._queue: Queue = Queue()
        self._fut: Future = Future()

    async def _set_result(self, data: Union[T, Exception]):
        await self._queue.put(data)

    async def _set_exception(self, ex: Exception):
        await self._set_result(ex)

    async def set_partial_result(self, data: dict):
        await self._set_result(self.map(data))

    def __await__(self):
        return self._fut.__await__()

    def cancel(self):
        ensure_future(self._set_exception(StopAsyncIteration()))


class BaseIteratorResult(BasePartialResult[T]):
    """
    Base iterable result.
    """

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        item = await self._queue.get()

        if isinstance(item, Exception):
            self._fut.set_exception(item)
            raise item

        return item


class IteratorResult(BaseIteratorResult[T]):
    """
    Iterator result. It is used as result of command which returns a list of object.

    .. warning::

        It is an async iterator.

    **How to use**

    .. code-block:: python3

        async for item in result_iterator:
            print(item)

    """

    def map(self, data) -> T:
        return super(IteratorResult, self).map(data['item'])


class MonitorResult(BaseIteratorResult[T]):
    """
    Monitor result. It is used as result of monitor command. It is a infinite iterator. Each change on object or
    field it is monitoring will be a new item on iterator.

    .. warning::

        It is an async iterator.

    **How to use**

    .. code-block:: python3

        async for item_changed in monitor:
            print(item_changed)

    """

    def __init__(self, result_id: str, *, fn_map: Optional[Callable[[dict], T]] = None):
        super(MonitorResult, self).__init__(result_id, fn_map=fn_map)

        self._callbacks: List[Callable[[Any], Awaitable[Any]]] = []

    def add_callback(self, fn: Callable[[T], Awaitable[Any]]):
        """
        Add a callback to be called each time object or field change.

        :param fn: Callback function
        """
        self._callbacks.append(fn)

    async def __anext__(self) -> T:
        evt: T = await super(MonitorResult, self).__anext__()
        [ensure_future(cb(evt)) for cb in self._callbacks]
        return evt

    async def _monitor(self):
        async for _ in self:
            pass

    def start_monitor(self):
        """
        Starts automatic monitor iteration. Useful when callback functions are defined.
        """
        ensure_future(self._monitor())


TypeResult = TypeVar('TypeResult', Result, IteratorResult, MonitorResult)
UnionResultType = Union[Type[Result], Type[IteratorResult], Type[MonitorResult]]
UnionResult = Union[Result, IteratorResult, MonitorResult]


class ResultManager:

    def __init__(self):
        self._pendant: Dict[str, UnionResult] = {}
        self._next_id = 1

    def get_next_id(self) -> str:
        v = self._next_id
        self._next_id += 1
        return str(v)

    def remove_result(self, result_id) -> Optional[UnionResult]:
        try:
            return self._pendant.pop(result_id)
        except KeyError:
            return None

    async def _autoclean_result(self, fut: UnionResult):
        try:
            await fut
        except Exception:
            pass
        finally:
            logger.debug('Remove result {}'.format(fut.result_id))
            self.remove_result(fut.result_id)

    def request_result(self, result_class: Type[TypeResult]) -> TypeResult:
        result_id = self.get_next_id()
        result = result_class(result_id)
        self._pendant[result_id] = result
        ensure_future(self._autoclean_result(result))
        return result

    def request_final_result(self) -> Result:
        return self.request_result(Result)

    def request_iterator_result(self) -> IteratorResult:
        return self.request_result(IteratorResult)

    def request_monitor_result(self) -> MonitorResult:
        return self.request_result(MonitorResult)

    def cancel_result(self, result_id: str):
        try:
            self._pendant[result_id].cancel()
        except KeyError:
            pass

    def cancel_all(self):
        [self.cancel_result(result_id) for result_id in self._pendant.keys()]

    async def set_final_result(self, result_id: str, data: Any):
        try:
            await self._pendant[result_id].set_final_result(data)
        except KeyError:
            pass

    async def set_error_result(self, result_id: str, data: Any):
        try:
            await self._pendant[result_id].set_error_result(data)
        except KeyError:
            pass

    async def set_partial_result(self, result_id: str, data: Any):
        try:
            await cast(BasePartialResult, self._pendant[result_id]).set_partial_result(data)
        except (KeyError, AttributeError):
            pass

    def get_iterators(self) -> List[IteratorResult]:
        return [it for it in self._pendant.values() if isinstance(it, IteratorResult)]

    def get_monitors(self) -> List[MonitorResult]:
        return [it for it in self._pendant.values() if isinstance(it, MonitorResult)]
