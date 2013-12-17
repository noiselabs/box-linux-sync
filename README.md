box-linux-sync - A naïve [Box.com](http://box.com/) Linux Client
================================================================

An unofficial attempt to create a Linux synchronization client because Box.com does not provide one.

NOTICE
------

If your Box sync stopped working please open your `/etc/fstab` file and update the WebDav URL from `https://www.box.com/dav` to `https://dav.box.com/dav`.

[Box.com blog post](https://support.box.com/entries/28641946-Features-to-be-removed-in-Q4-2013):

> On November 15, 2013, we will be transitioning from the current WebDav (https://www.box.com/dav) to a new version (https://dav.box.com/dav) that provides added stability and performance improvements. Please change the URL in any internal apps before November 15 to ensure your users can continue accessing content via WebDav. 

Overview
--------

File synchronization is currently done using the WebDAV interface provided by Box.com. There is also a [Python API](https://github.com/box/box-python-sdk) available but I haven't started to mess with it.

Requirements
------------

* [Python](http://www.python.org/download/releases/) 2.7 and up (may work on earlier versions, haven't tested).
* [Davfs2](http://savannah.nongnu.org/projects/davfs2). To install it use:
    * Debian, Ubuntu: `apt-get install davfs2`
    * Red Hat, SuSE, Fedora: `yum install davfs2`
    * Gentoo: `emerge davfs2`
    * ArchLinux: `pacman -S davfs2`

Installation
------------

    $ cd ~/path/of/your/choice
    $ git clone git://github.com/noiselabs/box-linux-sync.git

Installation via Pip is not currently available. Let's wait for a proper release, OK?.

Usage
-----

###### Check environment and setup `box-sync` and it's dependencies:

    $ cd ~/path/to/box-linux-sync/bin
    $ ./box-sync check && ./box-sync setup

###### Edit `~/.noiselabs/box/box-sync.cfg` to fit your preferences:

    $ vim ~/.noiselabs/box/box-sync.cfg

    ; box-sync.cfg
    [main]

    ; Path to your Box sync dir. Use a relative path to place this dir
    ; inside $HOME or an absolute path. Default: Box
    box_dir = Box

    ; Wether to use a WebDAV filesystem to synchronize your local and
    ; remote files. Default: true
    use_davfs = true

###### Start synchronization via Davfs:

    $ ./box-sync start

###### Stop synchronization:

    $ ./box-sync stop

###### Send `box-sync` into oblivion when you get tired of it.

This just removes `box-sync` configuration files and the repository, not your personal Box.com files (unless you have configured the `box_sync` dir to be inside `~/.noiselabs`).

    $ ./box-sync uninstall
    $ rm ~/path/to/box-linux-sync

License
-------

This application is licensed under the LGPLv3 License. See the [LICENSE file](https://github.com/noiselabs/box-linux-sync/blob/master/LICENSE) for details.

Authors
-------

Vítor Brandão - <vitor@noiselabs.org> ~ [twitter.com/noiselabs](http://twitter.com/noiselabs) ~ [blog.noiselabs.org](http://blog.noiselabs.org)

See also the list of [contributors](https://github.com/noiselabs/box-linux-sync/contributors) who participated in this project.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/noiselabs/box-linux-sync/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

