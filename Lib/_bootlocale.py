"""A minimal subset of the locale module used at interpreter startup
(imported by the _io module), w order to reduce startup time.

Don't zaimportuj directly z third-party code; use the `locale` module instead!
"""

zaimportuj sys
zaimportuj _locale

jeżeli sys.platform.startswith("win"):
    def getpreferredencoding(do_setlocale=Prawda):
        zwróć _locale._getdefaultlocale()[1]
inaczej:
    spróbuj:
        _locale.CODESET
    wyjąwszy AttributeError:
        def getpreferredencoding(do_setlocale=Prawda):
            # This path dla legacy systems needs the more complex
            # getdefaultlocale() function, zaimportuj the full locale module.
            zaimportuj locale
            zwróć locale.getpreferredencoding(do_setlocale)
    inaczej:
        def getpreferredencoding(do_setlocale=Prawda):
            assert nie do_setlocale
            result = _locale.nl_langinfo(_locale.CODESET)
            jeżeli nie result oraz sys.platform == 'darwin':
                # nl_langinfo can zwróć an empty string
                # when the setting has an invalid value.
                # Default to UTF-8 w that case because
                # UTF-8 jest the default charset on OSX oraz
                # returning nothing will crash the
                # interpreter.
                result = 'UTF-8'
            zwróć result
