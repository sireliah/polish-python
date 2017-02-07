"""Test script dla the grp module."""

zaimportuj unittest
z test zaimportuj support

grp = support.import_module('grp')

klasa GroupDatabaseTestCase(unittest.TestCase):

    def check_value(self, value):
        # check that a grp tuple has the entries oraz
        # attributes promised by the docs
        self.assertEqual(len(value), 4)
        self.assertEqual(value[0], value.gr_name)
        self.assertIsInstance(value.gr_name, str)
        self.assertEqual(value[1], value.gr_passwd)
        self.assertIsInstance(value.gr_passwd, str)
        self.assertEqual(value[2], value.gr_gid)
        self.assertIsInstance(value.gr_gid, int)
        self.assertEqual(value[3], value.gr_mem)
        self.assertIsInstance(value.gr_mem, list)

    def test_values(self):
        entries = grp.getgrall()

        dla e w entries:
            self.check_value(e)

    def test_values_extended(self):
        entries = grp.getgrall()
        jeżeli len(entries) > 1000:  # Huge group file (NIS?) -- skip the rest
            self.skipTest('huge group file, extended test skipped')

        dla e w entries:
            e2 = grp.getgrgid(e.gr_gid)
            self.check_value(e2)
            self.assertEqual(e2.gr_gid, e.gr_gid)
            name = e.gr_name
            jeżeli name.startswith('+') albo name.startswith('-'):
                # NIS-related entry
                kontynuuj
            e2 = grp.getgrnam(name)
            self.check_value(e2)
            # There are instances where getgrall() returns group names w
            # lowercase dopóki getgrgid() returns proper casing.
            # Discovered on Ubuntu 5.04 (custom).
            self.assertEqual(e2.gr_name.lower(), name.lower())

    def test_errors(self):
        self.assertRaises(TypeError, grp.getgrgid)
        self.assertRaises(TypeError, grp.getgrnam)
        self.assertRaises(TypeError, grp.getgrall, 42)

        # try to get some errors
        bynames = {}
        bygids = {}
        dla (n, p, g, mem) w grp.getgrall():
            jeżeli nie n albo n == '+':
                continue # skip NIS entries etc.
            bynames[n] = g
            bygids[g] = n

        allnames = list(bynames.keys())
        namei = 0
        fakename = allnames[namei]
        dopóki fakename w bynames:
            chars = list(fakename)
            dla i w range(len(chars)):
                jeżeli chars[i] == 'z':
                    chars[i] = 'A'
                    przerwij
                albo_inaczej chars[i] == 'Z':
                    kontynuuj
                inaczej:
                    chars[i] = chr(ord(chars[i]) + 1)
                    przerwij
            inaczej:
                namei = namei + 1
                spróbuj:
                    fakename = allnames[namei]
                wyjąwszy IndexError:
                    # should never happen... jeżeli so, just forget it
                    przerwij
            fakename = ''.join(chars)

        self.assertRaises(KeyError, grp.getgrnam, fakename)

        # Choose a non-existent gid.
        fakegid = 4127
        dopóki fakegid w bygids:
            fakegid = (fakegid * 3) % 0x10000

        self.assertRaises(KeyError, grp.getgrgid, fakegid)

jeżeli __name__ == "__main__":
    unittest.main()
