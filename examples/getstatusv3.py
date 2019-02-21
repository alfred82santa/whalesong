import mimetypes
from asyncio import ensure_future

from os import mkdir, path

from whalesong import Whalesong
from whalesong.managers.stream import Stream

OUTPUT_DIR = path.join(path.dirname(__file__), 'output', 'media')


class GetStatuses:
    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = Whalesong(
            profile=path.join(path.dirname(__file__), 'profile'),
            loadstyles=True,
            loop=loop
        )

        try:
            mkdir(OUTPUT_DIR)
        except FileExistsError:
            pass

    @property
    def loop(self):
        return self._driver.loop

    def echo(self, text):
        self._print_fn(text)

    async def check_stream(self):
        stream = await self._driver.stream.get_model()
        self.echo("Stream: {}".format(stream.stream))
        self.echo("State: {}".format(stream.state))

    async def monitor_stream(self):
        self.echo('Monitor stream')
        statuses_it = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))
 
            if evt['value'] == Stream.Stream.CONNECTED:
                if statuses_it is None:
                    statuses_it = self._driver.status_v3.get_items()
                    ensure_future(self.list_statuses(statuses_it))

            else:
                if statuses_it is not None:
                    statuses_it = None
                    await self._driver.cancel_iterators()

    async def list_statuses(self, it):
        self.echo('List statuses')

        async for status in it:
            async for msg in self._driver.status_v3[status.id].get_submanager('msgs').get_items():
                await self._driver.status_v3[status.id].send_read_status(msg.id)

    async def start(self):
        await self._driver.start()

        ensure_future(self.check_stream())
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = GetStatuses()
    monitor.loop.run_until_complete(monitor.start())
