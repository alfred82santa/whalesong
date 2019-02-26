from asyncio import ensure_future, get_event_loop
from os import path
from signal import SIGINT, SIGTERM

from whalesong import Whalesong
from whalesong.driver_chromium import WhalesongDriver
from whalesong.managers.stream import Stream


class GetLiveLocations:

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
        live_loc_it = None
        new_message_monitor = None
        message_ack_monitor = None

        async for evt in self._driver.stream.monitor_field('stream'):
            self.echo('Stream value: {}'.format(evt['value']))

            if evt['value'] == Stream.Stream.CONNECTED:

                if live_loc_it is None:
                    live_loc_it = self._driver.live_locations.get_items()
                    ensure_future(self.list_live_locations(live_loc_it))

                if new_message_monitor is None:
                    new_live_locations = self._driver.live_locations.monitor_add()
                    ensure_future(self.monitor_new_live_locations(new_live_locations))

            else:
                if live_loc_it is not None:
                    live_loc_it = None
                    await self._driver.cancel_iterators()

                if new_message_monitor is not None:
                    self._driver.stop_monitor(new_message_monitor)
                    new_message_monitor = None

                if message_ack_monitor is not None:
                    self._driver.stop_monitor(message_ack_monitor)
                    message_ack_monitor = None

    async def list_live_locations(self, it):
        self.echo('List live locations')
        async for live_location in it:
            self.echo('Live location: {}'.format(live_location))
            ensure_future(self.monitor_live_location(live_location))

        self.echo('List messages finished')

    async def monitor_new_live_locations(self, it):
        self.echo('Monitor live locations')
        async for live_location in it:
            self.echo('New live location: {}'.format(live_location))
            ensure_future(self.monitor_live_location(live_location))

    async def monitor_live_location(self, live_location):
        self._driver.live_locations[live_location.id].subscribe()

        for participant in live_location.participants:
            ensure_future(self.monitor_participant(live_location, participant))

        async for participant in self._driver.live_locations[live_location.id].participants.monitor_add():
            ensure_future(self.monitor_participant(live_location, participant))

    async def monitor_participant(self, live_location, participant):
        async for new_part in self._driver.live_locations[live_location.id] \
                .participants[participant.id].monitor_model():
            self.echo('Participant at live location `{}` now are in {}@{}'.format(live_location.id,
                                                                                  new_part.lat,
                                                                                  new_part.lng))

    async def start(self):
        await self._driver.start()

        loop = get_event_loop()
        loop.add_signal_handler(SIGINT, lambda *args: ensure_future(self._driver.stop()))
        loop.add_signal_handler(SIGTERM, lambda *args: ensure_future(self._driver.stop()))

        ensure_future(self.check_stream()),
        ensure_future(self.monitor_stream())

        await self._driver.wait_until_stop()


if __name__ == '__main__':
    monitor = GetLiveLocations()
    monitor.loop.run_until_complete(monitor.start())
