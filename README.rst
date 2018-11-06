=========
Whalesong
=========

Whalesong is a python library to manage WebApps remotely.
Currently WhatsappWeb is implemented

-------------
Documentation
-------------

http://whalesong.readthedocs.io/


------------
Requirements
------------

* Python 3.6+
* Geckodriver
* Firefox 50+

........................
Development requirements
........................

* node (only for development)
* npm (only for development)
* make (only for development)

------------
Installation
------------

.. code-block:: bash

    $ pip install whalesong


--------
Features
--------

* Non blocking driver. It can do more than one thing at same time.
* Monitor feature. Python code could react to Javascript event.
* Iterator feature. Large item list are passed to Python as async iterators.
* Persistent Firefox profile.
* Easy way to build new features.
* AmpersandJS/BackboneJS models and collection monitor.
* AmpersandJS/BackboneJS field monitor.
* Monitor localStorage.
* Take screenshots (page and css elements).

.................
Whatsapp features
.................

* Monitor connection state.
* Monitor QR changes.
* Monitor stream state.
* It's able to refresh QR.
* It's able to take over session.
* List chats.
* List contacts.
* List messages
* Monitor new messages.
* Monitor unread messages.
* Monitor message acks.
* Monitor new contacts.
* Monitor new chats.
* Send text messages.
* Reply messages.
* Send VCard messages.
* Send Media (image/video/pdf) messages.
* Send seen to chats.
* Create groups
* Manage groups (add/kick/promote/demote people)

---------
Changelog
---------

.............
Version 0.5.1
.............

* Fixed bug with user chats.
* Added new command `/send` to minibot example.

.............
Version 0.5.0
.............

* Added `ensure_chat_with_contact` to chat collection manager.
  Ensure chat with a whatsapp user, if it does not exist it will be created. (Be careful with SPAM)

* Added `create_group` to chat collection manager.
* Added `block` and `unblock` methods to contact manager.
* Added group participants management: add, remove, promote, demote.
* Added group link management.


.............
Version 0.4.4
.............

* Allow extra options for Firefox driver.
* Added `leave_group`. Thx @jabolina
* Added `delete_chat`. Thx @jabolina

.............
Version 0.4.0
.............

* Removed `send_vcard` on chats. It is not possible now because WhatsappWeb changes.
* Added `send_contact` and `send_contact_phone` in order to send contacts using contact id or contact name and phone.
* Small changes and refactors.


.............
Version 0.3.0
.............

* Reduce Firefox footprint.
* Message classes.
* Improved getMessages example. Now, it downloads media files.
* Package published at Pypi.

.............
Version 0.2.0
.............

.. warning:: Command separator changed from `.` to `|`.

* Simplified code to manage models.
* Added `remove_item_by_id`, `get_length`, `get_first` and `get_last` methods to collection managers.
* Added `load_earlier_messages` and `load_all_earlier_messages` methods to chat manager.


----
TODO
----

* Tests, tests, tests.
* Documentation.
* More examples.
* Missing Whatsapp features.
* Implement scriptlet for other WebApp (maybe `Android Messages<https://messages.android.com/>`_).
* Drop Selenium and Geckodriver.
* Create/Use a small footprint headless browser with async interface (like marionette).
* Push results. Avoid continuous polling.

---------------
Getting started
---------------

............................
Install library requirements
............................

.. code-block:: bash

    $ make requirements

.........................
Build Javascript scriplet
.........................

You have to rebuild scriptlet after any change if you want to use in Python code.

.. code-block:: bash

    $ make build-js

.............
Beautify code
.............

You must to beautify code before make a pull request. Ugly code will not be accepted.

.. code-block:: bash

    $ make beautify

--------
Examples
--------

...................
Raw driver examples
...................


State monitor
=============

It monitors Stream state, Connection state and localStorage.
It prints any change on them. It takes a page screenshot on each stream state change.

It tries to own WhatsappWeb session, it means that it will restore session
if you open a new session in other browser.

On the other hand, if session is not started, it will renew QR automatically when it expires.
It will save QR image each time it changes.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/driver/statemonitor.py


Get contacts
============

It prints contact list.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/driver/getcontacts.py


Get chats
=========

It prints chat list.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/driver/getchats.py


Get messages
============

It prints message list and monitors it. So, if new messages are received it will print them.
It monitors message acknowledgments and prints them, as well.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/driver/getmessages.py


........................
Whatsapp driver examples
........................


State monitor
=============

It monitors Stream state, Connection state and localStorage.
It prints any change on them. It takes a page screenshot on each stream state change.

It tries to own WhatsappWeb session, it means that it will restore session
if you open a new session in other browser.

On the other hand, if session is not started, it will renew QR automatically when it expires.
It will save QR image each time it changes.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/statemonitor.py

Get contacts
============

It prints contact list.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/getcontacts.py


Get chats
=========

It prints chat list.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/getchats.py


Get messages
============

It prints message list and monitors it. So, if new messages are received it will print them.
It monitors message acknowledgments and prints them, as well.

It stores files and thumbnails from media messages.

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/getmessages.py


Minibot
=======

Minibot implements 4 features:

Echo
----

When a contact sends `/echo [text]` it replies with `[text]`.


Example
.......

.. code-block::

    /echo Hello!

Contact
-------

When a contact sends `/contact [contactID]` it replies with the contact in VCard format.

Example
.......

.. code-block::

    /contact 495555555555

Download
--------

When a contact sends `/download [url]` it replies with content pointed by URL (image, pdf, video).

Example
.......

.. code-block::

    /download http://example.com/image.jpg

Send
----

When a contact sends `/send [contactId] [text]` it will send `[text]` to `[contactId]`. `[contactId]` must be
a phone number with country prefix: 495555555555 where `49` is Germany prefix.

Example
.......

.. code-block::

    /send 495555555555 Hello!

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/minibot.py


-----
Legal
-----

This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp
or any of its affiliates or subsidiaries. This is an independent and unofficial software.
Use at your own risk.