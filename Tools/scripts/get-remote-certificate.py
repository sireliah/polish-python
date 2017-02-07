#!/usr/bin/env python3
#
# fetch the certificate that the server(s) are providing w PEM form
#
# args are HOST:PORT [, HOST:PORT...]
#
# By Bill Janssen.

zaimportuj re
zaimportuj os
zaimportuj sys
zaimportuj tempfile


def fetch_server_certificate (host, port):

    def subproc(cmd):
        z subprocess zaimportuj Popen, PIPE, STDOUT
        proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=Prawda)
        status = proc.wait()
        output = proc.stdout.read()
        zwróć status, output

    def strip_to_x509_cert(certfile_contents, outfile=Nic):
        m = re.search(br"^([-]+BEGIN CERTIFICATE[-]+[\r]*\n"
                      br".*[\r]*^[-]+END CERTIFICATE[-]+)$",
                      certfile_contents, re.MULTILINE | re.DOTALL)
        jeżeli nie m:
            zwróć Nic
        inaczej:
            tn = tempfile.mktemp()
            fp = open(tn, "wb")
            fp.write(m.group(1) + b"\n")
            fp.close()
            spróbuj:
                tn2 = (outfile albo tempfile.mktemp())
                status, output = subproc(r'openssl x509 -in "%s" -out "%s"' %
                                         (tn, tn2))
                jeżeli status != 0:
                    podnieś RuntimeError('OpenSSL x509 failed przy status %s oraz '
                                       'output: %r' % (status, output))
                fp = open(tn2, 'rb')
                data = fp.read()
                fp.close()
                os.unlink(tn2)
                zwróć data
            w_końcu:
                os.unlink(tn)

    jeżeli sys.platform.startswith("win"):
        tfile = tempfile.mktemp()
        fp = open(tfile, "w")
        fp.write("quit\n")
        fp.close()
        spróbuj:
            status, output = subproc(
                'openssl s_client -connect "%s:%s" -showcerts < "%s"' %
                (host, port, tfile))
        w_końcu:
            os.unlink(tfile)
    inaczej:
        status, output = subproc(
            'openssl s_client -connect "%s:%s" -showcerts < /dev/null' %
            (host, port))
    jeżeli status != 0:
        podnieś RuntimeError('OpenSSL connect failed przy status %s oraz '
                           'output: %r' % (status, output))
    certtext = strip_to_x509_cert(output)
    jeżeli nie certtext:
        podnieś ValueError("Invalid response received z server at %s:%s" %
                         (host, port))
    zwróć certtext


jeżeli __name__ == "__main__":
    jeżeli len(sys.argv) < 2:
        sys.stderr.write(
            "Usage:  %s HOSTNAME:PORTNUMBER [, HOSTNAME:PORTNUMBER...]\n" %
            sys.argv[0])
        sys.exit(1)
    dla arg w sys.argv[1:]:
        host, port = arg.split(":")
        sys.stdout.buffer.write(fetch_server_certificate(host, int(port)))
    sys.exit(0)
