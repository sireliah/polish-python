zaimportuj os

jeżeli __name__ == '__main__':
    dopóki Prawda:
        buf = os.read(0, 1024)
        jeżeli nie buf:
            przerwij
        spróbuj:
            os.write(1, b'OUT:'+buf)
        wyjąwszy OSError jako ex:
            os.write(2, b'ERR:' + ex.__class__.__name__.encode('ascii'))
