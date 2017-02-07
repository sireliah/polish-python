klasa Delegator:

    # The cache jest only used to be able to change delegates!

    def __init__(self, delegate=Nic):
        self.delegate = delegate
        self.__cache = set()

    def __getattr__(self, name):
        attr = getattr(self.delegate, name) # May podnieś AttributeError
        setattr(self, name, attr)
        self.__cache.add(name)
        zwróć attr

    def resetcache(self):
        dla key w self.__cache:
            spróbuj:
                delattr(self, key)
            wyjąwszy AttributeError:
                dalej
        self.__cache.clear()

    def setdelegate(self, delegate):
        self.resetcache()
        self.delegate = delegate
