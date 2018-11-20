from asyncio import AbstractEventLoop, ensure_future, get_event_loop, sleep
from concurrent.futures import ThreadPoolExecutor
from json import dumps
from logging import Logger, getLogger
from typing import Any, Callable, Dict, List, Optional, Type, overload

from aiohttp import ClientSession
from functools import partial
from io import BytesIO
from os.path import abspath, dirname, join
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

from .firefox_profile import FirefoxProfile
from .results import Result, ResultManager, TypeResult


class WhalesongDriver:
    _URL = "https://web.whatsapp.com"

    def __init__(self, profile: str = None,
                 loadstyles: bool = False,
                 headless: bool = False,
                 extra_params: Optional[Dict[str, Any]] = None, *,
                 logger: Optional[Logger] = None,
                 loop: Optional[AbstractEventLoop] = None):
        self._start_fut = None

        self._profile = FirefoxProfile(profile_directory=abspath(profile) if profile else None)
        if not loadstyles:
            # Disable CSS
            self._profile.set_preference('permissions.default.stylesheet', 2)
            # Disable images
            self._profile.set_preference('permissions.default.image', 2)
            # Disable Flash
            self._profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                         'false')

        self._profile.update_preferences()

        self._driver_options = {'headless': headless, 'extra_params': extra_params or {}}

        self.loop = loop or get_event_loop()
        self.logger = logger or getLogger('whalesong.driver')

        self._pool_executor = ThreadPoolExecutor(max_workers=1)

        self.result_manager = ResultManager()

        self._pendant: List[Dict[str, Any]] = []

        self.driver: webdriver.Firefox = None
        ensure_future(self.start_driver(), loop=self.loop)

    async def _run_async(self, method: Callable, *args, **kwargs) -> Any:
        self.logger.debug('Running async method {}'.format(method.__name__))
        return await self.loop.run_in_executor(self._pool_executor, partial(method, *args, **kwargs))

    async def start_driver(self):
        if self._start_fut:
            await self._start_fut
            return

        def start():
            capabilities = DesiredCapabilities.FIREFOX.copy()
            capabilities['webStorageEnabled'] = True
            capabilities['databaseEnabled'] = True

            self.logger.info("Starting webdriver")
            options = Options()

            if self._driver_options['headless']:
                options.headless = True

            if self._profile:
                options.add_argument('-profile')
                options.add_argument(self._profile.profile_dir)

            driver = webdriver.Firefox(capabilities=capabilities,
                                       options=options,
                                       service_args=['--marionette-port', '2828'],
                                       **self._driver_options['extra_params'])

            driver.set_script_timeout(500)
            driver.implicitly_wait(10)
            return driver

        self._start_fut = ensure_future(self._run_async(start))
        self.driver = await self._start_fut

    async def connect(self):
        await self._run_async(self.driver.get, self._URL)
        self.result_manager.cancel_all()
        await sleep(1)
        await self.run_scriptlet()

    async def refresh(self):
        await self._run_async(self.driver.refresh)
        self.result_manager.cancel_all()
        await sleep(1)
        await self.run_scriptlet()

    async def run_scriptlet(self):
        with open(join(dirname(__file__), "js", "whalesong.js"), "r") as script:
            await self._run_async(self.driver.get, self._URL)
            self.driver.execute_script(script.read())

    async def screenshot(self) -> BytesIO:
        return BytesIO(await self._run_async(self.driver.get_screenshot_as_png))

    async def screenshot_element(self, css_selector: str) -> BytesIO:
        elem = await self._run_async(self.driver.find_element_by_css_selector, css_selector)

        if not elem:
            raise Exception('Element not found')

        def take_screenshot():
            return BytesIO(elem.screenshot_as_png)

        return await self._run_async(take_screenshot)

    @overload
    def execute_command(self, command: str,
                        params: Dict[str, Any] = None, *,
                        result_class: Type[Result] = None) -> Result:
        ...

    @overload
    def execute_command(self, command: str,
                        params: Dict[str, Any] = None, *,
                        result_class: Type[TypeResult] = None) -> TypeResult:
        ...

    def execute_command(self, command, params=None, *, result_class=None):
        if result_class is None:
            result_class = Result

        result = self.result_manager.request_result(result_class)
        self._pendant.append({'exId': result.result_id,
                              'command': command,
                              'params': params or {}})

        return result

    async def poll(self):
        pendant = self._pendant
        self._pendant = []
        try:
            results = await self._run_async(self.driver.execute_script,
                                            "return window.manager.poll({});".format(dumps(pendant)))
        except Exception as ex:
            self.logger.warning(ex)
            return

        try:
            for err in results['errors']:
                self.logger.error(err)
                try:
                    await self.result_manager.set_error_result(err['executionsObj']['exId'], err)
                except KeyError:
                    pass
        except KeyError:
            pass

        try:
            for result in results['results']:
                try:
                    if result['type'] == 'FINAL':
                        await self.result_manager.set_final_result(result['exId'], result['params'])
                    elif result['type'] == 'PARTIAL':
                        await self.result_manager.set_partial_result(result['exId'], result['params'])
                    elif result['type'] == 'ERROR':
                        await self.result_manager.set_error_result(result['exId'], result['params'])
                except Exception as ex:
                    self.logger.exception(ex)
        except KeyError:
            pass

    async def close(self):
        await self._run_async(self.driver.close)

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
