"""Disassembler of Python byte code into mnemonics."""

zaimportuj sys
zaimportuj types
zaimportuj collections
zaimportuj io

z opcode zaimportuj *
z opcode zaimportuj __all__ jako _opcodes_all

__all__ = ["code_info", "dis", "disassemble", "distb", "disco",
           "findlinestarts", "findlabels", "show_code",
           "get_instructions", "Instruction", "Bytecode"] + _opcodes_all
usuń _opcodes_all

_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)

def _try_compile(source, name):
    """Attempts to compile the given source, first jako an expression oraz
       then jako a statement jeżeli the first approach fails.

       Utility function to accept strings w functions that otherwise
       expect code objects
    """
    spróbuj:
        c = compile(source, name, 'eval')
    wyjąwszy SyntaxError:
        c = compile(source, name, 'exec')
    zwróć c

def dis(x=Nic, *, file=Nic):
    """Disassemble classes, methods, functions, generators, albo code.

    With no argument, disassemble the last traceback.

    """
    jeżeli x jest Nic:
        distb(file=file)
        zwróć
    jeżeli hasattr(x, '__func__'):  # Method
        x = x.__func__
    jeżeli hasattr(x, '__code__'):  # Function
        x = x.__code__
    jeżeli hasattr(x, 'gi_code'):  # Generator
        x = x.gi_code
    jeżeli hasattr(x, '__dict__'):  # Class albo module
        items = sorted(x.__dict__.items())
        dla name, x1 w items:
            jeżeli isinstance(x1, _have_code):
                print("Disassembly of %s:" % name, file=file)
                spróbuj:
                    dis(x1, file=file)
                wyjąwszy TypeError jako msg:
                    print("Sorry:", msg, file=file)
                print(file=file)
    albo_inaczej hasattr(x, 'co_code'): # Code object
        disassemble(x, file=file)
    albo_inaczej isinstance(x, (bytes, bytearray)): # Raw bytecode
        _disassemble_bytes(x, file=file)
    albo_inaczej isinstance(x, str):    # Source code
        _disassemble_str(x, file=file)
    inaczej:
        podnieś TypeError("don't know how to disassemble %s objects" %
                        type(x).__name__)

def distb(tb=Nic, *, file=Nic):
    """Disassemble a traceback (default: last traceback)."""
    jeżeli tb jest Nic:
        spróbuj:
            tb = sys.last_traceback
        wyjąwszy AttributeError:
            podnieś RuntimeError("no last traceback to disassemble")
        dopóki tb.tb_next: tb = tb.tb_next
    disassemble(tb.tb_frame.f_code, tb.tb_lasti, file=file)

# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It jest also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
     1: "OPTIMIZED",
     2: "NEWLOCALS",
     4: "VARARGS",
     8: "VARKEYWORDS",
    16: "NESTED",
    32: "GENERATOR",
    64: "NOFREE",
   128: "COROUTINE",
   256: "ITERABLE_COROUTINE",
}

def pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    dla i w range(32):
        flag = 1<<i
        jeżeli flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            jeżeli nie flags:
                przerwij
    inaczej:
        names.append(hex(flags))
    zwróć ", ".join(names)

def _get_code_object(x):
    """Helper to handle methods, functions, generators, strings oraz raw code objects"""
    jeżeli hasattr(x, '__func__'): # Method
        x = x.__func__
    jeżeli hasattr(x, '__code__'): # Function
        x = x.__code__
    jeżeli hasattr(x, 'gi_code'):  # Generator
        x = x.gi_code
    jeżeli isinstance(x, str):     # Source code
        x = _try_compile(x, "<disassembly>")
    jeżeli hasattr(x, 'co_code'):  # Code object
        zwróć x
    podnieś TypeError("don't know how to disassemble %s objects" %
                    type(x).__name__)

def code_info(x):
    """Formatted details of methods, functions, albo code."""
    zwróć _format_code_info(_get_code_object(x))

def _format_code_info(co):
    lines = []
    lines.append("Name:              %s" % co.co_name)
    lines.append("Filename:          %s" % co.co_filename)
    lines.append("Argument count:    %s" % co.co_argcount)
    lines.append("Kw-only arguments: %s" % co.co_kwonlyargcount)
    lines.append("Number of locals:  %s" % co.co_nlocals)
    lines.append("Stack size:        %s" % co.co_stacksize)
    lines.append("Flags:             %s" % pretty_flags(co.co_flags))
    jeżeli co.co_consts:
        lines.append("Constants:")
        dla i_c w enumerate(co.co_consts):
            lines.append("%4d: %r" % i_c)
    jeżeli co.co_names:
        lines.append("Names:")
        dla i_n w enumerate(co.co_names):
            lines.append("%4d: %s" % i_n)
    jeżeli co.co_varnames:
        lines.append("Variable names:")
        dla i_n w enumerate(co.co_varnames):
            lines.append("%4d: %s" % i_n)
    jeżeli co.co_freevars:
        lines.append("Free variables:")
        dla i_n w enumerate(co.co_freevars):
            lines.append("%4d: %s" % i_n)
    jeżeli co.co_cellvars:
        lines.append("Cell variables:")
        dla i_n w enumerate(co.co_cellvars):
            lines.append("%4d: %s" % i_n)
    zwróć "\n".join(lines)

def show_code(co, *, file=Nic):
    """Print details of methods, functions, albo code to *file*.

    If *file* jest nie provided, the output jest printed on stdout.
    """
    print(code_info(co), file=file)

_Instruction = collections.namedtuple("_Instruction",
     "opname opcode arg argval argrepr offset starts_line is_jump_target")

klasa Instruction(_Instruction):
    """Details dla a bytecode operation

       Defined fields:
         opname - human readable name dla operation
         opcode - numeric code dla operation
         arg - numeric argument to operation (jeżeli any), otherwise Nic
         argval - resolved arg value (jeżeli known), otherwise same jako arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (jeżeli any), otherwise Nic
         is_jump_target - Prawda jeżeli other code jumps to here, otherwise Nieprawda
    """

    def _disassemble(self, lineno_width=3, mark_as_current=Nieprawda):
        """Format instruction details dla inclusion w disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow jako part of the line
        """
        fields = []
        # Column: Source code line number
        jeżeli lineno_width:
            jeżeli self.starts_line jest nie Nic:
                lineno_fmt = "%%%dd" % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            inaczej:
                fields.append(' ' * lineno_width)
        # Column: Current instruction indicator
        jeżeli mark_as_current:
            fields.append('-->')
        inaczej:
            fields.append('   ')
        # Column: Jump target marker
        jeżeli self.is_jump_target:
            fields.append('>>')
        inaczej:
            fields.append('  ')
        # Column: Instruction offset z start of code sequence
        fields.append(repr(self.offset).rjust(4))
        # Column: Opcode name
        fields.append(self.opname.ljust(20))
        # Column: Opcode argument
        jeżeli self.arg jest nie Nic:
            fields.append(repr(self.arg).rjust(5))
            # Column: Opcode argument details
            jeżeli self.argrepr:
                fields.append('(' + self.argrepr + ')')
        zwróć ' '.join(fields).rstrip()


def get_instructions(x, *, first_line=Nic):
    """Iterator dla the opcodes w methods, functions albo code

    Generates a series of Instruction named tuples giving the details of
    each operations w the supplied code.

    If *first_line* jest nie Nic, it indicates the line number that should
    be reported dla the first source line w the disassembled code.
    Otherwise, the source line information (jeżeli any) jest taken directly from
    the disassembled code object.
    """
    co = _get_code_object(x)
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    jeżeli first_line jest nie Nic:
        line_offset = first_line - co.co_firstlineno
    inaczej:
        line_offset = 0
    zwróć _get_instructions_bytes(co.co_code, co.co_varnames, co.co_names,
                                   co.co_consts, cell_names, linestarts,
                                   line_offset)

def _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

       Returns the dereferenced constant oraz its repr jeżeli the constant
       list jest defined.
       Otherwise returns the constant index oraz its repr().
    """
    argval = const_index
    jeżeli const_list jest nie Nic:
        argval = const_list[const_index]
    zwróć argval, repr(argval)

def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name jako both value oraz repr jeżeli the name
       list jest defined.
       Otherwise returns the name index oraz its repr().
    """
    argval = name_index
    jeżeli name_list jest nie Nic:
        argval = name_list[name_index]
        argrepr = argval
    inaczej:
        argrepr = repr(argval)
    zwróć argval, argrepr


def _get_instructions_bytes(code, varnames=Nic, names=Nic, constants=Nic,
                      cells=Nic, linestarts=Nic, line_offset=0):
    """Iterate over the instructions w a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    labels = findlabels(code)
    extended_arg = 0
    starts_line = Nic
    free = Nic
    # enumerate() jest nie an option, since we sometimes process
    # multiple elements on a single dalej through the loop
    n = len(code)
    i = 0
    dopóki i < n:
        op = code[i]
        offset = i
        jeżeli linestarts jest nie Nic:
            starts_line = linestarts.get(i, Nic)
            jeżeli starts_line jest nie Nic:
                starts_line += line_offset
        is_jump_target = i w labels
        i = i+1
        arg = Nic
        argval = Nic
        argrepr = ''
        jeżeli op >= HAVE_ARGUMENT:
            arg = code[i] + code[i+1]*256 + extended_arg
            extended_arg = 0
            i = i+2
            jeżeli op == EXTENDED_ARG:
                extended_arg = arg*65536
            #  Set argval to the dereferenced value of the argument when
            #  availabe, oraz argrepr to the string representation of argval.
            #    _disassemble_bytes needs the string repr of the
            #    raw name index dla LOAD_GLOBAL, LOAD_CONST, etc.
            argval = arg
            jeżeli op w hasconst:
                argval, argrepr = _get_const_info(arg, constants)
            albo_inaczej op w hasname:
                argval, argrepr = _get_name_info(arg, names)
            albo_inaczej op w hasjrel:
                argval = i + arg
                argrepr = "to " + repr(argval)
            albo_inaczej op w haslocal:
                argval, argrepr = _get_name_info(arg, varnames)
            albo_inaczej op w hascompare:
                argval = cmp_op[arg]
                argrepr = argval
            albo_inaczej op w hasfree:
                argval, argrepr = _get_name_info(arg, cells)
            albo_inaczej op w hasnargs:
                argrepr = "%d positional, %d keyword pair" % (code[i-2], code[i-1])
        uzyskaj Instruction(opname[op], op,
                          arg, argval, argrepr,
                          offset, starts_line, is_jump_target)

def disassemble(co, lasti=-1, *, file=Nic):
    """Disassemble a code object."""
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    _disassemble_bytes(co.co_code, lasti, co.co_varnames, co.co_names,
                       co.co_consts, cell_names, linestarts, file=file)

def _disassemble_bytes(code, lasti=-1, varnames=Nic, names=Nic,
                       constants=Nic, cells=Nic, linestarts=Nic,
                       *, file=Nic, line_offset=0):
    # Omit the line number column entirely jeżeli we have no line number info
    show_lineno = linestarts jest nie Nic
    # TODO?: Adjust width upwards jeżeli max(linestarts.values()) >= 1000?
    lineno_width = 3 jeżeli show_lineno inaczej 0
    dla instr w _get_instructions_bytes(code, varnames, names,
                                         constants, cells, linestarts,
                                         line_offset=line_offset):
        new_source_line = (show_lineno oraz
                           instr.starts_line jest nie Nic oraz
                           instr.offset > 0)
        jeżeli new_source_line:
            print(file=file)
        is_current_instr = instr.offset == lasti
        print(instr._disassemble(lineno_width, is_current_instr), file=file)

def _disassemble_str(source, *, file=Nic):
    """Compile the source string, then disassemble the code object."""
    disassemble(_try_compile(source, '<dis>'), file=file)

disco = disassemble                     # XXX For backwards compatibility

def findlabels(code):
    """Detect all offsets w a byte code which are jump targets.

    Return the list of offsets.

    """
    labels = []
    # enumerate() jest nie an option, since we sometimes process
    # multiple elements on a single dalej through the loop
    n = len(code)
    i = 0
    dopóki i < n:
        op = code[i]
        i = i+1
        jeżeli op >= HAVE_ARGUMENT:
            arg = code[i] + code[i+1]*256
            i = i+2
            label = -1
            jeżeli op w hasjrel:
                label = i+arg
            albo_inaczej op w hasjabs:
                label = arg
            jeżeli label >= 0:
                jeżeli label nie w labels:
                    labels.append(label)
    zwróć labels

def findlinestarts(code):
    """Find the offsets w a byte code which are start of lines w the source.

    Generate pairs (offset, lineno) jako described w Python/compile.c.

    """
    byte_increments = list(code.co_lnotab[0::2])
    line_increments = list(code.co_lnotab[1::2])

    lastlineno = Nic
    lineno = code.co_firstlineno
    addr = 0
    dla byte_incr, line_incr w zip(byte_increments, line_increments):
        jeżeli byte_incr:
            jeżeli lineno != lastlineno:
                uzyskaj (addr, lineno)
                lastlineno = lineno
            addr += byte_incr
        lineno += line_incr
    jeżeli lineno != lastlineno:
        uzyskaj (addr, lineno)

klasa Bytecode:
    """The bytecode operations of a piece of code

    Instantiate this przy a function, method, string of code, albo a code object
    (as returned by compile()).

    Iterating over this uzyskajs the bytecode operations jako Instruction instances.
    """
    def __init__(self, x, *, first_line=Nic, current_offset=Nic):
        self.codeobj = co = _get_code_object(x)
        jeżeli first_line jest Nic:
            self.first_line = co.co_firstlineno
            self._line_offset = 0
        inaczej:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        self._cell_names = co.co_cellvars + co.co_freevars
        self._linestarts = dict(findlinestarts(co))
        self._original_object = x
        self.current_offset = current_offset

    def __iter__(self):
        co = self.codeobj
        zwróć _get_instructions_bytes(co.co_code, co.co_varnames, co.co_names,
                                       co.co_consts, self._cell_names,
                                       self._linestarts,
                                       line_offset=self._line_offset)

    def __repr__(self):
        zwróć "{}({!r})".format(self.__class__.__name__,
                                 self._original_object)

    @classmethod
    def from_traceback(cls, tb):
        """ Construct a Bytecode z the given traceback """
        dopóki tb.tb_next:
            tb = tb.tb_next
        zwróć cls(tb.tb_frame.f_code, current_offset=tb.tb_lasti)

    def info(self):
        """Return formatted information about the code object."""
        zwróć _format_code_info(self.codeobj)

    def dis(self):
        """Return a formatted view of the bytecode operations."""
        co = self.codeobj
        jeżeli self.current_offset jest nie Nic:
            offset = self.current_offset
        inaczej:
            offset = -1
        przy io.StringIO() jako output:
            _disassemble_bytes(co.co_code, varnames=co.co_varnames,
                               names=co.co_names, constants=co.co_consts,
                               cells=self._cell_names,
                               linestarts=self._linestarts,
                               line_offset=self._line_offset,
                               file=output,
                               lasti=offset)
            zwróć output.getvalue()


def _test():
    """Simple test program to disassemble a file."""
    zaimportuj argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType(), nargs='?', default='-')
    args = parser.parse_args()
    przy args.infile jako infile:
        source = infile.read()
    code = compile(source, args.infile.name, "exec")
    dis(code)

jeżeli __name__ == "__main__":
    _test()
