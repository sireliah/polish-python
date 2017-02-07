"""bytecode_helper - support tools dla testing correct bytecode generation"""

zaimportuj unittest
zaimportuj dis
zaimportuj io

_UNSPECIFIED = object()

klasa BytecodeTestCase(unittest.TestCase):
    """Custom assertion methods dla inspecting bytecode."""

    def get_disassembly_as_string(self, co):
        s = io.StringIO()
        dis.dis(co, file=s)
        zwróć s.getvalue()

    def assertInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Returns instr jeżeli op jest found, otherwise throws AssertionError"""
        dla instr w dis.get_instructions(x):
            jeżeli instr.opname == opname:
                jeżeli argval jest _UNSPECIFIED albo instr.argval == argval:
                    zwróć instr
        disassembly = self.get_disassembly_as_string(x)
        jeżeli argval jest _UNSPECIFIED:
            msg = '%s nie found w bytecode:\n%s' % (opname, disassembly)
        inaczej:
            msg = '(%s,%r) nie found w bytecode:\n%s'
            msg = msg % (opname, argval, disassembly)
        self.fail(msg)

    def assertNotInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Throws AssertionError jeżeli op jest found"""
        dla instr w dis.get_instructions(x):
            jeżeli instr.opname == opname:
                disassembly = self.get_disassembly_as_string(co)
                jeżeli opargval jest _UNSPECIFIED:
                    msg = '%s occurs w bytecode:\n%s' % (opname, disassembly)
                albo_inaczej instr.argval == argval:
                    msg = '(%s,%r) occurs w bytecode:\n%s'
                    msg = msg % (opname, argval, disassembly)
                self.fail(msg)
