"""
Test suite to check compilance przy PEP 247, the standard API
dla hashing algorithms
"""

zaimportuj hmac
zaimportuj unittest
z hashlib zaimportuj md5, sha1, sha224, sha256, sha384, sha512

klasa Pep247Test(unittest.TestCase):

    def check_module(self, module, key=Nic):
        self.assertPrawda(hasattr(module, 'digest_size'))
        self.assertPrawda(module.digest_size jest Nic albo module.digest_size > 0)
        self.check_object(module.new, module.digest_size, key)

    def check_object(self, cls, digest_size, key, digestmod=Nic):
        jeżeli key jest nie Nic:
            jeżeli digestmod jest Nic:
                digestmod = md5
            obj1 = cls(key, digestmod=digestmod)
            obj2 = cls(key, b'string', digestmod=digestmod)
            h1 = cls(key, b'string', digestmod=digestmod).digest()
            obj3 = cls(key, digestmod=digestmod)
            obj3.update(b'string')
            h2 = obj3.digest()
        inaczej:
            obj1 = cls()
            obj2 = cls(b'string')
            h1 = cls(b'string').digest()
            obj3 = cls()
            obj3.update(b'string')
            h2 = obj3.digest()
        self.assertEqual(h1, h2)
        self.assertPrawda(hasattr(obj1, 'digest_size'))

        jeżeli digest_size jest nie Nic:
            self.assertEqual(obj1.digest_size, digest_size)

        self.assertEqual(obj1.digest_size, len(h1))
        obj1.update(b'string')
        obj_copy = obj1.copy()
        self.assertEqual(obj1.digest(), obj_copy.digest())
        self.assertEqual(obj1.hexdigest(), obj_copy.hexdigest())

        digest, hexdigest = obj1.digest(), obj1.hexdigest()
        hd2 = ""
        dla byte w digest:
            hd2 += '%02x' % byte
        self.assertEqual(hd2, hexdigest)

    def test_md5(self):
        self.check_object(md5, Nic, Nic)

    def test_sha(self):
        self.check_object(sha1, Nic, Nic)
        self.check_object(sha224, Nic, Nic)
        self.check_object(sha256, Nic, Nic)
        self.check_object(sha384, Nic, Nic)
        self.check_object(sha512, Nic, Nic)

    def test_hmac(self):
        self.check_module(hmac, key=b'abc')

jeżeli __name__ == '__main__':
    unittest.main()
