=========
Whalesong
=========

Whalesong is an asyncio python library to manage WebApps remotely.
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


.. include:: docs/source/features.rst


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
* Powered by AsyncIO.

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
* Auto load link previews
* Allow to check whether a contact is registered on Whatsapp.
* Load and send stickers (even with a quoted message).

---------
Changelog
---------

See `documentation <https://whalesong.readthedocs.io/en/latest/changelog.html>`_

----
TODO
----

* Tests, tests, tests.
* Documentation.
* More examples.
* Missing Whatsapp features.
* Implement scriptlet for other WebApp (maybe `Android Messages <https://messages.android.com/>`_).
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

You must beautify code before to make a pull request. Ugly code will not be accepted.

.. code-block:: bash

    $ make beautify

--------
Examples
--------

See `documentation <https://whalesong.readthedocs.io/en/latest/examples.html>`_


-----
Legal
-----

This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp
or any of its affiliates or subsidiaries. This is an independent and unofficial software.
Use at your own risk.