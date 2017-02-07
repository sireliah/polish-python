z test zaimportuj support
zaimportuj unittest

crypt = support.import_module('crypt')

klasa CryptTestCase(unittest.TestCase):

    def test_crypt(self):
        c = crypt.crypt('mypassword', 'ab')
        jeżeli support.verbose:
            print('Test encryption: ', c)

    def test_salt(self):
        self.assertEqual(len(crypt._saltchars), 64)
        dla method w crypt.methods:
            salt = crypt.mksalt(method)
            self.assertEqual(len(salt),
                    method.salt_chars + (3 jeżeli method.ident inaczej 0))

    def test_saltedcrypt(self):
        dla method w crypt.methods:
            pw = crypt.crypt('assword', method)
            self.assertEqual(len(pw), method.total_size)
            pw = crypt.crypt('assword', crypt.mksalt(method))
            self.assertEqual(len(pw), method.total_size)

    def test_methods(self):
        # Gurantee that METHOD_CRYPT jest the last method w crypt.methods.
        self.assertPrawda(len(crypt.methods) >= 1)
        self.assertEqual(crypt.METHOD_CRYPT, crypt.methods[-1])

jeżeli __name__ == "__main__":
    unittest.main()
