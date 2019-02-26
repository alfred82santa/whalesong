.. _browser_backends:

================
Browser backends
================

Whalesong uses a browser backend in order to execute a WebApp (currently only WhatsAppWeb). All backends have
an interface to manage webviews and that is what Whalesong uses to manage applications. That interface changes
depending on browser, but there is a standard interface called
`WebDriver <https://developer.mozilla.org/en-US/docs/Web/WebDriver>`_. Firsts Whalesong versions used to use a
`Selenium <https://www.seleniumhq.org/>`_ library in order to communicate with Firefox browser.
This backend is the default one for now, **but it will be deprecated in next versions and removed in version 1.0**.

---------------
Firefox backend
---------------

It was the first backend developed. It uses `Selenium <https://www.seleniumhq.org/>`_ library and
`Geckodriver <https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/>`_ to communicate with
Firefox process. It is the most tested (the most, but not well).


....
Pros
....

* Tested (more or less).
* Use Firefox (I prefer it in front Chromium).

.......
Contras
.......

* Selenium is a huge library. It is wonderful for what it was created, but not for Whalesong.
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

..........
How to use
..........

Currently Firefox backend is the default one. But it will change on next versions. So, in order to ensure you use
Firefox backend you must instantiate Whalesong with proper driver.

.. code-block:: python3

   from whalesong import Whalesong
   from whalesong.driver_firefox import WhalesongDriver

   driver = WhalesongDriver(profile='/path/to/your/firefox/profile')
   whaleapp = Whalesong(driver=driver)


----------------
Chromium backend
----------------

It is the new one. It is implemented using `Pyppetter <https://github.com/miyakogi/pyppeteer>`_ which is inspired
on `Puppetter <https://pptr.dev/>`_ (a `node` library to control Chromium headless, mainly, for testing). It uses
`Devtools protocol <https://chromedevtools.github.io/devtools-protocol/>`_ in order to communicate with the browser.
It is an asynchronous protocol over websocket.

....
Pros
....

* No more polling! When a result is produced it will send proactively to Whalesong. No more `sleeps`, no more waitings.
* Small footprint (at least, it looks like, even being Chromium).
* No extra processes (No more Geckodriver).
* Application mode. No tabs, no URL field.
* No huge libraries (No more Selenium).

.......
Contras
.......

* It is Chromium. It uses Blink: over-vitaminized Webkit render. A memory eater.
* Currently Pypperter has a bug. It makes to loose connection after 20 seconds. It is resolved in
  `miyakogi/pyppeteer/#160 <https://github.com/miyakogi/pyppeteer/pull/160>`_ but is not
  approved yet (some test errors).

* It uses a patched Chromium version from Puppetter. Whalesong needs this patch because it uses `Runtime.addBinding`
  command. It is not available in regular stable version. So, you must `download it <using_chromium>`_ before to
  use the backend.

* Poorly tested.

* There is a bug in Chromium under Wayland. It makes impossible to get WhastappWeb QR when
  Chromium is executed with window (no headless).

..........
How to use
..........

In order to use Chromium backend you must inject Chromium driver to Whalesong service constructor.

.. code-block:: python3

   from whalesong import Whalesong
   from whalesong.driver_chromium import WhalesongDriver

   driver = WhalesongDriver(profile='/path/to/your/chromium/profile')
   whaleapp = Whalesong(driver=driver)

--------------
Other backends
--------------

No, there are no other backends. But I'm thinking about other possibilities:

* Create a small footprint webview using Webkit directly (GTK or QT ways are not an option).
* Create a small footprint webview using Servo directly (I want to learn rust language).

**Of course, any contribution will be welcome (so much).**

