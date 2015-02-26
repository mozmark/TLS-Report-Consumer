from etld import get_eTLD_service
from base64 import b64decode

from java.security.cert import X509Certificate, CertificateFactory
from java.io import StringBufferInputStream
from javax.naming.ldap import LdapName

cert_factory = CertificateFactory.getInstance('X.509')
svc = get_eTLD_service()

class CertChainFilter:
    def filter_document(self, document):
        failedCertChain = document['failedCertChain']
        document['failedCertChain'] = None
        document['restOfCertChain'] = failedCertChain[1:]
        cert = failedCertChain[0]
        cert_data = b64decode(cert)
        x509_cert = cert_factory.generateCertificate(StringBufferInputStream(cert_data))
        #x509_cert = X509Certificate.getInstance(cert_data)
        dn = x509_cert.getSubjectDN().getName()
        LDAP_dn = LdapName(dn)
        redacted_ee = {}
        cn = ''
        for rdn in LDAP_dn.getRdns():
            if rdn.getType() == 'CN':
                cn = rdn.getValue()
        redacted_ee['redactedCN'] = svc.get_base_domain(cn)
        document['redactedEE'] = redacted_ee
