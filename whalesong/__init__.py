from asyncio import AbstractEventLoop

from io import BytesIO

from .driver import BaseWhalesongDriver
from .managers import BaseManager
from .managers.chat import ChatCollectionManager
from .managers.conn import ConnManager
from .managers.contact import ContactCollectionManager
from .managers.display_info import DisplayInfoManager
from .managers.live_location import LiveLocationCollectionManager
from .managers.message import MessageCollectionManager
from .managers.mute import MuteCollectionManager
from .managers.status import StatusCollectionManager
from .managers.sticker_pack import StickerPack, StickerPackCollectionManager
from .managers.storage import StorageManager
from .managers.stream import StreamManager
from .managers.wap import WapManager
from .results import MonitorResult, Result

__version__ = '0.8.0'


class Whalesong(BaseManager):
    """
    Whalesong service.

    The main Whalesong manager.
    """

    def __init__(self, profile: str = None,
                 *,
                 autostart: bool = True,
                 headless: bool = False,
                 extra_options: dict = None,
                 driver: BaseWhalesongDriver = None,
                 loop: AbstractEventLoop = None,
                 **kwargs):
        """

        :param profile: Path to firefox profile.
        :param autostart: Whether driver must start immediately.

        :param headless: Whether browser must be started with headless flag. In production environments
                         it should be set to :class:`True`.
        :param extra_options: Extra parametres for browser commandline.
        :param loop: Event loop.

        :param loadstyles: Whether CSS styles must be loaded. It is need in order to get QR image. (Only for Firefox)
        :type loadstyles: bool
        :param interval: Polling responses interval in seconds. Default 0.5 seconds. (Only for Firefox)
        :type interval: float
        """

        if driver is None:
            from .driver_firefox import WhalesongDriver
            driver = WhalesongDriver(profile=profile,
                                     autostart=autostart,
                                     headless=headless,
                                     extra_options=extra_options,
                                     loop=loop,
                                     **kwargs)

        super(Whalesong, self).__init__(driver)

        self._submanagers['storage'] = StorageManager(self._driver, manager_path='storage')
        self._submanagers['stream'] = StreamManager(self._driver, manager_path='stream')
        self._submanagers['conn'] = ConnManager(self._driver, manager_path='conn')
        self._submanagers['contacts'] = ContactCollectionManager(self._driver, manager_path='contacts')
        self._submanagers['chats'] = ChatCollectionManager(self._driver, manager_path='chats')
        self._submanagers['messages'] = MessageCollectionManager(self._driver, manager_path='messages')
        self._submanagers['wap'] = WapManager(self._driver, manager_path='wap')
        self._submanagers['sticker_packs'] = StickerPackCollectionManager(self._driver, manager_path='stickerPacks')
        self._submanagers['status'] = StatusCollectionManager(self._driver, manager_path='status')
        self._submanagers['display_info'] = DisplayInfoManager(self._driver, manager_path='displayInfo')
        self._submanagers['live_locations'] = LiveLocationCollectionManager(self._driver, manager_path='liveLocations')
        self._submanagers['mutes'] = MuteCollectionManager(self._driver, manager_path='mutes')

        self._fut_running = None

    @property
    def loop(self):
        """
        Event loop.

        :return: Event loop.
        """
        return self._driver.loop

    async def start(self):
        """
        Start Whalesong service.
        """

        await self._driver.start_driver()
        await self._driver.connect()

    async def stop(self):
        """
        Stop Whalesong service.
        """
        await self._driver.close()

    async def wait_until_stop(self):
        """
        Wait until Whalesong service is stopped.
        """
        await self._driver.whai_until_stop()

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
