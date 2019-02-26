import mimetypes
from asyncio import ensure_future, get_event_loop
from os import mkdir, path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.managers.message import MediaFrameMixin, MediaMixin, StickerMessage
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
                    await self._driver.status_v3.sync()
                    statuses_it = self._driver.status_v3.get_unexpired(unread=True)
                    ensure_future(self.list_unread_statuses(statuses_it))

            else:
                if statuses_it is not None:
                    statuses_it = None
                    await self._driver.cancel_iterators()

    async def list_unread_statuses(self, it):
        self.echo('List statuses')

        async for status in it:
            print('Seeing all statuses from [{}]'.format(status.id))
            async for msg in self._driver.status_v3[status.id].get_submanager('msgs').get_items():
                await self._driver.status_v3[status.id].send_read_status(msg.id)
                if isinstance(msg, MediaMixin):
                    self.echo('Saving status media from [{}]'.format(status.id))
                    await self.download_media(msg)

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream())
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()

    async def download_media(self, message):
        if isinstance(message, MediaFrameMixin) and not isinstance(message, StickerMessage):
            await self.store_thumbnail(message.id, message.body)

        media_data = await self._driver.messages.download_media(message)

        mimetype = message.mimetype

        if ';' in mimetype:
            mimetype, _ = mimetype.split(';', 1)

        ext = mimetypes.guess_extension(mimetype, strict=False)

        await self._store_media('{}{}'.format(message.id, ext or '.bin'), media_data.read())

    async def store_thumbnail(self, message_id, image_data):
        await self._store_media('{}_thumb.jpg'.format(message_id), image_data)

    async def _store_media(self, filename, filedata):
        filepath = path.join(OUTPUT_DIR, filename)

        self.echo('Storing file {}'.format(filepath))

        with open(filepath, 'wb') as f:
            f.write(filedata)


if __name__ == '__main__':
    monitor = GetStatuses()
    monitor.loop.run_until_complete(monitor.start())
