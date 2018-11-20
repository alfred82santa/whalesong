from asyncio import AbstractEventLoop, Future, ensure_future, sleep, wait
from builtins import ConnectionRefusedError

from io import BytesIO

from .driver import WhalesongDriver
from .managers import BaseManager
from .managers.chat import ChatCollectionManager
from .managers.conn import ConnManager
from .managers.contact import ContactCollectionManager
from .managers.message import MessageCollectionManager
from .managers.sticker_pack import StickerPack, StickerPackCollectionManager
from .managers.storage import StorageManager
from .managers.stream import StreamManager
from .managers.wap import WapManager
from .results import MonitorResult, Result

__version__ = '0.6.0'


class Whalesong(BaseManager):
    """
    Main Whalesong manager.
    """

    def __init__(self, profile: str = None,
                 loadstyles: bool = False,
                 headless: bool = False,
                 extra_params: dict = None,
                 loop: AbstractEventLoop = None):
        """

        :param profile: Path to firefox profile.
        :param loadstyles: Whether CSS styles must be loaded. It is need in order to get QR image.
        :param headless: Whether firefox must be started with headless flag. In production environments
                         it should be set to :class:`True`.
        :param extra_params: Extra parametres for firefox.
        :param loop: Event loop.
        """
        super(Whalesong, self).__init__(WhalesongDriver(profile=profile,
                                                        loadstyles=loadstyles,
                                                        headless=headless,
                                                        extra_params=extra_params,
                                                        loop=loop))

        self._submanagers['storage'] = StorageManager(self._driver, manager_path='storage')
        self._submanagers['stream'] = StreamManager(self._driver, manager_path='stream')
        self._submanagers['conn'] = ConnManager(self._driver, manager_path='conn')
        self._submanagers['contacts'] = ContactCollectionManager(self._driver, manager_path='contacts')
        self._submanagers['chats'] = ChatCollectionManager(self._driver, manager_path='chats')
        self._submanagers['messages'] = MessageCollectionManager(self._driver, manager_path='messages')
        self._submanagers['wap'] = WapManager(self._driver, manager_path='wap')
        self._submanagers['sticker_packs'] = StickerPackCollectionManager(self._driver, manager_path='stickerPacks')

        self._fut_running = None

    @property
    def loop(self):
        """
        Event loop.

        :return: Event loop.
        """
        return self._driver.loop

    async def start(self, interval: float = 0.5):
        """
        Start Whalesong service.

        :param interval: Polling interval
        """
        if self._fut_running:
            return

        self._fut_running = Future()

        await self._driver.start_driver()
        await self._driver.connect()

        self._fut_polling = ensure_future(self._polling(interval), loop=self.loop)

    async def stop(self):
        """
        Stop Whalesong service.
        """
        self._fut_running.set_result(None)
        await self.wait_until_stop()

    async def wait_until_stop(self):
        """
        Wait until Whalesong service stop.
        """
        await self._fut_polling

    async def _polling(self, interval):
        try:
            while not self._fut_running.done():
                await self._driver.poll()
                await sleep(interval)
        finally:
            if not self._fut_running.done():
                self._fut_running.set_result(None)
            await wait([self._driver.cancel_iterators(),
                        self._driver.cancel_monitors()])
            self._driver.result_manager.cancel_all()

            try:
                await self._driver.close()
            except ConnectionRefusedError:
                pass

    async def screenshot(self) -> BytesIO:
        """
        Take a screenshot of whole page.

        :return: It returns a stream of a PNG image.
        """
        return await self._driver.screenshot()

    async def qr(self) -> BytesIO:
        """
        Take a screenshot of QR.

        :return: It returns a stream of a PNG image.
        """
        return await self._driver.screenshot_element('div[data-ref]')

    def stop_monitor(self, monitor: MonitorResult) -> Result[None]:
        """
        Stop a given monitor.

        :param monitor: Monitor object to stop.
        """
        return self._driver.execute_command('stopMonitor', {'monitorId': monitor.result_id})

    async def cancel_iterators(self):
        """
        Cancel all iterators.
        """
        return await self._driver.cancel_iterators()

    async def download_file(self, url: str) -> BytesIO:
        """
        Download a file by URL

        :param url: URL to the file
        :return: It returns a stream.
        """
        return await self._driver.download_file(url)
