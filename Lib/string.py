"""A collection of string constants.

Public module variables:

whitespace -- a string containing all ASCII whitespace
ascii_lowercase -- a string containing all ASCII lowercase letters
ascii_uppercase -- a string containing all ASCII uppercase letters
ascii_letters -- a string containing all ASCII letters
digits -- a string containing all ASCII decimal digits
hexdigits -- a string containing all ASCII hexadecimal digits
octdigits -- a string containing all ASCII octal digits
punctuation -- a string containing all ASCII punctuation characters
printable -- a string containing all ASCII characters considered printable

"""

zaimportuj _string

# Some strings dla ctype-style character classification
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace

# Functions which aren't available jako string methods.

# Capitalize the words w a string, e.g. " aBc  dEf " -> "Abc Def".
def capwords(s, sep=Nic):
    """capwords(s [,sep]) -> string

    Split the argument into words using split, capitalize each
    word using capitalize, oraz join the capitalized words using
    join.  If the optional second argument sep jest absent albo Nic,
    runs of whitespace characters are replaced by a single space
    oraz leading oraz trailing whitespace are removed, otherwise
    sep jest used to split oraz join the words.

    """
    zwróć (sep albo ' ').join(x.capitalize() dla x w s.split(sep))


####################################################################
zaimportuj re jako _re
z collections zaimportuj ChainMap

klasa _TemplateMetaclass(type):
    pattern = r"""
    %(delim)s(?:
      (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
      (?P<named>%(id)s)      |   # delimiter oraz a Python identifier
      {(?P<braced>%(id)s)}   |   # delimiter oraz a braced identifier
      (?P<invalid>)              # Other ill-formed delimiter exprs
    )
    """

    def __init__(cls, name, bases, dct):
        super(_TemplateMetaclass, cls).__init__(name, bases, dct)
        jeżeli 'pattern' w dct:
            pattern = cls.pattern
        inaczej:
            pattern = _TemplateMetaclass.pattern % {
                'delim' : _re.escape(cls.delimiter),
                'id'    : cls.idpattern,
                }
        cls.pattern = _re.compile(pattern, cls.flags | _re.VERBOSE)


klasa Template(metaclass=_TemplateMetaclass):
    """A string klasa dla supporting $-substitutions."""

    delimiter = '$'
    idpattern = r'[_a-z][_a-z0-9]*'
    flags = _re.IGNORECASE

    def __init__(self, template):
        self.template = template

    # Search dla $$, $identifier, ${identifier}, oraz any bare $'s

    def _invalid(self, mo):
        i = mo.start('invalid')
        lines = self.template[:i].splitlines(keepends=Prawda)
        jeżeli nie lines:
            colno = 1
            lineno = 1
        inaczej:
            colno = i - len(''.join(lines[:-1]))
            lineno = len(lines)
        podnieś ValueError('Invalid placeholder w string: line %d, col %d' %
                         (lineno, colno))

    def substitute(*args, **kws):
        jeżeli nie args:
            podnieś TypeError("descriptor 'substitute' of 'Template' object "
                            "needs an argument")
        self, *args = args  # allow the "self" keyword be dalejed
        jeżeli len(args) > 1:
            podnieś TypeError('Too many positional arguments')
        jeżeli nie args:
            mapping = kws
        albo_inaczej kws:
            mapping = ChainMap(kws, args[0])
        inaczej:
            mapping = args[0]
        # Helper function dla .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') albo mo.group('braced')
            jeżeli named jest nie Nic:
                val = mapping[named]
                # We use this idiom instead of str() because the latter will
                # fail jeżeli val jest a Unicode containing non-ASCII characters.
                zwróć '%s' % (val,)
            jeżeli mo.group('escaped') jest nie Nic:
                zwróć self.delimiter
            jeżeli mo.group('invalid') jest nie Nic:
                self._invalid(mo)
            podnieś ValueError('Unrecognized named group w pattern',
                             self.pattern)
        zwróć self.pattern.sub(convert, self.template)

    def safe_substitute(*args, **kws):
        jeżeli nie args:
            podnieś TypeError("descriptor 'safe_substitute' of 'Template' object "
                            "needs an argument")
        self, *args = args  # allow the "self" keyword be dalejed
        jeżeli len(args) > 1:
            podnieś TypeError('Too many positional arguments')
        jeżeli nie args:
            mapping = kws
        albo_inaczej kws:
            mapping = ChainMap(kws, args[0])
        inaczej:
            mapping = args[0]
        # Helper function dla .sub()
        def convert(mo):
            named = mo.group('named') albo mo.group('braced')
            jeżeli named jest nie Nic:
                spróbuj:
                    # We use this idiom instead of str() because the latter
                    # will fail jeżeli val jest a Unicode containing non-ASCII
                    zwróć '%s' % (mapping[named],)
                wyjąwszy KeyError:
                    zwróć mo.group()
            jeżeli mo.group('escaped') jest nie Nic:
                zwróć self.delimiter
            jeżeli mo.group('invalid') jest nie Nic:
                zwróć mo.group()
            podnieś ValueError('Unrecognized named group w pattern',
                             self.pattern)
        zwróć self.pattern.sub(convert, self.template)



########################################################################
# the Formatter class
# see PEP 3101 dla details oraz purpose of this class

# The hard parts are reused z the C implementation.  They're exposed jako "_"
# prefixed methods of str.

# The overall parser jest implemented w _string.formatter_parser.
# The field name parser jest implemented w _string.formatter_field_name_split

klasa Formatter:
    def format(*args, **kwargs):
        jeżeli nie args:
            podnieś TypeError("descriptor 'format' of 'Formatter' object "
                            "needs an argument")
        self, *args = args  # allow the "self" keyword be dalejed
        spróbuj:
            format_string, *args = args # allow the "format_string" keyword be dalejed
        wyjąwszy ValueError:
            jeżeli 'format_string' w kwargs:
                format_string = kwargs.pop('format_string')
                zaimportuj warnings
                warnings.warn("Passing 'format_string' jako keyword argument jest "
                              "deprecated", DeprecationWarning, stacklevel=2)
            inaczej:
                podnieś TypeError("format() missing 1 required positional "
                                "argument: 'format_string'") z Nic
        zwróć self.vformat(format_string, args, kwargs)

    def vformat(self, format_string, args, kwargs):
        used_args = set()
        result = self._vformat(format_string, args, kwargs, used_args, 2)
        self.check_unused_args(used_args, args, kwargs)
        zwróć result

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth,
                 auto_arg_index=0):
        jeżeli recursion_depth < 0:
            podnieś ValueError('Max string recursion exceeded')
        result = []
        dla literal_text, field_name, format_spec, conversion w \
                self.parse(format_string):

            # output the literal text
            jeżeli literal_text:
                result.append(literal_text)

            # jeżeli there's a field, output it
            jeżeli field_name jest nie Nic:
                # this jest some markup, find the object oraz do
                #  the formatting

                # handle arg indexing when empty field_names are given.
                jeżeli field_name == '':
                    jeżeli auto_arg_index jest Nieprawda:
                        podnieś ValueError('cannot switch z manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                albo_inaczej field_name.isdigit():
                    jeżeli auto_arg_index:
                        podnieś ValueError('cannot switch z manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, jeżeli it gets
                    # used later on, then an exception will be podnieśd
                    auto_arg_index = Nieprawda

                # given the field_name, find the object it references
                #  oraz the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, jeżeli needed
                format_spec = self._vformat(format_spec, args, kwargs,
                                            used_args, recursion_depth-1,
                                            auto_arg_index=auto_arg_index)

                # format the object oraz append to the result
                result.append(self.format_field(obj, format_spec))

        zwróć ''.join(result)


    def get_value(self, key, args, kwargs):
        jeżeli isinstance(key, int):
            zwróć args[key]
        inaczej:
            zwróć kwargs[key]


    def check_unused_args(self, used_args, args, kwargs):
        dalej


    def format_field(self, value, format_spec):
        zwróć format(value, format_spec)


    def convert_field(self, value, conversion):
        # do any conversion on the resulting object
        jeżeli conversion jest Nic:
            zwróć value
        albo_inaczej conversion == 's':
            zwróć str(value)
        albo_inaczej conversion == 'r':
            zwróć repr(value)
        albo_inaczej conversion == 'a':
            zwróć ascii(value)
        podnieś ValueError("Unknown conversion specifier {0!s}".format(conversion))


    # returns an iterable that contains tuples of the form:
    # (literal_text, field_name, format_spec, conversion)
    # literal_text can be zero length
    # field_name can be Nic, w which case there's no
    #  object to format oraz output
    # jeżeli field_name jest nie Nic, it jest looked up, formatted
    #  przy format_spec oraz conversion oraz then used
    def parse(self, format_string):
        zwróć _string.formatter_parser(format_string)


    # given a field_name, find the object it references.
    #  field_name:   the field being looked up, e.g. "0.name"
    #                 albo "lookup[3]"
    #  used_args:    a set of which args have been used
    #  args, kwargs: jako dalejed w to vformat
    def get_field(self, field_name, args, kwargs):
        first, rest = _string.formatter_field_name_split(field_name)

        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr albo getitem jako needed
        dla is_attr, i w rest:
            jeżeli is_attr:
                obj = getattr(obj, i)
            inaczej:
                obj = obj[i]

        zwróć obj, first
