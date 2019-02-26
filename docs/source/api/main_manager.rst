=================
Whalesong Service
=================

.. autoclass:: whalesong.Whalesong

    .. attribute:: storage

        :class:`~whalesong.managers.storage.StorageManager`

        Manager for local storage.

    .. attribute:: stream

        :class:`~whalesong.managers.stream.StreamManager`

        Manager for stream object.

    .. attribute:: conn

        :class:`~whalesong.managers.conn.ConnManager`

        Manager for connection object

    .. attribute:: contacts

        :class:`~whalesong.managers.contact.ContactCollectionManager`

        Manager for contact collection.

    .. attribute:: chats

        :class:`~whalesong.managers.chat.ChatCollectionManager`

        Manager for chat collection.

    .. attribute:: messages

        :class:`~whalesong.managers.message.MessageCollectionManager`

        Manager for messages collection.

    .. attribute:: wap

        :class:`~whalesong.managers.wap.WapManager`

        Manager for wap object.


    .. attribute:: sticker_packs

        :class:`~whalesong.managers.sticker_pack.StickerPackCollectionManager`

        Manager for sticker pack collection.


    .. attribute:: status

        :class:`~whalesong.managers.status.StatusCollectionManager`

        Manager for status collection.


    .. attribute:: display_info

        :class:`~whalesong.managers.display_info.DisplayInfoManager`

        Manager for display information.


    .. attribute:: live_locations

        :class:`~whalesong.managers.live_location.LiveLocationCollectionManager`

        Manager for live locations collection.


    .. attribute:: mutes

        :class:`~whalesong.managers.mute.MuteCollectionManager`

        Manager for mutes collection.

    .. attribute:: status_v3

        :class:`~whalesong.managers.status_v3.StatusV3CollectionManager`

        Manager for statuses version 3 (Stories) collection.
