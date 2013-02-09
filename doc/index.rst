.. box-linux-sync documentation master file, created by
   sphinx-quickstart on Sat Feb  9 22:09:07 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

box-linux-sync - A naïve `Box.com <http://box.com/>`_ Linux Client
==================================================================

An unofficial attempt to create a Linux synchronization client because
Box.com does not provide one.

Overview
--------

File synchronization is currently done using the WebDAV interface
provided by Box.com. There is also a `Python
API <https://github.com/box/box-python-sdk>`_ available but I haven't
started to mess with it.

Requirements
------------

-  `Python <http://www.python.org/download/releases/>`_ 2.7 and up (may
   work on earlier versions, haven't tested).
-  `Davfs2 <http://savannah.nongnu.org/projects/davfs2>`_. To install it
   use:

   -  Debian, Ubuntu: ``apt-get install davfs2``
   -  Red Hat, SuSE, Fedora: ``yum install davfs2``
   -  Gentoo: ``emerge davfs2``
   -  ArchLinux: ``pacman -S davfs2``

Installation
------------

.. code-block:: bash

    $ cd ~/path/of/your/choice
    $ git clone git://github.com/noiselabs/box-linux-sync.git

Installation via Pip is not currently available. Let's wait for a proper
release, OK?.

Usage
-----

Check environment and setup ``box-sync`` and it's dependencies:


.. code-block:: bash

    $ cd ~/path/to/box-linux-sync/bin
    $ ./box-sync check && ./box-sync setup

Edit ``~/.noiselabs/box/box-sync.cfg`` to fit your preferences:


.. code-block:: bash

    $ vim ~/.noiselabs/box/box-sync.cfg

.. code-block:: cfg

    ; box-sync.cfg
    [main]

    ; Path to your Box sync dir. Use a relative path to place this dir
    ; inside $HOME or an absolute path. Default: Box
    box_dir = Box

    ; Wether to use a WebDAV filesystem to synchronize your local and
    ; remote files. Default: true
    use_davfs = true

Start synchronization via Davfs:


.. code-block:: bash

    $ ./box-sync start

Stop synchronization:


.. code-block:: bash

    $ ./box-sync stop

Send ``box-sync`` into oblivion when you get tired of it.


This just removes ``box-sync`` configuration files and the repository,
not your personal Box.com files (unless you have configured the
``box_sync`` dir to be inside ``~/.noiselabs``).

.. code-block:: bash

    $ ./box-sync uninstall
    $ rm ~/path/to/box-linux-sync

License
-------

This application is licensed under the LGPLv3 License. See the `LICENSE
file <https://github.com/noiselabs/box-linux-sync/blob/master/LICENSE>`_
for details.

Authors
-------

Vítor Brandão - noisebleed@noiselabs.org ~
`twitter.com/noiselabs <http://twitter.com/noiselabs>`_ ~
`blog.noiselabs.org <http://blog.noiselabs.org>`_

See also the list of
`contributors <https://github.com/noiselabs/box-linux-sync/contributors>`_
who participated in this project.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

