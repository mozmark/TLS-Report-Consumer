import json, datetime
from datetime import datetime, time
from etld import get_eTLD_service
from base64 import b64decode
try:
    from certfilter import CertChainFilter
except:
    print 'unable to import CertChainFilter; maybe you are not running Jython?'

svc = get_eTLD_service()

'''
A filter to reduce timestamp accuracy to the day
'''
class DateFilter:
    def filter_document(self, document):
        fulltime = datetime.fromtimestamp(document['timestamp'])
        date = datetime.combine(fulltime.date(), time(0,0))
        timestamp = int((date - datetime(1970, 1, 1)).total_seconds())
        document['timestamp'] = timestamp

'''
A filter to replace fqdns with just the base domain.
'''
class HostnameFilter:
    def filter_document(self, document):
        initial = document['hostname']
        document['hostname'] = svc.get_base_domain(initial)

'''
A cert chain filter that removes end-entities in the absence of the Jython
CertChainFilter
'''
class RemovingCertChainFilter:
    def filter_document(self, document):
        failedCertChain = document['failedCertChain']
        document['failedCertChain'] = None
        document['restOfCertChain'] = failedCertChain[1:]

enabled_filters = [
        DateFilter,
        HostnameFilter
        ]

try:
    enabled_filters.append(CertChainFilter)
except:
    enabled_filters.append(RemovingCertChainFilter)

class Filter:
    def filter_document(self, document):
        filters = [x() for x in enabled_filters]

        for filt in filters:
            filt.filter_document(parsed)

if __name__ == '__main__':
    # load a sample report
    f = open('sample.json','r')
    data = f.read()
    f.close()
    parsed = json.loads(data)

    # print, filter, and print again
    #print(parsed)
    fltr = Filter();
    fltr.filter_document(parsed)
    print(parsed)
