#!/usr/bin/python3

import sys
import paho.mqtt.client as mqtt
from re import search
import rrdtool
import logging
import argparse

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    log.info("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for s in config.subscribes.keys():
        log.debug('Subscribing to '+s)
        client.subscribe(s)
    log.info('All subscribed')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    matches = list(filter(lambda x: search(x, msg.topic), config.translations.keys()))
    for m in matches:
        f = config.translations[m]
        if not config.dry_run:
            update_rrd(f, msg.payload)
        log.debug("Updated "+f+" to "+str(float(msg.payload)))
    if not len(matches):
        log.warning('Unmatched: '+msg.topic+" "+str(msg.payload))

# Update rrd file with a given value
# The default timestamp, N, means 'now'
def update_rrd(filename, value, timestamp='N'):
    filename = filename + '.rrd'
    rrdtool.update(filename, timestamp+':'+str(float(value)))

def connect():
    global client
    client = mqtt.Client(client_id=config.id, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(config.server['user'], config.server['passwd'])
    client.connect(config.server['host'], int(config.server['port']), 60)

# Parse command line args and load config file
def parse_args(args):
    global config
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose", \
                        default=False, action='store_true')
    parser.add_argument("-n", "--dry-run", help="dry run, do not update .rrd files", \
                        default=False, action='store_true')
    parser.add_argument("-i", "--id", help="MQTT Client ID", \
                        default='mqtt2rrd', type=str)
    parser.add_argument("-c", "--config", help="Config file", \
                        default='mqtt2rrd.ini', type=str)
    config = parser.parse_args(args)

    import configparser
    cfgfile = configparser.ConfigParser()
    cfgfile.read(config.config)

    # Validate translations section
    if not cfgfile.has_section('translations'):
        print('Error: config file '+config.config+' is missing translations section\n')
        sys.exit(1)
    if not len(cfgfile['translations'].keys()):
        print('Error: no translations found in config file '+config.config)
        sys.exit(1)
    config.translations = cfgfile['translations']

    # Validate subscribes section
    if not cfgfile.has_section('subscribes'):
        print('Error: config file '+config.config+' is missing subscribes section\n')
        sys.exit(1)
    if not len(cfgfile['subscribes'].keys()):
        print('Error: no subscribes found in config file '+config.config)
        sys.exit(1)
    config.subscribes = cfgfile['subscribes']

    # Validate server section
    if not cfgfile.has_section('server'):
        print('Error: config file '+config.config+' is missing server section\n')
        sys.exit(1)
    for k in ['host', 'port', 'user', 'passwd']:
        if not cfgfile['server'].__contains__(k):
            print('Error: entry server.'+k+' not found in config file '+config.config)
            sys.exit(1)
    config.server = cfgfile['server']

# Initialize subsystems according to configs that were loaded
def init():
    global log
    logging.basicConfig(format='%(asctime)s %(levelname)-8.8s %(name)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.ERROR)
    log = logging.getLogger('mqtt2rrd')
    if not config.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    parse_args(sys.argv[1:])
    init()
    connect()

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

