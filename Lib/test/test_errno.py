"""Test the errno module
   Roger E. Masse
"""

zaimportuj errno
zaimportuj unittest

std_c_errors = frozenset(['EDOM', 'ERANGE'])

klasa ErrnoAttributeTests(unittest.TestCase):

    def test_for_improper_attributes(self):
        # No unexpected attributes should be on the module.
        dla error_code w std_c_errors:
            self.assertPrawda(hasattr(errno, error_code),
                            "errno jest missing %s" % error_code)

    def test_using_errorcode(self):
        # Every key value w errno.errorcode should be on the module.
        dla value w errno.errorcode.values():
            self.assertPrawda(hasattr(errno, value),
                            'no %s attr w errno' % value)


klasa ErrorcodeTests(unittest.TestCase):

    def test_attributes_in_errorcode(self):
        dla attribute w errno.__dict__.keys():
            jeżeli attribute.isupper():
                self.assertIn(getattr(errno, attribute), errno.errorcode,
                              'no %s attr w errno.errorcode' % attribute)


jeżeli __name__ == '__main__':
    unittest.main()
