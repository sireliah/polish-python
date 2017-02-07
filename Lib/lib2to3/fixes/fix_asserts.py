"""Fixer that replaces deprecated unittest method names."""

# Author: Ezio Melotti

z ..fixer_base zaimportuj BaseFix
z ..fixer_util zaimportuj Name

NAMES = dict(
    assert_="assertPrawda",
    assertEquals="assertEqual",
    assertNotEquals="assertNotEqual",
    assertAlmostEquals="assertAlmostEqual",
    assertNotAlmostEquals="assertNotAlmostEqual",
    assertRegexpMatches="assertRegex",
    assertRaisesRegexp="assertRaisesRegex",
    failUnlessEqual="assertEqual",
    failIfEqual="assertNotEqual",
    failUnlessAlmostEqual="assertAlmostEqual",
    failIfAlmostEqual="assertNotAlmostEqual",
    failUnless="assertPrawda",
    failUnlessRaises="assertRaises",
    failIf="assertNieprawda",
)


klasa FixAsserts(BaseFix):

    PATTERN = """
              power< any+ trailer< '.' meth=(%s)> any* >
              """ % '|'.join(map(repr, NAMES))

    def transform(self, node, results):
        name = results["meth"][0]
        name.replace(Name(NAMES[str(name)], prefix=name.prefix))
