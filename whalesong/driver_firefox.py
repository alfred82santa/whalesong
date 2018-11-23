from asyncio import AbstractEventLoop, Future, ensure_future, sleep, wait
from concurrent.futures import ThreadPoolExecutor
from json import dumps
from logging import Logger
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from functools import partial
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

from .driver import BaseWhalesongDriver
from .firefox_profile import FirefoxProfile


class WhalesongDriver(BaseWhalesongDriver):

    def __init__(self, profile: str = None, *,
                 autostart: bool = True,
                 headless: bool = False,
                 interval: float = 0.5,
                 loadstyles: bool = False,
                 extra_options: Optional[Dict[str, Any]] = None,
                 logger: Optional[Logger] = None,
                 loop: Optional[AbstractEventLoop] = None):
        super(WhalesongDriver, self).__init__(autostart=autostart,
                                              headless=headless,
                                              extra_options=extra_options,
                                              logger=logger,
                                              loop=loop)

        self._profile = FirefoxProfile(profile_directory=str(Path(profile).resolve()) if profile else None)
        if not loadstyles:
            # Disable CSS
            self._profile.set_preference('permissions.default.stylesheet', 2)
            # Disable images
            self._profile.set_preference('permissions.default.image', 2)
            # Disable Flash
            self._profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                         'false')

        self._profile.update_preferences()

        self.options.update({
            'extra_params': extra_options or {},
        })

        self._pool_executor = ThreadPoolExecutor(max_workers=1)
        self._pendant: List[Dict[str, Any]] = []

        self.driver: webdriver.Firefox = None
        self._fut_running: Future = None
        self._fut_polling: Future = None

        self.interval = interval

    async def _run_async(self, method: Callable, *args, **kwargs) -> Any:
        self.logger.debug('Running async method {}'.format(method.__name__))
        return await self.loop.run_in_executor(self._pool_executor, partial(method, *args, **kwargs))

    async def _internal_start_driver(self):
        self.driver = await self._run_async(self._internal_start_driver_sync)

    def _internal_start_driver_sync(self):
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities['webStorageEnabled'] = True
        capabilities['databaseEnabled'] = True

        self.logger.info("Starting webdriver")
        options = Options()

        if self.options['headless']:
            options.headless = True

        if self._profile:
            options.add_argument('-profile')
            options.add_argument(self._profile.profile_dir)

        driver = webdriver.Firefox(capabilities=capabilities,
                                   options=options,
                                   service_args=['--marionette-port', '2828'],
                                   **self.options['extra_params'])

        driver.set_script_timeout(500)
        driver.implicitly_wait(10)
        return driver

    async def connect(self):
        await self._run_async(self.driver.get, self._URL)
        self.result_manager.cancel_all()
        await sleep(1)
        await self.run_scriptlet()
        self._fut_running = Future()
        self._fut_polling = ensure_future(self._polling())

    async def refresh(self):
        await self._run_async(self.driver.refresh)
        self.result_manager.cancel_all()
        await sleep(1)
        await self.run_scriptlet()

    async def _internal_run_scriptlet(self, script):
        await self._run_async(self.driver.execute_script, script)

    async def _internal_screenshot(self):
        return await self._run_async(self.driver.get_screenshot_as_png)

    async def _internal_element_screenshot(self, element) -> bytes:
        def take_screenshot():
            return element.screenshot_as_png

        return await self._run_async(take_screenshot)

    async def _internal_get_element(self, css_selector: str):
        await self._run_async(self.driver.find_element_by_css_selector, css_selector)

    async def _execute_command(self, result_id, command, params):
        self._pendant.append({'exId': result_id,
                              'command': command,
                              'params': params or {}})

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

    async def _internal_close(self):
        if not self._fut_running.done():
            self._fut_running.set_result(None)
            await self._fut_polling

        await self._run_async(self.driver.close)

    async def _polling(self):
        try:
            while not self._fut_running.done():
                await self.poll()
                await sleep(self.interval)
        finally:
            if not self._fut_running.done():
                self._fut_running.set_result(None)
            await wait([self.cancel_iterators(),
                        self.cancel_monitors()])
            self.result_manager.cancel_all()

            try:
                await self.close()
            except ConnectionRefusedError:
                pass
