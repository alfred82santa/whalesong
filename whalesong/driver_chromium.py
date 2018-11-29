from asyncio import AbstractEventLoop
from json import dumps
from logging import Logger
from pathlib import Path
from typing import Any, Dict, Optional

from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

from .driver import BaseWhalesongDriver

DEFAULT_CHROMIUM_ARGS = [
    '--single-process',
    '--disable-gpu',
    '--renderer',
    '--no-sandbox',
    '--no-service-autorun',
    '--no-experiments',
    '--no-default-browser-check',
    '--disable-webgl',
    '--disable-threaded-animation',
    '--disable-threaded-scrolling',
    '--disable-in-process-stack-traces',
    '--disable-histogram-customizer',
    '--disable-gl-extensions',
    '--disable-extensions',
    '--disable-composited-antialiasing',
    '--disable-canvas-aa',
    '--disable-3d-apis',
    '--disable-accelerated-2d-canvas',
    '--disable-accelerated-jpeg-decoding',
    '--disable-accelerated-mjpeg-decode',
    '--disable-app-list-dismiss-on-blur',
    '--disable-accelerated-video-decod',
    '--num-raster-threads=1'
]


class WhalesongDriver(BaseWhalesongDriver):

    def __init__(self, profile: str = None, *,
                 autostart: bool = True,
                 headless: bool = False,
                 extra_options: Optional[Dict[str, Any]] = None,
                 logger: Optional[Logger] = None,
                 loop: Optional[AbstractEventLoop] = None):
        super(WhalesongDriver, self).__init__(autostart=autostart,
                                              headless=headless,
                                              extra_options=extra_options,
                                              logger=logger,
                                              loop=loop)

        self.driver: Browser = None
        self.page: Page = None

        self.options.update({
            'userDataDir': Path(profile).resolve() if profile else None,
            'loop': self.loop
        })

        if 'args' not in self.options:
            chromium_args = [f'--app={self._URL}']
            chromium_args.extend(DEFAULT_CHROMIUM_ARGS)
            self.options['args'] = chromium_args

    async def _internal_start_driver(self):
        self.driver = await launch(
            **self.options)
        pages = await self.driver.pages()
        self.page = pages[0]
        await self.page.setUserAgent(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36'
        )
        await self.page.setViewport({'width': 800, 'height': 600})
        await self.page.exposeFunction('whalesongPushResult', self.process_result_sync)

    async def connect(self):
        await self.start_driver()
        await self.refresh()

    async def refresh(self):
        await self.page.goto(self._URL)
        self.result_manager.cancel_all()
        await self.run_scriptlet()

    async def _internal_run_scriptlet(self, script):
        await self.page.evaluate(script)

    async def _internal_screenshot(self):
        return await self.page.screenshot()

    async def _internal_element_screenshot(self, element) -> bytes:
        return await element.screenshot()

    async def _internal_get_element(self, css_selector: str):
        return await self.page.querySelector(css_selector)

    async def _execute_command(self, result_id, command, params):
        await self.page.evaluate(
            f'(function() {{window.manager.executeCommand("{result_id}", "{command}", {dumps(params)})}})()'
        )

    async def _internal_close(self):
        await self.driver.close()
