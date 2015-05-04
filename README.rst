mqtt-watchdir
=============

This simple Python program portably watches a directory recursively and
publishes the content of newly created and modified files as payload to
an `MQTT <http://mqtt.org>`_ broker. Files which are deleted are
published with a NULL payload.

The path to the directory to watch recursively (default ``.``), as well
as a list of files to ignore (``*.swp``, ``*.o``, ``*.pyc``), the broker
host (``localhost``) and port number (``1883``) must be specified in via
environment variables , together with the topic prefix to which to
publish to (``watch/``).

Installation
------------

::

    git clone https://github.com/jpmens/mqtt-watchdir.git
    cd mqtt-watchdir
    virtualenv watchdir
    source watchdir/bin/activate
    pip install -e .

Configuration
-------------

Set the following optional environment variables before invoking
*mqtt-watchdir.py*:

-  ``MQTTHOST`` (default ``"localhost"``) is the name/address of the MQTT broker.
-  ``MQTTPORT`` (default ``1883``) is the TCP port number of the broker.
-  ``MQTTWATCHDIR`` (default: ``"."``) is the path to the directory to watch.
-  ``MQTTQOS`` (default: ``0``) is the MQTT Quality of Service (QoS) to
   use on publish. Allowed values are ``0``, ``1``, or ``2``.
-  ``MQTTRETAIN`` (default: ``0``) specifies whether the "retain" flag
   should be set on publish. Set to ``1`` if you want messages to be retained.
-  ``MQTTPREFIX`` (default: ``"watch"``) is the prefix to be prepended
   (with a slash) to the MQTT topic name. The topic name is formed from
   this prefix plus the path name of the file that is being modified
   (i.e. watched). You can set this to an empty string (``""``) to avoid
   prefixing the topic name.
-  ``MQTTFILTER`` (default None) allows modifying payload (see below).
   Takes path to a Python file (e.g. ``"/path/to/example-filter.py"``.
-  ``MQTTFIXEDTOPIC`` (default None) sets a MQTT topic to which
   all messages are published. If set, the ``MQTTPREFIX`` setting is
   overruled and ignored.

-  Set ``WATCHDEBUG`` (default: ``0``) to ``1`` to show debugging
   information.

Testing
-------

Launch ``mosquitto_sub``:

::

    mosquitto_sub -v -t 'watch/#'

Launch this program and, in another terminal, try something like this:

::

    echo Hello World > message
    echo JP > myname
    rm myname

whereupon, on the first window, you should see:

::

    watch/message Hello World
    watch/myname JP
    watch/myname (null)

Filters
-------

Without a filter (the default), *mqtt-watchdir* reads the content of a
newly created or modified file and uses that as the MQTT payload. By
creating and enabling a so-called *filter*, *mqtt-watchdir* can pass the
payload into said filter (a Python function) to have a payload
translated.

Consider the included ``example-filter.py``:

::

    def mfilter(filename, topic, payload):
        '''Return a tuple [pub, newpayload] indicating whether this event
           should be published (True or False) and a new payload string
           or None'''

        print "Filter for topic %s" % topic

        if filename.endswith('.jpg'):
            return False, None

        if payload is not None:
            return True, payload.replace("\n", "-").replace(" ", "+")
        return True, None

The *mfilter* function is passed the fully qualified path to the file,
the (possibly prefixed) MQTT topic name and the payload. In this simple
example, spaces and newlines in the payload are replaced by dashes and
plusses.

The function must return a tuple with two elements:

1. The first specifies whether the payload will be published (True) or
   not (False)
2. The second is a string with a possibly modified payload or None. If
   the returned payload is *None*, the original payload is not modified.

Possible uses of filters include

-  Limiting payload lengths
-  Conversion to JSON
-  Ignore certain file types (e.g. binary data)
-  Process content of files, say, YAML or JSON, and extract elements
   returning as string

Requirements
------------

-  `watchdog <https://github.com/gorakhargosh/watchdog>`_, a Python
   library to monitor file-system events.
-  `Paho-MQTT <https://pypi.python.org/pypi/paho-mqtt>`_'s Python module

Related utilities & Credits
---------------------------

-  Roger Light (of `Mosquitto <http://mosquitto.org>`_ fame) created
   `mqttfs <https://bitbucket.org/oojah/mqttfs>`_, a FUSE driver (in C)
   which works similarly.
-  Roger Light (yes, the same busy gentleman) also made
   `treewatch <https://bitbucket.org/oojah/treewatch>`_, a program to
   watch a set of directories and execute a program when there is a
   change in the files within the directories.
-  Thanks to Karl Palsson for the ``setup.py`` and ``version.py`` magic.

