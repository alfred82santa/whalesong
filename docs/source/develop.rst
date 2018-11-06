==============
How to develop
==============

------------------------
Development requirements
------------------------

* node (only for development)
* npm (only for development)
* make (only for development)

----------------------------
Install library requirements
----------------------------

.. code-block:: bash

    $ make requirements

-------------------------
Build Javascript scriplet
-------------------------

You have to rebuild scriptlet after any change if you want to use in Python code.

.. code-block:: bash

    $ make build-js

-------------
Beautify code
-------------

You must to beautify code before make a pull request. Ugly code will not be accepted.

.. code-block:: bash

    $ make beautify