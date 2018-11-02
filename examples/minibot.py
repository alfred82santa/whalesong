from asyncio import ensure_future

from aiohttp import ClientSession, hdrs
from io import BytesIO
from os import path

from whalesong import Whalesong
from whalesong.managers.message import MessageTypes

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

    async def monitor_stream(self):
        self.echo('Monitor stream')
        new_message_monitor = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == 'CONNECTED':
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

        async with ClientSession() as session:
            async with session.get(url) as resp:
                content_type = resp.headers.get(hdrs.CONTENT_TYPE)
                data = BytesIO(await resp.read())

        if content_type and ';' in content_type:
            content_type = content_type[:content_type.index(';')]

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

    async def start(self):
        await self._driver.start()

        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    bot = Minibot()
    bot.loop.run_until_complete(bot.start())
