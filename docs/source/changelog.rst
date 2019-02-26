=========
Changelog
=========

-------------
Version 0.9.0
-------------

* Added Whatsapp Stories management (StatusV3). Thx to @jabolina.
* Added logout feature. Thx to @parthibd.
* Fixed stop/start driver (see `Issue #82 <https://github.com/alfred82santa/whalesong/issues/82>`_). Thx to @parthibd.
* Fixed Firefox driver initialization in order to allow more than one process. Thx to @parthibd.
* Fixed `wait_until_stop` driver method.
* Examples now stop gracefully.

-------------
Version 0.8.4
-------------

* Fixed requirements installation out of virtual enviorment. Thx to @Theblood.
* Enabled media codecs on Firefox profile template.
* Fixed problems with live location. `Issue #73 <https://github.com/alfred82santa/whalesong/issues/73>`_
* Fixed problem monitoring models.
* Added new examples: `getlivelocations-chromium.py` and `getlivelocations.py`

-------------
Version 0.8.2
-------------

* Fixed QR screenshot on Firefox.

-------------
Version 0.8.1
-------------

* Fixed Wap object discovery. Thx to @jabolina.
* Fixed screenshot method.
* Added Chromium version of some examples.

-------------
Version 0.8.0
-------------

* Live locations management.
* Mutes management.
* Revoke messages. Delete messages for others.
* Minimized scriptlet.

-------------
Version 0.7.2
-------------

* Capability to manage display information. It allows to mark current user as available in other
  to get presences from other users.

  There are some limitations. Look at :class:`documentation <whalesong.managers.presence.PresenceCollectionManager>`.

* Minor fixes.

* Remove some debug messages.

* Fix issues with presence.

* Added manual ping-pong for Chromium backend.

* Modified `presencemonitor-chromium.py` and `presencemonitor.py` examples in order to get presences
  permanently.

-------------
Version 0.7.1
-------------

* Fixed Chromium driver.
* Forced Websockets 6.0
* Added new example `presencemonitor-chromium.py`. It is same than `presencemonitor.py` but using Chromium.

-------------
Version 0.7.0
-------------

* Added support for Chromium.
* Added support for backends that are able to push results.
* Defined Connection model.
* Added new connection's method `updatePushname`.
* Defined Stream model and enumerations.
* Added Presence manager.
* Added new example: `presencemonitor.py`. It monitor user presences.
* Simplified some code.
* Fields' value are mapped on monitors.
* Profile and group's picture management.

* New chat methods: `pin`, `unpin`, `archive`, `unarchive`,
  `set_group_description`, `star_messages`, `unstar_messages`, `send_not_spam`,
  `send_spam_report`, `can_archive`, `can_send` and `can_pin`.

* New chat collection method: `forward_messages_to_chats`.

* New message methods: `can_star`, `star` and `unstar`.

* Status (old one) management.

* New commands in `minibot.py` example: `/status` and `/pushname`.

-------------
Version 0.6.0
-------------

* Ability to get message information, it includes message acks (with timestamps).
  In addition, it is possible to monitor ack changes.

  You must fetch message info before be able to monitor it.

  .. code-block:: python3

     msg_info: MessageInfo = await driver.messages[message_id].fetch_info()

  And in order to monitor acks (message information changes):

  .. code-block:: python3

     async for event in driver.messages[message_id].info.monitor_model():
        print(event)

* Added Sticker message.

* Load and send stickers.

* Better type hinting.

* Better documentation.

* Added new command to `minibot.py` example: `/sticker`.

* Added new example: `getstickers.py`. It downloads all stickers registered.


-------------
Version 0.5.3
-------------

* Add `query_exist` method to wap manager in order to get whether a contact indentifier exists or not.

* When send a text message with an url it will try to get link preview and attach to message.
  It's not compatible with quoted messages.

* Added two new commands to `minibot.py` example: `/link` and `/exist`.

-------------
Version 0.5.2
-------------

* Fixed bug when sending docs. Thx to @jabolina.
* Added `set_subject` method to chat manager in order to be able to change group title.
* Added `mark_composing` method to chat manager in order to show "typing..." message.
* Added `mark_recording` method to chat manager in order to show "recording audio..." message.
* Added `mark_paused` method to chat manager in order to remove "typing..." or "recording audio..." message.

-------------
Version 0.5.1
-------------

* Fixed bug with user chats.
* Added new command `/send` to minibot example.

-------------
Version 0.5.0
-------------

* Added `ensure_chat_with_contact` to chat collection manager.
  Ensure chat with a whatsapp user, if it does not exist it will be created. (Be careful with SPAM)

* Added `create_group` to chat collection manager.
* Added `block` and `unblock` methods to contact manager.
* Added group participants management: add, remove, promote, demote.
* Added group link management.


-------------
Version 0.4.4
-------------

* Allow extra options for Firefox driver.
* Added `leave_group`. Thx to @jabolina.
* Added `delete_chat`. Thx to @jabolina.

-------------
Version 0.4.0
-------------

* Removed `send_vcard` on chats. It is not possible now because WhatsappWeb changes.
* Added `send_contact` and `send_contact_phone` in order to send contacts using contact id or contact name and phone.
* Small changes and refactors.


-------------
Version 0.3.0
-------------

* Reduce Firefox footprint.
* Message classes.
* Improved getMessages example. Now, it downloads media files.
* Package published at Pypi.

-------------
Version 0.2.0
-------------

.. warning:: Command separator changed from `.` to `|`.

* Simplified code to manage models.
* Added `remove_item_by_id`, `get_length`, `get_first` and `get_last` methods to collection managers.
* Added `load_earlier_messages` and `load_all_earlier_messages` methods to chat manager.
