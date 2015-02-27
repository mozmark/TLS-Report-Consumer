TLS-Report-Consumer
===================

A Jython report consumer for Firefox TLS Error reports based on
https://github.com/meyarivan/kafka-simpleconsumer-jython.

Requires Jython > 2.7.4 (datetime.total_seconds is missing from >=2.7.4) -
you may need to build from jython trunk.

Requires following libraries under lib/ subdir.

* jopt-simple-3.2.jar
* kafka-0.7.1.jar
* log4j-1.2.15.jar
* protobuf-java-2.4.1.jar
* scala-library.jar
* snappy-java-1.0.4.1.jar
* zkclient-0.1.jar
* zookeeper-3.3.4.jar
* bagheera-0.15.jar
* fastjson-1.1.39.jar

To run / test the consumer:

* Update config.py with relevant values for your environment
* Download latest Jython standalone jar	([jython-2.7-b3])
* Generate initial offsets using any existing data or use gen_offsets.py

```
# fetch latest offset(s)
java -cp jython-standalone-2.7-*.jar org.python.util.jython gen_offsets.py > file_containing_offsets

# replace MAXHEAP with appropriate heapsize (ex: no of brokers * no of partitions * 64MB * 1.5)
java -XmxMAXHEAP -cp jython-standalone-2.7-*.jar org.python.util.jython main.py file_containing_offsets 2>>file_containing_offsets

```

Redaction
=========

The TLS error reports sent by FX can contain data not suitable for
publication. Since we want to use some of these data for public reports, we
filter the data. filters.py contains the code that performs filtering  of
the data.

[jython-2.7-b3]:http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7-b3/jython-standalone-2.7-b3.jar

