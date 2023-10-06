.. highlight:: python
.. currentmodule:: quotexpy

.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: http://jinja.pocoo.org/
.. _paste: http://pythonpaste.org/
.. _bjoern: https://github.com/jonashaag/bjoern
.. _flup: http://trac.saddi.com/flup
.. _cherrypy: http://www.cherrypy.org/
.. _QxBroker: https://www.qxbroker.com/
.. _Python: http://python.org/
.. _techniques: https://es.wikipedia.org/wiki/Web_scraping
.. _issue_tracker: https://github.com/bottlepy/bottle/issues
.. _PyPI: http://pypi.python.org/pypi/quotexpy
.. _gae: https://developers.google.com/appengine/

========================
QuotexPy: Websockets API
========================

📈 QuotexPy is a powerful wrapped API for interaction with QxBroker_. It is distributed as modules and uses authentication techniques_ to connect with the platform's websockets in a clean and simple way.


* **Routing:** Requests to function-call mapping with support for clean and  dynamic URLs.
* **Templates:** Fast and pythonic :ref:`built-in template engine <tutorial-templates>` and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP-related metadata.
* **Server:** Built-in HTTP development server and support for paste_, bjoern_, gae_, cherrypy_ or any other WSGI_ capable HTTP server.

.. rubric:: Download and Install

.. __: https://github.com/SantiiRepair/quotexpy#installing

Install the latest stable release with ``pip install quotexpy`` or `clone and install it manually`__ into your project directory. There are no hard [1]_ dependencies other than the Python standard library. QuotexPy supports **Python >=3.10**.

.. deprecated:: 1.0.0
    Support for Python <=3.9 was dropped with this release.


User's Guide
===============
Start here if you want to learn how to use the bottle framework for web development. If you have any questions not answered here, feel free to ask the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   configuration
   routing
   stpl
   deployment
   api
   plugins/index


Development and Contribution
============================

These chapters are intended for developers interested in the bottle development and release workflow.

.. toctree::
   :maxdepth: 2

   changelog
   development
   plugindev


.. toctree::
   :hidden:

   plugins/index
   contact

License
==================

Code and documentation are available according to the GPL-3.0 License:

.. include:: ../LICENSE
  :literal:

The Bottle logo however is *NOT* covered by that license. It is allowed to
use the logo as a link to the bottle homepage or in direct context with
the unmodified library. In all other cases please ask first.

.. rubric:: Footnotes

.. [1] Usage of the template or server adapter classes requires the corresponding template or server modules.

