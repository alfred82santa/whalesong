=========
Changelog
=========

---------------------------
Version 0.6.0 (in progress)
---------------------------

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
