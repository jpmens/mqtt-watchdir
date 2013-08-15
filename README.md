# mqtt-watchdir

This simple Python program portably watches a directory recursively and publishes the content
of newly created and modified files as payload to an [MQTT] broker. Files which
are deleted are published with a NULL payload.

The path to the directory to watch recursively (default `.`), as well as a list of files
to ignore (`*.swp`, `*.o`), the broker host (`localhost`)  and port number (`1883`)
must be specified in the program, together with the topic prefix to which to publish to
(`watch/`).

## Installation

```
git clone https://github.com/jpmens/mqtt-watchdir.git
virtualenv watchdir
source watchdir/bin/activate
pip install -e .
```

## Testing

Launch `mosquitto_sub`:

```bash
mosquitto_sub -v -t 'watch/#'
```

Launch this program and, in another terminal, try somthing like this:

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

* [watchdog](https://github.com/gorakhargosh/watchdog), a Python library to monitor filesystem events.
* [Mosquitto]'s Python module

## Related utilities & Credits

* Roger Light (of Mosquitto fame) created [mqttfs], a FUSE driver (in C) which works similarly.
* Roger Light (yes, the same busy gentleman) also made [treewatch], a program to watch a set of directories and execute a program when there is a change in the files within the directories.
* Thanks to Karl Palsson for `setup.py`.

 [mqttfs]: https://bitbucket.org/oojah/mqttfs
 [treewatch]: https://bitbucket.org/oojah/treewatch

 [MQTT]: http://mqtt.org
 [Mosquitto]: http://mosquitto.org
