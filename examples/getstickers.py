import mimetypes
from asyncio import ensure_future, get_event_loop
from os import mkdir, path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.managers.stream import Stream

OUTPUT_DIR = path.join(path.dirname(__file__), 'output', 'media')


class GetStickers:

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
        try:
            self.echo("Stream: {}".format(stream.stream))
            self.echo("State: {}".format(stream.state))
        except AttributeError:
            self.echo("Error: {}".format(stream))

    async def monitor_stream(self):
        self.echo('Monitor stream')

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:
                ensure_future(self.fetch_sticker_packs())

    async def fetch_sticker_packs(self):
        self.echo('Fetching all sticker packs')
        await self._driver.sticker_packs.fetch_all_pages()

        async for sticker_pack in self._driver.sticker_packs.get_items():
            await self._driver.sticker_packs[sticker_pack.id].stickers.fetch()
            await self.download_all_sticker(sticker_pack)

    async def download_all_sticker(self, sticker_pack):
        self.echo(f'Download all stickers from sticker pack {sticker_pack.name}')
        async for sticker in self._driver.sticker_packs[sticker_pack.id].stickers.get_items():
            self.echo(f'Download sticker {sticker.id} from sticker pack {sticker_pack.name}')
            await self.download_media(sticker_pack, sticker)

        self.echo(f'All stickers download from sticker pack {sticker_pack.name}')

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream()),
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()

    async def download_media(self, sticker_pack, sticker):
        media_data = await self._driver.sticker_packs[sticker_pack.id].stickers[sticker.id].download_image()

        ext = mimetypes.guess_extension(sticker.mimetype, strict=False)

        sticker_id = sticker.id.replace('/', '_').replace('\\', '_').replace('=', '_')

        await self._store_media(f'{sticker_pack.name}-{sticker_id}{ext}', media_data.read())

    async def _store_media(self, filename, filedata):
        filepath = path.join(OUTPUT_DIR, filename)

        self.echo('Storing file {}'.format(filepath))

        with open(filepath, 'wb') as f:
            f.write(filedata)


if __name__ == '__main__':
    monitor = GetStickers()
    monitor.loop.run_until_complete(monitor.start())
