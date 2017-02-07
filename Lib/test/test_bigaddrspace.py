"""
These tests are meant to exercise that requests to create objects bigger
than what the address space allows are properly met przy an OverflowError
(rather than crash weirdly).

Primarily, this means 32-bit builds przy at least 2 GB of available memory.
You need to dalej the -M option to regrtest (e.g. "-M 2.1G") dla tests to
be enabled.
"""

z test zaimportuj support
z test.support zaimportuj bigaddrspacetest, MAX_Py_ssize_t

zaimportuj unittest
zaimportuj operator
zaimportuj sys


klasa BytesTest(unittest.TestCase):

    @bigaddrspacetest
    def test_concat(self):
        # Allocate a bytestring that's near the maximum size allowed by
        # the address space, oraz then try to build a new, larger one through
        # concatenation.
        spróbuj:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.add, x, b"x" * 128)
        w_końcu:
            x = Nic

    @bigaddrspacetest
    def test_optimized_concat(self):
        spróbuj:
            x = b"x" * (MAX_Py_ssize_t - 128)

            przy self.assertRaises(OverflowError) jako cm:
                # this statement used a fast path w ceval.c
                x = x + b"x" * 128

            przy self.assertRaises(OverflowError) jako cm:
                # this statement used a fast path w ceval.c
                x +=  b"x" * 128
        w_końcu:
            x = Nic

    @bigaddrspacetest
    def test_repeat(self):
        spróbuj:
            x = b"x" * (MAX_Py_ssize_t - 128)
            self.assertRaises(OverflowError, operator.mul, x, 128)
        w_końcu:
            x = Nic


klasa StrTest(unittest.TestCase):

    unicodesize = 2 jeżeli sys.maxunicode < 65536 inaczej 4

    @bigaddrspacetest
    def test_concat(self):
        spróbuj:
            # Create a string that would fill almost the address space
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            # Unicode objects trigger MemoryError w case an operation that's
            # going to cause a size overflow jest executed
            self.assertRaises(MemoryError, operator.add, x, x)
        w_końcu:
            x = Nic

    @bigaddrspacetest
    def test_optimized_concat(self):
        spróbuj:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))

            przy self.assertRaises(MemoryError) jako cm:
                # this statement uses a fast path w ceval.c
                x = x + x

            przy self.assertRaises(MemoryError) jako cm:
                # this statement uses a fast path w ceval.c
                x +=  x
        w_końcu:
            x = Nic

    @bigaddrspacetest
    def test_repeat(self):
        spróbuj:
            x = "x" * int(MAX_Py_ssize_t // (1.1 * self.unicodesize))
            self.assertRaises(MemoryError, operator.mul, x, 2)
        w_końcu:
            x = Nic


def test_main():
    support.run_unittest(BytesTest, StrTest)

jeżeli __name__ == '__main__':
    jeżeli len(sys.argv) > 1:
        support.set_memlimit(sys.argv[1])
    test_main()
