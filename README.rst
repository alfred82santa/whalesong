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

.. include:: docs/source/changelog.rst

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