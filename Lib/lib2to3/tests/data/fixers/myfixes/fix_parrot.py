z lib2to3.fixer_base zaimportuj BaseFix
z lib2to3.fixer_util zaimportuj Name

klasa FixParrot(BaseFix):
    """
    Change functions named 'parrot' to 'cheese'.
    """

    PATTERN = """funcdef < 'def' name='parrot' any* >"""

    def transform(self, node, results):
        name = results["name"]
        name.replace(Name("cheese", name.prefix))
