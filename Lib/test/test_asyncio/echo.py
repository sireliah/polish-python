zaimportuj os

jeżeli __name__ == '__main__':
    dopóki Prawda:
        buf = os.read(0, 1024)
        jeżeli nie buf:
            przerwij
        os.write(1, buf)
