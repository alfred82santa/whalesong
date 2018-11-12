from asyncio import Future, ensure_future, sleep, wait
from builtins import ConnectionRefusedError

from io import BytesIO

from .driver import WhalesongDriver
from .managers import BaseManager
from .managers.chat import ChatCollectionManager
from .managers.conn import ConnManager
from .managers.contact import ContactCollectionManager
from .managers.message import MessageCollectionManager
from .managers.storage import StorageManager
from .managers.stream import StreamManager
from .managers.wap import WapManager
from .results import MonitorResult

__version__ = '0.5.3'


class Whalesong(BaseManager):
    """
    Main Whalesong manager.

    .. attribute:: storage

        :class:`~whalesong.managers.storage.StorageManager`

        Manager for local storage.

    .. attribute:: stream

        :class:`~whalesong.managers.stream.StreamManager`

        Manager for stream object.

    .. attribute:: conn

        :class:`~whalesong.managers.conn.ConnManager`

        Manager for connection object

    .. attribute:: contacts

        :class:`~`whalesong.managers.contact.ContactCollectionManager`

        Manager for contact collection.

    .. attribute:: chats

        :class:`~whalesong.managers.chat.ChatCollectionManager`

        Manager for chat collection.

    .. attribute:: messages

        :class:`~whalesong.managers.message.MessageCollectionManager`

        Manager for messages collection.

    .. attribute:: wap

        :class:`~whalesong.managers.wap.WapManager`

        Manager for wap object.
    """

    def __init__(self, profile=None, loadstyles=False, headless=False, extra_params=None, loop=None):
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

        self._fut_running = None

    @property
    def loop(self):
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

    def stop_monitor(self, monitor: MonitorResult) -> Future:
        """
        Stop a given monitor.

        :param monitor: Monitor object to stop.
        :return: a future which will be resolve when monitor stop.
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
