from asyncio import ensure_future, get_event_loop
from os import path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.driver_chromium import WhalesongDriver
from whalesong.managers.stream import Stream

OUTPUT_DIR = path.join(path.dirname(__file__), 'output')


class StatusMonitor:

    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = Whalesong(
            driver=WhalesongDriver(profile=path.join(path.dirname(__file__), 'profile-chromium'),
                                   headless=True,
                                   loop=loop),
            loop=loop
        )

    @property
    def loop(self):
        return self._driver.loop

    def echo(self, txt):
        self._print_fn(txt)

    async def check_stream(self):
        stream = await self._driver.stream.get_model()
        self.echo("Stream: {}".format(stream.stream))
        self.echo("State: {}".format(stream.state))

    async def check_conn(self):
        stream = await self._driver.conn.get_model()
        self.echo("REF: {}".format(stream.ref))
        self.echo("Battery: {}".format(stream.battery))

    async def check_storage(self):
        storage = await self._driver.storage.get_storage()
        self.echo("Storage: {}".format(storage))

    async def monitor_stream(self):
        self.echo('Monitor stream')
        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))
            img = await self._driver.screenshot()
            with open(path.join(OUTPUT_DIR, 'screenshot.png'), 'wb') as f:
                f.write(img.read())

            self.echo('Screenshot saved!')

    async def monitor_state(self):
        self.echo('Monitor state')
        async for evt in self._driver.stream.monitor_field('state'):
            self.echo(evt)
            self.echo('State value: {}'.format(evt['value']))
            if evt['value'] == Stream.State.UNPAIRED_IDLE:
                self.echo('Refreshing QR')
                await self._driver.stream.poke()
            elif evt['value'] == Stream.State.CONFLICT:
                self.echo('Taking over...')
                await self._driver.stream.takeover()

    async def monitor_ref(self):
        self.echo('Monitor ref')
        async for evt in self._driver.conn.monitor_field('ref'):
            self.echo('New REF value: {}'.format(evt['value']))

            try:
                img = await self._driver.qr()
                with open(path.join(OUTPUT_DIR, 'qr.png'), 'wb') as f:
                    f.write(img.read())

                self.echo('QR saved!')
            except Exception as ex:
                self.echo(ex)
                self.echo('Error getting qr')

    async def monitor_battery(self):
        self.echo('Monitor battery')
        async for evt in self._driver.conn.monitor_field('battery'):
            self.echo('Battery level: {}'.format(evt['value']))

    async def monitor_storage(self):
        self.echo('Monitor storage')
        async for evt in self._driver.storage.monitor_item_storage():
            self.echo('New storage item: {}'.format(evt))

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream())
        ensure_future(self.check_conn())
        ensure_future(self.check_storage())
        ensure_future(self.monitor_stream())
        ensure_future(self.monitor_state())
        ensure_future(self.monitor_ref())
        ensure_future(self.monitor_battery())
        ensure_future(self.monitor_storage())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = StatusMonitor()
    monitor.loop.run_until_complete(monitor.start())
