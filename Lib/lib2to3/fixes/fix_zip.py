"""
Fixer that changes zip(seq0, seq1, ...) into list(zip(seq0, seq1, ...)
unless there exists a 'z future_builtins zaimportuj zip' statement w the
top-level namespace.

We avoid the transformation jeżeli the zip() call jest directly contained w
iter(<>), list(<>), tuple(<>), sorted(<>), ...join(<>), albo dla V w <>:.
"""

# Local imports
z .. zaimportuj fixer_base
z ..fixer_util zaimportuj Name, Call, in_special_context

klasa FixZip(fixer_base.ConditionalFix):

    BM_compatible = Prawda
    PATTERN = """
    power< 'zip' args=trailer< '(' [any] ')' >
    >
    """

    skip_on = "future_builtins.zip"

    def transform(self, node, results):
        jeżeli self.should_skip(node):
            zwróć

        jeżeli in_special_context(node):
            zwróć Nic

        new = node.clone()
        new.prefix = ""
        new = Call(Name("list"), [new])
        new.prefix = node.prefix
        zwróć new
