from asyncio import Future, Queue, ensure_future
from logging import getLogger

from . import errors

logger = getLogger(__name__)


class BaseResultMixin:

    def __init__(self, result_id, *, fn_map=None):
        self.result_id = result_id
        self.fn_map = fn_map
        super(BaseResultMixin, self).__init__()

    def map(self, data):
        if self.fn_map:
            return self.fn_map(data)
        return data

    async def set_final_result(self, data):
        await self._set_result(self.map(data))

    async def set_error_result(self, data):
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


class Result(BaseResultMixin, Future):

    async def _set_result(self, data):
        self.set_result(data)

    async def _set_exception(self, ex):
        self.set_exception(ex)


class BasePartialResult(BaseResultMixin):

    def __init__(self, result_id, *, fn_map=None):
        super(BasePartialResult, self).__init__(result_id, fn_map=fn_map)
        self._queue = Queue()
        self._fut = Future()

    async def _set_result(self, data):
        await self._queue.put(data)

    async def _set_exception(self, ex):
        await self._set_result(ex)

    async def set_partial_result(self, data):
        await self._set_result(self.map(data))

    def __await__(self):
        return self._fut.__await__()

    def cancel(self):
        ensure_future(self._set_exception(StopAsyncIteration()))


class BaseIteratorResult(BasePartialResult):

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self._queue.get()

        if isinstance(item, Exception):
            self._fut.set_exception(item)
            raise item

        return item


class IteratorResult(BaseIteratorResult):

    def map(self, data):
        return super(IteratorResult, self).map(data['item'])


class MonitorResult(BaseIteratorResult):

    def __init__(self, result_id, *, fn_map=None):
        super(MonitorResult, self).__init__(result_id, fn_map=fn_map)

        self._callbacks = []

    def add_callback(self, fn):
        self._callbacks.append(fn)

    async def __anext__(self):
        evt = await super(MonitorResult, self).__anext__()
        [ensure_future(cb(evt)) for cb in self._callbacks]
        return evt

    async def _monitor(self):
        async for _ in self:
            pass

    def start_monitor(self):
        ensure_future(self._monitor())


class ResultManager:

    def __init__(self):
        self._pendant = {}
        self._next_id = 1

    def get_next_id(self):
        v = self._next_id
        self._next_id += 1
        return v

    def remove_result(self, result_id):
        try:
            return self._pendant.pop(result_id)
        except KeyError:
            return

    async def _autoclean_result(self, fut):
        try:
            await fut
        except Exception:
            pass
        finally:
            logger.debug('Remove result {}'.format(fut.result_id))
            self.remove_result(fut.result_id)

    def request_result(self, result_class):
        result_id = self.get_next_id()
        result = result_class(result_id)
        self._pendant[result_id] = result
        ensure_future(self._autoclean_result(result))
        return result

    def request_final_result(self):
        return self.request_result(Result)

    def request_iterator_result(self):
        return self.request_result(IteratorResult)

    def request_monitor_result(self):
        return self.request_result(MonitorResult)

    def cancel_result(self, result_id):
        try:
            self._pendant[result_id].cancel()
        except KeyError:
            pass

    def cancel_all(self):
        [self.cancel_result(result_id) for result_id in self._pendant.keys()]

    async def set_final_result(self, result_id, data):
        try:
            await self._pendant[result_id].set_final_result(data)
        except KeyError:
            pass

    async def set_error_result(self, result_id, data):
        try:
            await self._pendant[result_id].set_error_result(data)
        except KeyError:
            pass

    async def set_partial_result(self, result_id, data):
        try:
            await self._pendant[result_id].set_partial_result(data)
        except KeyError:
            pass

    def get_iterators(self):
        return [it for it in self._pendant.values() if isinstance(it, IteratorResult)]
