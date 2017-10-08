===========
Isshub Sync
===========

``isshub_sync`` is a python module to be used in the next version of the core of https://www.isshub.io

It's goal is to synchronize part of the content of repositories of code repositories, like github, gitlab, bitbucket...,
being the sass version of hosted versions if they exists.

The exact perimeter of this module is to be defined. It may be only the core tools of the synchronization, with
other modules, "adapters", for the different platforms, being hosted separately. Or not.

**IMPORTANT: this is an early work in progress!**

*************
Specificities
*************

The python version used is python 3.6+, with typing annotations, and using async features as much as possible (for
example we use ``aiohttp`` for http connections)


***********
Development
***********

To work on this project, you need to install the package with its dev dependencies.

You can do it with

.. code-block:: shell

    pip install -e .[dev]

Or if you are fan of requirements file, you can do

.. code-block:: shell

    pip install -r requirements.txt


Note that it will do the exact same thing.


*************
Documentation
*************

There is actually no documentation per-se, but code is documented following
`Numpy-doc <https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_

The code documentation is checked by pylint


*****
Tests
*****

The module contains to kinds of tests:

- classic pytest tests, in ``tests``
- doctests in some classes/functions

We also use ``coverage`` with the ``pytest-cov`` plugin.

To run the tests, simply call:

.. code-block:: shell

    pytest


*****
Tools
*****

Many tools are configured to be used to check code quality:

mypy
====

http://www.mypy-lang.org/

Will check static typing defined using python typing annotations.

The configuration is defined in ``setup.cfg`` under the ``[mypy]`` and ``[mypy-*]`` sections.

Usage:

.. code-block:: shell

    mypy .


prospector
==========

https://prospector.landscape.io

Will run a number of code quality tools:

- `dodgy <https://github.com/landscapeio/dodgy>`_
- `mccabe <https://github.com/PyCQA/mccabe>`_
- `pydocstyle (ex-pep257) <https://github.com/PyCQA/pydocstyle>`_
- `pep8.py <http://pep8.readthedocs.org/en/latest/>`_
- `pyflakes <https://launchpad.net/pyflakes>`_
- `pylint <http://www.pylint.org/>`_
- `pyroma <https://github.com/regebro/pyroma>`_

The configuration is defined in ``.prospector.yaml``.

.. code-block:: shell

    prospector

Note: we actually use a fork, ``prospector-fixes-232`` to handle a bug.
See https://github.com/landscapeio/prospector/issues/232 (and the tied PR)

*******
License
*******

This software is, for now, published under the MIT license. It may change in the future, for example
toward `License Zero <https://licensezero.com/>`_
