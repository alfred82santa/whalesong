from asyncio import ensure_future

from os import path

from whalesong import Whalesong


class GetMessages:

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
        messages_it = None
        new_message_monitor = None
        message_ack_monitor = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == 'CONNECTED':
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

        self.echo('List messages finished')

    async def monitor_new_messages(self, it):
        self.echo('Monitor new messages')
        async for message in it:
            self.echo('New message: {}'.format(message))

        self.echo('Stop new messages monitor')

    async def monitor_message_acks(self, it):
        self.echo('Monitor message ack')
        async for ack in it:
            self.echo('ACK: {}'.format(ack))

        self.echo('Stop message acks monitor')

    async def start(self):
        await self._driver.start()

        ensure_future(self.check_stream()),
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = GetMessages()
    monitor.loop.run_until_complete(monitor.start())
