=========
Whalesong
=========

Whalesong is a python library to manage WebApps remotely.
Currently WhatsappWeb is implemented

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


--------
Examples
--------

...................
Raw driver examples
...................


Status monitor
==============

It monitors Stream state, Connection state and localStorage.
It prints any change on them. It takes a page screenshot on each stream state change.

It tries to own WhatsappWeb session, it means that it will restore session
if you open a new session in other browser.

On the other hand, if no session is not started, it will renew QR automatically when it expires.
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