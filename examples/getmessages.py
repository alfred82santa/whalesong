import mimetypes
from asyncio import ensure_future, get_event_loop
from os import mkdir, path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.managers.message import LocationMessage, MediaFrameMixin, MediaMixin, StickerMessage, TextMessage
from whalesong.managers.stream import Stream

OUTPUT_DIR = path.join(path.dirname(__file__), 'output', 'media')


class GetMessages:

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

    def echo(self, txt):
        self._print_fn(txt)

    async def check_stream(self):
        stream = await self._driver.stream.get_model()
        self.echo("Stream: {}".format(stream.stream))
        self.echo("State: {}".format(stream.state))

    async def monitor_stream(self):
        self.echo('Monitor stream')
        messages_it = None
        new_message_monitor = None
        message_ack_monitor = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:
                if messages_it is None:
                    messages_it = self._driver.messages.get_items()
                    ensure_future(self.list_messages(messages_it))

                if new_message_monitor is None:
                    new_message_monitor = self._driver.messages.monitor_new()
                    ensure_future(self.monitor_new_messages(new_message_monitor))

                if message_ack_monitor is None:
                    message_ack_monitor = self._driver.messages.monitor_field('ack')
                    ensure_future(self.monitor_message_acks(message_ack_monitor))
            else:
                if messages_it is not None:
                    messages_it = None
                    await self._driver.cancel_iterators()

                if new_message_monitor is not None:
                    self._driver.stop_monitor(new_message_monitor)
                    new_message_monitor = None

                if message_ack_monitor is not None:
                    self._driver.stop_monitor(message_ack_monitor)
                    message_ack_monitor = None

    async def list_messages(self, it):
        self.echo('List messages')
        async for message in it:
            self.echo('Message: {}'.format(message))

            if isinstance(message, MediaMixin):
                await self.download_media(message)
            elif isinstance(message, LocationMessage):
                await self.store_thumbnail(message.id, message.body)
            elif isinstance(message, TextMessage) and message.thumbnail:
                await self.store_thumbnail(message.id, message.thumbnail)

        self.echo('List messages finished')

    async def monitor_new_messages(self, it):
        self.echo('Monitor new messages')
        async for message in it:
            self.echo('New message: {}'.format(message))

            if isinstance(message, MediaMixin):
                await self.download_media(message)
            elif isinstance(message, LocationMessage):
                await self.store_thumbnail(message.id, message.body)
            elif isinstance(message, TextMessage) and message.thumbnail:
                await self.store_thumbnail(message.id, message.thumbnail)

        self.echo('Stop new messages bot')

    async def monitor_message_acks(self, it):
        self.echo('Monitor message ack')
        async for ack in it:
            self.echo('ACK: {}'.format(ack))

        self.echo('Stop message acks bot')

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream()),
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
    monitor = GetMessages()
    monitor.loop.run_until_complete(monitor.start())
