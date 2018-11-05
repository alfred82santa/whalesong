=========
Changelog
=========

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
* Added `leave_group`. Thx @jabolina
* Added `delete_chat`. Thx @jabolina

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
