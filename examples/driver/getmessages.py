from asyncio import ensure_future, wait

from os import path

from whalesong.driver_firefox import WhalesongDriver
from whalesong.results import IteratorResult, MonitorResult


class GetMessages:

    def __init__(self, print_fn=print, loop=None):
        self._print_fn = print_fn
        self._driver = WhalesongDriver(profile=path.join(path.dirname(__file__), '..', 'profile'),
                                       # loadstyles=False,
                                       loop=loop)

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
        messages_it = None
        new_message_monitor = None
        message_ack_monitor = None

        async for evt in self._driver.execute_command('stream|monitorField',
                                                      {'field': 'stream'},
                                                      result_class=MonitorResult):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == 'CONNECTED':
                if messages_it is None:
                    messages_it = self._driver.execute_command('messages|getItems',
                                                               result_class=IteratorResult)
                    ensure_future(self.list_messages(messages_it))

                if new_message_monitor is None:
                    new_message_monitor = self._driver.execute_command('messages|monitorNew',
                                                                       result_class=MonitorResult)
                    ensure_future(self.monitor_new_messages(new_message_monitor))

                if message_ack_monitor is None:
                    message_ack_monitor = self._driver.execute_command('messages|monitorField',
                                                                       {'field': 'ack'},
                                                                       result_class=MonitorResult)
                    ensure_future(self.monitor_message_acks(message_ack_monitor))
            else:
                if messages_it is not None:
                    messages_it = None
                    await self._driver.cancel_iterators()

                if new_message_monitor is not None:
                    self._driver.execute_command('stopMonitor',
                                                 {'monitorId': new_message_monitor.result_id})
                    new_message_monitor = None

                if message_ack_monitor is not None:
                    self._driver.execute_command('stopMonitor',
                                                 {'monitorId': message_ack_monitor.result_id})
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

        self.echo('Stop new messages bot')

    async def monitor_message_acks(self, it):
        self.echo('Monitor message ack')
        async for ack in it:
            self.echo('ACK: {}'.format(ack))

        self.echo('Stop message acks bot')

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
    monitor = GetMessages()
    monitor.loop.run_until_complete(monitor.start())
