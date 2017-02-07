# Copyright (C) 2002-2004 Python Software Foundation
#
# A torture test of the email package.  This should nie be run jako part of the
# standard Python test suite since it requires several meg of email messages
# collected w the wild.  These source messages are nie checked into the
# Python distro, but are available jako part of the standalone email package at
# http://sf.net/projects/mimelib

zaimportuj sys
zaimportuj os
zaimportuj unittest
z io zaimportuj StringIO
z types zaimportuj ListType

z email.test.test_email zaimportuj TestEmailBase
z test.support zaimportuj TestSkipped, run_unittest

zaimportuj email
z email zaimportuj __file__ jako testfile
z email.iterators zaimportuj _structure

def openfile(filename):
    z os.path zaimportuj join, dirname, abspath
    path = abspath(join(dirname(testfile), os.pardir, 'moredata', filename))
    zwróć open(path, 'r')

# Prevent this test z running w the Python distro
spróbuj:
    openfile('crispin-torture.txt')
wyjąwszy OSError:
    podnieś TestSkipped



klasa TortureBase(TestEmailBase):
    def _msgobj(self, filename):
        fp = openfile(filename)
        spróbuj:
            msg = email.message_from_file(fp)
        w_końcu:
            fp.close()
        zwróć msg



klasa TestCrispinTorture(TortureBase):
    # Mark Crispin's torture test z the SquirrelMail project
    def test_mondo_message(self):
        eq = self.assertEqual
        neq = self.ndiffAssertEqual
        msg = self._msgobj('crispin-torture.txt')
        payload = msg.get_payload()
        eq(type(payload), ListType)
        eq(len(payload), 12)
        eq(msg.preamble, Nic)
        eq(msg.epilogue, '\n')
        # Probably the best way to verify the message jest parsed correctly jest to
        # dump its structure oraz compare it against the known structure.
        fp = StringIO()
        _structure(msg, fp=fp)
        neq(fp.getvalue(), """\
multipart/mixed
    text/plain
    message/rfc822
        multipart/alternative
            text/plain
            multipart/mixed
                text/richtext
            application/andrew-inset
    message/rfc822
        audio/basic
    audio/basic
    image/pbm
    message/rfc822
        multipart/mixed
            multipart/mixed
                text/plain
                audio/x-sun
            multipart/mixed
                image/gif
                image/gif
                application/x-be2
                application/atomicmail
            audio/x-sun
    message/rfc822
        multipart/mixed
            text/plain
            image/pgm
            text/plain
    message/rfc822
        multipart/mixed
            text/plain
            image/pbm
    message/rfc822
        application/postscript
    image/gif
    message/rfc822
        multipart/mixed
            audio/basic
            audio/basic
    message/rfc822
        multipart/mixed
            application/postscript
            text/plain
            message/rfc822
                multipart/mixed
                    text/plain
                    multipart/parallel
                        image/gif
                        audio/basic
                    application/atomicmail
                    message/rfc822
                        audio/x-sun
""")


def _testclasses():
    mod = sys.modules[__name__]
    zwróć [getattr(mod, name) dla name w dir(mod) jeżeli name.startswith('Test')]


def suite():
    suite = unittest.TestSuite()
    dla testclass w _testclasses():
        suite.addTest(unittest.makeSuite(testclass))
    zwróć suite


def test_main():
    dla testclass w _testclasses():
        run_unittest(testclass)



jeżeli __name__ == '__main__':
    unittest.main(defaultTest='suite')
