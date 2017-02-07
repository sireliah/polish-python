#!/usr/bin/env python3
#
# Argument Clinic
# Copyright 2012-2013 by Larry Hastings.
# Licensed to the PSF under a contributor agreement.
#

zaimportuj abc
zaimportuj ast
zaimportuj atexit
zaimportuj collections
zaimportuj contextlib
zaimportuj copy
zaimportuj cpp
zaimportuj functools
zaimportuj hashlib
zaimportuj inspect
zaimportuj io
zaimportuj itertools
zaimportuj os
zaimportuj pprint
zaimportuj re
zaimportuj shlex
zaimportuj string
zaimportuj sys
zaimportuj tempfile
zaimportuj textwrap
zaimportuj traceback
zaimportuj types
zaimportuj uuid

z types zaimportuj *
NicType = type(Nic)

# TODO:
#
# soon:
#
# * allow mixing any two of {positional-only, positional-or-keyword,
#   keyword-only}
#       * dict constructor uses positional-only oraz keyword-only
#       * max oraz min use positional only przy an optional group
#         oraz keyword-only
#

version = '1'

_empty = inspect._empty
_void = inspect._void

NicType = type(Nic)

klasa Unspecified:
    def __repr__(self):
        zwróć '<Unspecified>'

unspecified = Unspecified()


klasa Null:
    def __repr__(self):
        zwróć '<Null>'

NULL = Null()


klasa Unknown:
    def __repr__(self):
        zwróć '<Unknown>'

unknown = Unknown()

sig_end_marker = '--'


_text_accumulator_nt = collections.namedtuple("_text_accumulator", "text append output")

def _text_accumulator():
    text = []
    def output():
        s = ''.join(text)
        text.clear()
        zwróć s
    zwróć _text_accumulator_nt(text, text.append, output)


text_accumulator_nt = collections.namedtuple("text_accumulator", "text append")

def text_accumulator():
    """
    Creates a simple text accumulator / joiner.

    Returns a pair of callables:
        append, output
    "append" appends a string to the accumulator.
    "output" returns the contents of the accumulator
       joined together (''.join(accumulator)) oraz
       empties the accumulator.
    """
    text, append, output = _text_accumulator()
    zwróć text_accumulator_nt(append, output)


def warn_or_fail(fail=Nieprawda, *args, filename=Nic, line_number=Nic):
    joined = " ".join([str(a) dla a w args])
    add, output = text_accumulator()
    jeżeli fail:
        add("Error")
    inaczej:
        add("Warning")
    jeżeli clinic:
        jeżeli filename jest Nic:
            filename = clinic.filename
        jeżeli getattr(clinic, 'block_parser', Nic) oraz (line_number jest Nic):
            line_number = clinic.block_parser.line_number
    jeżeli filename jest nie Nic:
        add(' w file "' + filename + '"')
    jeżeli line_number jest nie Nic:
        add(" on line " + str(line_number))
    add(':\n')
    add(joined)
    print(output())
    jeżeli fail:
        sys.exit(-1)


def warn(*args, filename=Nic, line_number=Nic):
    zwróć warn_or_fail(Nieprawda, *args, filename=filename, line_number=line_number)

def fail(*args, filename=Nic, line_number=Nic):
    zwróć warn_or_fail(Prawda, *args, filename=filename, line_number=line_number)


def quoted_for_c_string(s):
    dla old, new w (
        ('\\', '\\\\'), # must be first!
        ('"', '\\"'),
        ("'", "\\'"),
        ):
        s = s.replace(old, new)
    zwróć s

def c_repr(s):
    zwróć '"' + s + '"'


is_legal_c_identifier = re.compile('^[A-Za-z_][A-Za-z0-9_]*$').match

def is_legal_py_identifier(s):
    zwróć all(is_legal_c_identifier(field) dla field w s.split('.'))

# identifiers that are okay w Python but aren't a good idea w C.
# so jeżeli they're used Argument Clinic will add "_value" to the end
# of the name w C.
c_keywords = set("""
asm auto przerwij case char const continue default do double
inaczej enum extern float dla goto jeżeli inline int long
register zwróć short signed sizeof static struct switch
typedef typeof union unsigned void volatile while
""".strip().split())

def ensure_legal_c_identifier(s):
    # dla now, just complain jeżeli what we're given isn't legal
    jeżeli nie is_legal_c_identifier(s):
        fail("Illegal C identifier: {}".format(s))
    # but jeżeli we picked a C keyword, pick something inaczej
    jeżeli s w c_keywords:
        zwróć s + "_value"
    zwróć s

def rstrip_lines(s):
    text, add, output = _text_accumulator()
    dla line w s.split('\n'):
        add(line.rstrip())
        add('\n')
    text.pop()
    zwróć output()

def linear_format(s, **kwargs):
    """
    Perform str.format-like substitution, wyjąwszy:
      * The strings substituted must be on lines by
        themselves.  (This line jest the "source line".)
      * If the substitution text jest empty, the source line
        jest removed w the output.
      * If the field jest nie recognized, the original line
        jest dalejed unmodified through to the output.
      * If the substitution text jest nie empty:
          * Each line of the substituted text jest indented
            by the indent of the source line.
          * A newline will be added to the end.
    """

    add, output = text_accumulator()
    dla line w s.split('\n'):
        indent, curly, trailing = line.partition('{')
        jeżeli nie curly:
            add(line)
            add('\n')
            kontynuuj

        name, curl, trailing = trailing.partition('}')
        jeżeli nie curly albo name nie w kwargs:
            add(line)
            add('\n')
            kontynuuj

        jeżeli trailing:
            fail("Text found after {" + name + "} block marker!  It must be on a line by itself.")
        jeżeli indent.strip():
            fail("Non-whitespace characters found before {" + name + "} block marker!  It must be on a line by itself.")

        value = kwargs[name]
        jeżeli nie value:
            kontynuuj

        value = textwrap.indent(rstrip_lines(value), indent)
        add(value)
        add('\n')

    zwróć output()[:-1]

def indent_all_lines(s, prefix):
    """
    Returns 's', przy 'prefix' prepended to all lines.

    If the last line jest empty, prefix jest nie prepended
    to it.  (If s jest blank, returns s unchanged.)

    (textwrap.indent only adds to non-blank lines.)
    """
    split = s.split('\n')
    last = split.pop()
    final = []
    dla line w split:
        final.append(prefix)
        final.append(line)
        final.append('\n')
    jeżeli last:
        final.append(prefix)
        final.append(last)
    zwróć ''.join(final)

def suffix_all_lines(s, suffix):
    """
    Returns 's', przy 'suffix' appended to all lines.

    If the last line jest empty, suffix jest nie appended
    to it.  (If s jest blank, returns s unchanged.)
    """
    split = s.split('\n')
    last = split.pop()
    final = []
    dla line w split:
        final.append(line)
        final.append(suffix)
        final.append('\n')
    jeżeli last:
        final.append(last)
        final.append(suffix)
    zwróć ''.join(final)


def version_splitter(s):
    """Splits a version string into a tuple of integers.

    The following ASCII characters are allowed, oraz employ
    the following conversions:
        a -> -3
        b -> -2
        c -> -1
    (This permits Python-style version strings such jako "1.4b3".)
    """
    version = []
    accumulator = []
    def flush():
        jeżeli nie accumulator:
            podnieś ValueError('Unsupported version string: ' + repr(s))
        version.append(int(''.join(accumulator)))
        accumulator.clear()

    dla c w s:
        jeżeli c.isdigit():
            accumulator.append(c)
        albo_inaczej c == '.':
            flush()
        albo_inaczej c w 'abc':
            flush()
            version.append('abc'.index(c) - 3)
        inaczej:
            podnieś ValueError('Illegal character ' + repr(c) + ' w version string ' + repr(s))
    flush()
    zwróć tuple(version)

def version_comparitor(version1, version2):
    iterator = itertools.zip_longest(version_splitter(version1), version_splitter(version2), fillvalue=0)
    dla i, (a, b) w enumerate(iterator):
        jeżeli a < b:
            zwróć -1
        jeżeli a > b:
            zwróć 1
    zwróć 0


klasa CRenderData:
    def __init__(self):

        # The C statements to declare variables.
        # Should be full lines przy \n eol characters.
        self.declarations = []

        # The C statements required to initialize the variables before the parse call.
        # Should be full lines przy \n eol characters.
        self.initializers = []

        # The C statements needed to dynamically modify the values
        # parsed by the parse call, before calling the impl.
        self.modifications = []

        # The entries dla the "keywords" array dla PyArg_ParseTuple.
        # Should be individual strings representing the names.
        self.keywords = []

        # The "format units" dla PyArg_ParseTuple.
        # Should be individual strings that will get
        self.format_units = []

        # The varargs arguments dla PyArg_ParseTuple.
        self.parse_arguments = []

        # The parameter declarations dla the impl function.
        self.impl_parameters = []

        # The arguments to the impl function at the time it's called.
        self.impl_arguments = []

        # For zwróć converters: the name of the variable that
        # should receive the value returned by the impl.
        self.return_value = "return_value"

        # For zwróć converters: the code to convert the zwróć
        # value z the parse function.  This jest also where
        # you should check the _return_value dla errors, oraz
        # "goto exit" jeżeli there are any.
        self.return_conversion = []

        # The C statements required to clean up after the impl call.
        self.cleanup = []


klasa FormatCounterFormatter(string.Formatter):
    """
    This counts how many instances of each formatter
    "replacement string" appear w the format string.

    e.g. after evaluating "string {a}, {b}, {c}, {a}"
         the counts dict would now look like
         {'a': 2, 'b': 1, 'c': 1}
    """
    def __init__(self):
        self.counts = collections.Counter()

    def get_value(self, key, args, kwargs):
        self.counts[key] += 1
        zwróć ''

klasa Language(metaclass=abc.ABCMeta):

    start_line = ""
    body_prefix = ""
    stop_line = ""
    checksum_line = ""

    def __init__(self, filename):
        dalej

    @abc.abstractmethod
    def render(self, clinic, signatures):
        dalej

    def parse_line(self, line):
        dalej

    def validate(self):
        def assert_only_one(attr, *additional_fields):
            """
            Ensures that the string found at getattr(self, attr)
            contains exactly one formatter replacement string for
            each valid field.  The list of valid fields jest
            ['dsl_name'] extended by additional_fields.

            e.g.
                self.fmt = "{dsl_name} {a} {b}"

                # this dalejes
                self.assert_only_one('fmt', 'a', 'b')

                # this fails, the format string has a {b} w it
                self.assert_only_one('fmt', 'a')

                # this fails, the format string doesn't have a {c} w it
                self.assert_only_one('fmt', 'a', 'b', 'c')

                # this fails, the format string has two {a}s w it,
                # it must contain exactly one
                self.fmt2 = '{dsl_name} {a} {a}'
                self.assert_only_one('fmt2', 'a')

            """
            fields = ['dsl_name']
            fields.extend(additional_fields)
            line = getattr(self, attr)
            fcf = FormatCounterFormatter()
            fcf.format(line)
            def local_fail(should_be_there_but_isnt):
                jeżeli should_be_there_but_isnt:
                    fail("{} {} must contain {{{}}} exactly once!".format(
                        self.__class__.__name__, attr, name))
                inaczej:
                    fail("{} {} must nie contain {{{}}}!".format(
                        self.__class__.__name__, attr, name))

            dla name, count w fcf.counts.items():
                jeżeli name w fields:
                    jeżeli count > 1:
                        local_fail(Prawda)
                inaczej:
                    local_fail(Nieprawda)
            dla name w fields:
                jeżeli fcf.counts.get(name) != 1:
                    local_fail(Prawda)

        assert_only_one('start_line')
        assert_only_one('stop_line')

        field = "arguments" jeżeli "{arguments}" w self.checksum_line inaczej "checksum"
        assert_only_one('checksum_line', field)



klasa PythonLanguage(Language):

    language      = 'Python'
    start_line    = "#/*[{dsl_name} input]"
    body_prefix   = "#"
    stop_line     = "#[{dsl_name} start generated code]*/"
    checksum_line = "#/*[{dsl_name} end generated code: {arguments}]*/"


def permute_left_option_groups(l):
    """
    Given [1, 2, 3], should uzyskaj:
       ()
       (3,)
       (2, 3)
       (1, 2, 3)
    """
    uzyskaj tuple()
    accumulator = []
    dla group w reversed(l):
        accumulator = list(group) + accumulator
        uzyskaj tuple(accumulator)


def permute_right_option_groups(l):
    """
    Given [1, 2, 3], should uzyskaj:
      ()
      (1,)
      (1, 2)
      (1, 2, 3)
    """
    uzyskaj tuple()
    accumulator = []
    dla group w l:
        accumulator.extend(group)
        uzyskaj tuple(accumulator)


def permute_optional_groups(left, required, right):
    """
    Generator function that computes the set of acceptable
    argument lists dla the provided iterables of
    argument groups.  (Actually it generates a tuple of tuples.)

    Algorithm: prefer left options over right options.

    If required jest empty, left must also be empty.
    """
    required = tuple(required)
    result = []

    jeżeli nie required:
        assert nie left

    accumulator = []
    counts = set()
    dla r w permute_right_option_groups(right):
        dla l w permute_left_option_groups(left):
            t = l + required + r
            jeżeli len(t) w counts:
                kontynuuj
            counts.add(len(t))
            accumulator.append(t)

    accumulator.sort(key=len)
    zwróć tuple(accumulator)


def strip_leading_and_trailing_blank_lines(s):
    lines = s.rstrip().split('\n')
    dopóki lines:
        line = lines[0]
        jeżeli line.strip():
            przerwij
        usuń lines[0]
    zwróć '\n'.join(lines)

@functools.lru_cache()
def normalize_snippet(s, *, indent=0):
    """
    Reformats s:
        * removes leading oraz trailing blank lines
        * ensures that it does nie end przy a newline
        * dedents so the first nonwhite character on any line jest at column "indent"
    """
    s = strip_leading_and_trailing_blank_lines(s)
    s = textwrap.dedent(s)
    jeżeli indent:
        s = textwrap.indent(s, ' ' * indent)
    zwróć s


def wrap_declarations(text, length=78):
    """
    A simple-minded text wrapper dla C function declarations.

    It views a declaration line jako looking like this:
        xxxxxxxx(xxxxxxxxx,xxxxxxxxx)
    If called przy length=30, it would wrap that line into
        xxxxxxxx(xxxxxxxxx,
                 xxxxxxxxx)
    (If the declaration has zero albo one parameters, this
    function won't wrap it.)

    If this doesn't work properly, it's probably better to
    start z scratch przy a more sophisticated algorithm,
    rather than try oraz improve/debug this dumb little function.
    """
    lines = []
    dla line w text.split('\n'):
        prefix, _, after_l_paren = line.partition('(')
        jeżeli nie after_l_paren:
            lines.append(line)
            kontynuuj
        parameters, _, after_r_paren = after_l_paren.partition(')')
        jeżeli nie _:
            lines.append(line)
            kontynuuj
        jeżeli ',' nie w parameters:
            lines.append(line)
            kontynuuj
        parameters = [x.strip() + ", " dla x w parameters.split(',')]
        prefix += "("
        jeżeli len(prefix) < length:
            spaces = " " * len(prefix)
        inaczej:
            spaces = " " * 4

        dopóki parameters:
            line = prefix
            first = Prawda
            dopóki parameters:
                jeżeli (nie first oraz
                    (len(line) + len(parameters[0]) > length)):
                    przerwij
                line += parameters.pop(0)
                first = Nieprawda
            jeżeli nie parameters:
                line = line.rstrip(", ") + ")" + after_r_paren
            lines.append(line.rstrip())
            prefix = spaces
    zwróć "\n".join(lines)


klasa CLanguage(Language):

    body_prefix   = "#"
    language      = 'C'
    start_line    = "/*[{dsl_name} input]"
    body_prefix   = ""
    stop_line     = "[{dsl_name} start generated code]*/"
    checksum_line = "/*[{dsl_name} end generated code: {arguments}]*/"

    def __init__(self, filename):
        super().__init__(filename)
        self.cpp = cpp.Monitor(filename)
        self.cpp.fail = fail

    def parse_line(self, line):
        self.cpp.writeline(line)

    def render(self, clinic, signatures):
        function = Nic
        dla o w signatures:
            jeżeli isinstance(o, Function):
                jeżeli function:
                    fail("You may specify at most one function per block.\nFound a block containing at least two:\n\t" + repr(function) + " oraz " + repr(o))
                function = o
        zwróć self.render_function(clinic, function)

    def docstring_for_c_string(self, f):
        text, add, output = _text_accumulator()
        # turn docstring into a properly quoted C string
        dla line w f.docstring.split('\n'):
            add('"')
            add(quoted_for_c_string(line))
            add('\\n"\n')

        jeżeli text[-2] == sig_end_marker:
            # If we only have a signature, add the blank line that the
            # __text_signature__ getter expects to be there.
            add('"\\n"')
        inaczej:
            text.pop()
            add('"')
        zwróć ''.join(text)

    def output_templates(self, f):
        parameters = list(f.parameters.values())
        assert parameters
        assert isinstance(parameters[0].converter, self_converter)
        usuń parameters[0]
        converters = [p.converter dla p w parameters]

        has_option_groups = parameters oraz (parameters[0].group albo parameters[-1].group)
        default_return_converter = (nie f.return_converter albo
            f.return_converter.type == 'PyObject *')

        positional = parameters oraz (parameters[-1].kind == inspect.Parameter.POSITIONAL_ONLY)
        all_boring_objects = Nieprawda # yes, this will be false jeżeli there are 0 parameters, it's fine
        first_optional = len(parameters)
        dla i, p w enumerate(parameters):
            c = p.converter
            jeżeli type(c) != object_converter:
                przerwij
            jeżeli c.format_unit != 'O':
                przerwij
            jeżeli p.default jest nie unspecified:
                first_optional = min(first_optional, i)
        inaczej:
            all_boring_objects = Prawda

        new_or_init = f.kind w (METHOD_NEW, METHOD_INIT)

        meth_o = (len(parameters) == 1 oraz
              parameters[0].kind == inspect.Parameter.POSITIONAL_ONLY oraz
              nie converters[0].is_optional() oraz
              nie new_or_init)

        # we have to set these things before we're done:
        #
        # docstring_prototype
        # docstring_definition
        # impl_prototype
        # methoddef_define
        # parser_prototype
        # parser_definition
        # impl_definition
        # cpp_if
        # cpp_endif
        # methoddef_ifndef

        return_value_declaration = "PyObject *return_value = NULL;"

        methoddef_define = normalize_snippet("""
            #define {methoddef_name}    \\
                {{"{name}", (PyCFunction){c_basename}, {methoddef_flags}, {c_basename}__doc__}},
            """)
        jeżeli new_or_init oraz nie f.docstring:
            docstring_prototype = docstring_definition = ''
        inaczej:
            docstring_prototype = normalize_snippet("""
                PyDoc_VAR({c_basename}__doc__);
                """)
            docstring_definition = normalize_snippet("""
                PyDoc_STRVAR({c_basename}__doc__,
                {docstring});
                """)
        impl_definition = normalize_snippet("""
            static {impl_return_type}
            {c_basename}_impl({impl_parameters})
            """)
        impl_prototype = parser_prototype = parser_definition = Nic

        parser_prototype_keyword = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *args, PyObject *kwargs)
            """)

        parser_prototype_varargs = normalize_snippet("""
            static PyObject *
            {c_basename}({self_type}{self_name}, PyObject *args)
            """)

        # parser_body_fields remembers the fields dalejed w to the
        # previous call to parser_body. this jest used dla an awful hack.
        parser_body_fields = ()
        def parser_body(prototype, *fields):
            nonlocal parser_body_fields
            add, output = text_accumulator()
            add(prototype)
            parser_body_fields = fields

            fields = list(fields)
            fields.insert(0, normalize_snippet("""
                {{
                    {return_value_declaration}
                    {declarations}
                    {initializers}
                """) + "\n")
            # just imagine--your code jest here w the middle
            fields.append(normalize_snippet("""
                    {modifications}
                    {return_value} = {c_basename}_impl({impl_arguments});
                    {return_conversion}

                {exit_label}
                    {cleanup}
                    zwróć return_value;
                }}
                """))
            dla field w fields:
                add('\n')
                add(field)
            zwróć output()

        def insert_keywords(s):
            zwróć linear_format(s, declarations="static char *_keywords[] = {{{keywords}, NULL}};\n{declarations}")

        jeżeli nie parameters:
            # no parameters, METH_NOARGS

            flags = "METH_NOARGS"

            parser_prototype = normalize_snippet("""
                static PyObject *
                {c_basename}({self_type}{self_name}, PyObject *Py_UNUSED(ignored))
                """)
            parser_definition = parser_prototype

            jeżeli default_return_converter:
                parser_definition = parser_prototype + '\n' + normalize_snippet("""
                    {{
                        zwróć {c_basename}_impl({impl_arguments});
                    }}
                    """)
            inaczej:
                parser_definition = parser_body(parser_prototype)

        albo_inaczej meth_o:
            flags = "METH_O"

            jeżeli (isinstance(converters[0], object_converter) oraz
                converters[0].format_unit == 'O'):
                meth_o_prototype = normalize_snippet("""
                    static PyObject *
                    {c_basename}({impl_parameters})
                    """)

                jeżeli default_return_converter:
                    # maps perfectly to METH_O, doesn't need a zwróć converter.
                    # so we skip making a parse function
                    # oraz call directly into the impl function.
                    impl_prototype = parser_prototype = parser_definition = ''
                    impl_definition = meth_o_prototype
                inaczej:
                    # SLIGHT HACK
                    # use impl_parameters dla the parser here!
                    parser_prototype = meth_o_prototype
                    parser_definition = parser_body(parser_prototype)

            inaczej:
                argname = 'arg'
                jeżeli parameters[0].name == argname:
                    argname += '_'
                parser_prototype = normalize_snippet("""
                    static PyObject *
                    {c_basename}({self_type}{self_name}, PyObject *%s)
                    """ % argname)

                parser_definition = parser_body(parser_prototype, normalize_snippet("""
                    jeżeli (!PyArg_Parse(%s, "{format_units}:{name}", {parse_arguments}))
                        goto exit;
                    """ % argname, indent=4))

        albo_inaczej has_option_groups:
            # positional parameters przy option groups
            # (we have to generate lots of PyArg_ParseTuple calls
            #  w a big switch statement)

            flags = "METH_VARARGS"
            parser_prototype = parser_prototype_varargs

            parser_definition = parser_body(parser_prototype, '    {option_group_parsing}')

        albo_inaczej positional oraz all_boring_objects:
            # positional-only, but no option groups,
            # oraz nothing but normal objects:
            # PyArg_UnpackTuple!

            flags = "METH_VARARGS"
            parser_prototype = parser_prototype_varargs

            parser_definition = parser_body(parser_prototype, normalize_snippet("""
                jeżeli (!PyArg_UnpackTuple(args, "{name}",
                    {unpack_min}, {unpack_max},
                    {parse_arguments}))
                    goto exit;
                """, indent=4))

        albo_inaczej positional:
            # positional-only, but no option groups
            # we only need one call to PyArg_ParseTuple

            flags = "METH_VARARGS"
            parser_prototype = parser_prototype_varargs

            parser_definition = parser_body(parser_prototype, normalize_snippet("""
                jeżeli (!PyArg_ParseTuple(args, "{format_units}:{name}",
                    {parse_arguments}))
                    goto exit;
                """, indent=4))

        inaczej:
            # positional-or-keyword arguments
            flags = "METH_VARARGS|METH_KEYWORDS"

            parser_prototype = parser_prototype_keyword

            body = normalize_snippet("""
                jeżeli (!PyArg_ParseTupleAndKeywords(args, kwargs, "{format_units}:{name}", _keywords,
                    {parse_arguments}))
                    goto exit;
            """, indent=4)
            parser_definition = parser_body(parser_prototype, normalize_snippet("""
                jeżeli (!PyArg_ParseTupleAndKeywords(args, kwargs, "{format_units}:{name}", _keywords,
                    {parse_arguments}))
                    goto exit;
                """, indent=4))
            parser_definition = insert_keywords(parser_definition)


        jeżeli new_or_init:
            methoddef_define = ''

            jeżeli f.kind == METHOD_NEW:
                parser_prototype = parser_prototype_keyword
            inaczej:
                return_value_declaration = "int return_value = -1;"
                parser_prototype = normalize_snippet("""
                    static int
                    {c_basename}({self_type}{self_name}, PyObject *args, PyObject *kwargs)
                    """)

            fields = list(parser_body_fields)
            parses_positional = 'METH_NOARGS' nie w flags
            parses_keywords = 'METH_KEYWORDS' w flags
            jeżeli parses_keywords:
                assert parses_positional

            jeżeli nie parses_keywords:
                fields.insert(0, normalize_snippet("""
                    jeżeli ({self_type_check}!_PyArg_NoKeywords("{name}", kwargs))
                        goto exit;
                    """, indent=4))
                jeżeli nie parses_positional:
                    fields.insert(0, normalize_snippet("""
                        jeżeli ({self_type_check}!_PyArg_NoPositional("{name}", args))
                            goto exit;
                        """, indent=4))

            parser_definition = parser_body(parser_prototype, *fields)
            jeżeli parses_keywords:
                parser_definition = insert_keywords(parser_definition)


        jeżeli f.methoddef_flags:
            flags += '|' + f.methoddef_flags

        methoddef_define = methoddef_define.replace('{methoddef_flags}', flags)

        methoddef_ifndef = ''
        conditional = self.cpp.condition()
        jeżeli nie conditional:
            cpp_jeżeli = cpp_endjeżeli = ''
        inaczej:
            cpp_jeżeli = "#jeżeli " + conditional
            cpp_endjeżeli = "#endjeżeli /* " + conditional + " */"

            jeżeli methoddef_define oraz f.name nie w clinic.ifndef_symbols:
                clinic.ifndef_symbols.add(f.name)
                methoddef_ifndef = normalize_snippet("""
                    #ifndef {methoddef_name}
                        #define {methoddef_name}
                    #endjeżeli /* !defined({methoddef_name}) */
                    """)


        # add ';' to the end of parser_prototype oraz impl_prototype
        # (they mustn't be Nic, but they could be an empty string.)
        assert parser_prototype jest nie Nic
        jeżeli parser_prototype:
            assert nie parser_prototype.endswith(';')
            parser_prototype += ';'

        jeżeli impl_prototype jest Nic:
            impl_prototype = impl_definition
        jeżeli impl_prototype:
            impl_prototype += ";"

        parser_definition = parser_definition.replace("{return_value_declaration}", return_value_declaration)

        d = {
            "docstring_prototype" : docstring_prototype,
            "docstring_definition" : docstring_definition,
            "impl_prototype" : impl_prototype,
            "methoddef_define" : methoddef_define,
            "parser_prototype" : parser_prototype,
            "parser_definition" : parser_definition,
            "impl_definition" : impl_definition,
            "cpp_if" : cpp_if,
            "cpp_endif" : cpp_endif,
            "methoddef_ifndef" : methoddef_ifndef,
        }

        # make sure we didn't forget to assign something,
        # oraz wrap each non-empty value w \n's
        d2 = {}
        dla name, value w d.items():
            assert value jest nie Nic, "got a Nic value dla template " + repr(name)
            jeżeli value:
                value = '\n' + value + '\n'
            d2[name] = value
        zwróć d2

    @staticmethod
    def group_to_variable_name(group):
        adjective = "left_" jeżeli group < 0 inaczej "right_"
        zwróć "group_" + adjective + str(abs(group))

    def render_option_group_parsing(self, f, template_dict):
        # positional only, grouped, optional arguments!
        # can be optional on the left albo right.
        # here's an example:
        #
        # [ [ [ A1 A2 ] B1 B2 B3 ] C1 C2 ] D1 D2 D3 [ E1 E2 E3 [ F1 F2 F3 ] ]
        #
        # Here group D are required, oraz all other groups are optional.
        # (Group D's "group" jest actually Nic.)
        # We can figure out which sets of arguments we have based on
        # how many arguments are w the tuple.
        #
        # Note that you need to count up on both sides.  For example,
        # you could have groups C+D, albo C+D+E, albo C+D+E+F.
        #
        # What jeżeli the number of arguments leads us to an ambiguous result?
        # Clinic prefers groups on the left.  So w the above example,
        # five arguments would map to B+C, nie C+D.

        add, output = text_accumulator()
        parameters = list(f.parameters.values())
        jeżeli isinstance(parameters[0].converter, self_converter):
            usuń parameters[0]

        groups = []
        group = Nic
        left = []
        right = []
        required = []
        last = unspecified

        dla p w parameters:
            group_id = p.group
            jeżeli group_id != last:
                last = group_id
                group = []
                jeżeli group_id < 0:
                    left.append(group)
                albo_inaczej group_id == 0:
                    group = required
                inaczej:
                    right.append(group)
            group.append(p)

        count_min = sys.maxsize
        count_max = -1

        add("switch (PyTuple_GET_SIZE(args)) {{\n")
        dla subset w permute_optional_groups(left, required, right):
            count = len(subset)
            count_min = min(count_min, count)
            count_max = max(count_max, count)

            jeżeli count == 0:
                add("""    case 0:
        przerwij;
""")
                kontynuuj

            group_ids = {p.group dla p w subset}  # eliminate duplicates
            d = {}
            d['count'] = count
            d['name'] = f.name
            d['groups'] = sorted(group_ids)
            d['format_units'] = "".join(p.converter.format_unit dla p w subset)

            parse_arguments = []
            dla p w subset:
                p.converter.parse_argument(parse_arguments)
            d['parse_arguments'] = ", ".join(parse_arguments)

            group_ids.discard(0)
            lines = [self.group_to_variable_name(g) + " = 1;" dla g w group_ids]
            lines = "\n".join(lines)

            s = """
    case {count}:
        jeżeli (!PyArg_ParseTuple(args, "{format_units}:{name}", {parse_arguments}))
            goto exit;
        {group_booleans}
        przerwij;
"""[1:]
            s = linear_format(s, group_booleans=lines)
            s = s.format_map(d)
            add(s)

        add("    default:\n")
        s = '        PyErr_SetString(PyExc_TypeError, "{} requires {} to {} arguments");\n'
        add(s.format(f.full_name, count_min, count_max))
        add('        goto exit;\n')
        add("}}")
        template_dict['option_group_parsing'] = output()

    def render_function(self, clinic, f):
        jeżeli nie f:
            zwróć ""

        add, output = text_accumulator()
        data = CRenderData()

        assert f.parameters, "We should always have a 'self' at this point!"
        parameters = f.render_parameters
        converters = [p.converter dla p w parameters]

        templates = self.output_templates(f)

        f_self = parameters[0]
        selfless = parameters[1:]
        assert isinstance(f_self.converter, self_converter), "No self parameter w " + repr(f.full_name) + "!"

        last_group = 0
        first_optional = len(selfless)
        positional = selfless oraz selfless[-1].kind == inspect.Parameter.POSITIONAL_ONLY
        new_or_init = f.kind w (METHOD_NEW, METHOD_INIT)
        default_return_converter = (nie f.return_converter albo
            f.return_converter.type == 'PyObject *')
        has_option_groups = Nieprawda

        # offset i by -1 because first_optional needs to ignore self
        dla i, p w enumerate(parameters, -1):
            c = p.converter

            jeżeli (i != -1) oraz (p.default jest nie unspecified):
                first_optional = min(first_optional, i)

            # insert group variable
            group = p.group
            jeżeli last_group != group:
                last_group = group
                jeżeli group:
                    group_name = self.group_to_variable_name(group)
                    data.impl_arguments.append(group_name)
                    data.declarations.append("int " + group_name + " = 0;")
                    data.impl_parameters.append("int " + group_name)
                    has_option_groups = Prawda

            c.render(p, data)

        jeżeli has_option_groups oraz (nie positional):
            fail("You cannot use optional groups ('[' oraz ']')\nunless all parameters are positional-only ('/').")

        # HACK
        # when we're METH_O, but have a custom zwróć converter,
        # we use "impl_parameters" dla the parsing function
        # because that works better.  but that means we must
        # suppress actually declaring the impl's parameters
        # jako variables w the parsing function.  but since it's
        # METH_O, we have exactly one anyway, so we know exactly
        # where it is.
        jeżeli ("METH_O" w templates['methoddef_define'] oraz
            '{impl_parameters}' w templates['parser_prototype']):
            data.declarations.pop(0)

        template_dict = {}

        full_name = f.full_name
        template_dict['full_name'] = full_name

        jeżeli new_or_init:
            name = f.cls.name
        inaczej:
            name = f.name

        template_dict['name'] = name

        jeżeli f.c_basename:
            c_basename = f.c_basename
        inaczej:
            fields = full_name.split(".")
            jeżeli fields[-1] == '__new__':
                fields.pop()
            c_basename = "_".join(fields)

        template_dict['c_basename'] = c_basename

        methoddef_name = "{}_METHODDEF".format(c_basename.upper())
        template_dict['methoddef_name'] = methoddef_name

        template_dict['docstring'] = self.docstring_for_c_string(f)

        template_dict['self_name'] = template_dict['self_type'] = template_dict['self_type_check'] = ''
        f_self.converter.set_template_dict(template_dict)

        f.return_converter.render(f, data)
        template_dict['impl_return_type'] = f.return_converter.type

        template_dict['declarations'] = "\n".join(data.declarations)
        template_dict['initializers'] = "\n\n".join(data.initializers)
        template_dict['modifications'] = '\n\n'.join(data.modifications)
        template_dict['keywords'] = '"' + '", "'.join(data.keywords) + '"'
        template_dict['format_units'] = ''.join(data.format_units)
        template_dict['parse_arguments'] = ', '.join(data.parse_arguments)
        template_dict['impl_parameters'] = ", ".join(data.impl_parameters)
        template_dict['impl_arguments'] = ", ".join(data.impl_arguments)
        template_dict['return_conversion'] = "".join(data.return_conversion).rstrip()
        template_dict['cleanup'] = "".join(data.cleanup)
        template_dict['return_value'] = data.return_value

        # used by unpack tuple code generator
        ignore_self = -1 jeżeli isinstance(converters[0], self_converter) inaczej 0
        unpack_min = first_optional
        unpack_max = len(selfless)
        template_dict['unpack_min'] = str(unpack_min)
        template_dict['unpack_max'] = str(unpack_max)

        jeżeli has_option_groups:
            self.render_option_group_parsing(f, template_dict)

        # buffers, nie destination
        dla name, destination w clinic.destination_buffers.items():
            template = templates[name]
            jeżeli has_option_groups:
                template = linear_format(template,
                        option_group_parsing=template_dict['option_group_parsing'])
            template = linear_format(template,
                declarations=template_dict['declarations'],
                return_conversion=template_dict['return_conversion'],
                initializers=template_dict['initializers'],
                modifications=template_dict['modifications'],
                cleanup=template_dict['cleanup'],
                )

            # Only generate the "exit:" label
            # jeżeli we have any gotos
            need_exit_label = "goto exit;" w template
            template = linear_format(template,
                exit_label="exit:" jeżeli need_exit_label inaczej ''
                )

            s = template.format_map(template_dict)

            # mild hack:
            # reflow long impl declarations
            jeżeli name w {"impl_prototype", "impl_definition"}:
                s = wrap_declarations(s)

            jeżeli clinic.line_prefix:
                s = indent_all_lines(s, clinic.line_prefix)
            jeżeli clinic.line_suffix:
                s = suffix_all_lines(s, clinic.line_suffix)

            destination.append(s)

        zwróć clinic.get_destination('block').dump()




@contextlib.contextmanager
def OverrideStdioWith(stdout):
    saved_stdout = sys.stdout
    sys.stdout = stdout
    spróbuj:
        uzyskaj
    w_końcu:
        assert sys.stdout jest stdout
        sys.stdout = saved_stdout


def create_regex(before, after, word=Prawda, whole_line=Prawda):
    """Create an re object dla matching marker lines."""
    group_re = "\w+" jeżeli word inaczej ".+"
    pattern = r'{}({}){}'
    jeżeli whole_line:
        pattern = '^' + pattern + '$'
    pattern = pattern.format(re.escape(before), group_re, re.escape(after))
    zwróć re.compile(pattern)


klasa Block:
    r"""
    Represents a single block of text embedded w
    another file.  If dsl_name jest Nic, the block represents
    verbatim text, raw original text z the file, w
    which case "input" will be the only non-false member.
    If dsl_name jest nie Nic, the block represents a Clinic
    block.

    input jest always str, przy embedded \n characters.
    input represents the original text z the file;
    jeżeli it's a Clinic block, it jest the original text with
    the body_prefix oraz redundant leading whitespace removed.

    dsl_name jest either str albo Nic.  If str, it's the text
    found on the start line of the block between the square
    brackets.

    signatures jest either list albo Nic.  If it's a list,
    it may only contain clinic.Module, clinic.Class, oraz
    clinic.Function objects.  At the moment it should
    contain at most one of each.

    output jest either str albo Nic.  If str, it's the output
    z this block, przy embedded '\n' characters.

    indent jest either str albo Nic.  It's the leading whitespace
    that was found on every line of input.  (If body_prefix jest
    nie empty, this jest the indent *after* removing the
    body_prefix.)

    preindent jest either str albo Nic.  It's the whitespace that
    was found w front of every line of input *before* the
    "body_prefix" (see the Language object).  If body_prefix
    jest empty, preindent must always be empty too.

    To illustrate indent oraz preindent: Assume that '_'
    represents whitespace.  If the block processed was w a
    Python file, oraz looked like this:
      ____#/*[python]
      ____#__dla a w range(20):
      ____#____print(a)
      ____#[python]*/
    "preindent" would be "____" oraz "indent" would be "__".

    """
    def __init__(self, input, dsl_name=Nic, signatures=Nic, output=Nic, indent='', preindent=''):
        assert isinstance(input, str)
        self.input = input
        self.dsl_name = dsl_name
        self.signatures = signatures albo []
        self.output = output
        self.indent = indent
        self.preindent = preindent

    def __repr__(self):
        dsl_name = self.dsl_name albo "text"
        def summarize(s):
            s = repr(s)
            jeżeli len(s) > 30:
                zwróć s[:26] + "..." + s[0]
            zwróć s
        zwróć "".join((
            "<Block ", dsl_name, " input=", summarize(self.input), " output=", summarize(self.output), ">"))


klasa BlockParser:
    """
    Block-oriented parser dla Argument Clinic.
    Iterator, uzyskajs Block objects.
    """

    def __init__(self, input, language, *, verify=Prawda):
        """
        "input" should be a str object
        przy embedded \n characters.

        "language" should be a Language object.
        """
        language.validate()

        self.input = collections.deque(reversed(input.splitlines(keepends=Prawda)))
        self.block_start_line_number = self.line_number = 0

        self.language = language
        before, _, after = language.start_line.partition('{dsl_name}')
        assert _ == '{dsl_name}'
        self.find_start_re = create_regex(before, after, whole_line=Nieprawda)
        self.start_re = create_regex(before, after)
        self.verify = verify
        self.last_checksum_re = Nic
        self.last_dsl_name = Nic
        self.dsl_name = Nic
        self.first_block = Prawda

    def __iter__(self):
        zwróć self

    def __next__(self):
        dopóki Prawda:
            jeżeli nie self.input:
                podnieś StopIteration

            jeżeli self.dsl_name:
                return_value = self.parse_clinic_block(self.dsl_name)
                self.dsl_name = Nic
                self.first_block = Nieprawda
                zwróć return_value
            block = self.parse_verbatim_block()
            jeżeli self.first_block oraz nie block.input:
                kontynuuj
            self.first_block = Nieprawda
            zwróć block


    def is_start_line(self, line):
        match = self.start_re.match(line.lstrip())
        zwróć match.group(1) jeżeli match inaczej Nic

    def _line(self, lookahead=Nieprawda):
        self.line_number += 1
        line = self.input.pop()
        jeżeli nie lookahead:
            self.language.parse_line(line)
        zwróć line

    def parse_verbatim_block(self):
        add, output = text_accumulator()
        self.block_start_line_number = self.line_number

        dopóki self.input:
            line = self._line()
            dsl_name = self.is_start_line(line)
            jeżeli dsl_name:
                self.dsl_name = dsl_name
                przerwij
            add(line)

        zwróć Block(output())

    def parse_clinic_block(self, dsl_name):
        input_add, input_output = text_accumulator()
        self.block_start_line_number = self.line_number + 1
        stop_line = self.language.stop_line.format(dsl_name=dsl_name)
        body_prefix = self.language.body_prefix.format(dsl_name=dsl_name)

        def is_stop_line(line):
            # make sure to recognize stop line even jeżeli it
            # doesn't end przy EOL (it could be the very end of the file)
            jeżeli nie line.startswith(stop_line):
                zwróć Nieprawda
            remainder = line[len(stop_line):]
            zwróć (nie remainder) albo remainder.isspace()

        # consume body of program
        dopóki self.input:
            line = self._line()
            jeżeli is_stop_line(line) albo self.is_start_line(line):
                przerwij
            jeżeli body_prefix:
                line = line.lstrip()
                assert line.startswith(body_prefix)
                line = line[len(body_prefix):]
            input_add(line)

        # consume output oraz checksum line, jeżeli present.
        jeżeli self.last_dsl_name == dsl_name:
            checksum_re = self.last_checksum_re
        inaczej:
            before, _, after = self.language.checksum_line.format(dsl_name=dsl_name, arguments='{arguments}').partition('{arguments}')
            assert _ == '{arguments}'
            checksum_re = create_regex(before, after, word=Nieprawda)
            self.last_dsl_name = dsl_name
            self.last_checksum_re = checksum_re

        # scan forward dla checksum line
        output_add, output_output = text_accumulator()
        arguments = Nic
        dopóki self.input:
            line = self._line(lookahead=Prawda)
            match = checksum_re.match(line.lstrip())
            arguments = match.group(1) jeżeli match inaczej Nic
            jeżeli arguments:
                przerwij
            output_add(line)
            jeżeli self.is_start_line(line):
                przerwij

        output = output_output()
        jeżeli arguments:
            d = {}
            dla field w shlex.split(arguments):
                name, equals, value = field.partition('=')
                jeżeli nie equals:
                    fail("Mangled Argument Clinic marker line: {!r}".format(line))
                d[name.strip()] = value.strip()

            jeżeli self.verify:
                jeżeli 'input' w d:
                    checksum = d['output']
                    input_checksum = d['input']
                inaczej:
                    checksum = d['checksum']
                    input_checksum = Nic

                computed = compute_checksum(output, len(checksum))
                jeżeli checksum != computed:
                    fail("Checksum mismatch!\nExpected: {}\nComputed: {}\n"
                         "Suggested fix: remove all generated code including "
                         "the end marker,\n"
                         "or use the '-f' option."
                        .format(checksum, computed))
        inaczej:
            # put back output
            output_lines = output.splitlines(keepends=Prawda)
            self.line_number -= len(output_lines)
            self.input.extend(reversed(output_lines))
            output = Nic

        zwróć Block(input_output(), dsl_name, output=output)


klasa BlockPrinter:

    def __init__(self, language, f=Nic):
        self.language = language
        self.f = f albo io.StringIO()

    def print_block(self, block):
        input = block.input
        output = block.output
        dsl_name = block.dsl_name
        write = self.f.write

        assert nie ((dsl_name == Nic) ^ (output == Nic)), "you must specify dsl_name oraz output together, dsl_name " + repr(dsl_name)

        jeżeli nie dsl_name:
            write(input)
            zwróć

        write(self.language.start_line.format(dsl_name=dsl_name))
        write("\n")

        body_prefix = self.language.body_prefix.format(dsl_name=dsl_name)
        jeżeli nie body_prefix:
            write(input)
        inaczej:
            dla line w input.split('\n'):
                write(body_prefix)
                write(line)
                write("\n")

        write(self.language.stop_line.format(dsl_name=dsl_name))
        write("\n")

        input = ''.join(block.input)
        output = ''.join(block.output)
        jeżeli output:
            jeżeli nie output.endswith('\n'):
                output += '\n'
            write(output)

        arguments="output={} input={}".format(compute_checksum(output, 16), compute_checksum(input, 16))
        write(self.language.checksum_line.format(dsl_name=dsl_name, arguments=arguments))
        write("\n")

    def write(self, text):
        self.f.write(text)


klasa BufferSeries:
    """
    Behaves like a "defaultlist".
    When you ask dla an index that doesn't exist yet,
    the object grows the list until that item exists.
    So o[n] will always work.

    Supports negative indices dla actual items.
    e.g. o[-1] jest an element immediately preceding o[0].
    """

    def __init__(self):
        self._start = 0
        self._array = []
        self._constructor = _text_accumulator

    def __getitem__(self, i):
        i -= self._start
        jeżeli i < 0:
            self._start += i
            prefix = [self._constructor() dla x w range(-i)]
            self._array = prefix + self._array
            i = 0
        dopóki i >= len(self._array):
            self._array.append(self._constructor())
        zwróć self._array[i]

    def clear(self):
        dla ta w self._array:
            ta._text.clear()

    def dump(self):
        texts = [ta.output() dla ta w self._array]
        zwróć "".join(texts)


klasa Destination:
    def __init__(self, name, type, clinic, *args):
        self.name = name
        self.type = type
        self.clinic = clinic
        valid_types = ('buffer', 'file', 'suppress')
        jeżeli type nie w valid_types:
            fail("Invalid destination type " + repr(type) + " dla " + name + " , must be " + ', '.join(valid_types))
        extra_arguments = 1 jeżeli type == "file" inaczej 0
        jeżeli len(args) < extra_arguments:
            fail("Not enough arguments dla destination " + name + " new " + type)
        jeżeli len(args) > extra_arguments:
            fail("Too many arguments dla destination " + name + " new " + type)
        jeżeli type =='file':
            d = {}
            filename = clinic.filename
            d['path'] = filename
            dirname, basename = os.path.split(filename)
            jeżeli nie dirname:
                dirname = '.'
            d['dirname'] = dirname
            d['basename'] = basename
            d['basename_root'], d['basename_extension'] = os.path.splitext(filename)
            self.filename = args[0].format_map(d)

        self.buffers = BufferSeries()

    def __repr__(self):
        jeżeli self.type == 'file':
            file_repr = " " + repr(self.filename)
        inaczej:
            file_repr = ''
        zwróć "".join(("<Destination ", self.name, " ", self.type, file_repr, ">"))

    def clear(self):
        jeżeli self.type != 'buffer':
            fail("Can't clear destination" + self.name + " , it's nie of type buffer")
        self.buffers.clear()

    def dump(self):
        zwróć self.buffers.dump()


# maps strings to Language objects.
# "languages" maps the name of the language ("C", "Python").
# "extensions" maps the file extension ("c", "py").
languages = { 'C': CLanguage, 'Python': PythonLanguage }
extensions = { name: CLanguage dla name w "c cc cpp cxx h hh hpp hxx".split() }
extensions['py'] = PythonLanguage


# maps strings to callables.
# these callables must be of the form:
#   def foo(name, default, *, ...)
# The callable may have any number of keyword-only parameters.
# The callable must zwróć a CConverter object.
# The callable should nie call builtins.print.
converters = {}

# maps strings to callables.
# these callables follow the same rules jako those dla "converters" above.
# note however that they will never be called przy keyword-only parameters.
legacy_converters = {}


# maps strings to callables.
# these callables must be of the form:
#   def foo(*, ...)
# The callable may have any number of keyword-only parameters.
# The callable must zwróć a CConverter object.
# The callable should nie call builtins.print.
return_converters = {}

clinic = Nic
klasa Clinic:

    presets_text = """
preset block
everything block
methoddef_ifndef buffer 1
docstring_prototype suppress
parser_prototype suppress
cpp_jeżeli suppress
cpp_endjeżeli suppress

preset original
everything block
methoddef_ifndef buffer 1
docstring_prototype suppress
parser_prototype suppress
cpp_jeżeli suppress
cpp_endjeżeli suppress

preset file
everything file
methoddef_ifndef file 1
docstring_prototype suppress
parser_prototype suppress
impl_definition block

preset buffer
everything buffer
methoddef_ifndef buffer 1
impl_definition block
docstring_prototype suppress
impl_prototype suppress
parser_prototype suppress

preset partial-buffer
everything buffer
methoddef_ifndef buffer 1
docstring_prototype block
impl_prototype suppress
methoddef_define block
parser_prototype block
impl_definition block

"""

    def __init__(self, language, printer=Nic, *, force=Nieprawda, verify=Prawda, filename=Nic):
        # maps strings to Parser objects.
        # (instantiated z the "parsers" global.)
        self.parsers = {}
        self.language = language
        jeżeli printer:
            fail("Custom printers are broken right now")
        self.printer = printer albo BlockPrinter(language)
        self.verify = verify
        self.force = force
        self.filename = filename
        self.modules = collections.OrderedDict()
        self.classes = collections.OrderedDict()
        self.functions = []

        self.line_prefix = self.line_suffix = ''

        self.destinations = {}
        self.add_destination("block", "buffer")
        self.add_destination("suppress", "suppress")
        self.add_destination("buffer", "buffer")
        jeżeli filename:
            self.add_destination("file", "file", "{dirname}/clinic/{basename}.h")

        d = self.get_destination_buffer
        self.destination_buffers = collections.OrderedDict((
            ('cpp_if', d('file')),
            ('docstring_prototype', d('suppress')),
            ('docstring_definition', d('file')),
            ('methoddef_define', d('file')),
            ('impl_prototype', d('file')),
            ('parser_prototype', d('suppress')),
            ('parser_definition', d('file')),
            ('cpp_endif', d('file')),
            ('methoddef_ifndef', d('file', 1)),
            ('impl_definition', d('block')),
        ))

        self.destination_buffers_stack = []
        self.ifndef_symbols = set()

        self.presets = {}
        preset = Nic
        dla line w self.presets_text.strip().split('\n'):
            line = line.strip()
            jeżeli nie line:
                kontynuuj
            name, value, *options = line.split()
            jeżeli name == 'preset':
                self.presets[value] = preset = collections.OrderedDict()
                kontynuuj

            jeżeli len(options):
                index = int(options[0])
            inaczej:
                index = 0
            buffer = self.get_destination_buffer(value, index)

            jeżeli name == 'everything':
                dla name w self.destination_buffers:
                    preset[name] = buffer
                kontynuuj

            assert name w self.destination_buffers
            preset[name] = buffer

        global clinic
        clinic = self

    def add_destination(self, name, type, *args):
        jeżeli name w self.destinations:
            fail("Destination already exists: " + repr(name))
        self.destinations[name] = Destination(name, type, self, *args)

    def get_destination(self, name):
        d = self.destinations.get(name)
        jeżeli nie d:
            fail("Destination does nie exist: " + repr(name))
        zwróć d

    def get_destination_buffer(self, name, item=0):
        d = self.get_destination(name)
        zwróć d.buffers[item]

    def parse(self, input):
        printer = self.printer
        self.block_parser = BlockParser(input, self.language, verify=self.verify)
        dla block w self.block_parser:
            dsl_name = block.dsl_name
            jeżeli dsl_name:
                jeżeli dsl_name nie w self.parsers:
                    assert dsl_name w parsers, "No parser to handle {!r} block.".format(dsl_name)
                    self.parsers[dsl_name] = parsers[dsl_name](self)
                parser = self.parsers[dsl_name]
                spróbuj:
                    parser.parse(block)
                wyjąwszy Exception:
                    fail('Exception podnieśd during parsing:\n' +
                         traceback.format_exc().rstrip())
            printer.print_block(block)

        second_pass_replacements = {}

        # these are destinations nie buffers
        dla name, destination w self.destinations.items():
            jeżeli destination.type == 'suppress':
                kontynuuj
            output = destination.dump()

            jeżeli output:

                block = Block("", dsl_name="clinic", output=output)

                jeżeli destination.type == 'buffer':
                    block.input = "dump " + name + "\n"
                    warn("Destination buffer " + repr(name) + " nie empty at end of file, emptying.")
                    printer.write("\n")
                    printer.print_block(block)
                    kontynuuj

                jeżeli destination.type == 'file':
                    spróbuj:
                        dirname = os.path.dirname(destination.filename)
                        spróbuj:
                            os.makedirs(dirname)
                        wyjąwszy FileExistsError:
                            jeżeli nie os.path.isdir(dirname):
                                fail("Can't write to destination {}, "
                                     "can't make directory {}!".format(
                                        destination.filename, dirname))
                        jeżeli self.verify:
                            przy open(destination.filename, "rt") jako f:
                                parser_2 = BlockParser(f.read(), language=self.language)
                                blocks = list(parser_2)
                                jeżeli (len(blocks) != 1) albo (blocks[0].input != 'preserve\n'):
                                    fail("Modified destination file " + repr(destination.filename) + ", nie overwriting!")
                    wyjąwszy FileNotFoundError:
                        dalej

                    block.input = 'preserve\n'
                    printer_2 = BlockPrinter(self.language)
                    printer_2.print_block(block)
                    przy open(destination.filename, "wt") jako f:
                        f.write(printer_2.f.getvalue())
                    kontynuuj
        text = printer.f.getvalue()

        jeżeli second_pass_replacements:
            printer_2 = BlockPrinter(self.language)
            parser_2 = BlockParser(text, self.language)
            changed = Nieprawda
            dla block w parser_2:
                jeżeli block.dsl_name:
                    dla id, replacement w second_pass_replacements.items():
                        jeżeli id w block.output:
                            changed = Prawda
                            block.output = block.output.replace(id, replacement)
                printer_2.print_block(block)
            jeżeli changed:
                text = printer_2.f.getvalue()

        zwróć text


    def _module_and_class(self, fields):
        """
        fields should be an iterable of field names.
        returns a tuple of (module, class).
        the module object could actually be self (a clinic object).
        this function jest only ever used to find the parent of where
        a new class/module should go.
        """
        in_classes = Nieprawda
        parent = module = self
        cls = Nic
        so_far = []

        dla field w fields:
            so_far.append(field)
            jeżeli nie in_classes:
                child = parent.modules.get(field)
                jeżeli child:
                    parent = module = child
                    kontynuuj
                in_classes = Prawda
            jeżeli nie hasattr(parent, 'classes'):
                zwróć module, cls
            child = parent.classes.get(field)
            jeżeli nie child:
                fail('Parent klasa albo module ' + '.'.join(so_far) + " does nie exist.")
            cls = parent = child

        zwróć module, cls


def parse_file(filename, *, force=Nieprawda, verify=Prawda, output=Nic, encoding='utf-8'):
    extension = os.path.splitext(filename)[1][1:]
    jeżeli nie extension:
        fail("Can't extract file type dla file " + repr(filename))

    spróbuj:
        language = extensions[extension](filename)
    wyjąwszy KeyError:
        fail("Can't identify file type dla file " + repr(filename))

    przy open(filename, 'r', encoding=encoding) jako f:
        raw = f.read()

    # exit quickly jeżeli there are no clinic markers w the file
    find_start_re = BlockParser("", language).find_start_re
    jeżeli nie find_start_re.search(raw):
        zwróć

    clinic = Clinic(language, force=force, verify=verify, filename=filename)
    cooked = clinic.parse(raw)
    jeżeli (cooked == raw) oraz nie force:
        zwróć

    directory = os.path.dirname(filename) albo '.'

    przy tempfile.TemporaryDirectory(prefix="clinic", dir=directory) jako tmpdir:
        bytes = cooked.encode(encoding)
        tmpfilename = os.path.join(tmpdir, os.path.basename(filename))
        przy open(tmpfilename, "wb") jako f:
            f.write(bytes)
        os.replace(tmpfilename, output albo filename)


def compute_checksum(input, length=Nic):
    input = input albo ''
    s = hashlib.sha1(input.encode('utf-8')).hexdigest()
    jeżeli length:
        s = s[:length]
    zwróć s




klasa PythonParser:
    def __init__(self, clinic):
        dalej

    def parse(self, block):
        s = io.StringIO()
        przy OverrideStdioWith(s):
            exec(block.input)
        block.output = s.getvalue()


klasa Module:
    def __init__(self, name, module=Nic):
        self.name = name
        self.module = self.parent = module

        self.modules = collections.OrderedDict()
        self.classes = collections.OrderedDict()
        self.functions = []

    def __repr__(self):
        zwróć "<clinic.Module " + repr(self.name) + " at " + str(id(self)) + ">"

klasa Class:
    def __init__(self, name, module=Nic, cls=Nic, typedef=Nic, type_object=Nic):
        self.name = name
        self.module = module
        self.cls = cls
        self.typedef = typedef
        self.type_object = type_object
        self.parent = cls albo module

        self.classes = collections.OrderedDict()
        self.functions = []

    def __repr__(self):
        zwróć "<clinic.Class " + repr(self.name) + " at " + str(id(self)) + ">"

unsupported_special_methods = set("""

__abs__
__add__
__and__
__bytes__
__call__
__complex__
__delitem__
__divmod__
__eq__
__float__
__floordiv__
__ge__
__getattr__
__getattribute__
__getitem__
__gt__
__hash__
__iadd__
__iand__
__ifloordiv__
__ilshift__
__imatmul__
__imod__
__imul__
__index__
__int__
__invert__
__ior__
__ipow__
__irshift__
__isub__
__iter__
__itruediv__
__ixor__
__le__
__len__
__lshift__
__lt__
__matmul__
__mod__
__mul__
__neg__
__new__
__next__
__or__
__pos__
__pow__
__radd__
__rand__
__rdivmod__
__repr__
__rfloordiv__
__rlshift__
__rmatmul__
__rmod__
__rmul__
__ror__
__round__
__rpow__
__rrshift__
__rshift__
__rsub__
__rtruediv__
__rxor__
__setattr__
__setitem__
__str__
__sub__
__truediv__
__xor__

""".strip().split())


INVALID, CALLABLE, STATIC_METHOD, CLASS_METHOD, METHOD_INIT, METHOD_NEW = """
INVALID, CALLABLE, STATIC_METHOD, CLASS_METHOD, METHOD_INIT, METHOD_NEW
""".replace(",", "").strip().split()

klasa Function:
    """
    Mutable duck type dla inspect.Function.

    docstring - a str containing
        * embedded line przerwijs
        * text outdented to the left margin
        * no trailing whitespace.
        It will always be true that
            (nie docstring) albo ((nie docstring[0].isspace()) oraz (docstring.rstrip() == docstring))
    """

    def __init__(self, parameters=Nic, *, name,
                 module, cls=Nic, c_basename=Nic,
                 full_name=Nic,
                 return_converter, return_annotation=_empty,
                 docstring=Nic, kind=CALLABLE, coexist=Nieprawda,
                 docstring_only=Nieprawda):
        self.parameters = parameters albo collections.OrderedDict()
        self.return_annotation = return_annotation
        self.name = name
        self.full_name = full_name
        self.module = module
        self.cls = cls
        self.parent = cls albo module
        self.c_basename = c_basename
        self.return_converter = return_converter
        self.docstring = docstring albo ''
        self.kind = kind
        self.coexist = coexist
        self.self_converter = Nic
        # docstring_only means "don't generate a machine-readable
        # signature, just a normal docstring".  it's Prawda for
        # functions przy optional groups because we can't represent
        # those accurately przy inspect.Signature w 3.4.
        self.docstring_only = docstring_only

        self.rendered_parameters = Nic

    __render_parameters__ = Nic
    @property
    def render_parameters(self):
        jeżeli nie self.__render_parameters__:
            self.__render_parameters__ = l = []
            dla p w self.parameters.values():
                p = p.copy()
                p.converter.pre_render()
                l.append(p)
        zwróć self.__render_parameters__

    @property
    def methoddef_flags(self):
        jeżeli self.kind w (METHOD_INIT, METHOD_NEW):
            zwróć Nic
        flags = []
        jeżeli self.kind == CLASS_METHOD:
            flags.append('METH_CLASS')
        albo_inaczej self.kind == STATIC_METHOD:
            flags.append('METH_STATIC')
        inaczej:
            assert self.kind == CALLABLE, "unknown kind: " + repr(self.kind)
        jeżeli self.coexist:
            flags.append('METH_COEXIST')
        zwróć '|'.join(flags)

    def __repr__(self):
        zwróć '<clinic.Function ' + self.name + '>'

    def copy(self, **overrides):
        kwargs = {
            'name': self.name, 'module': self.module, 'parameters': self.parameters,
            'cls': self.cls, 'c_basename': self.c_basename,
            'full_name': self.full_name,
            'return_converter': self.return_converter, 'return_annotation': self.return_annotation,
            'docstring': self.docstring, 'kind': self.kind, 'coexist': self.coexist,
            'docstring_only': self.docstring_only,
            }
        kwargs.update(overrides)
        f = Function(**kwargs)

        parameters = collections.OrderedDict()
        dla name, value w f.parameters.items():
            value = value.copy(function=f)
            parameters[name] = value
        f.parameters = parameters
        zwróć f


klasa Parameter:
    """
    Mutable duck type of inspect.Parameter.
    """

    def __init__(self, name, kind, *, default=_empty,
                 function, converter, annotation=_empty,
                 docstring=Nic, group=0):
        self.name = name
        self.kind = kind
        self.default = default
        self.function = function
        self.converter = converter
        self.annotation = annotation
        self.docstring = docstring albo ''
        self.group = group

    def __repr__(self):
        zwróć '<clinic.Parameter ' + self.name + '>'

    def is_keyword_only(self):
        zwróć self.kind == inspect.Parameter.KEYWORD_ONLY

    def is_positional_only(self):
        zwróć self.kind == inspect.Parameter.POSITIONAL_ONLY

    def copy(self, **overrides):
        kwargs = {
            'name': self.name, 'kind': self.kind, 'default':self.default,
                 'function': self.function, 'converter': self.converter, 'annotation': self.annotation,
                 'docstring': self.docstring, 'group': self.group,
            }
        kwargs.update(overrides)
        jeżeli 'converter' nie w overrides:
            converter = copy.copy(self.converter)
            converter.function = kwargs['function']
            kwargs['converter'] = converter
        zwróć Parameter(**kwargs)



klasa LandMine:
    # try to access any
    def __init__(self, message):
        self.__message__ = message

    def __repr__(self):
        zwróć '<LandMine ' + repr(self.__message__) + ">"

    def __getattribute__(self, name):
        jeżeli name w ('__repr__', '__message__'):
            zwróć super().__getattribute__(name)
        # podnieś RuntimeError(repr(name))
        fail("Stepped on a land mine, trying to access attribute " + repr(name) + ":\n" + self.__message__)


def add_c_converter(f, name=Nic):
    jeżeli nie name:
        name = f.__name__
        jeżeli nie name.endswith('_converter'):
            zwróć f
        name = name[:-len('_converter')]
    converters[name] = f
    zwróć f

def add_default_legacy_c_converter(cls):
    # automatically add converter dla default format unit
    # (but without stomping on the existing one jeżeli it's already
    # set, w case you subclass)
    jeżeli ((cls.format_unit nie w ('O&', '')) oraz
        (cls.format_unit nie w legacy_converters)):
        legacy_converters[cls.format_unit] = cls
    zwróć cls

def add_legacy_c_converter(format_unit, **kwargs):
    """
    Adds a legacy converter.
    """
    def closure(f):
        jeżeli nie kwargs:
            added_f = f
        inaczej:
            added_f = functools.partial(f, **kwargs)
        jeżeli format_unit:
            legacy_converters[format_unit] = added_f
        zwróć f
    zwróć closure

klasa CConverterAutoRegister(type):
    def __init__(cls, name, bases, classdict):
        add_c_converter(cls)
        add_default_legacy_c_converter(cls)

klasa CConverter(metaclass=CConverterAutoRegister):
    """
    For the init function, self, name, function, oraz default
    must be keyword-or-positional parameters.  All other
    parameters must be keyword-only.
    """

    # The C name to use dla this variable.
    name = Nic

    # The Python name to use dla this variable.
    py_name = Nic

    # The C type to use dla this variable.
    # 'type' should be a Python string specifying the type, e.g. "int".
    # If this jest a pointer type, the type string should end przy ' *'.
    type = Nic

    # The Python default value dla this parameter, jako a Python value.
    # Or the magic value "unspecified" jeżeli there jest no default.
    # Or the magic value "unknown" jeżeli this value jest a cannot be evaluated
    # at Argument-Clinic-preprocessing time (but jest presumed to be valid
    # at runtime).
    default = unspecified

    # If nie Nic, default must be isinstance() of this type.
    # (You can also specify a tuple of types.)
    default_type = Nic

    # "default" converted into a C value, jako a string.
    # Or Nic jeżeli there jest no default.
    c_default = Nic

    # "default" converted into a Python value, jako a string.
    # Or Nic jeżeli there jest no default.
    py_default = Nic

    # The default value used to initialize the C variable when
    # there jest no default, but nie specifying a default may
    # result w an "uninitialized variable" warning.  This can
    # easily happen when using option groups--although
    # properly-written code won't actually use the variable,
    # the variable does get dalejed w to the _impl.  (Ah, if
    # only dataflow analysis could inline the static function!)
    #
    # This value jest specified jako a string.
    # Every non-abstract subclass should supply a valid value.
    c_ignored_default = 'NULL'

    # The C converter *function* to be used, jeżeli any.
    # (If this jest nie Nic, format_unit must be 'O&'.)
    converter = Nic

    # Should Argument Clinic add a '&' before the name of
    # the variable when dalejing it into the _impl function?
    impl_by_reference = Nieprawda

    # Should Argument Clinic add a '&' before the name of
    # the variable when dalejing it into PyArg_ParseTuple (AndKeywords)?
    parse_by_reference = Prawda

    #############################################################
    #############################################################
    ## You shouldn't need to read anything below this point to ##
    ## write your own converter functions.                     ##
    #############################################################
    #############################################################

    # The "format unit" to specify dla this variable when
    # parsing arguments using PyArg_ParseTuple (AndKeywords).
    # Custom converters should always use the default value of 'O&'.
    format_unit = 'O&'

    # What encoding do we want dla this variable?  Only used
    # by format units starting przy 'e'.
    encoding = Nic

    # Should this object be required to be a subclass of a specific type?
    # If nie Nic, should be a string representing a pointer to a
    # PyTypeObject (e.g. "&PyUnicode_Type").
    # Only used by the 'O!' format unit (and the "object" converter).
    subclass_of = Nic

    # Do we want an adjacent '_length' variable dla this variable?
    # Only used by format units ending przy '#'.
    length = Nieprawda

    # Should we show this parameter w the generated
    # __text_signature__? This jest *almost* always Prawda.
    # (It's only Nieprawda dla __new__, __init__, oraz METH_STATIC functions.)
    show_in_signature = Prawda

    # Overrides the name used w a text signature.
    # The name used dla a "self" parameter must be one of
    # self, type, albo module; however users can set their own.
    # This lets the self_converter overrule the user-settable
    # name, *just* dla the text signature.
    # Only set by self_converter.
    signature_name = Nic

    # keep w sync przy self_converter.__init__!
    def __init__(self, name, py_name, function, default=unspecified, *, c_default=Nic, py_default=Nic, annotation=unspecified, **kwargs):
        self.name = name
        self.py_name = py_name

        jeżeli default jest nie unspecified:
            jeżeli self.default_type oraz nie isinstance(default, (self.default_type, Unknown)):
                jeżeli isinstance(self.default_type, type):
                    types_str = self.default_type.__name__
                inaczej:
                    types_str = ', '.join((cls.__name__ dla cls w self.default_type))
                fail("{}: default value {!r} dla field {} jest nie of type {}".format(
                    self.__class__.__name__, default, name, types_str))
            self.default = default

        jeżeli c_default:
            self.c_default = c_default
        jeżeli py_default:
            self.py_default = py_default

        jeżeli annotation != unspecified:
            fail("The 'annotation' parameter jest nie currently permitted.")

        # this jest deliberate, to prevent you z caching information
        # about the function w the init.
        # (that przerwijs jeżeli we get cloned.)
        # so after this change we will noisily fail.
        self.function = LandMine("Don't access members of self.function inside converter_init!")
        self.converter_init(**kwargs)
        self.function = function

    def converter_init(self):
        dalej

    def is_optional(self):
        zwróć (self.default jest nie unspecified)

    def _render_self(self, parameter, data):
        self.parameter = parameter
        original_name = self.name
        name = ensure_legal_c_identifier(original_name)

        # impl_arguments
        s = ("&" jeżeli self.impl_by_reference inaczej "") + name
        data.impl_arguments.append(s)
        jeżeli self.length:
            data.impl_arguments.append(self.length_name())

        # impl_parameters
        data.impl_parameters.append(self.simple_declaration(by_reference=self.impl_by_reference))
        jeżeli self.length:
            data.impl_parameters.append("Py_ssize_clean_t " + self.length_name())

    def _render_non_self(self, parameter, data):
        self.parameter = parameter
        original_name = self.name
        name = ensure_legal_c_identifier(original_name)

        # declarations
        d = self.declaration()
        data.declarations.append(d)

        # initializers
        initializers = self.initialize()
        jeżeli initializers:
            data.initializers.append('/* initializers dla ' + name + ' */\n' + initializers.rstrip())

        # modifications
        modifications = self.modify()
        jeżeli modifications:
            data.modifications.append('/* modifications dla ' + name + ' */\n' + modifications.rstrip())

        # keywords
        data.keywords.append(parameter.name)

        # format_units
        jeżeli self.is_optional() oraz '|' nie w data.format_units:
            data.format_units.append('|')
        jeżeli parameter.is_keyword_only() oraz '$' nie w data.format_units:
            data.format_units.append('$')
        data.format_units.append(self.format_unit)

        # parse_arguments
        self.parse_argument(data.parse_arguments)

        # cleanup
        cleanup = self.cleanup()
        jeżeli cleanup:
            data.cleanup.append('/* Cleanup dla ' + name + ' */\n' + cleanup.rstrip() + "\n")

    def render(self, parameter, data):
        """
        parameter jest a clinic.Parameter instance.
        data jest a CRenderData instance.
        """
        self._render_self(parameter, data)
        self._render_non_self(parameter, data)

    def length_name(self):
        """Computes the name of the associated "length" variable."""
        jeżeli nie self.length:
            zwróć Nic
        zwróć ensure_legal_c_identifier(self.name) + "_length"

    # Why jest this one broken out separately?
    # For "positional-only" function parsing,
    # which generates a bunch of PyArg_ParseTuple calls.
    def parse_argument(self, list):
        assert nie (self.converter oraz self.encoding)
        jeżeli self.format_unit == 'O&':
            assert self.converter
            list.append(self.converter)

        jeżeli self.encoding:
            list.append(c_repr(self.encoding))
        albo_inaczej self.subclass_of:
            list.append(self.subclass_of)

        legal_name = ensure_legal_c_identifier(self.name)
        s = ("&" jeżeli self.parse_by_reference inaczej "") + legal_name
        list.append(s)

        jeżeli self.length:
            list.append("&" + self.length_name())

    #
    # All the functions after here are intended jako extension points.
    #

    def simple_declaration(self, by_reference=Nieprawda):
        """
        Computes the basic declaration of the variable.
        Used w computing the prototype declaration oraz the
        variable declaration.
        """
        prototype = [self.type]
        jeżeli by_reference albo nie self.type.endswith('*'):
            prototype.append(" ")
        jeżeli by_reference:
            prototype.append('*')
        prototype.append(ensure_legal_c_identifier(self.name))
        zwróć "".join(prototype)

    def declaration(self):
        """
        The C statement to declare this variable.
        """
        declaration = [self.simple_declaration()]
        default = self.c_default
        jeżeli nie default oraz self.parameter.group:
            default = self.c_ignored_default
        jeżeli default:
            declaration.append(" = ")
            declaration.append(default)
        declaration.append(";")
        jeżeli self.length:
            declaration.append('\nPy_ssize_clean_t ')
            declaration.append(self.length_name())
            declaration.append(';')
        s = "".join(declaration)
        # double up curly-braces, this string will be used
        # jako part of a format_map() template later
        s = s.replace("{", "{{")
        s = s.replace("}", "}}")
        zwróć s

    def initialize(self):
        """
        The C statements required to set up this variable before parsing.
        Returns a string containing this code indented at column 0.
        If no initialization jest necessary, returns an empty string.
        """
        zwróć ""

    def modify(self):
        """
        The C statements required to modify this variable after parsing.
        Returns a string containing this code indented at column 0.
        If no initialization jest necessary, returns an empty string.
        """
        zwróć ""

    def cleanup(self):
        """
        The C statements required to clean up after this variable.
        Returns a string containing this code indented at column 0.
        If no cleanup jest necessary, returns an empty string.
        """
        zwróć ""

    def pre_render(self):
        """
        A second initialization function, like converter_init,
        called just before rendering.
        You are permitted to examine self.function here.
        """
        dalej


klasa bool_converter(CConverter):
    type = 'int'
    default_type = bool
    format_unit = 'p'
    c_ignored_default = '0'

    def converter_init(self):
        jeżeli self.default jest nie unspecified:
            self.default = bool(self.default)
            self.c_default = str(int(self.default))

klasa char_converter(CConverter):
    type = 'char'
    default_type = (bytes, bytearray)
    format_unit = 'c'
    c_ignored_default = "'\0'"

    def converter_init(self):
        jeżeli isinstance(self.default, self.default_type) oraz (len(self.default) != 1):
            fail("char_converter: illegal default value " + repr(self.default))


@add_legacy_c_converter('B', bitwise=Prawda)
klasa unsigned_char_converter(CConverter):
    type = 'unsigned char'
    default_type = int
    format_unit = 'b'
    c_ignored_default = "'\0'"

    def converter_init(self, *, bitwise=Nieprawda):
        jeżeli bitwise:
            self.format_unit = 'B'

klasa byte_converter(unsigned_char_converter): dalej

klasa short_converter(CConverter):
    type = 'short'
    default_type = int
    format_unit = 'h'
    c_ignored_default = "0"

klasa unsigned_short_converter(CConverter):
    type = 'unsigned short'
    default_type = int
    format_unit = 'H'
    c_ignored_default = "0"

    def converter_init(self, *, bitwise=Nieprawda):
        jeżeli nie bitwise:
            fail("Unsigned shorts must be bitwise (dla now).")

@add_legacy_c_converter('C', accept={str})
klasa int_converter(CConverter):
    type = 'int'
    default_type = int
    format_unit = 'i'
    c_ignored_default = "0"

    def converter_init(self, *, accept={int}, type=Nic):
        jeżeli accept == {str}:
            self.format_unit = 'C'
        albo_inaczej accept != {int}:
            fail("int_converter: illegal 'accept' argument " + repr(accept))
        jeżeli type != Nic:
            self.type = type

klasa unsigned_int_converter(CConverter):
    type = 'unsigned int'
    default_type = int
    format_unit = 'I'
    c_ignored_default = "0"

    def converter_init(self, *, bitwise=Nieprawda):
        jeżeli nie bitwise:
            fail("Unsigned ints must be bitwise (dla now).")

klasa long_converter(CConverter):
    type = 'long'
    default_type = int
    format_unit = 'l'
    c_ignored_default = "0"

klasa unsigned_long_converter(CConverter):
    type = 'unsigned long'
    default_type = int
    format_unit = 'k'
    c_ignored_default = "0"

    def converter_init(self, *, bitwise=Nieprawda):
        jeżeli nie bitwise:
            fail("Unsigned longs must be bitwise (dla now).")

klasa PY_LONG_LONG_converter(CConverter):
    type = 'PY_LONG_LONG'
    default_type = int
    format_unit = 'L'
    c_ignored_default = "0"

klasa unsigned_PY_LONG_LONG_converter(CConverter):
    type = 'unsigned PY_LONG_LONG'
    default_type = int
    format_unit = 'K'
    c_ignored_default = "0"

    def converter_init(self, *, bitwise=Nieprawda):
        jeżeli nie bitwise:
            fail("Unsigned PY_LONG_LONGs must be bitwise (dla now).")

klasa Py_ssize_t_converter(CConverter):
    type = 'Py_ssize_t'
    default_type = int
    format_unit = 'n'
    c_ignored_default = "0"


klasa float_converter(CConverter):
    type = 'float'
    default_type = float
    format_unit = 'f'
    c_ignored_default = "0.0"

klasa double_converter(CConverter):
    type = 'double'
    default_type = float
    format_unit = 'd'
    c_ignored_default = "0.0"


klasa Py_complex_converter(CConverter):
    type = 'Py_complex'
    default_type = complex
    format_unit = 'D'
    c_ignored_default = "{0.0, 0.0}"


klasa object_converter(CConverter):
    type = 'PyObject *'
    format_unit = 'O'

    def converter_init(self, *, converter=Nic, type=Nic, subclass_of=Nic):
        jeżeli converter:
            jeżeli subclass_of:
                fail("object: Cannot dalej w both 'converter' oraz 'subclass_of'")
            self.format_unit = 'O&'
            self.converter = converter
        albo_inaczej subclass_of:
            self.format_unit = 'O!'
            self.subclass_of = subclass_of

        jeżeli type jest nie Nic:
            self.type = type


#
# We define three conventions dla buffer types w the 'accept' argument:
#
#  buffer  : any object supporting the buffer interface
#  rwbuffer: any object supporting the buffer interface, but must be writeable
#  robuffer: any object supporting the buffer interface, but must nie be writeable
#

klasa buffer: dalej
klasa rwbuffer: dalej
klasa robuffer: dalej

def str_converter_key(types, encoding, zeroes):
    zwróć (frozenset(types), bool(encoding), bool(zeroes))

str_converter_argument_map = {}

klasa str_converter(CConverter):
    type = 'const char *'
    default_type = (str, Null, NicType)
    format_unit = 's'

    def converter_init(self, *, accept={str}, encoding=Nic, zeroes=Nieprawda):

        key = str_converter_key(accept, encoding, zeroes)
        format_unit = str_converter_argument_map.get(key)
        jeżeli nie format_unit:
            fail("str_converter: illegal combination of arguments", key)

        self.format_unit = format_unit
        self.length = bool(zeroes)
        jeżeli encoding:
            jeżeli self.default nie w (Null, Nic, unspecified):
                fail("str_converter: Argument Clinic doesn't support default values dla encoded strings")
            self.encoding = encoding
            self.type = 'char *'
            # sorry, clinic can't support preallocated buffers
            # dla es# oraz et#
            self.c_default = "NULL"

    def cleanup(self):
        jeżeli self.encoding:
            name = ensure_legal_c_identifier(self.name)
            zwróć "".join(["jeżeli (", name, ")\n   PyMem_FREE(", name, ");\n"])

#
# This jest the fourth albo fifth rewrite of registering all the
# crazy string converter format units.  Previous approaches hid
# bugs--generally mismatches between the semantics of the format
# unit oraz the arguments necessary to represent those semantics
# properly.  Hopefully przy this approach we'll get it 100% right.
#
# The r() function (short dla "register") both registers the
# mapping z arguments to format unit *and* registers the
# legacy C converter dla that format unit.
#
def r(format_unit, *, accept, encoding=Nieprawda, zeroes=Nieprawda):
    jeżeli nie encoding oraz format_unit != 's':
        # add the legacy c converters here too.
        #
        # note: add_legacy_c_converter can't work for
        #   es, es#, et, albo et#
        #   because of their extra encoding argument
        #
        # also don't add the converter dla 's' because
        # the metaclass dla CConverter adds it dla us.
        kwargs = {}
        jeżeli accept != {str}:
            kwargs['accept'] = accept
        jeżeli zeroes:
            kwargs['zeroes'] = Prawda
        added_f = functools.partial(str_converter, **kwargs)
        legacy_converters[format_unit] = added_f

    d = str_converter_argument_map
    key = str_converter_key(accept, encoding, zeroes)
    jeżeli key w d:
        sys.exit("Duplicate keys specified dla str_converter_argument_map!")
    d[key] = format_unit

r('es',  encoding=Prawda,              accept={str})
r('es#', encoding=Prawda, zeroes=Prawda, accept={str})
r('et',  encoding=Prawda,              accept={bytes, bytearray, str})
r('et#', encoding=Prawda, zeroes=Prawda, accept={bytes, bytearray, str})
r('s',                               accept={str})
r('s#',                 zeroes=Prawda, accept={robuffer, str})
r('y',                               accept={robuffer})
r('y#',                 zeroes=Prawda, accept={robuffer})
r('z',                               accept={str, NicType})
r('z#',                 zeroes=Prawda, accept={robuffer, str, NicType})
usuń r


klasa PyBytesObject_converter(CConverter):
    type = 'PyBytesObject *'
    format_unit = 'S'
    # accept = {bytes}

klasa PyByteArrayObject_converter(CConverter):
    type = 'PyByteArrayObject *'
    format_unit = 'Y'
    # accept = {bytearray}

klasa unicode_converter(CConverter):
    type = 'PyObject *'
    default_type = (str, Null, NicType)
    format_unit = 'U'

@add_legacy_c_converter('u#', zeroes=Prawda)
@add_legacy_c_converter('Z', accept={str, NicType})
@add_legacy_c_converter('Z#', accept={str, NicType}, zeroes=Prawda)
klasa Py_UNICODE_converter(CConverter):
    type = 'Py_UNICODE *'
    default_type = (str, Null, NicType)
    format_unit = 'u'

    def converter_init(self, *, accept={str}, zeroes=Nieprawda):
        format_unit = 'Z' jeżeli accept=={str, NicType} inaczej 'u'
        jeżeli zeroes:
            format_unit += '#'
            self.length = Prawda
        self.format_unit = format_unit

@add_legacy_c_converter('s*', accept={str, buffer})
@add_legacy_c_converter('z*', accept={str, buffer, NicType})
@add_legacy_c_converter('w*', accept={rwbuffer})
klasa Py_buffer_converter(CConverter):
    type = 'Py_buffer'
    format_unit = 'y*'
    impl_by_reference = Prawda
    c_ignored_default = "{NULL, NULL}"

    def converter_init(self, *, accept={buffer}):
        jeżeli self.default nie w (unspecified, Nic):
            fail("The only legal default value dla Py_buffer jest Nic.")

        self.c_default = self.c_ignored_default

        jeżeli accept == {str, buffer, NicType}:
            format_unit = 'z*'
        albo_inaczej accept == {str, buffer}:
            format_unit = 's*'
        albo_inaczej accept == {buffer}:
            format_unit = 'y*'
        albo_inaczej accept == {rwbuffer}:
            format_unit = 'w*'
        inaczej:
            fail("Py_buffer_converter: illegal combination of arguments")

        self.format_unit = format_unit

    def cleanup(self):
        name = ensure_legal_c_identifier(self.name)
        zwróć "".join(["jeżeli (", name, ".obj)\n   PyBuffer_Release(&", name, ");\n"])


def correct_name_for_self(f):
    jeżeli f.kind w (CALLABLE, METHOD_INIT):
        jeżeli f.cls:
            zwróć "PyObject *", "self"
        zwróć "PyModuleDef *", "module"
    jeżeli f.kind == STATIC_METHOD:
        zwróć "void *", "null"
    jeżeli f.kind w (CLASS_METHOD, METHOD_NEW):
        zwróć "PyTypeObject *", "type"
    podnieś RuntimeError("Unhandled type of function f: " + repr(f.kind))

def required_type_for_self_for_parser(f):
    type, _ = correct_name_for_self(f)
    jeżeli f.kind w (METHOD_INIT, METHOD_NEW, STATIC_METHOD, CLASS_METHOD):
        zwróć type
    zwróć Nic


klasa self_converter(CConverter):
    """
    A special-case converter:
    this jest the default converter used dla "self".
    """
    type = Nic
    format_unit = ''

    def converter_init(self, *, type=Nic):
        self.specified_type = type

    def pre_render(self):
        f = self.function
        default_type, default_name = correct_name_for_self(f)
        self.signature_name = default_name
        self.type = self.specified_type albo self.type albo default_type

        kind = self.function.kind
        new_or_init = kind w (METHOD_NEW, METHOD_INIT)

        jeżeli (kind == STATIC_METHOD) albo new_or_init:
            self.show_in_signature = Nieprawda

    # tp_new (METHOD_NEW) functions are of type newfunc:
    #     typedef PyObject *(*newfunc)(struct _typeobject *, PyObject *, PyObject *);
    # PyTypeObject jest a typedef dla struct _typeobject.
    #
    # tp_init (METHOD_INIT) functions are of type initproc:
    #     typedef int (*initproc)(PyObject *, PyObject *, PyObject *);
    #
    # All other functions generated by Argument Clinic are stored w
    # PyMethodDef structures, w the ml_meth slot, which jest of type PyCFunction:
    #     typedef PyObject *(*PyCFunction)(PyObject *, PyObject *);
    # However!  We habitually cast these functions to PyCFunction,
    # since functions that accept keyword arguments don't fit this signature
    # but are stored there anyway.  So strict type equality isn't important
    # dla these functions.
    #
    # So:
    #
    # * The name of the first parameter to the impl oraz the parsing function will always
    #   be self.name.
    #
    # * The type of the first parameter to the impl will always be of self.type.
    #
    # * If the function jest neither tp_new (METHOD_NEW) nor tp_init (METHOD_INIT):
    #   * The type of the first parameter to the parsing function jest also self.type.
    #     This means that jeżeli you step into the parsing function, your "self" parameter
    #     jest of the correct type, which may make debugging more pleasant.
    #
    # * Else jeżeli the function jest tp_new (METHOD_NEW):
    #   * The type of the first parameter to the parsing function jest "PyTypeObject *",
    #     so the type signature of the function call jest an exact match.
    #   * If self.type != "PyTypeObject *", we cast the first parameter to self.type
    #     w the impl call.
    #
    # * Else jeżeli the function jest tp_init (METHOD_INIT):
    #   * The type of the first parameter to the parsing function jest "PyObject *",
    #     so the type signature of the function call jest an exact match.
    #   * If self.type != "PyObject *", we cast the first parameter to self.type
    #     w the impl call.

    @property
    def parser_type(self):
        zwróć required_type_for_self_for_parser(self.function) albo self.type

    def render(self, parameter, data):
        """
        parameter jest a clinic.Parameter instance.
        data jest a CRenderData instance.
        """
        jeżeli self.function.kind == STATIC_METHOD:
            zwróć

        self._render_self(parameter, data)

        jeżeli self.type != self.parser_type:
            # insert cast to impl_argument[0], aka self.
            # we know we're w the first slot w all the CRenderData lists,
            # because we render parameters w order, oraz self jest always first.
            assert len(data.impl_arguments) == 1
            assert data.impl_arguments[0] == self.name
            data.impl_arguments[0] = '(' + self.type + ")" + data.impl_arguments[0]

    def set_template_dict(self, template_dict):
        template_dict['self_name'] = self.name
        template_dict['self_type'] = self.parser_type
        kind = self.function.kind
        cls = self.function.cls

        jeżeli ((kind w (METHOD_NEW, METHOD_INIT)) oraz cls oraz cls.typedef):
            jeżeli kind == METHOD_NEW:
                dalejed_in_type = self.name
            inaczej:
                dalejed_in_type = 'Py_TYPE({})'.format(self.name)

            line = '({passed_in_type} == {type_object}) &&\n        '
            d = {
                'type_object': self.function.cls.type_object,
                'passed_in_type': dalejed_in_type
                }
            template_dict['self_type_check'] = line.format_map(d)



def add_c_return_converter(f, name=Nic):
    jeżeli nie name:
        name = f.__name__
        jeżeli nie name.endswith('_return_converter'):
            zwróć f
        name = name[:-len('_return_converter')]
    return_converters[name] = f
    zwróć f


klasa CReturnConverterAutoRegister(type):
    def __init__(cls, name, bases, classdict):
        add_c_return_converter(cls)

klasa CReturnConverter(metaclass=CReturnConverterAutoRegister):

    # The C type to use dla this variable.
    # 'type' should be a Python string specifying the type, e.g. "int".
    # If this jest a pointer type, the type string should end przy ' *'.
    type = 'PyObject *'

    # The Python default value dla this parameter, jako a Python value.
    # Or the magic value "unspecified" jeżeli there jest no default.
    default = Nic

    def __init__(self, *, py_default=Nic, **kwargs):
        self.py_default = py_default
        spróbuj:
            self.return_converter_init(**kwargs)
        wyjąwszy TypeError jako e:
            s = ', '.join(name + '=' + repr(value) dla name, value w kwargs.items())
            sys.exit(self.__class__.__name__ + '(' + s + ')\n' + str(e))

    def return_converter_init(self):
        dalej

    def declare(self, data, name="_return_value"):
        line = []
        add = line.append
        add(self.type)
        jeżeli nie self.type.endswith('*'):
            add(' ')
        add(name + ';')
        data.declarations.append(''.join(line))
        data.return_value = name

    def err_occurred_if(self, expr, data):
        data.return_conversion.append('jeżeli (({}) && PyErr_Occurred())\n    goto exit;\n'.format(expr))

    def err_occurred_if_null_pointer(self, variable, data):
        data.return_conversion.append('jeżeli ({} == NULL)\n    goto exit;\n'.format(variable))

    def render(self, function, data):
        """
        function jest a clinic.Function instance.
        data jest a CRenderData instance.
        """
        dalej

add_c_return_converter(CReturnConverter, 'object')

klasa NicType_return_converter(CReturnConverter):
    def render(self, function, data):
        self.declare(data)
        data.return_conversion.append('''
jeżeli (_return_value != Py_Nic)
    goto exit;
return_value = Py_Nic;
Py_INCREF(Py_Nic);
'''.strip())

klasa bool_return_converter(CReturnConverter):
    type = 'int'

    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == -1", data)
        data.return_conversion.append('return_value = PyBool_FromLong((long)_return_value);\n')

klasa long_return_converter(CReturnConverter):
    type = 'long'
    conversion_fn = 'PyLong_FromLong'
    cast = ''
    unsigned_cast = ''

    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == {}-1".format(self.unsigned_cast), data)
        data.return_conversion.append(
            ''.join(('return_value = ', self.conversion_fn, '(', self.cast, '_return_value);\n')))

klasa int_return_converter(long_return_converter):
    type = 'int'
    cast = '(long)'

klasa init_return_converter(long_return_converter):
    """
    Special zwróć converter dla __init__ functions.
    """
    type = 'int'
    cast = '(long)'

    def render(self, function, data):
        dalej

klasa unsigned_long_return_converter(long_return_converter):
    type = 'unsigned long'
    conversion_fn = 'PyLong_FromUnsignedLong'
    unsigned_cast = '(unsigned long)'

klasa unsigned_int_return_converter(unsigned_long_return_converter):
    type = 'unsigned int'
    cast = '(unsigned long)'
    unsigned_cast = '(unsigned int)'

klasa Py_ssize_t_return_converter(long_return_converter):
    type = 'Py_ssize_t'
    conversion_fn = 'PyLong_FromSsize_t'

klasa size_t_return_converter(long_return_converter):
    type = 'size_t'
    conversion_fn = 'PyLong_FromSize_t'
    unsigned_cast = '(size_t)'


klasa double_return_converter(CReturnConverter):
    type = 'double'
    cast = ''

    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if("_return_value == -1.0", data)
        data.return_conversion.append(
            'return_value = PyFloat_FromDouble(' + self.cast + '_return_value);\n')

klasa float_return_converter(double_return_converter):
    type = 'float'
    cast = '(double)'


klasa DecodeFSDefault_return_converter(CReturnConverter):
    type = 'char *'

    def render(self, function, data):
        self.declare(data)
        self.err_occurred_if_null_pointer("_return_value", data)
        data.return_conversion.append(
            'return_value = PyUnicode_DecodeFSDefault(_return_value);\n')


def eval_ast_expr(node, globals, *, filename='-'):
    """
    Takes an ast.Expr node.  Compiles oraz evaluates it.
    Returns the result of the expression.

    globals represents the globals dict the expression
    should see.  (There's no equivalent dla "locals" here.)
    """

    jeżeli isinstance(node, ast.Expr):
        node = node.value

    node = ast.Expression(node)
    co = compile(node, filename, 'eval')
    fn = types.FunctionType(co, globals)
    zwróć fn()


klasa IndentStack:
    def __init__(self):
        self.indents = []
        self.margin = Nic

    def _ensure(self):
        jeżeli nie self.indents:
            fail('IndentStack expected indents, but none are defined.')

    def measure(self, line):
        """
        Returns the length of the line's margin.
        """
        jeżeli '\t' w line:
            fail('Tab characters are illegal w the Argument Clinic DSL.')
        stripped = line.lstrip()
        jeżeli nie len(stripped):
            # we can't tell anything z an empty line
            # so just pretend it's indented like our current indent
            self._ensure()
            zwróć self.indents[-1]
        zwróć len(line) - len(stripped)

    def infer(self, line):
        """
        Infer what jest now the current margin based on this line.
        Returns:
            1 jeżeli we have indented (or this jest the first margin)
            0 jeżeli the margin has nie changed
           -N jeżeli we have dedented N times
        """
        indent = self.measure(line)
        margin = ' ' * indent
        jeżeli nie self.indents:
            self.indents.append(indent)
            self.margin = margin
            zwróć 1
        current = self.indents[-1]
        jeżeli indent == current:
            zwróć 0
        jeżeli indent > current:
            self.indents.append(indent)
            self.margin = margin
            zwróć 1
        # indent < current
        jeżeli indent nie w self.indents:
            fail("Illegal outdent.")
        outdent_count = 0
        dopóki indent != current:
            self.indents.pop()
            current = self.indents[-1]
            outdent_count -= 1
        self.margin = margin
        zwróć outdent_count

    @property
    def depth(self):
        """
        Returns how many margins are currently defined.
        """
        zwróć len(self.indents)

    def indent(self, line):
        """
        Indents a line by the currently defined margin.
        """
        zwróć self.margin + line

    def dedent(self, line):
        """
        Dedents a line by the currently defined margin.
        (The inverse of 'indent'.)
        """
        margin = self.margin
        indent = self.indents[-1]
        jeżeli nie line.startswith(margin):
            fail('Cannot dedent, line does nie start przy the previous margin:')
        zwróć line[indent:]


klasa DSLParser:
    def __init__(self, clinic):
        self.clinic = clinic

        self.directives = {}
        dla name w dir(self):
            # functions that start przy directive_ are added to directives
            _, s, key = name.partition("directive_")
            jeżeli s:
                self.directives[key] = getattr(self, name)

            # functions that start przy at_ are too, przy an @ w front
            _, s, key = name.partition("at_")
            jeżeli s:
                self.directives['@' + key] = getattr(self, name)

        self.reset()

    def reset(self):
        self.function = Nic
        self.state = self.state_dsl_start
        self.parameter_indent = Nic
        self.keyword_only = Nieprawda
        self.group = 0
        self.parameter_state = self.ps_start
        self.seen_positional_with_default = Nieprawda
        self.indent = IndentStack()
        self.kind = CALLABLE
        self.coexist = Nieprawda
        self.parameter_continuation = ''
        self.preserve_output = Nieprawda

    def directive_version(self, required):
        global version
        jeżeli version_comparitor(version, required) < 0:
            fail("Insufficient Clinic version!\n  Version: " + version + "\n  Required: " + required)

    def directive_module(self, name):
        fields = name.split('.')
        new = fields.pop()
        module, cls = self.clinic._module_and_class(fields)
        jeżeli cls:
            fail("Can't nest a module inside a class!")

        jeżeli name w module.classes:
            fail("Already defined module " + repr(name) + "!")

        m = Module(name, module)
        module.modules[name] = m
        self.block.signatures.append(m)

    def directive_class(self, name, typedef, type_object):
        fields = name.split('.')
        in_classes = Nieprawda
        parent = self
        name = fields.pop()
        so_far = []
        module, cls = self.clinic._module_and_class(fields)

        parent = cls albo module
        jeżeli name w parent.classes:
            fail("Already defined klasa " + repr(name) + "!")

        c = Class(name, module, cls, typedef, type_object)
        parent.classes[name] = c
        self.block.signatures.append(c)

    def directive_set(self, name, value):
        jeżeli name nie w ("line_prefix", "line_suffix"):
            fail("unknown variable", repr(name))

        value = value.format_map({
            'block comment start': '/*',
            'block comment end': '*/',
            })

        self.clinic.__dict__[name] = value

    def directive_destination(self, name, command, *args):
        jeżeli command == 'new':
            self.clinic.add_destination(name, *args)
            zwróć

        jeżeli command == 'clear':
            self.clinic.get_destination(name).clear()
        fail("unknown destination command", repr(command))


    def directive_output(self, command_or_name, destination=''):
        fd = self.clinic.destination_buffers

        jeżeli command_or_name == "preset":
            preset = self.clinic.presets.get(destination)
            jeżeli nie preset:
                fail("Unknown preset " + repr(destination) + "!")
            fd.update(preset)
            zwróć

        jeżeli command_or_name == "push":
            self.clinic.destination_buffers_stack.append(fd.copy())
            zwróć

        jeżeli command_or_name == "pop":
            jeżeli nie self.clinic.destination_buffers_stack:
                fail("Can't 'output pop', stack jest empty!")
            previous_fd = self.clinic.destination_buffers_stack.pop()
            fd.update(previous_fd)
            zwróć

        # secret command dla debugging!
        jeżeli command_or_name == "print":
            self.block.output.append(pprint.pformat(fd))
            self.block.output.append('\n')
            zwróć

        d = self.clinic.get_destination(destination)

        jeżeli command_or_name == "everything":
            dla name w list(fd):
                fd[name] = d
            zwróć

        jeżeli command_or_name nie w fd:
            fail("Invalid command / destination name " + repr(command_or_name) + ", must be one of:\n  preset push pop print everything " + " ".join(fd))
        fd[command_or_name] = d

    def directive_dump(self, name):
        self.block.output.append(self.clinic.get_destination(name).dump())

    def directive_print(self, *args):
        self.block.output.append(' '.join(args))
        self.block.output.append('\n')

    def directive_preserve(self):
        jeżeli self.preserve_output:
            fail("Can't have preserve twice w one block!")
        self.preserve_output = Prawda

    def at_classmethod(self):
        jeżeli self.kind jest nie CALLABLE:
            fail("Can't set @classmethod, function jest nie a normal callable")
        self.kind = CLASS_METHOD

    def at_staticmethod(self):
        jeżeli self.kind jest nie CALLABLE:
            fail("Can't set @staticmethod, function jest nie a normal callable")
        self.kind = STATIC_METHOD

    def at_coexist(self):
        jeżeli self.coexist:
            fail("Called @coexist twice!")
        self.coexist = Prawda

    def parse(self, block):
        self.reset()
        self.block = block
        self.saved_output = self.block.output
        block.output = []
        block_start = self.clinic.block_parser.line_number
        lines = block.input.split('\n')
        dla line_number, line w enumerate(lines, self.clinic.block_parser.block_start_line_number):
            jeżeli '\t' w line:
                fail('Tab characters are illegal w the Clinic DSL.\n\t' + repr(line), line_number=block_start)
            self.state(line)

        self.next(self.state_terminal)
        self.state(Nic)

        block.output.extend(self.clinic.language.render(clinic, block.signatures))

        jeżeli self.preserve_output:
            jeżeli block.output:
                fail("'preserve' only works dla blocks that don't produce any output!")
            block.output = self.saved_output

    @staticmethod
    def ignore_line(line):
        # ignore comment-only lines
        jeżeli line.lstrip().startswith('#'):
            zwróć Prawda

        # Ignore empty lines too
        # (but nie w docstring sections!)
        jeżeli nie line.strip():
            zwróć Prawda

        zwróć Nieprawda

    @staticmethod
    def calculate_indent(line):
        zwróć len(line) - len(line.strip())

    def next(self, state, line=Nic):
        # real_print(self.state.__name__, "->", state.__name__, ", line=", line)
        self.state = state
        jeżeli line jest nie Nic:
            self.state(line)

    def state_dsl_start(self, line):
        # self.block = self.ClinicOutputBlock(self)
        jeżeli self.ignore_line(line):
            zwróć

        # jest it a directive?
        fields = shlex.split(line)
        directive_name = fields[0]
        directive = self.directives.get(directive_name, Nic)
        jeżeli directive:
            spróbuj:
                directive(*fields[1:])
            wyjąwszy TypeError jako e:
                fail(str(e))
            zwróć

        self.next(self.state_modulename_name, line)

    def state_modulename_name(self, line):
        # looking dla declaration, which establishes the leftmost column
        # line should be
        #     modulename.fnname [as c_basename] [-> zwróć annotation]
        # square brackets denote optional syntax.
        #
        # alternatively:
        #     modulename.fnname [as c_basename] = modulename.existing_fn_name
        # clones the parameters oraz zwróć converter z that
        # function.  you can't modify them.  you must enter a
        # new docstring.
        #
        # (but we might find a directive first!)
        #
        # this line jest permitted to start przy whitespace.
        # we'll call this number of spaces F (dla "function").

        jeżeli nie line.strip():
            zwróć

        self.indent.infer(line)

        # are we cloning?
        before, equals, existing = line.rpartition('=')
        jeżeli equals:
            full_name, _, c_basename = before.partition(' jako ')
            full_name = full_name.strip()
            c_basename = c_basename.strip()
            existing = existing.strip()
            jeżeli (is_legal_py_identifier(full_name) oraz
                (nie c_basename albo is_legal_c_identifier(c_basename)) oraz
                is_legal_py_identifier(existing)):
                # we're cloning!
                fields = [x.strip() dla x w existing.split('.')]
                function_name = fields.pop()
                module, cls = self.clinic._module_and_class(fields)

                dla existing_function w (cls albo module).functions:
                    jeżeli existing_function.name == function_name:
                        przerwij
                inaczej:
                    existing_function = Nic
                jeżeli nie existing_function:
                    print("class", cls, "module", module, "existing", existing)
                    print("cls. functions", cls.functions)
                    fail("Couldn't find existing function " + repr(existing) + "!")

                fields = [x.strip() dla x w full_name.split('.')]
                function_name = fields.pop()
                module, cls = self.clinic._module_and_class(fields)

                jeżeli nie (existing_function.kind == self.kind oraz existing_function.coexist == self.coexist):
                    fail("'kind' of function oraz cloned function don't match!  (@classmethod/@staticmethod/@coexist)")
                self.function = existing_function.copy(name=function_name, full_name=full_name, module=module, cls=cls, c_basename=c_basename, docstring='')

                self.block.signatures.append(self.function)
                (cls albo module).functions.append(self.function)
                self.next(self.state_function_docstring)
                zwróć

        line, _, returns = line.partition('->')

        full_name, _, c_basename = line.partition(' jako ')
        full_name = full_name.strip()
        c_basename = c_basename.strip() albo Nic

        jeżeli nie is_legal_py_identifier(full_name):
            fail("Illegal function name: {}".format(full_name))
        jeżeli c_basename oraz nie is_legal_c_identifier(c_basename):
            fail("Illegal C basename: {}".format(c_basename))

        return_converter = Nic
        jeżeli returns:
            ast_input = "def x() -> {}: dalej".format(returns)
            module = Nic
            spróbuj:
                module = ast.parse(ast_input)
            wyjąwszy SyntaxError:
                dalej
            jeżeli nie module:
                fail("Badly-formed annotation dla " + full_name + ": " + returns)
            spróbuj:
                name, legacy, kwargs = self.parse_converter(module.body[0].returns)
                jeżeli legacy:
                    fail("Legacy converter {!r} nie allowed jako a zwróć converter"
                         .format(name))
                jeżeli name nie w return_converters:
                    fail("No available zwróć converter called " + repr(name))
                return_converter = return_converters[name](**kwargs)
            wyjąwszy ValueError:
                fail("Badly-formed annotation dla " + full_name + ": " + returns)

        fields = [x.strip() dla x w full_name.split('.')]
        function_name = fields.pop()
        module, cls = self.clinic._module_and_class(fields)

        fields = full_name.split('.')
        jeżeli fields[-1] == '__new__':
            jeżeli (self.kind != CLASS_METHOD) albo (nie cls):
                fail("__new__ must be a klasa method!")
            self.kind = METHOD_NEW
        albo_inaczej fields[-1] == '__init__':
            jeżeli (self.kind != CALLABLE) albo (nie cls):
                fail("__init__ must be a normal method, nie a klasa albo static method!")
            self.kind = METHOD_INIT
            jeżeli nie return_converter:
                return_converter = init_return_converter()
        albo_inaczej fields[-1] w unsupported_special_methods:
            fail(fields[-1] + " jest a special method oraz cannot be converted to Argument Clinic!  (Yet.)")

        jeżeli nie return_converter:
            return_converter = CReturnConverter()

        jeżeli nie module:
            fail("Undefined module used w declaration of " + repr(full_name.strip()) + ".")
        self.function = Function(name=function_name, full_name=full_name, module=module, cls=cls, c_basename=c_basename,
                                 return_converter=return_converter, kind=self.kind, coexist=self.coexist)
        self.block.signatures.append(self.function)

        # insert a self converter automatically
        type, name = correct_name_for_self(self.function)
        kwargs = {}
        jeżeli cls oraz type == "PyObject *":
            kwargs['type'] = cls.typedef
        sc = self.function.self_converter = self_converter(name, name, self.function, **kwargs)
        p_self = Parameter(sc.name, inspect.Parameter.POSITIONAL_ONLY, function=self.function, converter=sc)
        self.function.parameters[sc.name] = p_self

        (cls albo module).functions.append(self.function)
        self.next(self.state_parameters_start)

    # Now entering the parameters section.  The rules, formally stated:
    #
    #   * All lines must be indented przy spaces only.
    #   * The first line must be a parameter declaration.
    #   * The first line must be indented.
    #       * This first line establishes the indent dla parameters.
    #       * We'll call this number of spaces P (dla "parameter").
    #   * Thenceforth:
    #       * Lines indented przy P spaces specify a parameter.
    #       * Lines indented przy > P spaces are docstrings dla the previous
    #         parameter.
    #           * We'll call this number of spaces D (dla "docstring").
    #           * All subsequent lines indented przy >= D spaces are stored as
    #             part of the per-parameter docstring.
    #           * All lines will have the first D spaces of the indent stripped
    #             before they are stored.
    #           * It's illegal to have a line starting przy a number of spaces X
    #             such that P < X < D.
    #       * A line przy < P spaces jest the first line of the function
    #         docstring, which ends processing dla parameters oraz per-parameter
    #         docstrings.
    #           * The first line of the function docstring must be at the same
    #             indent jako the function declaration.
    #       * It's illegal to have any line w the parameters section starting
    #         przy X spaces such that F < X < P.  (As before, F jest the indent
    #         of the function declaration.)
    #
    # Also, currently Argument Clinic places the following restrictions on groups:
    #   * Each group must contain at least one parameter.
    #   * Each group may contain at most one group, which must be the furthest
    #     thing w the group z the required parameters.  (The nested group
    #     must be the first w the group when it's before the required
    #     parameters, oraz the last thing w the group when after the required
    #     parameters.)
    #   * There may be at most one (top-level) group to the left albo right of
    #     the required parameters.
    #   * You must specify a slash, oraz it must be after all parameters.
    #     (In other words: either all parameters are positional-only,
    #      albo none are.)
    #
    #  Said another way:
    #   * Each group must contain at least one parameter.
    #   * All left square brackets before the required parameters must be
    #     consecutive.  (You can't have a left square bracket followed
    #     by a parameter, then another left square bracket.  You can't
    #     have a left square bracket, a parameter, a right square bracket,
    #     oraz then a left square bracket.)
    #   * All right square brackets after the required parameters must be
    #     consecutive.
    #
    # These rules are enforced przy a single state variable:
    # "parameter_state".  (Previously the code was a miasma of ifs oraz
    # separate boolean state variables.)  The states are:
    #
    #  [ [ a, b, ] c, ] d, e, f=3, [ g, h, [ i ] ] /   <- line
    # 01   2          3       4    5           6   7   <- state transitions
    #
    # 0: ps_start.  before we've seen anything.  legal transitions are to 1 albo 3.
    # 1: ps_left_square_before.  left square brackets before required parameters.
    # 2: ps_group_before.  w a group, before required parameters.
    # 3: ps_required.  required parameters, positional-or-keyword albo positional-only
    #     (we don't know yet).  (renumber left groups!)
    # 4: ps_optional.  positional-or-keyword albo positional-only parameters that
    #    now must have default values.
    # 5: ps_group_after.  w a group, after required parameters.
    # 6: ps_right_square_after.  right square brackets after required parameters.
    # 7: ps_seen_slash.  seen slash.
    ps_start, ps_left_square_before, ps_group_before, ps_required, \
    ps_optional, ps_group_after, ps_right_square_after, ps_seen_slash = range(8)

    def state_parameters_start(self, line):
        jeżeli self.ignore_line(line):
            zwróć

        # jeżeli this line jest nie indented, we have no parameters
        jeżeli nie self.indent.infer(line):
            zwróć self.next(self.state_function_docstring, line)

        self.parameter_continuation = ''
        zwróć self.next(self.state_parameter, line)


    def to_required(self):
        """
        Transition to the "required" parameter state.
        """
        jeżeli self.parameter_state != self.ps_required:
            self.parameter_state = self.ps_required
            dla p w self.function.parameters.values():
                p.group = -p.group

    def state_parameter(self, line):
        jeżeli self.parameter_continuation:
            line = self.parameter_continuation + ' ' + line.lstrip()
            self.parameter_continuation = ''

        jeżeli self.ignore_line(line):
            zwróć

        assert self.indent.depth == 2
        indent = self.indent.infer(line)
        jeżeli indent == -1:
            # we outdented, must be to definition column
            zwróć self.next(self.state_function_docstring, line)

        jeżeli indent == 1:
            # we indented, must be to new parameter docstring column
            zwróć self.next(self.state_parameter_docstring_start, line)

        line = line.rstrip()
        jeżeli line.endswith('\\'):
            self.parameter_continuation = line[:-1]
            zwróć

        line = line.lstrip()

        jeżeli line w ('*', '/', '[', ']'):
            self.parse_special_symbol(line)
            zwróć

        jeżeli self.parameter_state w (self.ps_start, self.ps_required):
            self.to_required()
        albo_inaczej self.parameter_state == self.ps_left_square_before:
            self.parameter_state = self.ps_group_before
        albo_inaczej self.parameter_state == self.ps_group_before:
            jeżeli nie self.group:
                self.to_required()
        albo_inaczej self.parameter_state w (self.ps_group_after, self.ps_optional):
            dalej
        inaczej:
            fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".a)")

        # handle "as" dla  parameters too
        c_name = Nic
        name, have_as_token, trailing = line.partition(' jako ')
        jeżeli have_as_token:
            name = name.strip()
            jeżeli ' ' nie w name:
                fields = trailing.strip().split(' ')
                jeżeli nie fields:
                    fail("Invalid 'as' clause!")
                c_name = fields[0]
                jeżeli c_name.endswith(':'):
                    name += ':'
                    c_name = c_name[:-1]
                fields[0] = name
                line = ' '.join(fields)

        base, equals, default = line.rpartition('=')
        jeżeli nie equals:
            base = default
            default = Nic

        module = Nic
        spróbuj:
            ast_input = "def x({}): dalej".format(base)
            module = ast.parse(ast_input)
        wyjąwszy SyntaxError:
            spróbuj:
                # the last = was probably inside a function call, like
                #   c: int(accept={str})
                # so assume there was no actual default value.
                default = Nic
                ast_input = "def x({}): dalej".format(line)
                module = ast.parse(ast_input)
            wyjąwszy SyntaxError:
                dalej
        jeżeli nie module:
            fail("Function " + self.function.name + " has an invalid parameter declaration:\n\t" + line)

        function_args = module.body[0].args

        jeżeli len(function_args.args) > 1:
            fail("Function " + self.function.name + " has an invalid parameter declaration (comma?):\n\t" + line)
        jeżeli function_args.defaults albo function_args.kw_defaults:
            fail("Function " + self.function.name + " has an invalid parameter declaration (default value?):\n\t" + line)
        jeżeli function_args.vararg albo function_args.kwarg:
            fail("Function " + self.function.name + " has an invalid parameter declaration (*args? **kwargs?):\n\t" + line)

        parameter = function_args.args[0]

        parameter_name = parameter.arg
        name, legacy, kwargs = self.parse_converter(parameter.annotation)

        jeżeli nie default:
            jeżeli self.parameter_state == self.ps_optional:
                fail("Can't have a parameter without a default (" + repr(parameter_name) + ")\nafter a parameter przy a default!")
            value = unspecified
            jeżeli 'py_default' w kwargs:
                fail("You can't specify py_default without specifying a default value!")
        inaczej:
            jeżeli self.parameter_state == self.ps_required:
                self.parameter_state = self.ps_optional
            default = default.strip()
            bad = Nieprawda
            ast_input = "x = {}".format(default)
            bad = Nieprawda
            spróbuj:
                module = ast.parse(ast_input)

                jeżeli 'c_default' nie w kwargs:
                    # we can only represent very simple data values w C.
                    # detect whether default jest okay, via a blacklist
                    # of disallowed ast nodes.
                    klasa DetectBadNodes(ast.NodeVisitor):
                        bad = Nieprawda
                        def bad_node(self, node):
                            self.bad = Prawda

                        # inline function call
                        visit_Call = bad_node
                        # inline jeżeli statement ("x = 3 jeżeli y inaczej z")
                        visit_IfExp = bad_node

                        # comprehensions oraz generator expressions
                        visit_ListComp = visit_SetComp = bad_node
                        visit_DictComp = visit_GeneratorExp = bad_node

                        # literals dla advanced types
                        visit_Dict = visit_Set = bad_node
                        visit_List = visit_Tuple = bad_node

                        # "starred": "a = [1, 2, 3]; *a"
                        visit_Starred = bad_node

                        # allow ellipsis, dla now
                        # visit_Ellipsis = bad_node

                    blacklist = DetectBadNodes()
                    blacklist.visit(module)
                    bad = blacklist.bad
                inaczej:
                    # jeżeli they specify a c_default, we can be more lenient about the default value.
                    # but at least make an attempt at ensuring it's a valid expression.
                    spróbuj:
                        value = eval(default)
                        jeżeli value == unspecified:
                            fail("'unspecified' jest nie a legal default value!")
                    wyjąwszy NameError:
                        dalej # probably a named constant
                    wyjąwszy Exception jako e:
                        fail("Malformed expression given jako default value\n"
                             "{!r} caused {!r}".format(default, e))
                jeżeli bad:
                    fail("Unsupported expression jako default value: " + repr(default))

                expr = module.body[0].value
                # mild hack: explicitly support NULL jako a default value
                jeżeli isinstance(expr, ast.Name) oraz expr.id == 'NULL':
                    value = NULL
                    py_default = 'Nic'
                    c_default = "NULL"
                albo_inaczej (isinstance(expr, ast.BinOp) albo
                    (isinstance(expr, ast.UnaryOp) oraz nie isinstance(expr.operand, ast.Num))):
                    c_default = kwargs.get("c_default")
                    jeżeli nie (isinstance(c_default, str) oraz c_default):
                        fail("When you specify an expression (" + repr(default) + ") jako your default value,\nyou MUST specify a valid c_default.")
                    py_default = default
                    value = unknown
                albo_inaczej isinstance(expr, ast.Attribute):
                    a = []
                    n = expr
                    dopóki isinstance(n, ast.Attribute):
                        a.append(n.attr)
                        n = n.value
                    jeżeli nie isinstance(n, ast.Name):
                        fail("Unsupported default value " + repr(default) + " (looked like a Python constant)")
                    a.append(n.id)
                    py_default = ".".join(reversed(a))

                    c_default = kwargs.get("c_default")
                    jeżeli nie (isinstance(c_default, str) oraz c_default):
                        fail("When you specify a named constant (" + repr(py_default) + ") jako your default value,\nyou MUST specify a valid c_default.")

                    spróbuj:
                        value = eval(py_default)
                    wyjąwszy NameError:
                        value = unknown
                inaczej:
                    value = ast.literal_eval(expr)
                    py_default = repr(value)
                    jeżeli isinstance(value, (bool, Nic.__class__)):
                        c_default = "Py_" + py_default
                    albo_inaczej isinstance(value, str):
                        c_default = c_repr(value)
                    inaczej:
                        c_default = py_default

            wyjąwszy SyntaxError jako e:
                fail("Syntax error: " + repr(e.text))
            wyjąwszy (ValueError, AttributeError):
                value = unknown
                c_default = kwargs.get("c_default")
                py_default = default
                jeżeli nie (isinstance(c_default, str) oraz c_default):
                    fail("When you specify a named constant (" + repr(py_default) + ") jako your default value,\nyou MUST specify a valid c_default.")

            kwargs.setdefault('c_default', c_default)
            kwargs.setdefault('py_default', py_default)

        dict = legacy_converters jeżeli legacy inaczej converters
        legacy_str = "legacy " jeżeli legacy inaczej ""
        jeżeli name nie w dict:
            fail('{} jest nie a valid {}converter'.format(name, legacy_str))
        # jeżeli you use a c_name dla the parameter, we just give that name to the converter
        # but the parameter object gets the python name
        converter = dict[name](c_name albo parameter_name, parameter_name, self.function, value, **kwargs)

        kind = inspect.Parameter.KEYWORD_ONLY jeżeli self.keyword_only inaczej inspect.Parameter.POSITIONAL_OR_KEYWORD

        jeżeli isinstance(converter, self_converter):
            jeżeli len(self.function.parameters) == 1:
                jeżeli (self.parameter_state != self.ps_required):
                    fail("A 'self' parameter cannot be marked optional.")
                jeżeli value jest nie unspecified:
                    fail("A 'self' parameter cannot have a default value.")
                jeżeli self.group:
                    fail("A 'self' parameter cannot be w an optional group.")
                kind = inspect.Parameter.POSITIONAL_ONLY
                self.parameter_state = self.ps_start
                self.function.parameters.clear()
            inaczej:
                fail("A 'self' parameter, jeżeli specified, must be the very first thing w the parameter block.")

        p = Parameter(parameter_name, kind, function=self.function, converter=converter, default=value, group=self.group)

        jeżeli parameter_name w self.function.parameters:
            fail("You can't have two parameters named " + repr(parameter_name) + "!")
        self.function.parameters[parameter_name] = p

    def parse_converter(self, annotation):
        jeżeli isinstance(annotation, ast.Str):
            zwróć annotation.s, Prawda, {}

        jeżeli isinstance(annotation, ast.Name):
            zwróć annotation.id, Nieprawda, {}

        jeżeli nie isinstance(annotation, ast.Call):
            fail("Annotations must be either a name, a function call, albo a string.")

        name = annotation.func.id
        symbols = globals()

        kwargs = {node.arg: eval_ast_expr(node.value, symbols) dla node w annotation.keywords}
        zwróć name, Nieprawda, kwargs

    def parse_special_symbol(self, symbol):
        jeżeli self.parameter_state == self.ps_seen_slash:
            fail("Function " + self.function.name + " specifies " + symbol + " after /, which jest unsupported.")

        jeżeli symbol == '*':
            jeżeli self.keyword_only:
                fail("Function " + self.function.name + " uses '*' more than once.")
            self.keyword_only = Prawda
        albo_inaczej symbol == '[':
            jeżeli self.parameter_state w (self.ps_start, self.ps_left_square_before):
                self.parameter_state = self.ps_left_square_before
            albo_inaczej self.parameter_state w (self.ps_required, self.ps_group_after):
                self.parameter_state = self.ps_group_after
            inaczej:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".b)")
            self.group += 1
            self.function.docstring_only = Prawda
        albo_inaczej symbol == ']':
            jeżeli nie self.group:
                fail("Function " + self.function.name + " has a ] without a matching [.")
            jeżeli nie any(p.group == self.group dla p w self.function.parameters.values()):
                fail("Function " + self.function.name + " has an empty group.\nAll groups must contain at least one parameter.")
            self.group -= 1
            jeżeli self.parameter_state w (self.ps_left_square_before, self.ps_group_before):
                self.parameter_state = self.ps_group_before
            albo_inaczej self.parameter_state w (self.ps_group_after, self.ps_right_square_after):
                self.parameter_state = self.ps_right_square_after
            inaczej:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".c)")
        albo_inaczej symbol == '/':
            # ps_required oraz ps_optional are allowed here, that allows positional-only without option groups
            # to work (and have default values!)
            jeżeli (self.parameter_state nie w (self.ps_required, self.ps_optional, self.ps_right_square_after, self.ps_group_before)) albo self.group:
                fail("Function " + self.function.name + " has an unsupported group configuration. (Unexpected state " + str(self.parameter_state) + ".d)")
            jeżeli self.keyword_only:
                fail("Function " + self.function.name + " mixes keyword-only oraz positional-only parameters, which jest unsupported.")
            self.parameter_state = self.ps_seen_slash
            # fixup preceding parameters
            dla p w self.function.parameters.values():
                jeżeli (p.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD oraz nie isinstance(p.converter, self_converter)):
                    fail("Function " + self.function.name + " mixes keyword-only oraz positional-only parameters, which jest unsupported.")
                p.kind = inspect.Parameter.POSITIONAL_ONLY

    def state_parameter_docstring_start(self, line):
        self.parameter_docstring_indent = len(self.indent.margin)
        assert self.indent.depth == 3
        zwróć self.next(self.state_parameter_docstring, line)

    # every line of the docstring must start przy at least F spaces,
    # where F > P.
    # these F spaces will be stripped.
    def state_parameter_docstring(self, line):
        stripped = line.strip()
        jeżeli stripped.startswith('#'):
            zwróć

        indent = self.indent.measure(line)
        jeżeli indent < self.parameter_docstring_indent:
            self.indent.infer(line)
            assert self.indent.depth < 3
            jeżeli self.indent.depth == 2:
                # back to a parameter
                zwróć self.next(self.state_parameter, line)
            assert self.indent.depth == 1
            zwróć self.next(self.state_function_docstring, line)

        assert self.function.parameters
        last_parameter = next(reversed(list(self.function.parameters.values())))

        new_docstring = last_parameter.docstring

        jeżeli new_docstring:
            new_docstring += '\n'
        jeżeli stripped:
            new_docstring += self.indent.dedent(line)

        last_parameter.docstring = new_docstring

    # the final stanza of the DSL jest the docstring.
    def state_function_docstring(self, line):
        jeżeli self.group:
            fail("Function " + self.function.name + " has a ] without a matching [.")

        stripped = line.strip()
        jeżeli stripped.startswith('#'):
            zwróć

        new_docstring = self.function.docstring
        jeżeli new_docstring:
            new_docstring += "\n"
        jeżeli stripped:
            line = self.indent.dedent(line).rstrip()
        inaczej:
            line = ''
        new_docstring += line
        self.function.docstring = new_docstring

    def format_docstring(self):
        f = self.function

        new_or_init = f.kind w (METHOD_NEW, METHOD_INIT)
        jeżeli new_or_init oraz nie f.docstring:
            # don't render a docstring at all, no signature, nothing.
            zwróć f.docstring

        text, add, output = _text_accumulator()
        parameters = f.render_parameters

        ##
        ## docstring first line
        ##

        jeżeli new_or_init:
            # classes get *just* the name of the class
            # nie __new__, nie __init__, oraz nie module.classname
            assert f.cls
            add(f.cls.name)
        inaczej:
            add(f.name)
        add('(')

        # populate "right_bracket_count" field dla every parameter
        assert parameters, "We should always have a self parameter. " + repr(f)
        assert isinstance(parameters[0].converter, self_converter)
        parameters[0].right_bracket_count = 0
        parameters_after_self = parameters[1:]
        jeżeli parameters_after_self:
            # dla now, the only way Clinic supports positional-only parameters
            # jest jeżeli all of them are positional-only...
            #
            # ... wyjąwszy dla self!  self jest always positional-only.

            positional_only_parameters = [p.kind == inspect.Parameter.POSITIONAL_ONLY dla p w parameters_after_self]
            jeżeli parameters_after_self[0].kind == inspect.Parameter.POSITIONAL_ONLY:
                assert all(positional_only_parameters)
                dla p w parameters:
                    p.right_bracket_count = abs(p.group)
            inaczej:
                # don't put any right brackets around non-positional-only parameters, ever.
                dla p w parameters_after_self:
                    p.right_bracket_count = 0

        right_bracket_count = 0

        def fix_right_bracket_count(desired):
            nonlocal right_bracket_count
            s = ''
            dopóki right_bracket_count < desired:
                s += '['
                right_bracket_count += 1
            dopóki right_bracket_count > desired:
                s += ']'
                right_bracket_count -= 1
            zwróć s

        need_slash = Nieprawda
        added_slash = Nieprawda
        need_a_trailing_slash = Nieprawda

        # we only need a trailing slash:
        #   * jeżeli this jest nie a "docstring_only" signature
        #   * oraz jeżeli the last *shown* parameter jest
        #     positional only
        jeżeli nie f.docstring_only:
            dla p w reversed(parameters):
                jeżeli nie p.converter.show_in_signature:
                    kontynuuj
                jeżeli p.is_positional_only():
                    need_a_trailing_slash = Prawda
                przerwij


        added_star = Nieprawda

        first_parameter = Prawda
        last_p = parameters[-1]
        line_length = len(''.join(text))
        indent = " " * line_length
        def add_parameter(text):
            nonlocal line_length
            nonlocal first_parameter
            jeżeli first_parameter:
                s = text
                first_parameter = Nieprawda
            inaczej:
                s = ' ' + text
                jeżeli line_length + len(s) >= 72:
                    add('\n')
                    add(indent)
                    line_length = len(indent)
                    s = text
            line_length += len(s)
            add(s)

        dla p w parameters:
            jeżeli nie p.converter.show_in_signature:
                kontynuuj
            assert p.name

            is_self = isinstance(p.converter, self_converter)
            jeżeli is_self oraz f.docstring_only:
                # this isn't a real machine-parsable signature,
                # so let's nie print the "self" parameter
                kontynuuj

            jeżeli p.is_positional_only():
                need_slash = nie f.docstring_only
            albo_inaczej need_slash oraz nie (added_slash albo p.is_positional_only()):
                added_slash = Prawda
                add_parameter('/,')

            jeżeli p.is_keyword_only() oraz nie added_star:
                added_star = Prawda
                add_parameter('*,')

            p_add, p_output = text_accumulator()
            p_add(fix_right_bracket_count(p.right_bracket_count))

            jeżeli isinstance(p.converter, self_converter):
                # annotate first parameter jako being a "self".
                #
                # jeżeli inspect.Signature gets this function,
                # oraz it's already bound, the self parameter
                # will be stripped off.
                #
                # jeżeli it's nie bound, it should be marked
                # jako positional-only.
                #
                # note: we don't print "self" dla __init__,
                # because this isn't actually the signature
                # dla __init__.  (it can't be, __init__ doesn't
                # have a docstring.)  jeżeli this jest an __init__
                # (or __new__), then this signature jest for
                # calling the klasa to construct a new instance.
                p_add('$')

            name = p.converter.signature_name albo p.name
            p_add(name)

            jeżeli p.converter.is_optional():
                p_add('=')
                value = p.converter.py_default
                jeżeli nie value:
                    value = repr(p.converter.default)
                p_add(value)

            jeżeli (p != last_p) albo need_a_trailing_slash:
                p_add(',')

            add_parameter(p_output())

        add(fix_right_bracket_count(0))
        jeżeli need_a_trailing_slash:
            add_parameter('/')
        add(')')

        # PEP 8 says:
        #
        #     The Python standard library will nie use function annotations
        #     jako that would result w a premature commitment to a particular
        #     annotation style. Instead, the annotations are left dla users
        #     to discover oraz experiment przy useful annotation styles.
        #
        # therefore this jest commented out:
        #
        # jeżeli f.return_converter.py_default:
        #     add(' -> ')
        #     add(f.return_converter.py_default)

        jeżeli nie f.docstring_only:
            add("\n" + sig_end_marker + "\n")

        docstring_first_line = output()

        # now fix up the places where the brackets look wrong
        docstring_first_line = docstring_first_line.replace(', ]', ',] ')

        # okay.  now we're officially building the "parameters" section.
        # create substitution text dla {parameters}
        spacer_line = Nieprawda
        dla p w parameters:
            jeżeli nie p.docstring.strip():
                kontynuuj
            jeżeli spacer_line:
                add('\n')
            inaczej:
                spacer_line = Prawda
            add("  ")
            add(p.name)
            add('\n')
            add(textwrap.indent(rstrip_lines(p.docstring.rstrip()), "    "))
        parameters = output()
        jeżeli parameters:
            parameters += '\n'

        ##
        ## docstring body
        ##

        docstring = f.docstring.rstrip()
        lines = [line.rstrip() dla line w docstring.split('\n')]

        # Enforce the summary line!
        # The first line of a docstring should be a summary of the function.
        # It should fit on one line (80 columns? 79 maybe?) oraz be a paragraph
        # by itself.
        #
        # Argument Clinic enforces the following rule:
        #  * either the docstring jest empty,
        #  * albo it must have a summary line.
        #
        # Guido said Clinic should enforce this:
        # http://mail.python.org/pipermail/python-dev/2013-June/127110.html

        jeżeli len(lines) >= 2:
            jeżeli lines[1]:
                fail("Docstring dla " + f.full_name + " does nie have a summary line!\n" +
                    "Every non-blank function docstring must start with\n" +
                    "a single line summary followed by an empty line.")
        albo_inaczej len(lines) == 1:
            # the docstring jest only one line right now--the summary line.
            # add an empty line after the summary line so we have space
            # between it oraz the {parameters} we're about to add.
            lines.append('')

        parameters_marker_count = len(docstring.split('{parameters}')) - 1
        jeżeli parameters_marker_count > 1:
            fail('You may nie specify {parameters} more than once w a docstring!')

        jeżeli nie parameters_marker_count:
            # insert after summary line
            lines.insert(2, '{parameters}')

        # insert at front of docstring
        lines.insert(0, docstring_first_line)

        docstring = "\n".join(lines)

        add(docstring)
        docstring = output()

        docstring = linear_format(docstring, parameters=parameters)
        docstring = docstring.rstrip()

        zwróć docstring

    def state_terminal(self, line):
        """
        Called when processing the block jest done.
        """
        assert nie line

        jeżeli nie self.function:
            zwróć

        jeżeli self.keyword_only:
            values = self.function.parameters.values()
            jeżeli nie values:
                no_parameter_after_star = Prawda
            inaczej:
                last_parameter = next(reversed(list(values)))
                no_parameter_after_star = last_parameter.kind != inspect.Parameter.KEYWORD_ONLY
            jeżeli no_parameter_after_star:
                fail("Function " + self.function.name + " specifies '*' without any parameters afterwards.")

        # remove trailing whitespace z all parameter docstrings
        dla name, value w self.function.parameters.items():
            jeżeli nie value:
                kontynuuj
            value.docstring = value.docstring.rstrip()

        self.function.docstring = self.format_docstring()




# maps strings to callables.
# the callable should zwróć an object
# that implements the clinic parser
# interface (__init__ oraz parse).
#
# example parsers:
#   "clinic", handles the Clinic DSL
#   "python", handles running Python code
#
parsers = {'clinic' : DSLParser, 'python': PythonParser}


clinic = Nic


def main(argv):
    zaimportuj sys

    jeżeli sys.version_info.major < 3 albo sys.version_info.minor < 3:
        sys.exit("Error: clinic.py requires Python 3.3 albo greater.")

    zaimportuj argparse
    cmdline = argparse.ArgumentParser()
    cmdline.add_argument("-f", "--force", action='store_true')
    cmdline.add_argument("-o", "--output", type=str)
    cmdline.add_argument("-v", "--verbose", action='store_true')
    cmdline.add_argument("--converters", action='store_true')
    cmdline.add_argument("--make", action='store_true')
    cmdline.add_argument("filename", type=str, nargs="*")
    ns = cmdline.parse_args(argv)

    jeżeli ns.converters:
        jeżeli ns.filename:
            print("Usage error: can't specify --converters oraz a filename at the same time.")
            print()
            cmdline.print_usage()
            sys.exit(-1)
        converters = []
        return_converters = []
        ignored = set("""
            add_c_converter
            add_c_return_converter
            add_default_legacy_c_converter
            add_legacy_c_converter
            """.strip().split())
        module = globals()
        dla name w module:
            dla suffix, ids w (
                ("_return_converter", return_converters),
                ("_converter", converters),
            ):
                jeżeli name w ignored:
                    kontynuuj
                jeżeli name.endswith(suffix):
                    ids.append((name, name[:-len(suffix)]))
                    przerwij
        print()

        print("Legacy converters:")
        legacy = sorted(legacy_converters)
        print('    ' + ' '.join(c dla c w legacy jeżeli c[0].isupper()))
        print('    ' + ' '.join(c dla c w legacy jeżeli c[0].islower()))
        print()

        dla title, attribute, ids w (
            ("Converters", 'converter_init', converters),
            ("Return converters", 'return_converter_init', return_converters),
        ):
            print(title + ":")
            longest = -1
            dla name, short_name w ids:
                longest = max(longest, len(short_name))
            dla name, short_name w sorted(ids, key=lambda x: x[1].lower()):
                cls = module[name]
                callable = getattr(cls, attribute, Nic)
                jeżeli nie callable:
                    kontynuuj
                signature = inspect.signature(callable)
                parameters = []
                dla parameter_name, parameter w signature.parameters.items():
                    jeżeli parameter.kind == inspect.Parameter.KEYWORD_ONLY:
                        jeżeli parameter.default != inspect.Parameter.empty:
                            s = '{}={!r}'.format(parameter_name, parameter.default)
                        inaczej:
                            s = parameter_name
                        parameters.append(s)
                print('    {}({})'.format(short_name, ', '.join(parameters)))
            print()
        print("All converters also accept (c_default=Nic, py_default=Nic, annotation=Nic).")
        print("All zwróć converters also accept (py_default=Nic).")
        sys.exit(0)

    jeżeli ns.make:
        jeżeli ns.output albo ns.filename:
            print("Usage error: can't use -o albo filenames przy --make.")
            print()
            cmdline.print_usage()
            sys.exit(-1)
        dla root, dirs, files w os.walk('.'):
            dla rcs_dir w ('.svn', '.git', '.hg', 'build', 'externals'):
                jeżeli rcs_dir w dirs:
                    dirs.remove(rcs_dir)
            dla filename w files:
                jeżeli nie (filename.endswith('.c') albo filename.endswith('.h')):
                    kontynuuj
                path = os.path.join(root, filename)
                jeżeli ns.verbose:
                    print(path)
                parse_file(path, force=ns.force, verify=nie ns.force)
        zwróć

    jeżeli nie ns.filename:
        cmdline.print_usage()
        sys.exit(-1)

    jeżeli ns.output oraz len(ns.filename) > 1:
        print("Usage error: can't use -o przy multiple filenames.")
        print()
        cmdline.print_usage()
        sys.exit(-1)

    dla filename w ns.filename:
        jeżeli ns.verbose:
            print(filename)
        parse_file(filename, output=ns.output, force=ns.force, verify=nie ns.force)


jeżeli __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
