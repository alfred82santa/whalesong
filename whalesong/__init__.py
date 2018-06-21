from asyncio import Future, sleep, ensure_future

from whalesong.managers.chat import ChatCollectionManager
from whalesong.managers.conn import ConnManager
from whalesong.managers.contact import ContactCollectionManager
from whalesong.managers.message import MessageCollectionManager
from whalesong.managers.storage import StorageManager
from whalesong.managers.stream import StreamManager
from .driver import WhalesongDriver
from .managers import BaseManager


__version__ = '0.2.0'


class Whalesong(BaseManager):

    def __init__(self, profile=None, loadstyles=False, headless=False, loop=None):
        super(Whalesong, self).__init__(WhalesongDriver(profile=profile,
                                                        loadstyles=loadstyles,
                                                        headless=headless,
                                                        loop=loop))

        self._submanagers['storage'] = StorageManager(self._driver, manager_path='storage')
        self._submanagers['stream'] = StreamManager(self._driver, manager_path='stream')
        self._submanagers['conn'] = ConnManager(self._driver, manager_path='conn')
        self._submanagers['contacts'] = ContactCollectionManager(self._driver, manager_path='contacts')
        self._submanagers['chats'] = ChatCollectionManager(self._driver, manager_path='chats')
        self._submanagers['messages'] = MessageCollectionManager(self._driver, manager_path='messages')

        self._fut_running = None
        self._fut_stopped = None

    @property
    def loop(self):
        return self._driver.loop

    async def start(self, interval=0.5):
        if self._fut_running:
            return

        self._fut_running = Future()
        self._fut_stopped = Future()

        await self._driver.start_driver()
        await self._driver.connect()

        ensure_future(self._polling(interval), loop=self.loop)

    async def stop(self):
        self._fut_running.set_result(None)
        await self.wait_until_stop()

    async def wait_until_stop(self):
        await self._fut_stopped

    async def _polling(self, interval):
        try:
            while not self._fut_running.done():
                await self._driver.poll()
                await sleep(interval)
        finally:
            if not self._fut_running.done():
                self._fut_running.set_result(None)
            await self._driver.cancel_iterators()
            self._driver.result_manager.cancel_all()
            await self._driver.close()
            self._fut_stopped.set_result(None)

    async def screenshot(self):
        return await self._driver.screenshot()

    async def qr(self):
        return await self._driver.screenshot_element('div[data-ref]')

    def stop_monitor(self, monitor):
        return self._driver.execute_command('stopMonitor', {'monitorId': monitor.result_id})

    async def cancel_iterators(self):
        return await self._driver.cancel_iterators()
