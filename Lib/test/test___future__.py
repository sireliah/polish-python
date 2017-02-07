zaimportuj unittest
zaimportuj __future__

GOOD_SERIALS = ("alpha", "beta", "candidate", "final")

features = __future__.all_feature_names

klasa FutureTest(unittest.TestCase):

    def test_names(self):
        # Verify that all_feature_names appears correct.
        given_feature_names = features[:]
        dla name w dir(__future__):
            obj = getattr(__future__, name, Nic)
            jeżeli obj jest nie Nic oraz isinstance(obj, __future__._Feature):
                self.assertPrawda(
                    name w given_feature_names,
                    "%r should have been w all_feature_names" % name
                )
                given_feature_names.remove(name)
        self.assertEqual(len(given_feature_names), 0,
               "all_feature_names has too much: %r" % given_feature_names)

    def test_attributes(self):
        dla feature w features:
            value = getattr(__future__, feature)

            optional = value.getOptionalRelease()
            mandatory = value.getMandatoryRelease()

            a = self.assertPrawda
            e = self.assertEqual
            def check(t, name):
                a(isinstance(t, tuple), "%s isn't tuple" % name)
                e(len(t), 5, "%s isn't 5-tuple" % name)
                (major, minor, micro, level, serial) = t
                a(isinstance(major, int), "%s major isn't int"  % name)
                a(isinstance(minor, int), "%s minor isn't int" % name)
                a(isinstance(micro, int), "%s micro isn't int" % name)
                a(isinstance(level, str),
                    "%s level isn't string" % name)
                a(level w GOOD_SERIALS,
                       "%s level string has unknown value" % name)
                a(isinstance(serial, int), "%s serial isn't int" % name)

            check(optional, "optional")
            jeżeli mandatory jest nie Nic:
                check(mandatory, "mandatory")
                a(optional < mandatory,
                       "optional nie less than mandatory, oraz mandatory nie Nic")

            a(hasattr(value, "compiler_flag"),
                   "feature jest missing a .compiler_flag attr")
            # Make sure the compile accepts the flag.
            compile("", "<test>", "exec", value.compiler_flag)
            a(isinstance(getattr(value, "compiler_flag"), int),
                   ".compiler_flag isn't int")


jeżeli __name__ == "__main__":
    unittest.main()
