"""Policy framework dla the email package.

Allows fine grained feature control of how the package parses oraz emits data.
"""

zaimportuj abc
z email zaimportuj header
z email zaimportuj charset jako _charset
z email.utils zaimportuj _has_surrogates

__all__ = [
    'Policy',
    'Compat32',
    'compat32',
    ]


klasa _PolicyBase:

    """Policy Object basic framework.

    This klasa jest useless unless subclassed.  A subclass should define
    klasa attributes przy defaults dla any values that are to be
    managed by the Policy object.  The constructor will then allow
    non-default values to be set dla these attributes at instance
    creation time.  The instance will be callable, taking these same
    attributes keyword arguments, oraz returning a new instance
    identical to the called instance wyjąwszy dla those values changed
    by the keyword arguments.  Instances may be added, uzyskajing new
    instances przy any non-default values z the right hand
    operand overriding those w the left hand operand.  That is,

        A + B == A(<non-default values of B>)

    The repr of an instance can be used to reconstruct the object
    jeżeli oraz only jeżeli the repr of the values can be used to reconstruct
    those values.

    """

    def __init__(self, **kw):
        """Create new Policy, possibly overriding some defaults.

        See klasa docstring dla a list of overridable attributes.

        """
        dla name, value w kw.items():
            jeżeli hasattr(self, name):
                super(_PolicyBase,self).__setattr__(name, value)
            inaczej:
                podnieś TypeError(
                    "{!r} jest an invalid keyword argument dla {}".format(
                        name, self.__class__.__name__))

    def __repr__(self):
        args = [ "{}={!r}".format(name, value)
                 dla name, value w self.__dict__.items() ]
        zwróć "{}({})".format(self.__class__.__name__, ', '.join(args))

    def clone(self, **kw):
        """Return a new instance przy specified attributes changed.

        The new instance has the same attribute values jako the current object,
        wyjąwszy dla the changes dalejed w jako keyword arguments.

        """
        newpolicy = self.__class__.__new__(self.__class__)
        dla attr, value w self.__dict__.items():
            object.__setattr__(newpolicy, attr, value)
        dla attr, value w kw.items():
            jeżeli nie hasattr(self, attr):
                podnieś TypeError(
                    "{!r} jest an invalid keyword argument dla {}".format(
                        attr, self.__class__.__name__))
            object.__setattr__(newpolicy, attr, value)
        zwróć newpolicy

    def __setattr__(self, name, value):
        jeżeli hasattr(self, name):
            msg = "{!r} object attribute {!r} jest read-only"
        inaczej:
            msg = "{!r} object has no attribute {!r}"
        podnieś AttributeError(msg.format(self.__class__.__name__, name))

    def __add__(self, other):
        """Non-default values z right operand override those z left.

        The object returned jest a new instance of the subclass.

        """
        zwróć self.clone(**other.__dict__)


def _append_doc(doc, added_doc):
    doc = doc.rsplit('\n', 1)[0]
    added_doc = added_doc.split('\n', 1)[1]
    zwróć doc + '\n' + added_doc

def _extend_docstrings(cls):
    jeżeli cls.__doc__ oraz cls.__doc__.startswith('+'):
        cls.__doc__ = _append_doc(cls.__bases__[0].__doc__, cls.__doc__)
    dla name, attr w cls.__dict__.items():
        jeżeli attr.__doc__ oraz attr.__doc__.startswith('+'):
            dla c w (c dla base w cls.__bases__ dla c w base.mro()):
                doc = getattr(getattr(c, name), '__doc__')
                jeżeli doc:
                    attr.__doc__ = _append_doc(doc, attr.__doc__)
                    przerwij
    zwróć cls


klasa Policy(_PolicyBase, metaclass=abc.ABCMeta):

    r"""Controls dla how messages are interpreted oraz formatted.

    Most of the classes oraz many of the methods w the email package accept
    Policy objects jako parameters.  A Policy object contains a set of values oraz
    functions that control how input jest interpreted oraz how output jest rendered.
    For example, the parameter 'raise_on_defect' controls whether albo nie an RFC
    violation results w an error being podnieśd albo not, dopóki 'max_line_length'
    controls the maximum length of output lines when a Message jest serialized.

    Any valid attribute may be overridden when a Policy jest created by dalejing
    it jako a keyword argument to the constructor.  Policy objects are immutable,
    but a new Policy object can be created przy only certain values changed by
    calling the Policy instance przy keyword arguments.  Policy objects can
    also be added, producing a new Policy object w which the non-default
    attributes set w the right hand operand overwrite those specified w the
    left operand.

    Settable attributes:

    podnieś_on_defect     -- If true, then defects should be podnieśd jako errors.
                           Default: Nieprawda.

    linesep             -- string containing the value to use jako separation
                           between output lines.  Default '\n'.

    cte_type            -- Type of allowed content transfer encodings

                           7bit  -- ASCII only
                           8bit  -- Content-Transfer-Encoding: 8bit jest allowed

                           Default: 8bit.  Also controls the disposition of
                           (RFC invalid) binary data w headers; see the
                           documentation of the binary_fold method.

    max_line_length     -- maximum length of lines, excluding 'linesep',
                           during serialization.  Nic albo 0 means no line
                           wrapping jest done.  Default jest 78.

    mangle_from_        -- a flag that, when Prawda escapes From_ lines w the
                           body of the message by putting a `>' w front of
                           them. This jest used when the message jest being
                           serialized by a generator. Default: Prawda.

    """

    podnieś_on_defect = Nieprawda
    linesep = '\n'
    cte_type = '8bit'
    max_line_length = 78
    mangle_from_ = Nieprawda

    def handle_defect(self, obj, defect):
        """Based on policy, either podnieś defect albo call register_defect.

            handle_defect(obj, defect)

        defect should be a Defect subclass, but w any case must be an
        Exception subclass.  obj jest the object on which the defect should be
        registered jeżeli it jest nie podnieśd.  If the podnieś_on_defect jest Prawda, the
        defect jest podnieśd jako an error, otherwise the object oraz the defect are
        dalejed to register_defect.

        This method jest intended to be called by parsers that discover defects.
        The email package parsers always call it przy Defect instances.

        """
        jeżeli self.raise_on_defect:
            podnieś defect
        self.register_defect(obj, defect)

    def register_defect(self, obj, defect):
        """Record 'defect' on 'obj'.

        Called by handle_defect jeżeli podnieś_on_defect jest Nieprawda.  This method jest
        part of the Policy API so that Policy subclasses can implement custom
        defect handling.  The default implementation calls the append method of
        the defects attribute of obj.  The objects used by the email package by
        default that get dalejed to this method will always have a defects
        attribute przy an append method.

        """
        obj.defects.append(defect)

    def header_max_count(self, name):
        """Return the maximum allowed number of headers named 'name'.

        Called when a header jest added to a Message object.  If the returned
        value jest nie 0 albo Nic, oraz there are already a number of headers with
        the name 'name' equal to the value returned, a ValueError jest podnieśd.

        Because the default behavior of Message's __setitem__ jest to append the
        value to the list of headers, it jest easy to create duplicate headers
        without realizing it.  This method allows certain headers to be limited
        w the number of instances of that header that may be added to a
        Message programmatically.  (The limit jest nie observed by the parser,
        which will faithfully produce jako many headers jako exist w the message
        being parsed.)

        The default implementation returns Nic dla all header names.
        """
        zwróć Nic

    @abc.abstractmethod
    def header_source_parse(self, sourcelines):
        """Given a list of linesep terminated strings constituting the lines of
        a single header, zwróć the (name, value) tuple that should be stored
        w the model.  The input lines should retain their terminating linesep
        characters.  The lines dalejed w by the email package may contain
        surrogateescaped binary data.
        """
        podnieś NotImplementedError

    @abc.abstractmethod
    def header_store_parse(self, name, value):
        """Given the header name oraz the value provided by the application
        program, zwróć the (name, value) that should be stored w the model.
        """
        podnieś NotImplementedError

    @abc.abstractmethod
    def header_fetch_parse(self, name, value):
        """Given the header name oraz the value z the model, zwróć the value
        to be returned to the application program that jest requesting that
        header.  The value dalejed w by the email package may contain
        surrogateescaped binary data jeżeli the lines were parsed by a BytesParser.
        The returned value should nie contain any surrogateescaped data.

        """
        podnieś NotImplementedError

    @abc.abstractmethod
    def fold(self, name, value):
        """Given the header name oraz the value z the model, zwróć a string
        containing linesep characters that implement the folding of the header
        according to the policy controls.  The value dalejed w by the email
        package may contain surrogateescaped binary data jeżeli the lines were
        parsed by a BytesParser.  The returned value should nie contain any
        surrogateescaped data.

        """
        podnieś NotImplementedError

    @abc.abstractmethod
    def fold_binary(self, name, value):
        """Given the header name oraz the value z the model, zwróć binary
        data containing linesep characters that implement the folding of the
        header according to the policy controls.  The value dalejed w by the
        email package may contain surrogateescaped binary data.

        """
        podnieś NotImplementedError


@_extend_docstrings
klasa Compat32(Policy):

    """+
    This particular policy jest the backward compatibility Policy.  It
    replicates the behavior of the email package version 5.1.
    """

    mangle_from_ = Prawda

    def _sanitize_header(self, name, value):
        # If the header value contains surrogates, zwróć a Header using
        # the unknown-8bit charset to encode the bytes jako encoded words.
        jeżeli nie isinstance(value, str):
            # Assume it jest already a header object
            zwróć value
        jeżeli _has_surrogates(value):
            zwróć header.Header(value, charset=_charset.UNKNOWN8BIT,
                                 header_name=name)
        inaczej:
            zwróć value

    def header_source_parse(self, sourcelines):
        """+
        The name jest parsed jako everything up to the ':' oraz returned unmodified.
        The value jest determined by stripping leading whitespace off the
        remainder of the first line, joining all subsequent lines together, oraz
        stripping any trailing carriage zwróć albo linefeed characters.

        """
        name, value = sourcelines[0].split(':', 1)
        value = value.lstrip(' \t') + ''.join(sourcelines[1:])
        zwróć (name, value.rstrip('\r\n'))

    def header_store_parse(self, name, value):
        """+
        The name oraz value are returned unmodified.
        """
        zwróć (name, value)

    def header_fetch_parse(self, name, value):
        """+
        If the value contains binary data, it jest converted into a Header object
        using the unknown-8bit charset.  Otherwise it jest returned unmodified.
        """
        zwróć self._sanitize_header(name, value)

    def fold(self, name, value):
        """+
        Headers are folded using the Header folding algorithm, which preserves
        existing line przerwijs w the value, oraz wraps each resulting line to the
        max_line_length.  Non-ASCII binary data are CTE encoded using the
        unknown-8bit charset.

        """
        zwróć self._fold(name, value, sanitize=Prawda)

    def fold_binary(self, name, value):
        """+
        Headers are folded using the Header folding algorithm, which preserves
        existing line przerwijs w the value, oraz wraps each resulting line to the
        max_line_length.  If cte_type jest 7bit, non-ascii binary data jest CTE
        encoded using the unknown-8bit charset.  Otherwise the original source
        header jest used, przy its existing line przerwijs and/or binary data.

        """
        folded = self._fold(name, value, sanitize=self.cte_type=='7bit')
        zwróć folded.encode('ascii', 'surrogateescape')

    def _fold(self, name, value, sanitize):
        parts = []
        parts.append('%s: ' % name)
        jeżeli isinstance(value, str):
            jeżeli _has_surrogates(value):
                jeżeli sanitize:
                    h = header.Header(value,
                                      charset=_charset.UNKNOWN8BIT,
                                      header_name=name)
                inaczej:
                    # If we have raw 8bit data w a byte string, we have no idea
                    # what the encoding is.  There jest no safe way to split this
                    # string.  If it's ascii-subset, then we could do a normal
                    # ascii split, but jeżeli it's multibyte then we could przerwij the
                    # string.  There's no way to know so the least harm seems to
                    # be to nie split the string oraz risk it being too long.
                    parts.append(value)
                    h = Nic
            inaczej:
                h = header.Header(value, header_name=name)
        inaczej:
            # Assume it jest a Header-like object.
            h = value
        jeżeli h jest nie Nic:
            parts.append(h.encode(linesep=self.linesep,
                                  maxlinelen=self.max_line_length))
        parts.append(self.linesep)
        zwróć ''.join(parts)


compat32 = Compat32()
