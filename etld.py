# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
path = os.path.dirname(os.path.realpath(__file__))

def split_into_labels(domain):
    return domain.split('.')

'''
A helper for finding eTLDs or base domains for a given domain. See 
http://publicsuffix.org for more info.
'''
class ETLDService:
    exceptions = []
    rules = []

    '''
    Initializes the ETLDService with effective_tld_names.dat from the directory
    that this file lives in. Don't use this, use the helper function (See below)
    '''
    def __init__(self):
        f = open(os.path.join(path,'effective_tld_names.dat'),'r')
        lines = f.readlines()
        f.close()
        for trimmed in [line.rstrip().strip() for line in lines]:
            if len(trimmed) > 0 and '/' != trimmed[0]:
                if '!' == trimmed[0]:
                    self.exceptions.append(split_into_labels(trimmed[1:]))
                else:
                    self.rules.append(split_into_labels(trimmed))

    def _find_matches(self, ruleset, labels):
        matches = []
        if len(labels) > 0:
            try:
                if ruleset.index(labels):
                    matches.append(labels)
                    return matches
            except:
                wild = ['*']
                try:
                    wild.extend(labels[1:])
                    if ruleset.index(wild):
                        matches.append(labels)
                        return matches
                except:
                    pass
            matches.extend(self._find_matches(ruleset, labels[1:]))
        return matches


    '''
    Get the effective top-level domain of a given domain.
    Takes a list of labels for a domain (input domain)
    Returns a list of labels for the top level domain (tld)
    '''
    def get_eTLD_labels(self, labels):
        matching_rules = self._find_matches(self.rules, labels)
        matching_exceptions = self._find_matches(self.exceptions, labels)
        rules = matching_rules
        # Exceptions override other rules
        if len(matching_exceptions) > 0:
            rules = matching_exceptions
        # the longest matching rule wins
        rule = []
        for matching in rules:
            if len(matching) > len(rule):
                rule = matching
        return rule

    '''
    Get the effective top-level domain of a given domain.
    Takes a string (input domain)
    Returns a string (tld)
    '''
    def get_eTLD(self, domain):
        labels = split_into_labels(domain)
        return '.'.join(self.get_eTLD_labels(labels))

    '''
    Get the base domain of a given domain.
    Takes a list of labels for a domain (input domain)
    Returns a list of labels for the base domain (tld)
    '''
    def get_base_domain_labels(self, labels):
        eTLD_labels = self.get_eTLD_labels(labels)
        return labels[-1*(len(eTLD_labels)+1):]

    '''
    Get the base domain of a given domain.
    Takes a stirng (input domain)
    Returns a string (base domain)
    '''
    def get_base_domain(self, domain):
        labels = split_into_labels(domain)
        return '.'.join(self.get_base_domain_labels(labels))


_eTLD_service = ETLDService()

'''
Get the ETLDService. We only need one of these. Using this method ensures
we don't constantly re-read the effective TLD list more than we need to.
'''
def get_eTLD_service():
    return _eTLD_service

if __name__ == '__main__':
    svc = get_eTLD_service()
    print svc.get_base_domain('people.mozilla.org')
    print svc.get_base_domain('foo.yoichi.hokkaido.jp')
    print svc.get_base_domain('yoichi.hokkaido.jp')
    print svc.get_base_domain('foo.bar.ke')
