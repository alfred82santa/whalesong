from typing import Optional

from dirty_models import EnumField, StringIdField

from . import BaseCollectionManager, BaseModelManager
from .message import MediaMixin, MessageTypes, download_media
from ..models import BaseModel
from ..results import Result


class Sticker(MediaMixin, BaseModel):
    type = EnumField(enum_class=MessageTypes, read_only=True, default=MessageTypes.STICKER)


class StickerPack(BaseModel):
    name = StringIdField()
    """
    Sticker pack name.
    """

    url = StringIdField()
    """
    Sticker pack url image.
    """


class StickerManager(BaseModelManager):
    """
    Sticker manager. It allows manage a sticker.
    """

    MODEL_CLASS = Sticker

    def send_to_chat(self, chat_id: str, quoted_msg_id: Optional[str] = None) -> Result:
        """
        Send this sticker to a chat.

        :param chat_id: Chat indentifier where to send sticker.
        :param quoted_msg_id: Quoted message identifier.
        :return: Message identifier.
        """

        params = {'chatId': chat_id}

        if quoted_msg_id:
            params['quotedMsgId'] = quoted_msg_id

        return self._execute_command('sendToChat', params)

    async def download_image(self):
        """
        Download sticker's image file. It will decrypt image file using key on sticker object.

        :return: Image stream
        """
        model = await self.get_model()

        return await download_media(self._driver, model)


class StickerCollectionManager(BaseCollectionManager):
    """
    Sticker collection manager. It allows manage sticker collection.
    """

    MODEL_MANAGER_CLASS = StickerManager

    def fetch(self) -> Result:
        """
        Fetch all stickers. You must fetch stickers before try to us them.
        """
        return self._execute_command('fetch')


class StickerPackManager(BaseModelManager):
    """
    Sticker pack manager. It allows manage a sticker pack.


    .. attribute:: stickers

        :class:`~whalesong.managers.sticker_pack.StickerCollectionManager`

        Sticker collection manager.
    """

    MODEL_CLASS = StickerPack

    def __init__(self, driver, manager_path=''):
        super(StickerPackManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('stickers', StickerCollectionManager(
            driver=self._driver,
            manager_path=self._build_command('stickers')
        ))


class StickerPackCollectionManager(BaseCollectionManager):
    """
    Sticker pack collection manager. It allows manage sticker pack collection.
    """

    MODEL_MANAGER_CLASS = StickerPackManager

    def fetch_page(self, page: int) -> Result:
        """
        Fetch a sticker pack page.
        """
        return self._execute_command('fetchPage', {'page': page})

    def fetch_all_pages(self) -> Result:
        """
        Fetch all sticker pack pages.
        """
        return self._execute_command('fetchAllPages')

    def reset(self) -> Result:
        """
        Reset sticker pack collection.
        """
        return self._execute_command('reset')
