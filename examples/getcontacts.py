from asyncio import ensure_future, get_event_loop
from os import path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.managers.stream import Stream


class GetContacts:

    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = Whalesong(
            profile=path.join(path.dirname(__file__), 'profile'),
            loadstyles=True,
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

    async def monitor_stream(self):
        self.echo('Monitor stream')
        contact_it = None
        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:
                if contact_it is None:
                    contact_it = self._driver.contacts.get_items()
                    ensure_future(self.list_contacts(contact_it))
            else:
                if contact_it is not None:
                    await self._driver.cancel_iterators()
                    contact_it = None

    async def list_contacts(self, it):
        self.echo('List contacts')
        async for contact in it:
            self.echo('Contact: {}'.format(contact))

        self.echo('List contacts finished')

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream()),
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = GetContacts()
    monitor.loop.run_until_complete(monitor.start())
