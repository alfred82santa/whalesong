
.. |badge-python-versions| image:: https://img.shields.io/pypi/pyversions/whalesong.svg
   :alt: Python versions


.. |badge-version| image:: https://img.shields.io/pypi/v/whalesong.svg
   :alt: Last version
   :target: https://pypi.org/project/whalesong/

.. |badge-license| image:: https://img.shields.io/pypi/l/whalesong.svg
   :alt: License


.. |badge-status| image:: https://img.shields.io/pypi/status/whalesong.svg
   :alt: Status

|badge-status| |badge-license| |badge-version| |badge-python-versions|

.. warning::

   **NEW VERSION 0.7.0**

   With new version some new requirements have been defined and some API change have been
   committed.

   Version 0.7.0 introduces new driver for Chromium browser. It has required some changes on base
   driver's API. It should not affect anyone. But be aware.


.. warning::

   **NEW VERSION 0.7.0**

   Stream model now uses enumerations. It means that if you check stream states
   you must be aware that they are not a string anymore, now they are enumerations. Look at
   :class:`documentation <whalesong.managers.stream.Stream>`.


=========
Whalesong
=========

Whalesong is an asyncio python library to manage WebApps remotely.
Currently WhatsappWeb is implemented

-------------
Documentation
-------------

http://whalesong.readthedocs.io/


-------------------
Binary Requirements
-------------------

* Python 3.6+

.............
Using Firefox
.............

* Geckodriver
* Firefox 50+

..............
Using Chromium
..............

* Execute this after installation:

  .. code-block:: bash

     $ pyppeteer-install


........................
Development requirements
........................

* node (only for development)
* npm (only for development)
* make (only for development)

------------
Installation
------------

Starting with version `0.7.0` Whalesong introduces new `browsers backends <browser_backends>`_. It means you must
decide which browser backend you want to use. So, depending on it:

.. tip::

   You could install both with no problems.

.............
Using Firefox
.............

.. code-block:: bash

   $ pip3 install whalesong[firefox]


.. _using_chromium:

..............
Using Chronium
..............


.. code-block:: bash

   $ pip3 install whalesong[chromium]


If you choose Chromium backend, you should execute this after installation:

.. code-block:: bash

   $ pyppeteer-install

It will download a patched Chromium distribution needed for that backend.

--------
Features
--------

* Non blocking driver. It can do more than one thing at same time.
* Monitor feature. Python code could react to Javascript event.
* Iterator feature. Large item list are passed to Python as async iterators.
* Persistent browser profile.
* Easy way to build new features.
* AmpersandJS/BackboneJS models and collection monitor.
* AmpersandJS/BackboneJS field monitor.
* Monitor localStorage.
* Take screenshots (page and css elements).
* Powered by AsyncIO.
* Firefox backend.
* Chromium backend.

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
* Presence monitor.
* Profile and group's picture management.
* (Un)Pin and (un)archive chats.
* Report spam.
* (Un)Star messages.
* Status management.
* Pushname management.
* Display information management.
* Live location management.
* Mutes management.
* It's able to revoke messages (delete messages for others).
* List and manage WhatsApp Status version 3 (Stories).

---------
Changelog
---------

See `documentation <https://whalesong.readthedocs.io/en/latest/changelog.html>`_

----
TODO
----

* Tests, tests, tests.
* Documentation. (`Work in progress <https://whalesong.readthedocs.io>`_)
* More examples.
* Missing Whatsapp features. (Work in progress)
* Implement scriptlet for other WebApp (maybe `Android Messages <https://messages.android.com/>`_).
* Drop Selenium and Geckodriver. (Work in progress)
* Create/Use a small footprint headless browser with async interface (like marionette). (Work in progress)
* Push results. Avoid continuous polling. (Work in progress)


.. _browser_backends:

----------------
Browser backends
----------------

Whalesong use a browser backend in order to execute a WebApp (currently only WhatsAppWeb). All backends have
an interface to manage webviews and that is what Whalesong use to manage applications. That interface change
depending on browser, but there is a standard interface called
`WebDriver <https://developer.mozilla.org/en-US/docs/Web/WebDriver>`_. Firsts Whalesong versions used to use a
`Selenium <https://www.seleniumhq.org/>`_ library in order to communicate with Firefox browser.
This backend is the default one for now, **but it will be deprecated in next versions and removed in version 1.0**.

...............
Firefox backend
...............

It was the first backend developed. It uses `Selenium <https://www.seleniumhq.org/>`_ library and
`Geckodriver <https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/>`_ to communicate with
Firefox process. It is the most tested (the most, but not well).


Pros
====

* Tested (more or less).
* Use Firefox (I prefer it in front Chromium).

Contras
=======

* Selenium is a huge library. It is wonderful for what it was created, but not for Whalsong.
* Selenium is a synchronous library. It is a problem, because Whalesong is an asynchronous
  library. It means, Whalesong creates a thread pool to communicate with Selenium.

* We need Geckodriver. Firefox does not implement Webdriver protocol by itself. Firefox has its
  own protocol called `Marionette <https://firefox-source-docs.mozilla.org/testing/marionette/marionette/Intro.html>`_.
  So Geckodriver is used as proxy between Webdriver protocol and Marionette protocol.

* As Webdriver is a synchronous protocol. Whalesong must poll continuously to Firefox in order to get new events.
  There is no way to make Firefox notify Whalesong proactively. It means, Whalesong is polling for new results
  continuously, with an interval (by default 0.5 seconds).



.. note::

    **There is only one way for the Firefox backend to survive:**

    Drop Selenium, drop Geckodriver, implement Marionette protocol directly and implement a notification
    system (I'm not sure it is possible in Marionette, currently).


How to use
==========

Currently Firefox backend is the default one. But it will change on next versions. So, in order to ensure you use
Firefox backend you must instantiate Whalesong with proper driver.

.. code-block:: python3

   from whalesong import Whalesong
   from whalesong.driver_firefox import WhalesongDriver

   driver = WhalesongDriver(profile='/path/to/your/firefox/profile')
   whaleapp = Whalesong(driver=driver)

................
Chromium backend
................

It is the new one. It is implemented using `Pyppetter <https://github.com/miyakogi/pyppeteer>`_ which is inspired
on `Puppetter <https://pptr.dev/>`_ (a `node` library to control Chromium headless, mainly, for testing). It uses
`Devtools protocol <https://chromedevtools.github.io/devtools-protocol/>`_ in order to communicate with the browser.
It is an asynchronous protocol over websocket.

Pros
====

* No more polling! When a result is produced it will send proactively to Whalesong. No more `sleeps`, no more waitings.
* Small footprint (at least, it looks like, even being Chromium).
* No extra processes (No more Geckodriver).
* Application mode. No tabs, no URL field.
* No huge libraries (No more Selenium).
* No more threads in order to communicate with synchronous libraries.

Contras
=======

* It is Chromium. It uses Blink: over-vitaminized Webkit render. A memory eater.
* Currently Pypperter has a bug. It makes to loose connection after 20 seconds. It is resolved in
  `miyakogi/pyppeteer/#160 <https://github.com/miyakogi/pyppeteer/pull/160>`_ but is not approved
  yet (some test errors).

* It uses a patched Chromium version from Puppetter. Whalesong needs this patch because it uses `Runtime.addBinding`
  command. It is not available in regular stable version. So, you must `download it <using_chromium>`_ before
  use the backend.

* Poorly tested.

* There is a bug in Chromium under Wayland. It makes impossible to get WhastappWeb QR when
  Chromium is executed with window (no headless).

How to use
==========

In order to use Chromium backend you must inject Chromium driver to Whalesong service constructor.

.. code-block:: python3

   from whalesong import Whalesong
   from whalesong.driver_chromium import WhalesongDriver

   driver = WhalesongDriver(profile='/path/to/your/chromium/profile')
   whaleapp = Whalesong(driver=driver)

..............
Other backends
..............

No, there are no other backends. But I'm thinking about other possibilities:

* Create a small footprint webview using Webkit directly (GTK or QT ways are not an option).
* Create a small footprint webview using Servo directly (I want to learn rust language).

**Of course, any contribution will be welcome (so much).**

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

----------------
Related projects
----------------

............
whalesong-js
............

Port of Whalesong to Node.js.

**Author:** `@jabolina <https://github.com/jabolina>`_

**Repository:** https://github.com/jabolina/whalesong-js


-----
Legal
-----

This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp
or any of its affiliates or subsidiaries. This is an independent and unofficial software.
Use at your own risk.
