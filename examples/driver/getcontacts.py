from asyncio import ensure_future, wait

from os import path

from whalesong.driver_firefox import WhalesongDriver
from whalesong.results import IteratorResult, MonitorResult


class GetContacts:

    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = WhalesongDriver(profile=path.join(path.dirname(__file__), '..', 'profile'),
                                       loadstyles=False, loop=loop)

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

    async def monitor_stream(self):
        self.echo('Monitor stream')
        contact_it = None

        async for evt in self._driver.execute_command('stream|monitorField',
                                                      {'field': 'stream'},
                                                      result_class=MonitorResult):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == 'CONNECTED':
                if contact_it is None:
                    contact_it = self._driver.execute_command('contacts|getItems',
                                                              result_class=IteratorResult)
                    ensure_future(self.list_contacts(contact_it))
            else:
                if contact_it is not None:
                    self._driver.cancel_iterators()
                    contact_it = None

    async def list_contacts(self, it):
        self.echo('List contacts')
        async for contact in it:
            self.echo('Contact: {}'.format(contact))

        self.echo('List contacts finished')

    async def start(self):
        await self.init()
        futs = [ensure_future(self.monitor_stream())]

        try:
            await self._driver.whai_until_stop()
        finally:
            await self._driver.cancel_iterators()
            self._driver.result_manager.cancel_all()
            await wait(futs)
            await self._driver.close()


if __name__ == '__main__':
    monitor = GetContacts()
    monitor.loop.run_until_complete(monitor.start())
