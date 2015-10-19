import datetime
import json
import os
import sys
import time
import traceback

from consumer import KafkaConsumer
from processor import BagheeraMessageProcessor

import Queue
import threading

import config
import codecs

sys.path.extend(['log4j.properties'])
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

from java.lang import System
from java.util.zip import GZIPOutputStream
from java.io import FileOutputStream
from java.io import PrintWriter
import com.alibaba.fastjson.JSON as JSON

from reportfilter import Filter

def runner(offsets):
    fltr = Filter()
    queues = {}
    bmp_map = {}
    offset_update_freq = config.offset_update_freq

    for host in config.bagheera_nodes:
        for topic in config.topics:
            for partition in config.partitions:
                queue = Queue.Queue(256)
                queues[(host, topic, partition)] = queue

                bmp = BagheeraMessageProcessor(queue)
                bmp_map[id(bmp)] = (host, topic, partition)

                offset = offsets[(host, topic, partition)]
                kc = KafkaConsumer(host, {}, topic, partition, bmp.processor, offset, offset_update_freq)
                t = threading.Thread(target = kc.process_messages_forever)
                t.start()

    strtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    fos = FileOutputStream("redacted_%s.gz"%(strtime))
    gos = GZIPOutputStream(fos)
    writer = PrintWriter(gos)

    uf_fos = FileOutputStream("unfiltered_%s.gz"%(strtime))
    uf_gos = GZIPOutputStream(uf_fos)
    uf_writer = PrintWriter(uf_gos)

    err_fos = FileOutputStream("errors_%s.gz"%(strtime))
    err_gos = GZIPOutputStream(err_fos)
    err_writer = PrintWriter(err_gos)

    count = 0

    while True:
        for htp, q in queues.iteritems():
            try:
                v = q.get(False)
            except Queue.Empty:
                continue

            if v[1] == 'PUT':
                count = count + 1
                pid, op, ts, ipaddr, doc_id, payload = v
                json_payload = JSON.toJSONString(payload)
                uf_writer.println(json_payload)
                #TODO: figure out less braindead way of working with
                # java.util.HashMaps in jython
                try:
                    filtered = json.loads(json_payload)
                    # System.out.println('%s %s %d %s %s %s' % (htp[1], op, ts, ipaddr, doc_id, json_payload))
                    fltr.filter_document(filtered)
                    filtered['doc_id'] = doc_id
                    writer.println(json.dumps(filtered))
                    #print doc_id
                except:
                    err_writer.println(doc_id+" "+json_payload);
                if count % 10000 == 0:
                    print ts

def parse_offsets(filex):
    offsets = {}

    # lines in this "file" contain one serialized (json) entry per line with following fields
    # time_millis hostname topic partition offset
    #

    for i in open(filex, "r"):
        try:
            dictx = json.loads(i)
            host = dictx['hostname']
            topic = dictx['topic']
            partition = dictx['partition']
            offset = dictx['offset']

            offsets[(host, topic, partition)] = offset
        except:
            pass
            
    if (not offsets) or (len(offsets) != (len(config.topics) * len(config.partitions) * len(config.bagheera_nodes))):
        System.err.println("ERROR: could not find valid initial offsets for given configuration")
        sys.exit(1)

    return offsets


if __name__ == '__main__':
    if len(sys.argv) != 2:
        System.err.println("Needs file containing offsets as first argument")
        sys.exit(1)
    
    try:
        runner(parse_offsets(sys.argv[1]))
    except:
        System.err.println("ERROR: " + traceback.format_exc())
    finally:
        System.exit(1)


