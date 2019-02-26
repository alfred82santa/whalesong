from asyncio import ensure_future, get_event_loop
from os import path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.driver_chromium import WhalesongDriver
from whalesong.managers.stream import Stream


class PresenceMonitor:

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

    async def monitor_stream(self):
        self.echo('Monitor stream')
        chat_it = None
        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:
                self._driver.display_info.set_available_permanent()

                if chat_it is None:
                    chat_it = self._driver.chats.get_items()
                    ensure_future(self.start_monitor_presences(chat_it))
            else:
                if chat_it is not None:
                    await self._driver.cancel_iterators()
                    chat_it = None

    async def start_monitor_presences(self, it):
        self.echo('Listing chats...')
        async for chat in it:
            self.echo('Starting: {}'.format(chat.name))
            ensure_future(self.monitor_chat(chat))

        self.echo('List chats finished')

    async def monitor_chat(self, chat):
        if chat.is_group:
            self.echo(f'Chat `{chat.name}` is group')
            await self._driver.chats[chat.id].presence.subscribe()

            async for chat_state in self._driver.chats[chat.id].presence.chat_states.get_items():
                ensure_future(self.monitor_chat_state(
                    chat,
                    self._driver.chats[chat.id].presence.chat_states[chat_state.id])
                )

            async for chat_state in self._driver.chats[chat.id].presence.chat_states.monitor_add():
                ensure_future(self.monitor_chat_state(
                    chat,
                    self._driver.chats[chat.id].presence.chat_states[chat_state.id])
                )

        else:
            ensure_future(self.monitor_chat_state(
                chat,
                self._driver.chats[chat.id].presence.chat_state
            ))

    async def monitor_chat_state(self, chat, chat_state_manager):
        chat_state = await chat_state_manager.get_model()

        def echo_state(type):
            self.echo(f'User {chat_state.id} is {type} in chat {chat.name} ({chat.id})')

        echo_state(chat_state.type)

        async for evt in chat_state_manager.monitor_field('type'):
            echo_state(evt['value'])

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream()),
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = PresenceMonitor()
    monitor.loop.run_until_complete(monitor.start())
