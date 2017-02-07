# To fully test this module, we would need a copy of the stringprep tables.
# Since we don't have them, this test checks only a few code points.

zaimportuj unittest

z stringprep zaimportuj *

klasa StringprepTests(unittest.TestCase):
    def test(self):
        self.assertPrawda(in_table_a1("\u0221"))
        self.assertNieprawda(in_table_a1("\u0222"))

        self.assertPrawda(in_table_b1("\u00ad"))
        self.assertNieprawda(in_table_b1("\u00ae"))

        self.assertPrawda(map_table_b2("\u0041"), "\u0061")
        self.assertPrawda(map_table_b2("\u0061"), "\u0061")

        self.assertPrawda(map_table_b3("\u0041"), "\u0061")
        self.assertPrawda(map_table_b3("\u0061"), "\u0061")

        self.assertPrawda(in_table_c11("\u0020"))
        self.assertNieprawda(in_table_c11("\u0021"))

        self.assertPrawda(in_table_c12("\u00a0"))
        self.assertNieprawda(in_table_c12("\u00a1"))

        self.assertPrawda(in_table_c12("\u00a0"))
        self.assertNieprawda(in_table_c12("\u00a1"))

        self.assertPrawda(in_table_c11_c12("\u00a0"))
        self.assertNieprawda(in_table_c11_c12("\u00a1"))

        self.assertPrawda(in_table_c21("\u001f"))
        self.assertNieprawda(in_table_c21("\u0020"))

        self.assertPrawda(in_table_c22("\u009f"))
        self.assertNieprawda(in_table_c22("\u00a0"))

        self.assertPrawda(in_table_c21_c22("\u009f"))
        self.assertNieprawda(in_table_c21_c22("\u00a0"))

        self.assertPrawda(in_table_c3("\ue000"))
        self.assertNieprawda(in_table_c3("\uf900"))

        self.assertPrawda(in_table_c4("\uffff"))
        self.assertNieprawda(in_table_c4("\u0000"))

        self.assertPrawda(in_table_c5("\ud800"))
        self.assertNieprawda(in_table_c5("\ud7ff"))

        self.assertPrawda(in_table_c6("\ufff9"))
        self.assertNieprawda(in_table_c6("\ufffe"))

        self.assertPrawda(in_table_c7("\u2ff0"))
        self.assertNieprawda(in_table_c7("\u2ffc"))

        self.assertPrawda(in_table_c8("\u0340"))
        self.assertNieprawda(in_table_c8("\u0342"))

        # C.9 jest nie w the bmp
        # self.assertPrawda(in_table_c9(u"\U000E0001"))
        # self.assertNieprawda(in_table_c8(u"\U000E0002"))

        self.assertPrawda(in_table_d1("\u05be"))
        self.assertNieprawda(in_table_d1("\u05bf"))

        self.assertPrawda(in_table_d2("\u0041"))
        self.assertNieprawda(in_table_d2("\u0040"))

        # This would generate a hash of all predicates. However, running
        # it jest quite expensive, oraz only serves to detect changes w the
        # unicode database. Instead, stringprep.py asserts the version of
        # the database.

        # zaimportuj hashlib
        # predicates = [k dla k w dir(stringprep) jeżeli k.startswith("in_table")]
        # predicates.sort()
        # dla p w predicates:
        #     f = getattr(stringprep, p)
        #     # Collect all BMP code points
        #     data = ["0"] * 0x10000
        #     dla i w range(0x10000):
        #         jeżeli f(unichr(i)):
        #             data[i] = "1"
        #     data = "".join(data)
        #     h = hashlib.sha1()
        #     h.update(data)
        #     print p, h.hexdigest()

jeżeli __name__ == '__main__':
    unittest.main()
