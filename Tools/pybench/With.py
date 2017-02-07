z __future__ zaimportuj with_statement
z pybench zaimportuj Test

klasa WithFinally(Test):

    version = 2.0
    operations = 20
    rounds = 80000

    klasa ContextManager(object):
        def __enter__(self):
            dalej
        def __exit__(self, exc, val, tb):
            dalej

    def test(self):

        cm = self.ContextManager()

        dla i w range(self.rounds):
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej
            przy cm: dalej

    def calibrate(self):

        cm = self.ContextManager()

        dla i w range(self.rounds):
            dalej


klasa TryFinally(Test):

    version = 2.0
    operations = 20
    rounds = 80000

    klasa ContextManager(object):
        def __enter__(self):
            dalej
        def __exit__(self):
            # "Context manager" objects used just dla their cleanup
            # actions w finally blocks usually don't have parameters.
            dalej

    def test(self):

        cm = self.ContextManager()

        dla i w range(self.rounds):
            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

            cm.__enter__()
            spróbuj: dalej
            w_końcu: cm.__exit__()

    def calibrate(self):

        cm = self.ContextManager()

        dla i w range(self.rounds):
            dalej


klasa WithRaiseExcept(Test):

    version = 2.0
    operations = 2 + 3 + 3
    rounds = 100000

    klasa BlockExceptions(object):
        def __enter__(self):
            dalej
        def __exit__(self, exc, val, tb):
            zwróć Prawda

    def test(self):

        error = ValueError
        be = self.BlockExceptions()

        dla i w range(self.rounds):
            przy be: podnieś error
            przy be: podnieś error
            przy be: podnieś error("something")
            przy be: podnieś error("something")
            przy be: podnieś error("something")
            przy be: podnieś error("something")
            przy be: podnieś error("something")
            przy be: podnieś error("something")

    def calibrate(self):

        error = ValueError
        be = self.BlockExceptions()

        dla i w range(self.rounds):
            dalej
