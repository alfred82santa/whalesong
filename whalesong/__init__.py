from whalesong.managers.chat import ChatCollectionManager
from whalesong.managers.conn import ConnManager
from whalesong.managers.contact import ContactCollectionManager
from whalesong.managers.message import MessageCollectionManager
from whalesong.managers.storage import StorageManager
from whalesong.managers.stream import StreamManager
from .driver import WhalesongDriver
from .managers import BaseManager


__version__ = '0.1.0'


class Whalesong(BaseManager):

    def __init__(self, profile=None, loadstyles=False, headless=False, loop=None):
        super(Whalesong, self).__init__(WhalesongDriver(profile=profile,
                                                        loadstyles=loadstyles,
                                                        headless=headless,
                                                        loop=loop))

        self._submanagers['storage'] = StorageManager(self._driver)
        self._submanagers['stream'] = StreamManager(self._driver)
        self._submanagers['conn'] = ConnManager(self._driver)
        self._submanagers['contact'] = ContactCollectionManager(self._driver)
        self._submanagers['chat'] = ChatCollectionManager(self._driver)
        self._submanagers['message'] = MessageCollectionManager(self._driver)
