z test zaimportuj support
zaimportuj unittest
zaimportuj sys

# Skip test jeżeli nis module does nie exist.
nis = support.import_module('nis')


klasa NisTests(unittest.TestCase):
    def test_maps(self):
        spróbuj:
            maps = nis.maps()
        wyjąwszy nis.error jako msg:
            # NIS jest probably nie active, so this test isn't useful
            self.skipTest(str(msg))
        spróbuj:
            # On some systems, this map jest only accessible to the
            # super user
            maps.remove("passwd.adjunct.byname")
        wyjąwszy ValueError:
            dalej

        done = 0
        dla nismap w maps:
            mapping = nis.cat(nismap)
            dla k, v w mapping.items():
                jeżeli nie k:
                    kontynuuj
                jeżeli nis.match(k, nismap) != v:
                    self.fail("NIS match failed dla key `%s' w map `%s'" % (k, nismap))
                inaczej:
                    # just test the one key, otherwise this test could take a
                    # very long time
                    done = 1
                    przerwij
            jeżeli done:
                przerwij

jeżeli __name__ == '__main__':
    unittest.main()
