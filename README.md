# mqtt-watchdir

This simple Python program portably watches a directory recursively and publishes the content
of newly created and modified files as payload to an [MQTT] broker. Files which
are deleted are published with a NULL payload.

The path to the directory to watch recursively (default `.`), as well as a list of files
to ignore (`*.swp`, `*.o`, `*.pyc`), the broker host (`localhost`)  and port number (`1883`)
must be specified in via environment variables , together with the topic prefix to which to publish to (`watch/`).

## Installation

```
git clone https://github.com/jpmens/mqtt-watchdir.git
cd mqtt-watchdir
virtualenv watchdir
source watchdir/bin/activate
pip install -e .
```

## Configuration

Set the following optional environment variables before invoking _mqtt-watchdir.py_:

* `MQTTHOST` (default `"localhost"`) is the name/address of the MQTT broker.
* `MQTTPORT` (default `1883`) is the TCP port number of the broker.
* `MQTTWATCHDIR` (default: `"."`) is the path to the directory to watch.
* `MQTTQOS` (default: `0`) is the MQTT Quality of Service (QoS) to use on publish. Allowed values are `0`, `1`, or `2`.
* `MQTTRETAIN` (default: `0`) specifies whether the "retain" flag should be set on publish. Set to `1` if you want messages to be retained.
* `MQTTPREFIX` (default: `"watch"`) is the prefix to be prepended (with a slash) to the MQTT topic name. The topic name is formed from this prefix plus the path name of the file that is being modified (i.e. watched). You can set this to an empty string (`""`) to avoid prefixing the topic name.

* Set `WATCHDEBUG` (default: `0`) to `1` to show debugging information.

## Testing

Launch `mosquitto_sub`:

```bash
mosquitto_sub -v -t 'watch/#'
```

Launch this program and, in another terminal, try something like this:

```bash
echo Hello World > message
echo JP > myname
rm myname
```

whereupon, on the first window, you should see:

```
watch/message Hello World
watch/myname JP
watch/myname (null)
```

## Requirements

* [watchdog](https://github.com/gorakhargosh/watchdog), a Python library to monitor file-system events.
* [Mosquitto]'s Python module

## Related utilities & Credits

* Roger Light (of [Mosquitto] fame) created [mqttfs], a FUSE driver (in C) which works similarly.
* Roger Light (yes, the same busy gentleman) also made [treewatch], a program to watch a set of directories and execute a program when there is a change in the files within the directories.
* Thanks to Karl Palsson for `setup.py`.

 [mqttfs]: https://bitbucket.org/oojah/mqttfs
 [treewatch]: https://bitbucket.org/oojah/treewatch

 [MQTT]: http://mqtt.org
 [Mosquitto]: http://mosquitto.org
