from typing import Optional

from dirty_models import EnumField, StringIdField
from io import BytesIO

from . import BaseCollectionManager, BaseModelManager
from .message import MediaMixin, MessageTypes, download_media
from ..driver import BaseWhalesongDriver
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


class StickerManager(BaseModelManager[Sticker]):
    """
    Sticker manager. It allows manage a sticker.
    """

    MODEL_CLASS = Sticker

    def send_to_chat(self, chat_id: str, quoted_msg_id: Optional[str] = None) -> Result[str]:
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

    async def download_image(self) -> BytesIO:
        """
        Download sticker's image file. It will decrypt image file using key on sticker object.

        :return: Image stream
        """
        model = await self.get_model()

        return await download_media(self._driver, model)


class StickerCollectionManager(BaseCollectionManager[StickerManager]):
    """
    Sticker collection manager. It allows manage sticker collection.
    """

    MODEL_MANAGER_CLASS = StickerManager

    def fetch(self) -> Result[None]:
        """
        Fetch all stickers. You must fetch stickers before try to us them.
        """
        return self._execute_command('fetch')


class StickerPackManager(BaseModelManager[StickerPack]):
    """
    Sticker pack manager. It allows manage a sticker pack.


    .. attribute:: stickers

        :class:`~whalesong.managers.sticker_pack.StickerCollectionManager`

        Sticker collection manager.
    """

    MODEL_CLASS = StickerPack

    def __init__(self, driver: BaseWhalesongDriver, manager_path: str = ''):
        super(StickerPackManager, self).__init__(driver=driver, manager_path=manager_path)

        self.add_submanager('stickers', StickerCollectionManager(
            driver=self._driver,
            manager_path=self._build_command('stickers')
        ))


class StickerPackCollectionManager(BaseCollectionManager[StickerPackManager]):
    """
    Sticker pack collection manager. It allows manage sticker pack collection.
    """

    MODEL_MANAGER_CLASS = StickerPackManager

    def fetch_page(self, page: int) -> Result:
        """
        Fetch a sticker pack page.
        """
        return self._execute_command('fetchPage', {'page': page})

    def fetch_all_pages(self) -> Result[bool]:
        """
        Fetch all sticker pack pages.
        """
        return self._execute_command('fetchAllPages')

    def reset(self) -> Result:
        """
        Reset sticker pack collection.
        """
        return self._execute_command('reset')

    def get_item_by_name(self, name: str) -> Result[StickerPack]:
        """
        Get sticker pack by name.

        :param name: Sticker pack name.
        :return: Sticker pack object.
        """
        return self._execute_command('getItemByName',
                                     {'name': name},
                                     result_class=self.get_item_result_class())
