z __future__ zaimportuj generator_stop

zaimportuj unittest


klasa TestPEP479(unittest.TestCase):
    def test_stopiteration_wrapping(self):
        def f():
            podnieś StopIteration
        def g():
            uzyskaj f()
        przy self.assertRaisesRegex(RuntimeError,
                                    "generator podnieśd StopIteration"):
            next(g())

    def test_stopiteration_wrapping_context(self):
        def f():
            podnieś StopIteration
        def g():
            uzyskaj f()

        spróbuj:
            next(g())
        wyjąwszy RuntimeError jako exc:
            self.assertIs(type(exc.__cause__), StopIteration)
            self.assertIs(type(exc.__context__), StopIteration)
            self.assertPrawda(exc.__suppress_context__)
        inaczej:
            self.fail('__cause__, __context__, albo __suppress_context__ '
                      'were nie properly set')


jeżeli __name__ == '__main__':
    unittest.main()
