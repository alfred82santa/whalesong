from asyncio import ensure_future, sleep, wait

from os import path

from whalesong.driver import WhalesongDriver
from whalesong.results import MonitorResult


OUTPUT_DIR = path.join(path.dirname(__file__), '..', 'output')


class StatusMonitor:

    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = WhalesongDriver(profile=path.join(path.dirname(
            __file__), '..', 'profile'), loadstyles=True, loop=loop)

    def echo(self, txt):
        self._print_fn(txt)

    @property
    def loop(self):
        return self._driver.loop

    async def init(self):
        await self._driver.start_driver()
        await self._driver.connect()
        self.echo('Connected')

    async def check_stream(self):
        stream = await self._driver.execute_command('stream|getModel')
        self.echo("Stream: {}".format(stream['stream']))
        self.echo("State: {}".format(stream['state']))

    async def check_conn(self):
        stream = await self._driver.execute_command('conn|getModel')
        self.echo("REF: {}".format(stream['ref']))
        self.echo("Battery: {}".format(stream['battery']))

    async def check_storage(self):
        storage = await self._driver.execute_command('storage|getStorage')
        self.echo("Storage: {}".format(storage))

    async def monitor_stream(self):
        self.echo('Monitor stream')
        async for evt in self._driver.execute_command('stream|monitorField',
                                                      {'field': 'stream'},
                                                      result_class=MonitorResult):
            self.echo('Stream value: {}'.format(evt['value']))
            img = await self._driver.screenshot()
            with open(path.join(OUTPUT_DIR, 'screenshot.png'), 'wb') as f:
                f.write(img.read())

            self.echo('Screenshot saved!')

    async def monitor_state(self):
        self.echo('Monitor state')
        async for evt in self._driver.execute_command('stream|monitorField',
                                                      {'field': 'state'},
                                                      result_class=MonitorResult):
            self.echo('State value: {}'.format(evt['value']))
            if evt['value'] == 'UNPAIRED_IDLE':
                self.echo('Refreshing QR')
                self._driver.execute_command('stream|poke')
            elif evt['value'] == 'CONFLICT':
                self.echo('Taking over...')
                self._driver.execute_command('stream|takeover')

    async def monitor_ref(self):
        self.echo('Monitor ref')
        async for evt in self._driver.execute_command('conn|monitorField',
                                                      {'field': 'ref'},
                                                      result_class=MonitorResult):
            self.echo('New REF value: {}'.format(evt['value']))

            try:
                img = await self._driver.screenshot_element('div[data-ref]')
                with open(path.join(OUTPUT_DIR, 'qr.png'), 'wb') as f:
                    f.write(img.read())

                self.echo('QR saved!')
            except Exception as ex:
                self.echo(ex)
                self.echo('Error getting qr')

    async def monitor_battery(self):
        self.echo('Monitor battery')
        async for evt in self._driver.execute_command('conn|monitorField',
                                                      {'field': 'battery'},
                                                      result_class=MonitorResult):
            self.echo('Battery level: {}'.format(evt['value']))

    async def monitor_storage(self):
        self.echo('Monitor storage')
        async for evt in self._driver.execute_command('storage|monitorItemStorage',
                                                      result_class=MonitorResult):
            self.echo('New storage item: {}'.format(evt))

    async def start(self):
        await self.init()
        futs = [ensure_future(self.check_stream()),
                ensure_future(self.check_conn()),
                ensure_future(self.check_storage()),
                ensure_future(self.monitor_stream()),
                ensure_future(self.monitor_state()),
                ensure_future(self.monitor_ref()),
                ensure_future(self.monitor_battery()),
                ensure_future(self.monitor_storage())]

        try:
            while True:
                await self._driver.poll()
                await sleep(0.5)
        finally:
            await self._driver.cancel_iterators()
            self._driver.result_manager.cancel_all()
            await wait(futs)
            await self._driver.close()


if __name__ == '__main__':
    monitor = StatusMonitor()
    monitor.loop.run_until_complete(monitor.start())
