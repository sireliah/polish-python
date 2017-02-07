"""Make the custom certificate oraz private key files used by test_ssl
and friends."""

zaimportuj os
zaimportuj shutil
zaimportuj sys
zaimportuj tempfile
z subprocess zaimportuj *

req_template = """
    [req]
    distinguished_name     = req_distinguished_name
    x509_extensions        = req_x509_extensions
    prompt                 = no

    [req_distinguished_name]
    C                      = XY
    L                      = Castle Anthrax
    O                      = Python Software Foundation
    CN                     = {hostname}

    [req_x509_extensions]
    subjectAltName         = DNS:{hostname}

    [ ca ]
    default_ca      = CA_default

    [ CA_default ]
    dir = cadir
    database  = $dir/index.txt
    crlnumber = $dir/crl.txt
    default_md = sha1
    default_days = 3600
    default_crl_days = 3600
    certificate = pycacert.pem
    private_key = pycakey.pem
    serial    = $dir/serial
    RANDFILE  = $dir/.rand

    policy          = policy_match

    [ policy_match ]
    countryName             = match
    stateOrProvinceName     = optional
    organizationName        = match
    organizationalUnitName  = optional
    commonName              = supplied
    emailAddress            = optional

    [ policy_anything ]
    countryName   = optional
    stateOrProvinceName = optional
    localityName    = optional
    organizationName  = optional
    organizationalUnitName  = optional
    commonName    = supplied
    emailAddress    = optional


    [ v3_ca ]

    subjectKeyIdentifier=hash
    authorityKeyIdentifier=keyid:always,issuer
    basicConstraints = CA:true

    """

here = os.path.abspath(os.path.dirname(__file__))

def make_cert_key(hostname, sign=Nieprawda):
    print("creating cert dla " + hostname)
    tempnames = []
    dla i w range(3):
        przy tempfile.NamedTemporaryFile(delete=Nieprawda) jako f:
            tempnames.append(f.name)
    req_file, cert_file, key_file = tempnames
    spróbuj:
        przy open(req_file, 'w') jako f:
            f.write(req_template.format(hostname=hostname))
        args = ['req', '-new', '-days', '3650', '-nodes',
                '-newkey', 'rsa:1024', '-keyout', key_file,
                '-config', req_file]
        jeżeli sign:
            przy tempfile.NamedTemporaryFile(delete=Nieprawda) jako f:
                tempnames.append(f.name)
                reqfile = f.name
            args += ['-out', reqfile ]

        inaczej:
            args += ['-x509', '-out', cert_file ]
        check_call(['openssl'] + args)

        jeżeli sign:
            args = ['ca', '-config', req_file, '-out', cert_file, '-outdir', 'cadir',
                    '-policy', 'policy_anything', '-batch', '-infiles', reqfile ]
            check_call(['openssl'] + args)


        przy open(cert_file, 'r') jako f:
            cert = f.read()
        przy open(key_file, 'r') jako f:
            key = f.read()
        zwróć cert, key
    w_końcu:
        dla name w tempnames:
            os.remove(name)

TMP_CADIR = 'cadir'

def unmake_ca():
    shutil.rmtree(TMP_CADIR)

def make_ca():
    os.mkdir(TMP_CADIR)
    przy open(os.path.join('cadir','index.txt'),'a+') jako f:
        dalej # empty file
    przy open(os.path.join('cadir','crl.txt'),'a+') jako f:
        f.write("00")
    przy open(os.path.join('cadir','index.txt.attr'),'w+') jako f:
        f.write('unique_subject = no')

    przy tempfile.NamedTemporaryFile("w") jako t:
        t.write(req_template.format(hostname='our-ca-server'))
        t.flush()
        przy tempfile.NamedTemporaryFile() jako f:
            args = ['req', '-new', '-days', '3650', '-extensions', 'v3_ca', '-nodes',
                    '-newkey', 'rsa:2048', '-keyout', 'pycakey.pem',
                    '-out', f.name,
                    '-subj', '/C=XY/L=Castle Anthrax/O=Python Software Foundation CA/CN=our-ca-server']
            check_call(['openssl'] + args)
            args = ['ca', '-config', t.name, '-create_serial',
                    '-out', 'pycacert.pem', '-batch', '-outdir', TMP_CADIR,
                    '-keyfile', 'pycakey.pem', '-days', '3650',
                    '-selfsign', '-extensions', 'v3_ca', '-infiles', f.name ]
            check_call(['openssl'] + args)
            args = ['ca', '-config', t.name, '-gencrl', '-out', 'revocation.crl']
            check_call(['openssl'] + args)

jeżeli __name__ == '__main__':
    os.chdir(here)
    cert, key = make_cert_key('localhost')
    przy open('ssl_cert.pem', 'w') jako f:
        f.write(cert)
    przy open('ssl_key.pem', 'w') jako f:
        f.write(key)
    print("password protecting ssl_key.pem w ssl_key.passwd.pem")
    check_call(['openssl','rsa','-in','ssl_key.pem','-out','ssl_key.passwd.pem','-des3','-passout','pass:somepass'])
    check_call(['openssl','rsa','-in','ssl_key.pem','-out','keycert.passwd.pem','-des3','-passout','pass:somepass'])

    przy open('keycert.pem', 'w') jako f:
        f.write(key)
        f.write(cert)

    przy open('keycert.passwd.pem', 'a+') jako f:
        f.write(cert)

    # For certificate matching tests
    make_ca()
    cert, key = make_cert_key('fakehostname')
    przy open('keycert2.pem', 'w') jako f:
        f.write(key)
        f.write(cert)

    cert, key = make_cert_key('localhost', Prawda)
    przy open('keycert3.pem', 'w') jako f:
        f.write(key)
        f.write(cert)

    cert, key = make_cert_key('fakehostname', Prawda)
    przy open('keycert4.pem', 'w') jako f:
        f.write(key)
        f.write(cert)

    unmake_ca()
    print("\n\nPlease change the values w test_ssl.py, test_parse_cert function related to notAfter,notBefore oraz serialNumber")
    check_call(['openssl','x509','-in','keycert.pem','-dates','-serial','-noout'])
