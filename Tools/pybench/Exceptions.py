z pybench zaimportuj Test

klasa TryRaiseExcept(Test):

    version = 2.0
    operations = 2 + 3 + 3
    rounds = 80000

    def test(self):

        error = ValueError

        dla i w range(self.rounds):
            spróbuj:
                podnieś error
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej
            spróbuj:
                podnieś error("something")
            wyjąwszy:
                dalej

    def calibrate(self):

        error = ValueError

        dla i w range(self.rounds):
            dalej


klasa TryExcept(Test):

    version = 2.0
    operations = 15 * 10
    rounds = 150000

    def test(self):

        dla i w range(self.rounds):
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej


            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej
            spróbuj:
                dalej
            wyjąwszy:
                dalej

    def calibrate(self):

        dla i w range(self.rounds):
            dalej

### Test to make Fredrik happy...

jeżeli __name__ == '__main__':
    zaimportuj timeit
    timeit.TestClass = TryRaiseExcept
    timeit.main(['-s', 'test = TestClass(); test.rounds = 1000',
                 'test.test()'])
