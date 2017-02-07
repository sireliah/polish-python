
zaimportuj unittest

klasa ExceptionTestCase(unittest.TestCase):
    def test_try_except_inaczej_finally(self):
        hit_wyjąwszy = Nieprawda
        hit_inaczej = Nieprawda
        hit_finally = Nieprawda

        spróbuj:
            podnieś Exception('nyaa!')
        wyjąwszy:
            hit_wyjąwszy = Prawda
        inaczej:
            hit_inaczej = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertPrawda(hit_except)
        self.assertPrawda(hit_finally)
        self.assertNieprawda(hit_inaczej)

    def test_try_except_inaczej_finally_no_exception(self):
        hit_wyjąwszy = Nieprawda
        hit_inaczej = Nieprawda
        hit_finally = Nieprawda

        spróbuj:
            dalej
        wyjąwszy:
            hit_wyjąwszy = Prawda
        inaczej:
            hit_inaczej = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertNieprawda(hit_except)
        self.assertPrawda(hit_finally)
        self.assertPrawda(hit_inaczej)

    def test_try_except_finally(self):
        hit_wyjąwszy = Nieprawda
        hit_finally = Nieprawda

        spróbuj:
            podnieś Exception('yarr!')
        wyjąwszy:
            hit_wyjąwszy = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertPrawda(hit_except)
        self.assertPrawda(hit_finally)

    def test_try_except_finally_no_exception(self):
        hit_wyjąwszy = Nieprawda
        hit_finally = Nieprawda

        spróbuj:
            dalej
        wyjąwszy:
            hit_wyjąwszy = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertNieprawda(hit_except)
        self.assertPrawda(hit_finally)

    def test_try_except(self):
        hit_wyjąwszy = Nieprawda

        spróbuj:
            podnieś Exception('ahoy!')
        wyjąwszy:
            hit_wyjąwszy = Prawda

        self.assertPrawda(hit_except)

    def test_try_except_no_exception(self):
        hit_wyjąwszy = Nieprawda

        spróbuj:
            dalej
        wyjąwszy:
            hit_wyjąwszy = Prawda

        self.assertNieprawda(hit_except)

    def test_try_except_inaczej(self):
        hit_wyjąwszy = Nieprawda
        hit_inaczej = Nieprawda

        spróbuj:
            podnieś Exception('foo!')
        wyjąwszy:
            hit_wyjąwszy = Prawda
        inaczej:
            hit_inaczej = Prawda

        self.assertNieprawda(hit_inaczej)
        self.assertPrawda(hit_except)

    def test_try_except_inaczej_no_exception(self):
        hit_wyjąwszy = Nieprawda
        hit_inaczej = Nieprawda

        spróbuj:
            dalej
        wyjąwszy:
            hit_wyjąwszy = Prawda
        inaczej:
            hit_inaczej = Prawda

        self.assertNieprawda(hit_except)
        self.assertPrawda(hit_inaczej)

    def test_try_finally_no_exception(self):
        hit_finally = Nieprawda

        spróbuj:
            dalej
        w_końcu:
            hit_finally = Prawda

        self.assertPrawda(hit_finally)

    def test_nested(self):
        hit_finally = Nieprawda
        hit_inner_wyjąwszy = Nieprawda
        hit_inner_finally = Nieprawda

        spróbuj:
            spróbuj:
                podnieś Exception('inner exception')
            wyjąwszy:
                hit_inner_wyjąwszy = Prawda
            w_końcu:
                hit_inner_finally = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertPrawda(hit_inner_except)
        self.assertPrawda(hit_inner_finally)
        self.assertPrawda(hit_finally)

    def test_nested_inaczej(self):
        hit_inaczej = Nieprawda
        hit_finally = Nieprawda
        hit_wyjąwszy = Nieprawda
        hit_inner_wyjąwszy = Nieprawda
        hit_inner_inaczej = Nieprawda

        spróbuj:
            spróbuj:
                dalej
            wyjąwszy:
                hit_inner_wyjąwszy = Prawda
            inaczej:
                hit_inner_inaczej = Prawda

            podnieś Exception('outer exception')
        wyjąwszy:
            hit_wyjąwszy = Prawda
        inaczej:
            hit_inaczej = Prawda
        w_końcu:
            hit_finally = Prawda

        self.assertNieprawda(hit_inner_except)
        self.assertPrawda(hit_inner_inaczej)
        self.assertNieprawda(hit_inaczej)
        self.assertPrawda(hit_finally)
        self.assertPrawda(hit_except)

jeżeli __name__ == '__main__':
    unittest.main()
