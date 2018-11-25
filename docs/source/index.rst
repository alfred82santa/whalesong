:tocdepth: 4

=========
Whalesong
=========

Whalesong is an asyncio python library to manage WebApps remotely.
Currently WhatsappWeb is implemented

.. warning::

   **NEW VERSION 0.7.0 (Work in progress)**

   With new version some new requirements have been defined and some API change have been
   committed.

   Version 0.7.0 introduces new driver for Chromium browser. It has required some changes on base
   driver's API. It should not affect anyone. But be aware.


.. warning::

   **NEW VERSION 0.7.0 (Work in progress)**

   Stream model now uses enumerations. It means that if you check stream states
   you must be aware that they are not a string anymore, now they are enumerations. Look at
   :class:`documentation <whalesong.managers.stream.Stream>`.

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



-----------------
Table of contents
-----------------

.. toctree::
   :maxdepth: 4

   features
   backends
   examples
   api/index
   develop
   changelog


------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



-----
Legal
-----

This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp
or any of its affiliates or subsidiaries. This is an independent and unofficial software.
Use at your own risk.