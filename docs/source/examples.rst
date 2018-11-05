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

.. code-block:: text

    /echo Hello!

Contact
-------

When a contact sends `/contact [contactID]` it replies with the contact in VCard format.

Example
.......

.. code-block:: text

    /contact 495555555555

Download
--------

When a contact sends `/download [url]` it replies with content pointed by URL (image, pdf, video).

Example
.......

.. code-block:: text

    /download http://example.com/image.jpg

Send
----

When a contact sends `/send [contactId] [text]` it will send `[text]` to `[contactId]`. `[contactId]` must be
a phone number with country prefix: 495555555555 where `49` is Germany prefix.

Example
.......

.. code-block:: text

    /send 495555555555 Hello!

.. code-block:: bash

    $ PYTHONPATH=.:$PYTHONPATH python3 examples/minibot.py
