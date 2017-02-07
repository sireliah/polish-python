zaimportuj unittest
z io zaimportuj StringIO

z test zaimportuj support

NotDefined = object()

# A dispatch table all 8 combinations of providing
# sep, end, oraz file.
# I use this machinery so that I'm nie just dalejing default
# values to print, I'm either dalejing albo nie dalejing w the
# arguments.
dispatch = {
    (Nieprawda, Nieprawda, Nieprawda):
        lambda args, sep, end, file: print(*args),
    (Nieprawda, Nieprawda, Prawda):
        lambda args, sep, end, file: print(file=file, *args),
    (Nieprawda, Prawda,  Nieprawda):
        lambda args, sep, end, file: print(end=end, *args),
    (Nieprawda, Prawda,  Prawda):
        lambda args, sep, end, file: print(end=end, file=file, *args),
    (Prawda,  Nieprawda, Nieprawda):
        lambda args, sep, end, file: print(sep=sep, *args),
    (Prawda,  Nieprawda, Prawda):
        lambda args, sep, end, file: print(sep=sep, file=file, *args),
    (Prawda,  Prawda,  Nieprawda):
        lambda args, sep, end, file: print(sep=sep, end=end, *args),
    (Prawda,  Prawda,  Prawda):
        lambda args, sep, end, file: print(sep=sep, end=end, file=file, *args),
}


# Class used to test __str__ oraz print
klasa ClassWith__str__:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        zwróć self.x


klasa TestPrint(unittest.TestCase):
    """Test correct operation of the print function."""

    def check(self, expected, args,
              sep=NotDefined, end=NotDefined, file=NotDefined):
        # Capture sys.stdout w a StringIO.  Call print przy args,
        # oraz przy sep, end, oraz file, jeżeli they're defined.  Result
        # must match expected.

        # Look up the actual function to call, based on jeżeli sep, end,
        # oraz file are defined.
        fn = dispatch[(sep jest nie NotDefined,
                       end jest nie NotDefined,
                       file jest nie NotDefined)]

        przy support.captured_stdout() jako t:
            fn(args, sep, end, file)

        self.assertEqual(t.getvalue(), expected)

    def test_print(self):
        def x(expected, args, sep=NotDefined, end=NotDefined):
            # Run the test 2 ways: nie using file, oraz using
            # file directed to a StringIO.

            self.check(expected, args, sep=sep, end=end)

            # When writing to a file, stdout jest expected to be empty
            o = StringIO()
            self.check('', args, sep=sep, end=end, file=o)

            # And o will contain the expected output
            self.assertEqual(o.getvalue(), expected)

        x('\n', ())
        x('a\n', ('a',))
        x('Nic\n', (Nic,))
        x('1 2\n', (1, 2))
        x('1   2\n', (1, ' ', 2))
        x('1*2\n', (1, 2), sep='*')
        x('1 s', (1, 's'), end='')
        x('a\nb\n', ('a', 'b'), sep='\n')
        x('1.01', (1.0, 1), sep='', end='')
        x('1*a*1.3+', (1, 'a', 1.3), sep='*', end='+')
        x('a\n\nb\n', ('a\n', 'b'), sep='\n')
        x('\0+ +\0\n', ('\0', ' ', '\0'), sep='+')

        x('a\n b\n', ('a\n', 'b'))
        x('a\n b\n', ('a\n', 'b'), sep=Nic)
        x('a\n b\n', ('a\n', 'b'), end=Nic)
        x('a\n b\n', ('a\n', 'b'), sep=Nic, end=Nic)

        x('*\n', (ClassWith__str__('*'),))
        x('abc 1\n', (ClassWith__str__('abc'), 1))

        # errors
        self.assertRaises(TypeError, print, '', sep=3)
        self.assertRaises(TypeError, print, '', end=3)
        self.assertRaises(AttributeError, print, '', file='')

    def test_print_flush(self):
        # operation of the flush flag
        klasa filelike:
            def __init__(self):
                self.written = ''
                self.flushed = 0

            def write(self, str):
                self.written += str

            def flush(self):
                self.flushed += 1

        f = filelike()
        print(1, file=f, end='', flush=Prawda)
        print(2, file=f, end='', flush=Prawda)
        print(3, file=f, flush=Nieprawda)
        self.assertEqual(f.written, '123\n')
        self.assertEqual(f.flushed, 2)

        # ensure exceptions z flush are dalejed through
        klasa noflush:
            def write(self, str):
                dalej

            def flush(self):
                podnieś RuntimeError
        self.assertRaises(RuntimeError, print, 1, file=noflush(), flush=Prawda)

jeżeli __name__ == "__main__":
    unittest.main()
