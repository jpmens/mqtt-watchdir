#!/usr/bin/env python

# Copyright (c) 2013 Jan-Piet Mens <jpmens()gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__author__ = "Jan-Piet Mens"
__copyright__ = "Copyright (C) 2013-2015 by Jan-Piet Mens"

import os, sys
import signal
import time
import paho.mqtt.client as paho
# https://github.com/gorakhargosh/watchdog
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import platform
import imp

MQTTHOST        = os.getenv('MQTTHOST', 'localhost')
MQTTPORT        = int(os.getenv('MQTTPORT', 1883))
MQTTWATCHDIR    = os.getenv('MQTTWATCHDIR', '.')
MQTTQOS         = int(os.getenv('MQTTQOS', 0))
MQTTRETAIN      = int(os.getenv('MQTTRETAIN', 0))

# May be None in which case neither prefix no separating slash are prepended
MQTTPREFIX      = os.getenv('MQTTPREFIX', 'watch')
MQTTFILTER      = os.getenv('MQTTFILTER', None)

# Publish all messages to a fixed topic. E.g. if the file contents already/also 
# contains the name of the file or in certain situations with retained messages.
# Overrules and ignores the MQTTPREFIX setting.
MQTTFIXEDTOPIC  = os.getenv('MQTTFIXEDTOPIC', None)

WATCHDEBUG      = os.getenv('WATCHDEBUG', 0)

if MQTTPREFIX == '':
    MQTTPREFIX = None

if MQTTFIXEDTOPIC == '':
    MQTTFIXEDTOPIC = None

if MQTTFIXEDTOPIC:
    print 'Publishing ALL messages to the topic: %s' % MQTTFIXEDTOPIC

ignore_patterns = [ '*.swp', '*.o', '*.pyc' ]

# Publish with retain (True or False)
if MQTTRETAIN == 1:
    MQTTRETAIN=True
else:
    MQTTRETAIN=False

# Ensure absolute path (incl. symlink expansion)
DIR = os.path.abspath(os.path.expanduser(MQTTWATCHDIR))

OS = platform.system()

mf = None
if MQTTFILTER is not None:
    try:
        mf = imp.load_source('mfilter', MQTTFILTER)
    except Exception, e:
        sys.exit("Can't import filter from file %s: %s" % (MQTTFILTER, e))

clientid = 'mqtt-watchdir-%s' % os.getpid()
mqtt = paho.Client(clientid, clean_session=True)

def on_publish(mosq, userdata, mid):
    pass
    # print("mid: "+str(mid))

def on_disconnect(mosq, userdata, rc):
    print "disconnected"
    time.sleep(5)

def signal_handler(signal, frame):
    """ Bail out at the top level """

    mqtt.loop_stop()
    mqtt.disconnect()

    sys.exit(0)

class MyHandler(PatternMatchingEventHandler):
    """
    React to changes in files, handling create, update, unlink
    explicitly. Ignore directories. Warning: does not handle move
    operations (i.e. `mv f1 f2' isn't handled).
    """

    def catch_all(self, event, op):

        if event.is_directory:
            return

        path = event.src_path

        if OS == 'Linux' and op != 'DEL':

            try:
                # On Linux, a new file is NEW and MOD. Ensure we publish once only
                ctime = os.path.getctime(path)
                mtime = os.path.getmtime(path)

                if op == 'NEW' and mtime == ctime:
                        return
            except:
                pass

        # Create relative path name and append to topic prefix
        filename = path.replace(DIR + '/', '')

        if MQTTFIXEDTOPIC is not None:
            topic = MQTTFIXEDTOPIC
        else:
            if MQTTPREFIX is not None:
                topic = '%s/%s' % (MQTTPREFIX, filename)
            else:
                topic = filename

        if WATCHDEBUG:
            print "%s %s. Topic: %s" % (op, filename, topic)

        if op == 'DEL':
            payload = None
        else:
            try:
                f = open(path)
                payload = f.read()
                f.close()
                payload = payload.rstrip()
            except Exception, e:
                print "Can't open file %s: %s" % (path, e)
                return

        # If we've loaded a filter, run data through the filter to obtain
        # a (possibly) modified payload

        if mf is not None:
            try:
                publish, new_payload = mf.mfilter(path, topic, payload)
                if publish is False:
                    if WATCHDEBUG:
                        print "NOT publishing %s" % path
                    return
                if new_payload is not None:
                    payload = new_payload
            except Exception, e:
                print "mfilter: %s" % (e)

        mqtt.publish(topic, payload, qos=MQTTQOS, retain=MQTTRETAIN)

    def on_created(self, event):
        self.catch_all(event, 'NEW')

    def on_modified(self, event):
        self.catch_all(event, 'MOD')

    def on_deleted(self, event):
        self.catch_all(event, 'DEL')

def main():

    mqtt.on_disconnect = on_disconnect
    mqtt.on_publish = on_publish

    mqtt.connect(MQTTHOST, MQTTPORT)

    mqtt.loop_start()

    signal.signal(signal.SIGINT, signal_handler)
    while 1:
    
        observer = Observer()
        event_handler = MyHandler( ignore_patterns=ignore_patterns )
        observer.schedule(event_handler, DIR, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
