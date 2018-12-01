from asyncio import AbstractEventLoop, Future, ensure_future, get_event_loop
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Dict, Optional, Type, overload

from abc import ABC, abstractmethod
from aiohttp import ClientSession
from io import BytesIO

from .results import IteratorResult, MonitorResult, Result, ResultManager


class BaseWhalesongDriver(ABC):
    _URL = "https://web.whatsapp.com"

    def __init__(self, *,
                 autostart: bool = True,
                 headless: bool = False,
                 extra_options: Optional[Dict[str, Any]] = None,
                 logger: Optional[Logger] = None,
                 loop: Optional[AbstractEventLoop] = None):
        self._fut_start: Future = None
        self._fut_stop: Future = None
        self.loop = loop or get_event_loop()
        self.logger = logger or getLogger('whalesong.driver')
        self.result_manager = ResultManager()

        self.options = {
            'headless': headless
        }

        try:
            self.options.update(extra_options)
        except TypeError:
            pass

        if autostart:
            ensure_future(self.start_driver(), loop=self.loop)

    async def start_driver(self):
        if self._fut_stop is None:
            self._fut_stop = Future()

        if self._fut_start:
            await self._fut_start
            return

        self._fut_start = ensure_future(self._internal_start_driver())
        await self._fut_start

    @abstractmethod
    async def _internal_start_driver(self):
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def refresh(self):
        pass

    async def run_scriptlet(self):
        with open(Path(Path(__file__).parent, "js", "whalesong.js"), "r") as script:
            await self._internal_run_scriptlet(script.read())

    @abstractmethod
    async def _internal_run_scriptlet(self, script):
        pass

    async def screenshot(self) -> BytesIO:
        return BytesIO(await self._internal_run_scriptlet())

    @abstractmethod
    async def _internal_screenshot(self):
        pass

    async def screenshot_element(self, css_selector: str) -> BytesIO:
        elem = await self._internal_get_element(css_selector)

        if not elem:
            raise Exception('Element not found')

        return BytesIO(await self._internal_element_screenshot(elem))

    @abstractmethod
    async def _internal_element_screenshot(self, element) -> bytes:
        pass

    @abstractmethod
    async def _internal_get_element(self, css_selector: str):
        pass

    @overload
    def execute_command(self, command: str,
                        params: Dict[str, Any] = None, *,
                        result_class: Type[Result] = None) -> Result:
        pass

    @overload
    def execute_command(self, command: str,
                        params: Dict[str, Any] = None, *,
                        result_class: Type[IteratorResult] = None) -> IteratorResult:
        pass

    @overload
    def execute_command(self, command: str,
                        params: Dict[str, Any] = None, *,
                        result_class: Type[MonitorResult] = None) -> MonitorResult:
        pass

    def execute_command(self, command, params=None, *, result_class=None):
        if result_class is None:
            result_class = Result

        result = self.result_manager.request_result(result_class)

        ensure_future(self._execute_command(result_id=result.result_id,
                                            command=command,
                                            params=params),
                      loop=self.loop)
        return result

    @abstractmethod
    async def _execute_command(self, result_id, command, params):
        pass

    def process_result_sync(self, result):
        ensure_future(self.process_result(result), loop=self.loop)
        return True

    async def process_result(self, result):
        try:
            if result['type'] == 'FINAL':
                await self.result_manager.set_final_result(result['exId'], result['params'])
            elif result['type'] == 'PARTIAL':
                await self.result_manager.set_partial_result(result['exId'], result['params'])
            elif result['type'] == 'ERROR':
                await self.result_manager.set_error_result(result['exId'], result['params'])
        except Exception as ex:
            self.logger.exception(ex)

    async def close(self):
        await self._internal_close()
        self._fut_stop.set_result(None)

    @abstractmethod
    async def _internal_close(self):
        pass

    async def cancel_iterators(self):
        for it in self.result_manager.get_iterators():
            await it.set_error_result({'name': 'StopIterator'})

    async def cancel_monitors(self):
        for it in self.result_manager.get_monitors():
            await it.set_error_result({'name': 'StopIterator'})

    async def download_file(self, url) -> BytesIO:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                return BytesIO(await resp.read())

    async def whai_until_stop(self):
        if self._fut_stop is None:
            raise RuntimeError('Driver not started')

        await self._fut_stop
