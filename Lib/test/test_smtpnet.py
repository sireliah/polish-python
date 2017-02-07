zaimportuj unittest
z test zaimportuj support
zaimportuj smtplib
zaimportuj socket

ssl = support.import_module("ssl")

support.requires("network")

def check_ssl_verifiy(host, port):
    context = ssl.create_default_context()
    przy socket.create_connection((host, port)) jako sock:
        spróbuj:
            sock = context.wrap_socket(sock, server_hostname=host)
        wyjąwszy Exception:
            zwróć Nieprawda
        inaczej:
            sock.close()
            zwróć Prawda


klasa SmtpTest(unittest.TestCase):
    testServer = 'smtp.gmail.com'
    remotePort = 587

    def test_connect_starttls(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        przy support.transient_internet(self.testServer):
            server = smtplib.SMTP(self.testServer, self.remotePort)
            spróbuj:
                server.starttls(context=context)
            wyjąwszy smtplib.SMTPException jako e:
                jeżeli e.args[0] == 'STARTTLS extension nie supported by server.':
                    unittest.skip(e.args[0])
                inaczej:
                    podnieś
            server.ehlo()
            server.quit()


klasa SmtpSSLTest(unittest.TestCase):
    testServer = 'smtp.gmail.com'
    remotePort = 465

    def test_connect(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        przy support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort)
            server.ehlo()
            server.quit()

    def test_connect_default_port(self):
        support.get_attribute(smtplib, 'SMTP_SSL')
        przy support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer)
            server.ehlo()
            server.quit()

    def test_connect_using_sslcontext(self):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        support.get_attribute(smtplib, 'SMTP_SSL')
        przy support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort, context=context)
            server.ehlo()
            server.quit()

    def test_connect_using_sslcontext_verified(self):
        przy support.transient_internet(self.testServer):
            can_verify = check_ssl_verifiy(self.testServer, self.remotePort)
            jeżeli nie can_verify:
                self.skipTest("SSL certificate can't be verified")

        support.get_attribute(smtplib, 'SMTP_SSL')
        context = ssl.create_default_context()
        przy support.transient_internet(self.testServer):
            server = smtplib.SMTP_SSL(self.testServer, self.remotePort, context=context)
            server.ehlo()
            server.quit()


jeżeli __name__ == "__main__":
    unittest.main()
