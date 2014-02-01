.. box-linux-sync documentation master file, created by
   sphinx-quickstart on Sat Feb  9 22:09:07 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

box-linux-sync - A naïve `Box.com <http://box.com/>`_ Linux Client
==================================================================

An unofficial attempt to create a Linux synchronization client because Box.com does not provide one.

BIG FAT WARNING
---------------

This is work in progress. The daemon is not yet functional. But suggestions and patches are welcome ;) Thanks!

Requirements
------------

-  `Python <http://www.python.org/download/releases/>`_ 2.7 and up (may
   work on earlier versions, haven't tested).
- `Box.py  <https://github.com/sookasa/box.py>`_
- `Peewee <https://github.com/coleifer/peewee)
- `Pyinotify <https://github.com/seb-m/pyinotify>`_
- `Tornado <http://www.tornadoweb.org/>`_

Installation
------------

.. code-block:: bash

    $ pip install box.py peewee pyinotify tornado
    $ cd ~/path/of/your/choice
    $ git clone git://github.com/noiselabs/box-linux-sync.git

Installation via Pip is not currently available. Let's wait for a proper
release, OK?.

Usage
-----

Check environment and setup ``box-sync`` and it's dependencies:


.. code-block:: bash

    $ box-linux-sync.git/bin/boxsync help

    BoxSync command-line interface

    commands:

    Note: use boxsync help <command> to view usage for a specific command.

     status       get current status of the boxsyncd
     help         provide help
     stop         stop boxsyncd
     running      return whether boxsync is running
     start        start boxsyncd
     filestatus   get current sync status of one or more files
     ls           list directory contents with current sync status
     debug        run boxsyncd in debug mode
     exclude      ignores/excludes a directory from syncing


For developers::

    $  box-linux-sync.git/bin/boxsync debug

License
-------

This application is licensed under the LGPLv3 License. See the `LICENSE
file <https://github.com/noiselabs/box-linux-sync/blob/master/LICENSE>`_
for details.

Authors
-------

Vítor Brandão - vitor@noiselabs.org ~
`twitter.com/noiselabs <http://twitter.com/noiselabs>`_ ~
`noiselabs.org <http://noiselabs.org>`_

See also the list of
`contributors <https://github.com/noiselabs/box-linux-sync/contributors>`_
who participated in this project.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

