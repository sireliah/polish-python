zaimportuj unittest
zaimportuj builtins
zaimportuj rlcompleter

klasa CompleteMe:
    """ Trivial klasa used w testing rlcompleter.Completer. """
    spam = 1


klasa TestRlcompleter(unittest.TestCase):
    def setUp(self):
        self.stdcompleter = rlcompleter.Completer()
        self.completer = rlcompleter.Completer(dict(spam=int,
                                                    egg=str,
                                                    CompleteMe=CompleteMe))

        # forces stdcompleter to bind builtins namespace
        self.stdcompleter.complete('', 0)

    def test_namespace(self):
        klasa A(dict):
            dalej
        klasa B(list):
            dalej

        self.assertPrawda(self.stdcompleter.use_main_ns)
        self.assertNieprawda(self.completer.use_main_ns)
        self.assertNieprawda(rlcompleter.Completer(A()).use_main_ns)
        self.assertRaises(TypeError, rlcompleter.Completer, B((1,)))

    def test_global_matches(self):
        # test przy builtins namespace
        self.assertEqual(sorted(self.stdcompleter.global_matches('di')),
                         [x+'(' dla x w dir(builtins) jeżeli x.startswith('di')])
        self.assertEqual(sorted(self.stdcompleter.global_matches('st')),
                         [x+'(' dla x w dir(builtins) jeżeli x.startswith('st')])
        self.assertEqual(self.stdcompleter.global_matches('akaksajadhak'), [])

        # test przy a customized namespace
        self.assertEqual(self.completer.global_matches('CompleteM'),
                         ['CompleteMe('])
        self.assertEqual(self.completer.global_matches('eg'),
                         ['egg('])
        # XXX: see issue5256
        self.assertEqual(self.completer.global_matches('CompleteM'),
                         ['CompleteMe('])

    def test_attr_matches(self):
        # test przy builtins namespace
        self.assertEqual(self.stdcompleter.attr_matches('str.s'),
                         ['str.{}('.format(x) dla x w dir(str)
                          jeżeli x.startswith('s')])
        self.assertEqual(self.stdcompleter.attr_matches('tuple.foospamegg'), [])

        # test przy a customized namespace
        self.assertEqual(self.completer.attr_matches('CompleteMe.sp'),
                         ['CompleteMe.spam'])
        self.assertEqual(self.completer.attr_matches('Completeme.egg'), [])

        CompleteMe.me = CompleteMe
        self.assertEqual(self.completer.attr_matches('CompleteMe.me.me.sp'),
                         ['CompleteMe.me.me.spam'])
        self.assertEqual(self.completer.attr_matches('egg.s'),
                         ['egg.{}('.format(x) dla x w dir(str)
                          jeżeli x.startswith('s')])

    def test_complete(self):
        completer = rlcompleter.Completer()
        self.assertEqual(completer.complete('', 0), '\t')
        self.assertEqual(completer.complete('a', 0), 'and')
        self.assertEqual(completer.complete('a', 1), 'as')
        self.assertEqual(completer.complete('as', 2), 'assert')
        self.assertEqual(completer.complete('an', 0), 'and')

jeżeli __name__ == '__main__':
    unittest.main()
