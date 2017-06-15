# mqtt2rrd

This is the application I use to listen for messages on a MQTT server
and feed their values into [RRD files](http://oss.oetiker.ch/rrdtool/).

The config file has a list of matching regular expressions to do the
translation between topic and rrd file. The messages should contain
only the new value, as they are currently fed directly into rrd without
any transformation.

There is a template config file availble in the repository. Usage, then,
is like:

```
$ ./mqtt2rrd.py -v
10:29:48 INFO     mqtt2rrd: Connected with result code 0
10:29:48 DEBUG    mqtt2rrd: Subscribing to greenhouse/#
10:29:49 WARNING  mqtt2rrd: Unmatched: greenhouse/greenery/status b'1'
10:29:49 DEBUG    mqtt2rrd: Updated solution_temperature to 16.5625
10:29:49 DEBUG    mqtt2rrd: Updated greenhouse_temperature to 21.0
10:29:49 DEBUG    mqtt2rrd: Updated greenhouse_humidity to 48.0
10:29:59 WARNING  mqtt2rrd: Unmatched: greenhouse/greenery/pump b'0'
10:29:59 DEBUG    mqtt2rrd: Updated greenhouse_temperature to 21.0
10:29:59 DEBUG    mqtt2rrd: Updated greenhouse_humidity to 48.0
10:30:00 DEBUG    mqtt2rrd: Updated solution_temperature to 16.75
10:34:59 DEBUG    mqtt2rrd: Updated greenhouse_temperature to 20.0
10:34:59 DEBUG    mqtt2rrd: Updated greenhouse_humidity to 49.0
10:35:00 DEBUG    mqtt2rrd: Updated solution_temperature to 16.875
10:39:59 DEBUG    mqtt2rrd: Updated greenhouse_temperature to 20.0
```

