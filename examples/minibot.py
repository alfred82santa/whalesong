from asyncio import ensure_future, get_event_loop
from io import BytesIO
from os import path
from random import choice
from signal import SIGINT, SIGTERM

from aiohttp import ClientSession, hdrs

from whalesong import Whalesong
from whalesong.managers.message import MessageTypes
from whalesong.managers.stream import Stream

OUTPUT_DIR = path.join(path.dirname(__file__), 'output')


class Minibot:

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

    async def download_url(self, url):
        async with ClientSession() as session:
            async with session.get(url) as resp:
                content_type = resp.headers.get(hdrs.CONTENT_TYPE)
                data = BytesIO(await resp.read())

        if content_type and ';' in content_type:
            content_type = content_type[:content_type.index(';')]

        return content_type, data

    async def monitor_stream(self):
        self.echo('Monitor stream')
        new_message_monitor = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:
                if new_message_monitor is None:
                    new_message_monitor = self._driver.messages.monitor_new()
                    ensure_future(self.monitor_new_messages(new_message_monitor))
            else:
                if new_message_monitor is not None:
                    self._driver.stop_monitor(new_message_monitor)
                    new_message_monitor = None

    async def monitor_new_messages(self, it):
        self.echo('Monitor new messages')
        async for message in it:
            try:
                if message.type == MessageTypes.CHAT:
                    if message.body.startswith('/echo '):
                        ensure_future(self.make_echo(message))
                    elif message.body.startswith('/contact '):
                        ensure_future(self.make_contact(message))
                    elif message.body.startswith('/download '):
                        ensure_future(self.make_download(message))
                    elif message.body.startswith('/send '):
                        ensure_future(self.make_message(message))
                    elif message.body.startswith('/link '):
                        ensure_future(self.make_link(message))
                    elif message.body.startswith('/exist '):
                        ensure_future(self.make_exists(message))
                    elif message.body.startswith('/sticker '):
                        ensure_future(self.make_sticker(message))
                    elif message.body.startswith('/status '):
                        ensure_future(self.make_status(message))
                    elif message.body.startswith('/pushname '):
                        ensure_future(self.make_pushname(message))

            except Exception as ex:
                self.echo('Ignoring message {} because error : {}'.format(message.id, ex))

        self.echo('Stop new messages bot')

    async def make_echo(self, message):
        self._driver.chats[message.chat.id].send_seen()
        self.echo(message.chat.id)
        text = message.body[len('/echo '):].strip()
        self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_text(text,
                                                                                                message.id)))

    async def make_contact(self, message):
        self._driver.chats[message.chat.id].send_seen()
        contact_id = message.body[len('/contact '):].strip()

        contact = await self._driver.contacts.get_item_by_id(contact_id)

        self.echo('Sent message (by phone): {}'.format(
            await self._driver.chats[message.chat.id].send_contact_phone(
                contact.formatted_name,
                contact.userid,
                message.id
            )
        ))

        self.echo('Sent message (by contact id): {}'.format(
            await self._driver.chats[message.chat.id].send_contact(
                contact_id,
                message.id
            )
        ))

    async def make_download(self, message):
        self._driver.chats[message.chat.id].send_seen()
        url = message.body[len('/download '):].strip()

        content_type, data = await self.download_url(url)

        filename = url
        if '?' in filename:
            filename = filename[:filename.index('?')]
        if '#' in filename:
            filename = filename[:filename.index('#')]
        _, filename = filename.rstrip('/').rsplit('/', 1)

        self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_media(data,
                                                                                                 content_type,
                                                                                                 filename,
                                                                                                 url,
                                                                                                 message.id)))

    async def make_message(self, message):
        self._driver.chats[message.chat.id].send_seen()
        self.echo(message.chat.id)
        cmd = message.body[len('/send '):].strip()
        contact_id, text = cmd.split(' ')
        if not contact_id.endswith('@c.us'):
            contact_id = f'{contact_id.strip()}@c.us'

        chat = await self._driver.chats.ensure_chat_with_contact(contact_id=contact_id)
        msg = await self._driver.chats[chat.id].send_text(text)
        self.echo('Sent message: {}'.format(msg))

        await self._driver.chats[message.chat.id].send_text(f'Message sent to {chat.id}')

    async def make_link(self, message):
        self._driver.chats[message.chat.id].send_seen()
        self.echo(message.chat.id)
        text = message.body[len('/link '):].strip()
        self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_text(text)))

    async def make_exists(self, message):
        self._driver.chats[message.chat.id].send_seen()

        contact_id = message.body[len('/exist '):].strip()

        if not contact_id.endswith('@c.us'):
            contact_id = f'{contact_id.strip()}@c.us'

        exists = await self._driver.wap.query_exist(contact_id=contact_id)
        self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_text(
            'It exists' if exists else 'It does not exist',
            message.id
        )))

    async def make_sticker(self, message):
        self._driver.chats[message.chat.id].send_seen()

        sticker_pack_name = message.body[len('/sticker '):].strip()

        if sticker_pack_name == 'list':
            ensure_future(self.make_sticker_pack_list(message))
            return

        await self._driver.sticker_packs.fetch_all_pages()

        try:
            sticker_pack = await self._driver.sticker_packs.get_item_by_name(sticker_pack_name)
        except ModuleNotFoundError:
            self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_text(
                f'Sticker pack "{sticker_pack_name}" does not exist',
                message.id
            )))

            return

        await self._driver.sticker_packs[sticker_pack.id].stickers.fetch()

        sticker = choice([s async for s in self._driver.sticker_packs[sticker_pack.id].stickers.get_items()])

        msg = await self._driver.sticker_packs[sticker_pack.id].stickers[sticker.id].send_to_chat(
            chat_id=message.chat.id,
            quoted_msg_id=message.id
        )

        self.echo(f'Sent message: {msg}')

    async def make_sticker_pack_list(self, message):
        await self._driver.sticker_packs.fetch_all_pages()

        async for sticker_pack in self._driver.sticker_packs.get_items():
            content_type, image = await self.download_url(sticker_pack.url)

            self.echo('Sent message: {}'.format(await self._driver.chats[message.chat.id].send_media(
                image,
                content_type,
                caption=sticker_pack.name
            )))

    async def make_status(self, message):
        new_status = message.body[len('/status '):].strip()
        await self._driver.status.set_my_status(new_status=new_status)
        self.echo(f'Set status: {new_status}')

    async def make_pushname(self, message):
        new_pushname = message.body[len('/pushname '):].strip()
        await self._driver.conn.update_pushname(name=new_pushname)
        self.echo(f'Set pushname: {new_pushname}')

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    bot = Minibot()
    bot.loop.run_until_complete(bot.start())
