"""Get useful information z live Python objects.

This module encapsulates the interface provided by the internal special
attributes (co_*, im_*, tb_*, etc.) w a friendlier fashion.
It also provides some help dla examining source code oraz klasa layout.

Here are some of the useful functions provided by this module:

    ismodule(), isclass(), ismethod(), isfunction(), isgeneratorfunction(),
        isgenerator(), istraceback(), isframe(), iscode(), isbuiltin(),
        isroutine() - check object types
    getmembers() - get members of an object that satisfy a given condition

    getfile(), getsourcefile(), getsource() - find an object's source code
    getdoc(), getcomments() - get documentation on an object
    getmodule() - determine the module that an object came from
    getclasstree() - arrange classes so jako to represent their hierarchy

    getargspec(), getargvalues(), getcallargs() - get info about function arguments
    getfullargspec() - same, przy support dla Python 3 features
    formatargspec(), formatargvalues() - format an argument spec
    getouterframes(), getinnerframes() - get info about frames
    currentframe() - get the current stack frame
    stack(), trace() - get info about frames on the stack albo w a traceback

    signature() - get a Signature object dla the callable
"""

# This module jest w the public domain.  No warranties.

__author__ = ('Ka-Ping Yee <ping@lfw.org>',
              'Yury Selivanov <yselivanov@sprymix.com>')

zaimportuj ast
zaimportuj dis
zaimportuj collections.abc
zaimportuj enum
zaimportuj importlib.machinery
zaimportuj itertools
zaimportuj linecache
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj tokenize
zaimportuj token
zaimportuj types
zaimportuj warnings
zaimportuj functools
zaimportuj builtins
z operator zaimportuj attrgetter
z collections zaimportuj namedtuple, OrderedDict

# Create constants dla the compiler flags w Include/code.h
# We try to get them z dis to avoid duplication
mod_dict = globals()
dla k, v w dis.COMPILER_FLAG_NAMES.items():
    mod_dict["CO_" + v] = k

# See Include/object.h
TPFLAGS_IS_ABSTRACT = 1 << 20

# ----------------------------------------------------------- type-checking
def ismodule(object):
    """Return true jeżeli the object jest a module.

    Module objects provide these attributes:
        __cached__      pathname to byte compiled file
        __doc__         documentation string
        __file__        filename (missing dla built-in modules)"""
    zwróć isinstance(object, types.ModuleType)

def isclass(object):
    """Return true jeżeli the object jest a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module w which this klasa was defined"""
    zwróć isinstance(object, type)

def ismethod(object):
    """Return true jeżeli the object jest an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name przy which this method was defined
        __func__        function object containing implementation of method
        __self__        instance to which this method jest bound"""
    zwróć isinstance(object, types.MethodType)

def ismethoddescriptor(object):
    """Return true jeżeli the object jest a method descriptor.

    But nie jeżeli ismethod() albo isclass() albo isfunction() are true.

    This jest new w Python 2.2, and, dla example, jest true of int.__add__.
    An object dalejing this test has a __get__ attribute but nie a __set__
    attribute, but beyond that the set of attributes varies.  __name__ jest
    usually sensible, oraz __doc__ often is.

    Methods implemented via descriptors that also dalej one of the other
    tests zwróć false z the ismethoddescriptor() test, simply because
    the other tests promise more -- you can, e.g., count on having the
    __func__ attribute (etc) when an object dalejes ismethod()."""
    jeżeli isclass(object) albo ismethod(object) albo isfunction(object):
        # mutual exclusion
        zwróć Nieprawda
    tp = type(object)
    zwróć hasattr(tp, "__get__") oraz nie hasattr(tp, "__set__")

def isdatadescriptor(object):
    """Return true jeżeli the object jest a data descriptor.

    Data descriptors have both a __get__ oraz a __set__ attribute.  Examples are
    properties (defined w Python) oraz getsets oraz members (defined w C).
    Typically, data descriptors will also have __name__ oraz __doc__ attributes
    (properties, getsets, oraz members have both of these attributes), but this
    jest nie guaranteed."""
    jeżeli isclass(object) albo ismethod(object) albo isfunction(object):
        # mutual exclusion
        zwróć Nieprawda
    tp = type(object)
    zwróć hasattr(tp, "__set__") oraz hasattr(tp, "__get__")

jeżeli hasattr(types, 'MemberDescriptorType'):
    # CPython oraz equivalent
    def ismemberdescriptor(object):
        """Return true jeżeli the object jest a member descriptor.

        Member descriptors are specialized descriptors defined w extension
        modules."""
        zwróć isinstance(object, types.MemberDescriptorType)
inaczej:
    # Other implementations
    def ismemberdescriptor(object):
        """Return true jeżeli the object jest a member descriptor.

        Member descriptors are specialized descriptors defined w extension
        modules."""
        zwróć Nieprawda

jeżeli hasattr(types, 'GetSetDescriptorType'):
    # CPython oraz equivalent
    def isgetsetdescriptor(object):
        """Return true jeżeli the object jest a getset descriptor.

        getset descriptors are specialized descriptors defined w extension
        modules."""
        zwróć isinstance(object, types.GetSetDescriptorType)
inaczej:
    # Other implementations
    def isgetsetdescriptor(object):
        """Return true jeżeli the object jest a getset descriptor.

        getset descriptors are specialized descriptors defined w extension
        modules."""
        zwróć Nieprawda

def isfunction(object):
    """Return true jeżeli the object jest a user-defined function.

    Function objects provide these attributes:
        __doc__         documentation string
        __name__        name przy which this function was defined
        __code__        code object containing compiled function bytecode
        __defaults__    tuple of any default values dla arguments
        __globals__     global namespace w which this function was defined
        __annotations__ dict of parameter annotations
        __kwdefaults__  dict of keyword only parameters przy defaults"""
    zwróć isinstance(object, types.FunctionType)

def isgeneratorfunction(object):
    """Return true jeżeli the object jest a user-defined generator function.

    Generator function objects provides same attributes jako functions.

    See help(isfunction) dla attributes listing."""
    zwróć bool((isfunction(object) albo ismethod(object)) oraz
                object.__code__.co_flags & CO_GENERATOR)

def iscoroutinefunction(object):
    """Return true jeżeli the object jest a coroutine function.

    Coroutine functions are defined przy "async def" syntax,
    albo generators decorated przy "types.coroutine".
    """
    zwróć bool((isfunction(object) albo ismethod(object)) oraz
                object.__code__.co_flags & CO_COROUTINE)

def isgenerator(object):
    """Return true jeżeli the object jest a generator.

    Generator objects provide these attributes:
        __iter__        defined to support iteration over container
        close           podnieśs a new GeneratorExit exception inside the
                        generator to terminate the iteration
        gi_code         code object
        gi_frame        frame object albo possibly Nic once the generator has
                        been exhausted
        gi_running      set to 1 when generator jest executing, 0 otherwise
        next            zwróć the next item z the container
        send            resumes the generator oraz "sends" a value that becomes
                        the result of the current uzyskaj-expression
        throw           used to podnieś an exception inside the generator"""
    zwróć isinstance(object, types.GeneratorType)

def iscoroutine(object):
    """Return true jeżeli the object jest a coroutine."""
    zwróć isinstance(object, types.CoroutineType)

def isawaitable(object):
    """Return true jest object can be dalejed to an ``await`` expression."""
    zwróć (isinstance(object, types.CoroutineType) albo
            isinstance(object, types.GeneratorType) oraz
                object.gi_code.co_flags & CO_ITERABLE_COROUTINE albo
            isinstance(object, collections.abc.Awaitable))

def istraceback(object):
    """Return true jeżeli the object jest a traceback.

    Traceback objects provide these attributes:
        tb_frame        frame object at this level
        tb_lasti        index of last attempted instruction w bytecode
        tb_lineno       current line number w Python source code
        tb_next         next inner traceback object (called by this level)"""
    zwróć isinstance(object, types.TracebackType)

def isframe(object):
    """Return true jeżeli the object jest a frame object.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed w this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction w bytecode
        f_lineno        current line number w Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function dla this frame, albo Nic"""
    zwróć isinstance(object, types.FrameType)

def iscode(object):
    """Return true jeżeli the object jest a code object.

    Code objects provide these attributes:
        co_argcount     number of arguments (nie including * albo ** args)
        co_code         string of raw compiled bytecode
        co_consts       tuple of constants used w the bytecode
        co_filename     name of file w which this code object was created
        co_firstlineno  number of first line w Python source code
        co_flags        bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg
        co_lnotab       encoded mapping of line numbers to bytecode indices
        co_name         name przy which this code object was defined
        co_names        tuple of names of local variables
        co_nlocals      number of local variables
        co_stacksize    virtual machine stack space required
        co_varnames     tuple of names of arguments oraz local variables"""
    zwróć isinstance(object, types.CodeType)

def isbuiltin(object):
    """Return true jeżeli the object jest a built-in function albo method.

    Built-in functions oraz methods provide these attributes:
        __doc__         documentation string
        __name__        original name of this function albo method
        __self__        instance to which a method jest bound, albo Nic"""
    zwróć isinstance(object, types.BuiltinFunctionType)

def isroutine(object):
    """Return true jeżeli the object jest any kind of function albo method."""
    zwróć (isbuiltin(object)
            albo isfunction(object)
            albo ismethod(object)
            albo ismethoddescriptor(object))

def isabstract(object):
    """Return true jeżeli the object jest an abstract base klasa (ABC)."""
    zwróć bool(isinstance(object, type) oraz object.__flags__ & TPFLAGS_IS_ABSTRACT)

def getmembers(object, predicate=Nic):
    """Return all members of an object jako (name, value) pairs sorted by name.
    Optionally, only zwróć members that satisfy a given predicate."""
    jeżeli isclass(object):
        mro = (object,) + getmro(object)
    inaczej:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names jeżeli object jest a class;
    # this may result w duplicate entries if, dla example, a virtual
    # attribute przy the same name jako a DynamicClassAttribute exists
    spróbuj:
        dla base w object.__bases__:
            dla k, v w base.__dict__.items():
                jeżeli isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    wyjąwszy AttributeError:
        dalej
    dla key w names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking w the __dict__.
        spróbuj:
            value = getattr(object, key)
            # handle the duplicate key
            jeżeli key w processed:
                podnieś AttributeError
        wyjąwszy AttributeError:
            dla base w mro:
                jeżeli key w base.__dict__:
                    value = base.__dict__[key]
                    przerwij
            inaczej:
                # could be a (currently) missing slot member, albo a buggy
                # __dir__; discard oraz move on
                kontynuuj
        jeżeli nie predicate albo predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    zwróć results

Attribute = namedtuple('Attribute', 'name kind defining_class object')

def classify_class_attrs(cls):
    """Return list of attribute-descriptor tuples.

    For each name w dir(cls), the zwróć list contains a 4-tuple
    przy these elements:

        0. The name (a string).

        1. The kind of attribute this is, one of these strings:
               'class method'    created via classmethod()
               'static method'   created via staticmethod()
               'property'        created via property()
               'method'          any other flavor of method albo descriptor
               'data'            nie a method

        2. The klasa which defined this attribute (a class).

        3. The object jako obtained by calling getattr; jeżeli this fails, albo jeżeli the
           resulting object does nie live anywhere w the class' mro (including
           metaclasses) then the object jest looked up w the defining class's
           dict (found by walking the mro).

    If one of the items w dir(cls) jest stored w the metaclass it will now
    be discovered oraz nie have Nic be listed jako the klasa w which it was
    defined.  Any items whose home klasa cannot be discovered are skipped.
    """

    mro = getmro(cls)
    metamro = getmro(type(cls)) # dla attributes stored w the metaclass
    metamro = tuple([cls dla cls w metamro jeżeli cls nie w (type, object)])
    class_bases = (cls,) + mro
    all_bases = class_bases + metamro
    names = dir(cls)
    # :dd any DynamicClassAttributes to the list of names;
    # this may result w duplicate entries if, dla example, a virtual
    # attribute przy the same name jako a DynamicClassAttribute exists.
    dla base w mro:
        dla k, v w base.__dict__.items():
            jeżeli isinstance(v, types.DynamicClassAttribute):
                names.append(k)
    result = []
    processed = set()

    dla name w names:
        # Get the object associated przy the name, oraz where it was defined.
        # Normal objects will be looked up przy both getattr oraz directly w
        # its class' dict (in case getattr fails [bug #1785], oraz also to look
        # dla a docstring).
        # For DynamicClassAttributes on the second dalej we only look w the
        # class's dict.
        #
        # Getting an obj z the __dict__ sometimes reveals more than
        # using getattr.  Static oraz klasa methods are dramatic examples.
        homecls = Nic
        get_obj = Nic
        dict_obj = Nic
        jeżeli name nie w processed:
            spróbuj:
                jeżeli name == '__dict__':
                    podnieś Exception("__dict__ jest special, don't want the proxy")
                get_obj = getattr(cls, name)
            wyjąwszy Exception jako exc:
                dalej
            inaczej:
                homecls = getattr(get_obj, "__objclass__", homecls)
                jeżeli homecls nie w class_bases:
                    # jeżeli the resulting object does nie live somewhere w the
                    # mro, drop it oraz search the mro manually
                    homecls = Nic
                    last_cls = Nic
                    # first look w the classes
                    dla srch_cls w class_bases:
                        srch_obj = getattr(srch_cls, name, Nic)
                        jeżeli srch_obj jest get_obj:
                            last_cls = srch_cls
                    # then check the metaclasses
                    dla srch_cls w metamro:
                        spróbuj:
                            srch_obj = srch_cls.__getattr__(cls, name)
                        wyjąwszy AttributeError:
                            kontynuuj
                        jeżeli srch_obj jest get_obj:
                            last_cls = srch_cls
                    jeżeli last_cls jest nie Nic:
                        homecls = last_cls
        dla base w all_bases:
            jeżeli name w base.__dict__:
                dict_obj = base.__dict__[name]
                jeżeli homecls nie w metamro:
                    homecls = base
                przerwij
        jeżeli homecls jest Nic:
            # unable to locate the attribute anywhere, most likely due to
            # buggy custom __dir__; discard oraz move on
            kontynuuj
        obj = get_obj jeżeli get_obj jest nie Nic inaczej dict_obj
        # Classify the object albo its descriptor.
        jeżeli isinstance(dict_obj, staticmethod):
            kind = "static method"
            obj = dict_obj
        albo_inaczej isinstance(dict_obj, classmethod):
            kind = "class method"
            obj = dict_obj
        albo_inaczej isinstance(dict_obj, property):
            kind = "property"
            obj = dict_obj
        albo_inaczej isroutine(obj):
            kind = "method"
        inaczej:
            kind = "data"
        result.append(Attribute(name, kind, homecls, obj))
        processed.add(name)
    zwróć result

# ----------------------------------------------------------- klasa helpers

def getmro(cls):
    "Return tuple of base classes (including cls) w method resolution order."
    zwróć cls.__mro__

# -------------------------------------------------------- function helpers

def unwrap(func, *, stop=Nic):
    """Get the object wrapped by *func*.

   Follows the chain of :attr:`__wrapped__` attributes returning the last
   object w the chain.

   *stop* jest an optional callback accepting an object w the wrapper chain
   jako its sole argument that allows the unwrapping to be terminated early if
   the callback returns a true value. If the callback never returns a true
   value, the last object w the chain jest returned jako usual. For example,
   :func:`signature` uses this to stop unwrapping jeżeli any object w the
   chain has a ``__signature__`` attribute defined.

   :exc:`ValueError` jest podnieśd jeżeli a cycle jest encountered.

    """
    jeżeli stop jest Nic:
        def _is_wrapper(f):
            zwróć hasattr(f, '__wrapped__')
    inaczej:
        def _is_wrapper(f):
            zwróć hasattr(f, '__wrapped__') oraz nie stop(f)
    f = func  # remember the original func dla error reporting
    memo = {id(f)} # Memoise by id to tolerate non-hashable objects
    dopóki _is_wrapper(func):
        func = func.__wrapped__
        id_func = id(func)
        jeżeli id_func w memo:
            podnieś ValueError('wrapper loop when unwrapping {!r}'.format(f))
        memo.add(id_func)
    zwróć func

# -------------------------------------------------- source code extraction
def indentsize(line):
    """Return the indent size, w spaces, at the start of a line of text."""
    expline = line.expandtabs()
    zwróć len(expline) - len(expline.lstrip())

def _findclass(func):
    cls = sys.modules.get(func.__module__)
    jeżeli cls jest Nic:
        zwróć Nic
    dla name w func.__qualname__.split('.')[:-1]:
        cls = getattr(cls, name)
    jeżeli nie isclass(cls):
        zwróć Nic
    zwróć cls

def _finddoc(obj):
    jeżeli isclass(obj):
        dla base w obj.__mro__:
            jeżeli base jest nie object:
                spróbuj:
                    doc = base.__doc__
                wyjąwszy AttributeError:
                    kontynuuj
                jeżeli doc jest nie Nic:
                    zwróć doc
        zwróć Nic

    jeżeli ismethod(obj):
        name = obj.__func__.__name__
        self = obj.__self__
        jeżeli (isclass(self) oraz
            getattr(getattr(self, name, Nic), '__func__') jest obj.__func__):
            # classmethod
            cls = self
        inaczej:
            cls = self.__class__
    albo_inaczej isfunction(obj):
        name = obj.__name__
        cls = _findclass(obj)
        jeżeli cls jest Nic albo getattr(cls, name) jest nie obj:
            zwróć Nic
    albo_inaczej isbuiltin(obj):
        name = obj.__name__
        self = obj.__self__
        jeżeli (isclass(self) oraz
            self.__qualname__ + '.' + name == obj.__qualname__):
            # classmethod
            cls = self
        inaczej:
            cls = self.__class__
    albo_inaczej ismethoddescriptor(obj) albo isdatadescriptor(obj):
        name = obj.__name__
        cls = obj.__objclass__
        jeżeli getattr(cls, name) jest nie obj:
            zwróć Nic
    albo_inaczej isinstance(obj, property):
        func = f.fget
        name = func.__name__
        cls = _findclass(func)
        jeżeli cls jest Nic albo getattr(cls, name) jest nie obj:
            zwróć Nic
    inaczej:
        zwróć Nic

    dla base w cls.__mro__:
        spróbuj:
            doc = getattr(base, name).__doc__
        wyjąwszy AttributeError:
            kontynuuj
        jeżeli doc jest nie Nic:
            zwróć doc
    zwróć Nic

def getdoc(object):
    """Get the documentation string dla an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up przy blocks of code, any whitespace than can be
    uniformly removed z the second line onwards jest removed."""
    spróbuj:
        doc = object.__doc__
    wyjąwszy AttributeError:
        zwróć Nic
    jeżeli doc jest Nic:
        spróbuj:
            doc = _finddoc(object)
        wyjąwszy (AttributeError, TypeError):
            zwróć Nic
    jeżeli nie isinstance(doc, str):
        zwróć Nic
    zwróć cleandoc(doc)

def cleandoc(doc):
    """Clean up indentation z docstrings.

    Any whitespace that can be uniformly removed z the second line
    onwards jest removed."""
    spróbuj:
        lines = doc.expandtabs().split('\n')
    wyjąwszy UnicodeError:
        zwróć Nic
    inaczej:
        # Find minimum indentation of any non-blank lines after first line.
        margin = sys.maxsize
        dla line w lines[1:]:
            content = len(line.lstrip())
            jeżeli content:
                indent = len(line) - content
                margin = min(margin, indent)
        # Remove indentation.
        jeżeli lines:
            lines[0] = lines[0].lstrip()
        jeżeli margin < sys.maxsize:
            dla i w range(1, len(lines)): lines[i] = lines[i][margin:]
        # Remove any trailing albo leading blank lines.
        dopóki lines oraz nie lines[-1]:
            lines.pop()
        dopóki lines oraz nie lines[0]:
            lines.pop(0)
        zwróć '\n'.join(lines)

def getfile(object):
    """Work out which source albo compiled file an object was defined in."""
    jeżeli ismodule(object):
        jeżeli hasattr(object, '__file__'):
            zwróć object.__file__
        podnieś TypeError('{!r} jest a built-in module'.format(object))
    jeżeli isclass(object):
        jeżeli hasattr(object, '__module__'):
            object = sys.modules.get(object.__module__)
            jeżeli hasattr(object, '__file__'):
                zwróć object.__file__
        podnieś TypeError('{!r} jest a built-in class'.format(object))
    jeżeli ismethod(object):
        object = object.__func__
    jeżeli isfunction(object):
        object = object.__code__
    jeżeli istraceback(object):
        object = object.tb_frame
    jeżeli isframe(object):
        object = object.f_code
    jeżeli iscode(object):
        zwróć object.co_filename
    podnieś TypeError('{!r} jest nie a module, class, method, '
                    'function, traceback, frame, albo code object'.format(object))

ModuleInfo = namedtuple('ModuleInfo', 'name suffix mode module_type')

def getmoduleinfo(path):
    """Get the module name, suffix, mode, oraz module type dla a given file."""
    warnings.warn('inspect.getmoduleinfo() jest deprecated', DeprecationWarning,
                  2)
    przy warnings.catch_warnings():
        warnings.simplefilter('ignore', PendingDeprecationWarning)
        zaimportuj imp
    filename = os.path.basename(path)
    suffixes = [(-len(suffix), suffix, mode, mtype)
                    dla suffix, mode, mtype w imp.get_suffixes()]
    suffixes.sort() # try longest suffixes first, w case they overlap
    dla neglen, suffix, mode, mtype w suffixes:
        jeżeli filename[neglen:] == suffix:
            zwróć ModuleInfo(filename[:neglen], suffix, mode, mtype)

def getmodulename(path):
    """Return the module name dla a given file, albo Nic."""
    fname = os.path.basename(path)
    # Check dla paths that look like an actual module file
    suffixes = [(-len(suffix), suffix)
                    dla suffix w importlib.machinery.all_suffixes()]
    suffixes.sort() # try longest suffixes first, w case they overlap
    dla neglen, suffix w suffixes:
        jeżeli fname.endswith(suffix):
            zwróć fname[:neglen]
    zwróć Nic

def getsourcefile(object):
    """Return the filename that can be used to locate an object's source.
    Return Nic jeżeli no way can be identified to get the source.
    """
    filename = getfile(object)
    all_bytecode_suffixes = importlib.machinery.DEBUG_BYTECODE_SUFFIXES[:]
    all_bytecode_suffixes += importlib.machinery.OPTIMIZED_BYTECODE_SUFFIXES[:]
    jeżeli any(filename.endswith(s) dla s w all_bytecode_suffixes):
        filename = (os.path.splitext(filename)[0] +
                    importlib.machinery.SOURCE_SUFFIXES[0])
    albo_inaczej any(filename.endswith(s) dla s w
                 importlib.machinery.EXTENSION_SUFFIXES):
        zwróć Nic
    jeżeli os.path.exists(filename):
        zwróć filename
    # only zwróć a non-existent filename jeżeli the module has a PEP 302 loader
    jeżeli getattr(getmodule(object, filename), '__loader__', Nic) jest nie Nic:
        zwróć filename
    # albo it jest w the linecache
    jeżeli filename w linecache.cache:
        zwróć filename

def getabsfile(object, _filename=Nic):
    """Return an absolute path to the source albo compiled file dla an object.

    The idea jest dla each object to have a unique origin, so this routine
    normalizes the result jako much jako possible."""
    jeżeli _filename jest Nic:
        _filename = getsourcefile(object) albo getfile(object)
    zwróć os.path.normcase(os.path.abspath(_filename))

modulesbyfile = {}
_filesbymodname = {}

def getmodule(object, _filename=Nic):
    """Return the module an object was defined in, albo Nic jeżeli nie found."""
    jeżeli ismodule(object):
        zwróć object
    jeżeli hasattr(object, '__module__'):
        zwróć sys.modules.get(object.__module__)
    # Try the filename to modulename cache
    jeżeli _filename jest nie Nic oraz _filename w modulesbyfile:
        zwróć sys.modules.get(modulesbyfile[_filename])
    # Try the cache again przy the absolute file name
    spróbuj:
        file = getabsfile(object, _filename)
    wyjąwszy TypeError:
        zwróć Nic
    jeżeli file w modulesbyfile:
        zwróć sys.modules.get(modulesbyfile[file])
    # Update the filename to module name cache oraz check yet again
    # Copy sys.modules w order to cope przy changes dopóki iterating
    dla modname, module w list(sys.modules.items()):
        jeżeli ismodule(module) oraz hasattr(module, '__file__'):
            f = module.__file__
            jeżeli f == _filesbymodname.get(modname, Nic):
                # Have already mapped this module, so skip it
                kontynuuj
            _filesbymodname[modname] = f
            f = getabsfile(module)
            # Always map to the name the module knows itself by
            modulesbyfile[f] = modulesbyfile[
                os.path.realpath(f)] = module.__name__
    jeżeli file w modulesbyfile:
        zwróć sys.modules.get(modulesbyfile[file])
    # Check the main module
    main = sys.modules['__main__']
    jeżeli nie hasattr(object, '__name__'):
        zwróć Nic
    jeżeli hasattr(main, object.__name__):
        mainobject = getattr(main, object.__name__)
        jeżeli mainobject jest object:
            zwróć main
    # Check builtins
    builtin = sys.modules['builtins']
    jeżeli hasattr(builtin, object.__name__):
        builtinobject = getattr(builtin, object.__name__)
        jeżeli builtinobject jest object:
            zwróć builtin

def findsource(object):
    """Return the entire source file oraz starting line number dla an object.

    The argument may be a module, class, method, function, traceback, frame,
    albo code object.  The source code jest returned jako a list of all the lines
    w the file oraz the line number indexes a line w that list.  An OSError
    jest podnieśd jeżeli the source code cannot be retrieved."""

    file = getsourcefile(object)
    jeżeli file:
        # Invalidate cache jeżeli needed.
        linecache.checkcache(file)
    inaczej:
        file = getfile(object)
        # Allow filenames w form of "<something>" to dalej through.
        # `doctest` monkeypatches `linecache` module to enable
        # inspection, so let `linecache.getlines` to be called.
        jeżeli nie (file.startswith('<') oraz file.endswith('>')):
            podnieś OSError('source code nie available')

    module = getmodule(object, file)
    jeżeli module:
        lines = linecache.getlines(file, module.__dict__)
    inaczej:
        lines = linecache.getlines(file)
    jeżeli nie lines:
        podnieś OSError('could nie get source code')

    jeżeli ismodule(object):
        zwróć lines, 0

    jeżeli isclass(object):
        name = object.__name__
        pat = re.compile(r'^(\s*)class\s*' + name + r'\b')
        # make some effort to find the best matching klasa definition:
        # use the one przy the least indentation, which jest the one
        # that's most probably nie inside a function definition.
        candidates = []
        dla i w range(len(lines)):
            match = pat.match(lines[i])
            jeżeli match:
                # jeżeli it's at toplevel, it's already the best one
                jeżeli lines[i][0] == 'c':
                    zwróć lines, i
                # inaczej add whitespace to candidate list
                candidates.append((match.group(1), i))
        jeżeli candidates:
            # this will sort by whitespace, oraz by line number,
            # less whitespace first
            candidates.sort()
            zwróć lines, candidates[0][1]
        inaczej:
            podnieś OSError('could nie find klasa definition')

    jeżeli ismethod(object):
        object = object.__func__
    jeżeli isfunction(object):
        object = object.__code__
    jeżeli istraceback(object):
        object = object.tb_frame
    jeżeli isframe(object):
        object = object.f_code
    jeżeli iscode(object):
        jeżeli nie hasattr(object, 'co_firstlineno'):
            podnieś OSError('could nie find function definition')
        lnum = object.co_firstlineno - 1
        pat = re.compile(r'^(\s*def\s)|(\s*async\s+def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)')
        dopóki lnum > 0:
            jeżeli pat.match(lines[lnum]): przerwij
            lnum = lnum - 1
        zwróć lines, lnum
    podnieś OSError('could nie find code object')

def getcomments(object):
    """Get lines of comments immediately preceding an object's source code.

    Returns Nic when source can't be found.
    """
    spróbuj:
        lines, lnum = findsource(object)
    wyjąwszy (OSError, TypeError):
        zwróć Nic

    jeżeli ismodule(object):
        # Look dla a comment block at the top of the file.
        start = 0
        jeżeli lines oraz lines[0][:2] == '#!': start = 1
        dopóki start < len(lines) oraz lines[start].strip() w ('', '#'):
            start = start + 1
        jeżeli start < len(lines) oraz lines[start][:1] == '#':
            comments = []
            end = start
            dopóki end < len(lines) oraz lines[end][:1] == '#':
                comments.append(lines[end].expandtabs())
                end = end + 1
            zwróć ''.join(comments)

    # Look dla a preceding block of comments at the same indentation.
    albo_inaczej lnum > 0:
        indent = indentsize(lines[lnum])
        end = lnum - 1
        jeżeli end >= 0 oraz lines[end].lstrip()[:1] == '#' oraz \
            indentsize(lines[end]) == indent:
            comments = [lines[end].expandtabs().lstrip()]
            jeżeli end > 0:
                end = end - 1
                comment = lines[end].expandtabs().lstrip()
                dopóki comment[:1] == '#' oraz indentsize(lines[end]) == indent:
                    comments[:0] = [comment]
                    end = end - 1
                    jeżeli end < 0: przerwij
                    comment = lines[end].expandtabs().lstrip()
            dopóki comments oraz comments[0].strip() == '#':
                comments[:1] = []
            dopóki comments oraz comments[-1].strip() == '#':
                comments[-1:] = []
            zwróć ''.join(comments)

klasa EndOfBlock(Exception): dalej

klasa BlockFinder:
    """Provide a tokeneater() method to detect the end of a code block."""
    def __init__(self):
        self.indent = 0
        self.islambda = Nieprawda
        self.started = Nieprawda
        self.passline = Nieprawda
        self.indecorator = Nieprawda
        self.decoratorhasargs = Nieprawda
        self.last = 1

    def tokeneater(self, type, token, srowcol, erowcol, line):
        jeżeli nie self.started oraz nie self.indecorator:
            # skip any decorators
            jeżeli token == "@":
                self.indecorator = Prawda
            # look dla the first "def", "class" albo "lambda"
            albo_inaczej token w ("def", "class", "lambda"):
                jeżeli token == "lambda":
                    self.islambda = Prawda
                self.started = Prawda
            self.passline = Prawda    # skip to the end of the line
        albo_inaczej token == "(":
            jeżeli self.indecorator:
                self.decoratorhasargs = Prawda
        albo_inaczej token == ")":
            jeżeli self.indecorator:
                self.indecorator = Nieprawda
                self.decoratorhasargs = Nieprawda
        albo_inaczej type == tokenize.NEWLINE:
            self.passline = Nieprawda   # stop skipping when a NEWLINE jest seen
            self.last = srowcol[0]
            jeżeli self.islambda:       # lambdas always end at the first NEWLINE
                podnieś EndOfBlock
            # hitting a NEWLINE when w a decorator without args
            # ends the decorator
            jeżeli self.indecorator oraz nie self.decoratorhasargs:
                self.indecorator = Nieprawda
        albo_inaczej self.passline:
            dalej
        albo_inaczej type == tokenize.INDENT:
            self.indent = self.indent + 1
            self.passline = Prawda
        albo_inaczej type == tokenize.DEDENT:
            self.indent = self.indent - 1
            # the end of matching indent/dedent pairs end a block
            # (niee that this only works dla "def"/"class" blocks,
            #  nie e.g. dla "if: inaczej:" albo "spróbuj: w_końcu:" blocks)
            jeżeli self.indent <= 0:
                podnieś EndOfBlock
        albo_inaczej self.indent == 0 oraz type nie w (tokenize.COMMENT, tokenize.NL):
            # any other token on the same indentation level end the previous
            # block jako well, wyjąwszy the pseudo-tokens COMMENT oraz NL.
            podnieś EndOfBlock

def getblock(lines):
    """Extract the block of code at the top of the given list of lines."""
    blockfinder = BlockFinder()
    spróbuj:
        tokens = tokenize.generate_tokens(iter(lines).__next__)
        dla _token w tokens:
            blockfinder.tokeneater(*_token)
    wyjąwszy (EndOfBlock, IndentationError):
        dalej
    zwróć lines[:blockfinder.last]

def getsourcelines(object):
    """Return a list of source lines oraz starting line number dla an object.

    The argument may be a module, class, method, function, traceback, frame,
    albo code object.  The source code jest returned jako a list of the lines
    corresponding to the object oraz the line number indicates where w the
    original source file the first line of code was found.  An OSError jest
    podnieśd jeżeli the source code cannot be retrieved."""
    object = unwrap(object)
    lines, lnum = findsource(object)

    jeżeli ismodule(object):
        zwróć lines, 0
    inaczej:
        zwróć getblock(lines[lnum:]), lnum + 1

def getsource(object):
    """Return the text of the source code dla an object.

    The argument may be a module, class, method, function, traceback, frame,
    albo code object.  The source code jest returned jako a single string.  An
    OSError jest podnieśd jeżeli the source code cannot be retrieved."""
    lines, lnum = getsourcelines(object)
    zwróć ''.join(lines)

# --------------------------------------------------- klasa tree extraction
def walktree(classes, children, parent):
    """Recursive helper function dla getclasstree()."""
    results = []
    classes.sort(key=attrgetter('__module__', '__name__'))
    dla c w classes:
        results.append((c, c.__bases__))
        jeżeli c w children:
            results.append(walktree(children[c], children, c))
    zwróć results

def getclasstree(classes, unique=Nieprawda):
    """Arrange the given list of classes into a hierarchy of nested lists.

    Where a nested list appears, it contains classes derived z the class
    whose entry immediately precedes the list.  Each entry jest a 2-tuple
    containing a klasa oraz a tuple of its base classes.  If the 'unique'
    argument jest true, exactly one entry appears w the returned structure
    dla each klasa w the given list.  Otherwise, classes using multiple
    inheritance oraz their descendants will appear multiple times."""
    children = {}
    roots = []
    dla c w classes:
        jeżeli c.__bases__:
            dla parent w c.__bases__:
                jeżeli nie parent w children:
                    children[parent] = []
                jeżeli c nie w children[parent]:
                    children[parent].append(c)
                jeżeli unique oraz parent w classes: przerwij
        albo_inaczej c nie w roots:
            roots.append(c)
    dla parent w children:
        jeżeli parent nie w classes:
            roots.append(parent)
    zwróć walktree(roots, children, Nic)

# ------------------------------------------------ argument list extraction
Arguments = namedtuple('Arguments', 'args, varargs, varkw')

def getargs(co):
    """Get information about the arguments accepted by a code object.

    Three things are returned: (args, varargs, varkw), where
    'args' jest the list of argument names. Keyword-only arguments are
    appended. 'varargs' oraz 'varkw' are the names of the * oraz **
    arguments albo Nic."""
    args, varargs, kwonlyargs, varkw = _getfullargs(co)
    zwróć Arguments(args + kwonlyargs, varargs, varkw)

def _getfullargs(co):
    """Get information about the arguments accepted by a code object.

    Four things are returned: (args, varargs, kwonlyargs, varkw), where
    'args' oraz 'kwonlyargs' are lists of argument names, oraz 'varargs'
    oraz 'varkw' are the names of the * oraz ** arguments albo Nic."""

    jeżeli nie iscode(co):
        podnieś TypeError('{!r} jest nie a code object'.format(co))

    nargs = co.co_argcount
    names = co.co_varnames
    nkwargs = co.co_kwonlyargcount
    args = list(names[:nargs])
    kwonlyargs = list(names[nargs:nargs+nkwargs])
    step = 0

    nargs += nkwargs
    varargs = Nic
    jeżeli co.co_flags & CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = Nic
    jeżeli co.co_flags & CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]
    zwróć args, varargs, kwonlyargs, varkw


ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

def getargspec(func):
    """Get the names oraz default values of a function's arguments.

    A tuple of four things jest returned: (args, varargs, keywords, defaults).
    'args' jest a list of the argument names, including keyword-only argument names.
    'varargs' oraz 'keywords' are the names of the * oraz ** arguments albo Nic.
    'defaults' jest an n-tuple of the default values of the last n arguments.

    Use the getfullargspec() API dla Python 3 code, jako annotations
    oraz keyword arguments are supported. getargspec() will podnieś ValueError
    jeżeli the func has either annotations albo keyword arguments.
    """
    warnings.warn("inspect.getargspec() jest deprecated, "
                  "use inspect.signature() instead", DeprecationWarning,
                  stacklevel=2)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = \
        getfullargspec(func)
    jeżeli kwonlyargs albo ann:
        podnieś ValueError("Function has keyword-only arguments albo annotations"
                         ", use getfullargspec() API which can support them")
    zwróć ArgSpec(args, varargs, varkw, defaults)

FullArgSpec = namedtuple('FullArgSpec',
    'args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations')

def getfullargspec(func):
    """Get the names oraz default values of a callable object's arguments.

    A tuple of seven things jest returned:
    (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults annotations).
    'args' jest a list of the argument names.
    'varargs' oraz 'varkw' are the names of the * oraz ** arguments albo Nic.
    'defaults' jest an n-tuple of the default values of the last n arguments.
    'kwonlyargs' jest a list of keyword-only argument names.
    'kwonlydefaults' jest a dictionary mapping names z kwonlyargs to defaults.
    'annotations' jest a dictionary mapping argument names to annotations.

    The first four items w the tuple correspond to getargspec().

    This function jest deprecated, use inspect.signature() instead.
    """

    spróbuj:
        # Re: `skip_bound_arg=Nieprawda`
        #
        # There jest a notable difference w behaviour between getfullargspec
        # oraz Signature: the former always returns 'self' parameter dla bound
        # methods, whereas the Signature always shows the actual calling
        # signature of the dalejed object.
        #
        # To simulate this behaviour, we "unbind" bound methods, to trick
        # inspect.signature to always zwróć their first parameter ("self",
        # usually)

        # Re: `follow_wrapper_chains=Nieprawda`
        #
        # getfullargspec() historically ignored __wrapped__ attributes,
        # so we ensure that remains the case w 3.3+

        sig = _signature_from_callable(func,
                                       follow_wrapper_chains=Nieprawda,
                                       skip_bound_arg=Nieprawda,
                                       sigcls=Signature)
    wyjąwszy Exception jako ex:
        # Most of the times 'signature' will podnieś ValueError.
        # But, it can also podnieś AttributeError, and, maybe something
        # inaczej. So to be fully backwards compatible, we catch all
        # possible exceptions here, oraz reraise a TypeError.
        podnieś TypeError('unsupported callable') z ex

    args = []
    varargs = Nic
    varkw = Nic
    kwonlyargs = []
    defaults = ()
    annotations = {}
    defaults = ()
    kwdefaults = {}

    jeżeli sig.return_annotation jest nie sig.empty:
        annotations['return'] = sig.return_annotation

    dla param w sig.parameters.values():
        kind = param.kind
        name = param.name

        jeżeli kind jest _POSITIONAL_ONLY:
            args.append(name)
        albo_inaczej kind jest _POSITIONAL_OR_KEYWORD:
            args.append(name)
            jeżeli param.default jest nie param.empty:
                defaults += (param.default,)
        albo_inaczej kind jest _VAR_POSITIONAL:
            varargs = name
        albo_inaczej kind jest _KEYWORD_ONLY:
            kwonlyargs.append(name)
            jeżeli param.default jest nie param.empty:
                kwdefaults[name] = param.default
        albo_inaczej kind jest _VAR_KEYWORD:
            varkw = name

        jeżeli param.annotation jest nie param.empty:
            annotations[name] = param.annotation

    jeżeli nie kwdefaults:
        # compatibility przy 'func.__kwdefaults__'
        kwdefaults = Nic

    jeżeli nie defaults:
        # compatibility przy 'func.__defaults__'
        defaults = Nic

    zwróć FullArgSpec(args, varargs, varkw, defaults,
                       kwonlyargs, kwdefaults, annotations)


ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')

def getargvalues(frame):
    """Get information about arguments dalejed into a particular frame.

    A tuple of four things jest returned: (args, varargs, varkw, locals).
    'args' jest a list of the argument names.
    'varargs' oraz 'varkw' are the names of the * oraz ** arguments albo Nic.
    'locals' jest the locals dictionary of the given frame."""
    args, varargs, varkw = getargs(frame.f_code)
    zwróć ArgInfo(args, varargs, varkw, frame.f_locals)

def formatannotation(annotation, base_module=Nic):
    jeżeli isinstance(annotation, type):
        jeżeli annotation.__module__ w ('builtins', base_module):
            zwróć annotation.__qualname__
        zwróć annotation.__module__+'.'+annotation.__qualname__
    zwróć repr(annotation)

def formatannotationrelativeto(object):
    module = getattr(object, '__module__', Nic)
    def _formatannotation(annotation):
        zwróć formatannotation(annotation, module)
    zwróć _formatannotation

def formatargspec(args, varargs=Nic, varkw=Nic, defaults=Nic,
                  kwonlyargs=(), kwonlydefaults={}, annotations={},
                  formatarg=str,
                  formatvarargs=lambda name: '*' + name,
                  formatvarkw=lambda name: '**' + name,
                  formatvalue=lambda value: '=' + repr(value),
                  formatreturns=lambda text: ' -> ' + text,
                  formatannotation=formatannotation):
    """Format an argument spec z the values returned by getargspec
    albo getfullargspec.

    The first seven arguments are (args, varargs, varkw, defaults,
    kwonlyargs, kwonlydefaults, annotations).  The other five arguments
    are the corresponding optional formatting functions that are called to
    turn names oraz values into strings.  The last argument jest an optional
    function to format the sequence of arguments."""
    def formatargandannotation(arg):
        result = formatarg(arg)
        jeżeli arg w annotations:
            result += ': ' + formatannotation(annotations[arg])
        zwróć result
    specs = []
    jeżeli defaults:
        firstdefault = len(args) - len(defaults)
    dla i, arg w enumerate(args):
        spec = formatargandannotation(arg)
        jeżeli defaults oraz i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)
    jeżeli varargs jest nie Nic:
        specs.append(formatvarargs(formatargandannotation(varargs)))
    inaczej:
        jeżeli kwonlyargs:
            specs.append('*')
    jeżeli kwonlyargs:
        dla kwonlyarg w kwonlyargs:
            spec = formatargandannotation(kwonlyarg)
            jeżeli kwonlydefaults oraz kwonlyarg w kwonlydefaults:
                spec += formatvalue(kwonlydefaults[kwonlyarg])
            specs.append(spec)
    jeżeli varkw jest nie Nic:
        specs.append(formatvarkw(formatargandannotation(varkw)))
    result = '(' + ', '.join(specs) + ')'
    jeżeli 'return' w annotations:
        result += formatreturns(formatannotation(annotations['return']))
    zwróć result

def formatargvalues(args, varargs, varkw, locals,
                    formatarg=str,
                    formatvarargs=lambda name: '*' + name,
                    formatvarkw=lambda name: '**' + name,
                    formatvalue=lambda value: '=' + repr(value)):
    """Format an argument spec z the 4 values returned by getargvalues.

    The first four arguments are (args, varargs, varkw, locals).  The
    next four arguments are the corresponding optional formatting functions
    that are called to turn names oraz values into strings.  The ninth
    argument jest an optional function to format the sequence of arguments."""
    def convert(name, locals=locals,
                formatarg=formatarg, formatvalue=formatvalue):
        zwróć formatarg(name) + formatvalue(locals[name])
    specs = []
    dla i w range(len(args)):
        specs.append(convert(args[i]))
    jeżeli varargs:
        specs.append(formatvarargs(varargs) + formatvalue(locals[varargs]))
    jeżeli varkw:
        specs.append(formatvarkw(varkw) + formatvalue(locals[varkw]))
    zwróć '(' + ', '.join(specs) + ')'

def _missing_arguments(f_name, argnames, pos, values):
    names = [repr(name) dla name w argnames jeżeli name nie w values]
    missing = len(names)
    jeżeli missing == 1:
        s = names[0]
    albo_inaczej missing == 2:
        s = "{} oraz {}".format(*names)
    inaczej:
        tail = ", {} oraz {}".format(*names[-2:])
        usuń names[-2:]
        s = ", ".join(names) + tail
    podnieś TypeError("%s() missing %i required %s argument%s: %s" %
                    (f_name, missing,
                      "positional" jeżeli pos inaczej "keyword-only",
                      "" jeżeli missing == 1 inaczej "s", s))

def _too_many(f_name, args, kwonly, varargs, defcount, given, values):
    atleast = len(args) - defcount
    kwonly_given = len([arg dla arg w kwonly jeżeli arg w values])
    jeżeli varargs:
        plural = atleast != 1
        sig = "at least %d" % (atleast,)
    albo_inaczej defcount:
        plural = Prawda
        sig = "z %d to %d" % (atleast, len(args))
    inaczej:
        plural = len(args) != 1
        sig = str(len(args))
    kwonly_sig = ""
    jeżeli kwonly_given:
        msg = " positional argument%s (and %d keyword-only argument%s)"
        kwonly_sig = (msg % ("s" jeżeli given != 1 inaczej "", kwonly_given,
                             "s" jeżeli kwonly_given != 1 inaczej ""))
    podnieś TypeError("%s() takes %s positional argument%s but %d%s %s given" %
            (f_name, sig, "s" jeżeli plural inaczej "", given, kwonly_sig,
             "was" jeżeli given == 1 oraz nie kwonly_given inaczej "were"))

def getcallargs(*func_and_positional, **named):
    """Get the mapping of arguments to values.

    A dict jest returned, przy keys the function argument names (including the
    names of the * oraz ** arguments, jeżeli any), oraz values the respective bound
    values z 'positional' oraz 'named'."""
    func = func_and_positional[0]
    positional = func_and_positional[1:]
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, ann = spec
    f_name = func.__name__
    arg2value = {}


    jeżeli ismethod(func) oraz func.__self__ jest nie Nic:
        # implicit 'self' (or 'cls' dla classmethods) argument
        positional = (func.__self__,) + positional
    num_pos = len(positional)
    num_args = len(args)
    num_defaults = len(defaults) jeżeli defaults inaczej 0

    n = min(num_pos, num_args)
    dla i w range(n):
        arg2value[args[i]] = positional[i]
    jeżeli varargs:
        arg2value[varargs] = tuple(positional[n:])
    possible_kwargs = set(args + kwonlyargs)
    jeżeli varkw:
        arg2value[varkw] = {}
    dla kw, value w named.items():
        jeżeli kw nie w possible_kwargs:
            jeżeli nie varkw:
                podnieś TypeError("%s() got an unexpected keyword argument %r" %
                                (f_name, kw))
            arg2value[varkw][kw] = value
            kontynuuj
        jeżeli kw w arg2value:
            podnieś TypeError("%s() got multiple values dla argument %r" %
                            (f_name, kw))
        arg2value[kw] = value
    jeżeli num_pos > num_args oraz nie varargs:
        _too_many(f_name, args, kwonlyargs, varargs, num_defaults,
                   num_pos, arg2value)
    jeżeli num_pos < num_args:
        req = args[:num_args - num_defaults]
        dla arg w req:
            jeżeli arg nie w arg2value:
                _missing_arguments(f_name, req, Prawda, arg2value)
        dla i, arg w enumerate(args[num_args - num_defaults:]):
            jeżeli arg nie w arg2value:
                arg2value[arg] = defaults[i]
    missing = 0
    dla kwarg w kwonlyargs:
        jeżeli kwarg nie w arg2value:
            jeżeli kwonlydefaults oraz kwarg w kwonlydefaults:
                arg2value[kwarg] = kwonlydefaults[kwarg]
            inaczej:
                missing += 1
    jeżeli missing:
        _missing_arguments(f_name, kwonlyargs, Nieprawda, arg2value)
    zwróć arg2value

ClosureVars = namedtuple('ClosureVars', 'nonlocals globals builtins unbound')

def getclosurevars(func):
    """
    Get the mapping of free variables to their current values.

    Returns a named tuple of dicts mapping the current nonlocal, global
    oraz builtin references jako seen by the body of the function. A final
    set of unbound names that could nie be resolved jest also provided.
    """

    jeżeli ismethod(func):
        func = func.__func__

    jeżeli nie isfunction(func):
        podnieś TypeError("'{!r}' jest nie a Python function".format(func))

    code = func.__code__
    # Nonlocal references are named w co_freevars oraz resolved
    # by looking them up w __closure__ by positional index
    jeżeli func.__closure__ jest Nic:
        nonlocal_vars = {}
    inaczej:
        nonlocal_vars = {
            var : cell.cell_contents
            dla var, cell w zip(code.co_freevars, func.__closure__)
       }

    # Global oraz builtin references are named w co_names oraz resolved
    # by looking them up w __globals__ albo __builtins__
    global_ns = func.__globals__
    builtin_ns = global_ns.get("__builtins__", builtins.__dict__)
    jeżeli ismodule(builtin_ns):
        builtin_ns = builtin_ns.__dict__
    global_vars = {}
    builtin_vars = {}
    unbound_names = set()
    dla name w code.co_names:
        jeżeli name w ("Nic", "Prawda", "Nieprawda"):
            # Because these used to be builtins instead of keywords, they
            # may still show up jako name references. We ignore them.
            kontynuuj
        spróbuj:
            global_vars[name] = global_ns[name]
        wyjąwszy KeyError:
            spróbuj:
                builtin_vars[name] = builtin_ns[name]
            wyjąwszy KeyError:
                unbound_names.add(name)

    zwróć ClosureVars(nonlocal_vars, global_vars,
                       builtin_vars, unbound_names)

# -------------------------------------------------- stack frame extraction

Traceback = namedtuple('Traceback', 'filename lineno function code_context index')

def getframeinfo(frame, context=1):
    """Get information about a frame albo traceback object.

    A tuple of five things jest returned: the filename, the line number of
    the current line, the function name, a list of lines of context from
    the source code, oraz the index of the current line within that list.
    The optional second argument specifies the number of lines of context
    to return, which are centered around the current line."""
    jeżeli istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    inaczej:
        lineno = frame.f_lineno
    jeżeli nie isframe(frame):
        podnieś TypeError('{!r} jest nie a frame albo traceback object'.format(frame))

    filename = getsourcefile(frame) albo getfile(frame)
    jeżeli context > 0:
        start = lineno - 1 - context//2
        spróbuj:
            lines, lnum = findsource(frame)
        wyjąwszy OSError:
            lines = index = Nic
        inaczej:
            start = max(start, 1)
            start = max(0, min(start, len(lines) - context))
            lines = lines[start:start+context]
            index = lineno - 1 - start
    inaczej:
        lines = index = Nic

    zwróć Traceback(filename, lineno, frame.f_code.co_name, lines, index)

def getlineno(frame):
    """Get the line number z a frame object, allowing dla optimization."""
    # FrameType.f_lineno jest now a descriptor that grovels co_lnotab
    zwróć frame.f_lineno

FrameInfo = namedtuple('FrameInfo', ('frame',) + Traceback._fields)

def getouterframes(frame, context=1):
    """Get a list of records dla a frame oraz all higher (calling) frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, oraz index within the context."""
    framelist = []
    dopóki frame:
        frameinfo = (frame,) + getframeinfo(frame, context)
        framelist.append(FrameInfo(*frameinfo))
        frame = frame.f_back
    zwróć framelist

def getinnerframes(tb, context=1):
    """Get a list of records dla a traceback's frame oraz all lower frames.

    Each record contains a frame object, filename, line number, function
    name, a list of lines of context, oraz index within the context."""
    framelist = []
    dopóki tb:
        frameinfo = (tb.tb_frame,) + getframeinfo(tb, context)
        framelist.append(FrameInfo(*frameinfo))
        tb = tb.tb_next
    zwróć framelist

def currentframe():
    """Return the frame of the caller albo Nic jeżeli this jest nie possible."""
    zwróć sys._getframe(1) jeżeli hasattr(sys, "_getframe") inaczej Nic

def stack(context=1):
    """Return a list of records dla the stack above the caller's frame."""
    zwróć getouterframes(sys._getframe(1), context)

def trace(context=1):
    """Return a list of records dla the stack below the current exception."""
    zwróć getinnerframes(sys.exc_info()[2], context)


# ------------------------------------------------ static version of getattr

_sentinel = object()

def _static_getmro(klass):
    zwróć type.__dict__['__mro__'].__get__(klass)

def _check_instance(obj, attr):
    instance_dict = {}
    spróbuj:
        instance_dict = object.__getattribute__(obj, "__dict__")
    wyjąwszy AttributeError:
        dalej
    zwróć dict.get(instance_dict, attr, _sentinel)


def _check_class(klass, attr):
    dla entry w _static_getmro(klass):
        jeżeli _shadowed_dict(type(entry)) jest _sentinel:
            spróbuj:
                zwróć entry.__dict__[attr]
            wyjąwszy KeyError:
                dalej
    zwróć _sentinel

def _is_type(obj):
    spróbuj:
        _static_getmro(obj)
    wyjąwszy TypeError:
        zwróć Nieprawda
    zwróć Prawda

def _shadowed_dict(klass):
    dict_attr = type.__dict__["__dict__"]
    dla entry w _static_getmro(klass):
        spróbuj:
            class_dict = dict_attr.__get__(entry)["__dict__"]
        wyjąwszy KeyError:
            dalej
        inaczej:
            jeżeli nie (type(class_dict) jest types.GetSetDescriptorType oraz
                    class_dict.__name__ == "__dict__" oraz
                    class_dict.__objclass__ jest entry):
                zwróć class_dict
    zwróć _sentinel

def getattr_static(obj, attr, default=_sentinel):
    """Retrieve attributes without triggering dynamic lookup via the
       descriptor protocol,  __getattr__ albo __getattribute__.

       Note: this function may nie be able to retrieve all attributes
       that getattr can fetch (like dynamically created attributes)
       oraz may find attributes that getattr can't (like descriptors
       that podnieś AttributeError). It can also zwróć descriptor objects
       instead of instance members w some cases. See the
       documentation dla details.
    """
    instance_result = _sentinel
    jeżeli nie _is_type(obj):
        klass = type(obj)
        dict_attr = _shadowed_dict(klass)
        jeżeli (dict_attr jest _sentinel albo
            type(dict_attr) jest types.MemberDescriptorType):
            instance_result = _check_instance(obj, attr)
    inaczej:
        klass = obj

    klass_result = _check_class(klass, attr)

    jeżeli instance_result jest nie _sentinel oraz klass_result jest nie _sentinel:
        jeżeli (_check_class(type(klass_result), '__get__') jest nie _sentinel oraz
            _check_class(type(klass_result), '__set__') jest nie _sentinel):
            zwróć klass_result

    jeżeli instance_result jest nie _sentinel:
        zwróć instance_result
    jeżeli klass_result jest nie _sentinel:
        zwróć klass_result

    jeżeli obj jest klass:
        # dla types we check the metaclass too
        dla entry w _static_getmro(type(klass)):
            jeżeli _shadowed_dict(type(entry)) jest _sentinel:
                spróbuj:
                    zwróć entry.__dict__[attr]
                wyjąwszy KeyError:
                    dalej
    jeżeli default jest nie _sentinel:
        zwróć default
    podnieś AttributeError(attr)


# ------------------------------------------------ generator introspection

GEN_CREATED = 'GEN_CREATED'
GEN_RUNNING = 'GEN_RUNNING'
GEN_SUSPENDED = 'GEN_SUSPENDED'
GEN_CLOSED = 'GEN_CLOSED'

def getgeneratorstate(generator):
    """Get current state of a generator-iterator.

    Possible states are:
      GEN_CREATED: Waiting to start execution.
      GEN_RUNNING: Currently being executed by the interpreter.
      GEN_SUSPENDED: Currently suspended at a uzyskaj expression.
      GEN_CLOSED: Execution has completed.
    """
    jeżeli generator.gi_running:
        zwróć GEN_RUNNING
    jeżeli generator.gi_frame jest Nic:
        zwróć GEN_CLOSED
    jeżeli generator.gi_frame.f_lasti == -1:
        zwróć GEN_CREATED
    zwróć GEN_SUSPENDED


def getgeneratorlocals(generator):
    """
    Get the mapping of generator local variables to their current values.

    A dict jest returned, przy the keys the local variable names oraz values the
    bound values."""

    jeżeli nie isgenerator(generator):
        podnieś TypeError("'{!r}' jest nie a Python generator".format(generator))

    frame = getattr(generator, "gi_frame", Nic)
    jeżeli frame jest nie Nic:
        zwróć generator.gi_frame.f_locals
    inaczej:
        zwróć {}


# ------------------------------------------------ coroutine introspection

CORO_CREATED = 'CORO_CREATED'
CORO_RUNNING = 'CORO_RUNNING'
CORO_SUSPENDED = 'CORO_SUSPENDED'
CORO_CLOSED = 'CORO_CLOSED'

def getcoroutinestate(coroutine):
    """Get current state of a coroutine object.

    Possible states are:
      CORO_CREATED: Waiting to start execution.
      CORO_RUNNING: Currently being executed by the interpreter.
      CORO_SUSPENDED: Currently suspended at an await expression.
      CORO_CLOSED: Execution has completed.
    """
    jeżeli coroutine.cr_running:
        zwróć CORO_RUNNING
    jeżeli coroutine.cr_frame jest Nic:
        zwróć CORO_CLOSED
    jeżeli coroutine.cr_frame.f_lasti == -1:
        zwróć CORO_CREATED
    zwróć CORO_SUSPENDED


def getcoroutinelocals(coroutine):
    """
    Get the mapping of coroutine local variables to their current values.

    A dict jest returned, przy the keys the local variable names oraz values the
    bound values."""
    frame = getattr(coroutine, "cr_frame", Nic)
    jeżeli frame jest nie Nic:
        zwróć frame.f_locals
    inaczej:
        zwróć {}


###############################################################################
### Function Signature Object (PEP 362)
###############################################################################


_WrapperDescriptor = type(type.__call__)
_MethodWrapper = type(all.__call__)
_ClassMethodWrapper = type(int.__dict__['from_bytes'])

_NonUserDefinedCallables = (_WrapperDescriptor,
                            _MethodWrapper,
                            _ClassMethodWrapper,
                            types.BuiltinFunctionType)


def _signature_get_user_defined_method(cls, method_name):
    """Private helper. Checks jeżeli ``cls`` has an attribute
    named ``method_name`` oraz returns it only jeżeli it jest a
    pure python function.
    """
    spróbuj:
        meth = getattr(cls, method_name)
    wyjąwszy AttributeError:
        zwróć
    inaczej:
        jeżeli nie isinstance(meth, _NonUserDefinedCallables):
            # Once '__signature__' will be added to 'C'-level
            # callables, this check won't be necessary
            zwróć meth


def _signature_get_partial(wrapped_sig, partial, extra_args=()):
    """Private helper to calculate how 'wrapped_sig' signature will
    look like after applying a 'functools.partial' object (or alike)
    on it.
    """

    old_params = wrapped_sig.parameters
    new_params = OrderedDict(old_params.items())

    partial_args = partial.args albo ()
    partial_keywords = partial.keywords albo {}

    jeżeli extra_args:
        partial_args = extra_args + partial_args

    spróbuj:
        ba = wrapped_sig.bind_partial(*partial_args, **partial_keywords)
    wyjąwszy TypeError jako ex:
        msg = 'partial object {!r} has incorrect arguments'.format(partial)
        podnieś ValueError(msg) z ex


    transform_to_kwonly = Nieprawda
    dla param_name, param w old_params.items():
        spróbuj:
            arg_value = ba.arguments[param_name]
        wyjąwszy KeyError:
            dalej
        inaczej:
            jeżeli param.kind jest _POSITIONAL_ONLY:
                # If positional-only parameter jest bound by partial,
                # it effectively disappears z the signature
                new_params.pop(param_name)
                kontynuuj

            jeżeli param.kind jest _POSITIONAL_OR_KEYWORD:
                jeżeli param_name w partial_keywords:
                    # This means that this parameter, oraz all parameters
                    # after it should be keyword-only (and var-positional
                    # should be removed). Here's why. Consider the following
                    # function:
                    #     foo(a, b, *args, c):
                    #         dalej
                    #
                    # "partial(foo, a='spam')" will have the following
                    # signature: "(*, a='spam', b, c)". Because attempting
                    # to call that partial przy "(10, 20)" arguments will
                    # podnieś a TypeError, saying that "a" argument received
                    # multiple values.
                    transform_to_kwonly = Prawda
                    # Set the new default value
                    new_params[param_name] = param.replace(default=arg_value)
                inaczej:
                    # was dalejed jako a positional argument
                    new_params.pop(param.name)
                    kontynuuj

            jeżeli param.kind jest _KEYWORD_ONLY:
                # Set the new default value
                new_params[param_name] = param.replace(default=arg_value)

        jeżeli transform_to_kwonly:
            assert param.kind jest nie _POSITIONAL_ONLY

            jeżeli param.kind jest _POSITIONAL_OR_KEYWORD:
                new_param = new_params[param_name].replace(kind=_KEYWORD_ONLY)
                new_params[param_name] = new_param
                new_params.move_to_end(param_name)
            albo_inaczej param.kind w (_KEYWORD_ONLY, _VAR_KEYWORD):
                new_params.move_to_end(param_name)
            albo_inaczej param.kind jest _VAR_POSITIONAL:
                new_params.pop(param.name)

    zwróć wrapped_sig.replace(parameters=new_params.values())


def _signature_bound_method(sig):
    """Private helper to transform signatures dla unbound
    functions to bound methods.
    """

    params = tuple(sig.parameters.values())

    jeżeli nie params albo params[0].kind w (_VAR_KEYWORD, _KEYWORD_ONLY):
        podnieś ValueError('invalid method signature')

    kind = params[0].kind
    jeżeli kind w (_POSITIONAL_OR_KEYWORD, _POSITIONAL_ONLY):
        # Drop first parameter:
        # '(p1, p2[, ...])' -> '(p2[, ...])'
        params = params[1:]
    inaczej:
        jeżeli kind jest nie _VAR_POSITIONAL:
            # Unless we add a new parameter type we never
            # get here
            podnieś ValueError('invalid argument type')
        # It's a var-positional parameter.
        # Do nothing. '(*args[, ...])' -> '(*args[, ...])'

    zwróć sig.replace(parameters=params)


def _signature_is_builtin(obj):
    """Private helper to test jeżeli `obj` jest a callable that might
    support Argument Clinic's __text_signature__ protocol.
    """
    zwróć (isbuiltin(obj) albo
            ismethoddescriptor(obj) albo
            isinstance(obj, _NonUserDefinedCallables) albo
            # Can't test 'isinstance(type)' here, jako it would
            # also be Prawda dla regular python classes
            obj w (type, object))


def _signature_is_functionlike(obj):
    """Private helper to test jeżeli `obj` jest a duck type of FunctionType.
    A good example of such objects are functions compiled with
    Cython, which have all attributes that a pure Python function
    would have, but have their code statically compiled.
    """

    jeżeli nie callable(obj) albo isclass(obj):
        # All function-like objects are obviously callables,
        # oraz nie classes.
        zwróć Nieprawda

    name = getattr(obj, '__name__', Nic)
    code = getattr(obj, '__code__', Nic)
    defaults = getattr(obj, '__defaults__', _void) # Important to use _void ...
    kwdefaults = getattr(obj, '__kwdefaults__', _void) # ... oraz nie Nic here
    annotations = getattr(obj, '__annotations__', Nic)

    zwróć (isinstance(code, types.CodeType) oraz
            isinstance(name, str) oraz
            (defaults jest Nic albo isinstance(defaults, tuple)) oraz
            (kwdefaults jest Nic albo isinstance(kwdefaults, dict)) oraz
            isinstance(annotations, dict))


def _signature_get_bound_param(spec):
    """ Private helper to get first parameter name z a
    __text_signature__ of a builtin method, which should
    be w the following format: '($param1, ...)'.
    Assumptions are that the first argument won't have
    a default value albo an annotation.
    """

    assert spec.startswith('($')

    pos = spec.find(',')
    jeżeli pos == -1:
        pos = spec.find(')')

    cpos = spec.find(':')
    assert cpos == -1 albo cpos > pos

    cpos = spec.find('=')
    assert cpos == -1 albo cpos > pos

    zwróć spec[2:pos]


def _signature_strip_non_python_syntax(signature):
    """
    Private helper function. Takes a signature w Argument Clinic's
    extended signature format.

    Returns a tuple of three things:
      * that signature re-rendered w standard Python syntax,
      * the index of the "self" parameter (generally 0), albo Nic if
        the function does nie have a "self" parameter, oraz
      * the index of the last "positional only" parameter,
        albo Nic jeżeli the signature has no positional-only parameters.
    """

    jeżeli nie signature:
        zwróć signature, Nic, Nic

    self_parameter = Nic
    last_positional_only = Nic

    lines = [l.encode('ascii') dla l w signature.split('\n')]
    generator = iter(lines).__next__
    token_stream = tokenize.tokenize(generator)

    delayed_comma = Nieprawda
    skip_next_comma = Nieprawda
    text = []
    add = text.append

    current_parameter = 0
    OP = token.OP
    ERRORTOKEN = token.ERRORTOKEN

    # token stream always starts przy ENCODING token, skip it
    t = next(token_stream)
    assert t.type == tokenize.ENCODING

    dla t w token_stream:
        type, string = t.type, t.string

        jeżeli type == OP:
            jeżeli string == ',':
                jeżeli skip_next_comma:
                    skip_next_comma = Nieprawda
                inaczej:
                    assert nie delayed_comma
                    delayed_comma = Prawda
                    current_parameter += 1
                kontynuuj

            jeżeli string == '/':
                assert nie skip_next_comma
                assert last_positional_only jest Nic
                skip_next_comma = Prawda
                last_positional_only = current_parameter - 1
                kontynuuj

        jeżeli (type == ERRORTOKEN) oraz (string == '$'):
            assert self_parameter jest Nic
            self_parameter = current_parameter
            kontynuuj

        jeżeli delayed_comma:
            delayed_comma = Nieprawda
            jeżeli nie ((type == OP) oraz (string == ')')):
                add(', ')
        add(string)
        jeżeli (string == ','):
            add(' ')
    clean_signature = ''.join(text)
    zwróć clean_signature, self_parameter, last_positional_only


def _signature_fromstr(cls, obj, s, skip_bound_arg=Prawda):
    """Private helper to parse content of '__text_signature__'
    oraz zwróć a Signature based on it.
    """

    Parameter = cls._parameter_cls

    clean_signature, self_parameter, last_positional_only = \
        _signature_strip_non_python_syntax(s)

    program = "def foo" + clean_signature + ": dalej"

    spróbuj:
        module = ast.parse(program)
    wyjąwszy SyntaxError:
        module = Nic

    jeżeli nie isinstance(module, ast.Module):
        podnieś ValueError("{!r} builtin has invalid signature".format(obj))

    f = module.body[0]

    parameters = []
    empty = Parameter.empty
    invalid = object()

    module = Nic
    module_dict = {}
    module_name = getattr(obj, '__module__', Nic)
    jeżeli module_name:
        module = sys.modules.get(module_name, Nic)
        jeżeli module:
            module_dict = module.__dict__
    sys_module_dict = sys.modules

    def parse_name(node):
        assert isinstance(node, ast.arg)
        jeżeli node.annotation != Nic:
            podnieś ValueError("Annotations are nie currently supported")
        zwróć node.arg

    def wrap_value(s):
        spróbuj:
            value = eval(s, module_dict)
        wyjąwszy NameError:
            spróbuj:
                value = eval(s, sys_module_dict)
            wyjąwszy NameError:
                podnieś RuntimeError()

        jeżeli isinstance(value, str):
            zwróć ast.Str(value)
        jeżeli isinstance(value, (int, float)):
            zwróć ast.Num(value)
        jeżeli isinstance(value, bytes):
            zwróć ast.Bytes(value)
        jeżeli value w (Prawda, Nieprawda, Nic):
            zwróć ast.NameConstant(value)
        podnieś RuntimeError()

    klasa RewriteSymbolics(ast.NodeTransformer):
        def visit_Attribute(self, node):
            a = []
            n = node
            dopóki isinstance(n, ast.Attribute):
                a.append(n.attr)
                n = n.value
            jeżeli nie isinstance(n, ast.Name):
                podnieś RuntimeError()
            a.append(n.id)
            value = ".".join(reversed(a))
            zwróć wrap_value(value)

        def visit_Name(self, node):
            jeżeli nie isinstance(node.ctx, ast.Load):
                podnieś ValueError()
            zwróć wrap_value(node.id)

    def p(name_node, default_node, default=empty):
        name = parse_name(name_node)
        jeżeli name jest invalid:
            zwróć Nic
        jeżeli default_node oraz default_node jest nie _empty:
            spróbuj:
                default_node = RewriteSymbolics().visit(default_node)
                o = ast.literal_eval(default_node)
            wyjąwszy ValueError:
                o = invalid
            jeżeli o jest invalid:
                zwróć Nic
            default = o jeżeli o jest nie invalid inaczej default
        parameters.append(Parameter(name, kind, default=default, annotation=empty))

    # non-keyword-only parameters
    args = reversed(f.args.args)
    defaults = reversed(f.args.defaults)
    iter = itertools.zip_longest(args, defaults, fillvalue=Nic)
    jeżeli last_positional_only jest nie Nic:
        kind = Parameter.POSITIONAL_ONLY
    inaczej:
        kind = Parameter.POSITIONAL_OR_KEYWORD
    dla i, (name, default) w enumerate(reversed(list(iter))):
        p(name, default)
        jeżeli i == last_positional_only:
            kind = Parameter.POSITIONAL_OR_KEYWORD

    # *args
    jeżeli f.args.vararg:
        kind = Parameter.VAR_POSITIONAL
        p(f.args.vararg, empty)

    # keyword-only arguments
    kind = Parameter.KEYWORD_ONLY
    dla name, default w zip(f.args.kwonlyargs, f.args.kw_defaults):
        p(name, default)

    # **kwargs
    jeżeli f.args.kwarg:
        kind = Parameter.VAR_KEYWORD
        p(f.args.kwarg, empty)

    jeżeli self_parameter jest nie Nic:
        # Possibly strip the bound argument:
        #    - We *always* strip first bound argument if
        #      it jest a module.
        #    - We don't strip first bound argument if
        #      skip_bound_arg jest Nieprawda.
        assert parameters
        _self = getattr(obj, '__self__', Nic)
        self_isbound = _self jest nie Nic
        self_ismodule = ismodule(_self)
        jeżeli self_isbound oraz (self_ismodule albo skip_bound_arg):
            parameters.pop(0)
        inaczej:
            # dla builtins, self parameter jest always positional-only!
            p = parameters[0].replace(kind=Parameter.POSITIONAL_ONLY)
            parameters[0] = p

    zwróć cls(parameters, return_annotation=cls.empty)


def _signature_from_builtin(cls, func, skip_bound_arg=Prawda):
    """Private helper function to get signature for
    builtin callables.
    """

    jeżeli nie _signature_is_builtin(func):
        podnieś TypeError("{!r} jest nie a Python builtin "
                        "function".format(func))

    s = getattr(func, "__text_signature__", Nic)
    jeżeli nie s:
        podnieś ValueError("no signature found dla builtin {!r}".format(func))

    zwróć _signature_fromstr(cls, func, s, skip_bound_arg)


def _signature_from_function(cls, func):
    """Private helper: constructs Signature dla the given python function."""

    is_duck_function = Nieprawda
    jeżeli nie isfunction(func):
        jeżeli _signature_is_functionlike(func):
            is_duck_function = Prawda
        inaczej:
            # If it's nie a pure Python function, oraz nie a duck type
            # of pure function:
            podnieś TypeError('{!r} jest nie a Python function'.format(func))

    Parameter = cls._parameter_cls

    # Parameter information.
    func_code = func.__code__
    pos_count = func_code.co_argcount
    arg_names = func_code.co_varnames
    positional = tuple(arg_names[:pos_count])
    keyword_only_count = func_code.co_kwonlyargcount
    keyword_only = arg_names[pos_count:(pos_count + keyword_only_count)]
    annotations = func.__annotations__
    defaults = func.__defaults__
    kwdefaults = func.__kwdefaults__

    jeżeli defaults:
        pos_default_count = len(defaults)
    inaczej:
        pos_default_count = 0

    parameters = []

    # Non-keyword-only parameters w/o defaults.
    non_default_count = pos_count - pos_default_count
    dla name w positional[:non_default_count]:
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_POSITIONAL_OR_KEYWORD))

    # ... w/ defaults.
    dla offset, name w enumerate(positional[non_default_count:]):
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_POSITIONAL_OR_KEYWORD,
                                    default=defaults[offset]))

    # *args
    jeżeli func_code.co_flags & CO_VARARGS:
        name = arg_names[pos_count + keyword_only_count]
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_VAR_POSITIONAL))

    # Keyword-only parameters.
    dla name w keyword_only:
        default = _empty
        jeżeli kwdefaults jest nie Nic:
            default = kwdefaults.get(name, _empty)

        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_KEYWORD_ONLY,
                                    default=default))
    # **kwargs
    jeżeli func_code.co_flags & CO_VARKEYWORDS:
        index = pos_count + keyword_only_count
        jeżeli func_code.co_flags & CO_VARARGS:
            index += 1

        name = arg_names[index]
        annotation = annotations.get(name, _empty)
        parameters.append(Parameter(name, annotation=annotation,
                                    kind=_VAR_KEYWORD))

    # Is 'func' jest a pure Python function - don't validate the
    # parameters list (dla correct order oraz defaults), it should be OK.
    zwróć cls(parameters,
               return_annotation=annotations.get('return', _empty),
               __validate_parameters__=is_duck_function)


def _signature_from_callable(obj, *,
                             follow_wrapper_chains=Prawda,
                             skip_bound_arg=Prawda,
                             sigcls):

    """Private helper function to get signature dla arbitrary
    callable objects.
    """

    jeżeli nie callable(obj):
        podnieś TypeError('{!r} jest nie a callable object'.format(obj))

    jeżeli isinstance(obj, types.MethodType):
        # In this case we skip the first parameter of the underlying
        # function (usually `self` albo `cls`).
        sig = _signature_from_callable(
            obj.__func__,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls)

        jeżeli skip_bound_arg:
            zwróć _signature_bound_method(sig)
        inaczej:
            zwróć sig

    # Was this function wrapped by a decorator?
    jeżeli follow_wrapper_chains:
        obj = unwrap(obj, stop=(lambda f: hasattr(f, "__signature__")))
        jeżeli isinstance(obj, types.MethodType):
            # If the unwrapped object jest a *method*, we might want to
            # skip its first parameter (self).
            # See test_signature_wrapped_bound_method dla details.
            zwróć _signature_from_callable(
                obj,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

    spróbuj:
        sig = obj.__signature__
    wyjąwszy AttributeError:
        dalej
    inaczej:
        jeżeli sig jest nie Nic:
            jeżeli nie isinstance(sig, Signature):
                podnieś TypeError(
                    'unexpected object {!r} w __signature__ '
                    'attribute'.format(sig))
            zwróć sig

    spróbuj:
        partialmethod = obj._partialmethod
    wyjąwszy AttributeError:
        dalej
    inaczej:
        jeżeli isinstance(partialmethod, functools.partialmethod):
            # Unbound partialmethod (see functools.partialmethod)
            # This means, that we need to calculate the signature
            # jako jeżeli it's a regular partial object, but taking into
            # account that the first positional argument
            # (usually `self`, albo `cls`) will nie be dalejed
            # automatically (as dla boundmethods)

            wrapped_sig = _signature_from_callable(
                partialmethod.func,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)

            sig = _signature_get_partial(wrapped_sig, partialmethod, (Nic,))

            first_wrapped_param = tuple(wrapped_sig.parameters.values())[0]
            new_params = (first_wrapped_param,) + tuple(sig.parameters.values())

            zwróć sig.replace(parameters=new_params)

    jeżeli isfunction(obj) albo _signature_is_functionlike(obj):
        # If it's a pure Python function, albo an object that jest duck type
        # of a Python function (Cython functions, dla instance), then:
        zwróć _signature_from_function(sigcls, obj)

    jeżeli _signature_is_builtin(obj):
        zwróć _signature_from_builtin(sigcls, obj,
                                       skip_bound_arg=skip_bound_arg)

    jeżeli isinstance(obj, functools.partial):
        wrapped_sig = _signature_from_callable(
            obj.func,
            follow_wrapper_chains=follow_wrapper_chains,
            skip_bound_arg=skip_bound_arg,
            sigcls=sigcls)
        zwróć _signature_get_partial(wrapped_sig, obj)

    sig = Nic
    jeżeli isinstance(obj, type):
        # obj jest a klasa albo a metaclass

        # First, let's see jeżeli it has an overloaded __call__ defined
        # w its metaclass
        call = _signature_get_user_defined_method(type(obj), '__call__')
        jeżeli call jest nie Nic:
            sig = _signature_from_callable(
                call,
                follow_wrapper_chains=follow_wrapper_chains,
                skip_bound_arg=skip_bound_arg,
                sigcls=sigcls)
        inaczej:
            # Now we check jeżeli the 'obj' klasa has a '__new__' method
            new = _signature_get_user_defined_method(obj, '__new__')
            jeżeli new jest nie Nic:
                sig = _signature_from_callable(
                    new,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            inaczej:
                # Finally, we should have at least __init__ implemented
                init = _signature_get_user_defined_method(obj, '__init__')
                jeżeli init jest nie Nic:
                    sig = _signature_from_callable(
                        init,
                        follow_wrapper_chains=follow_wrapper_chains,
                        skip_bound_arg=skip_bound_arg,
                        sigcls=sigcls)

        jeżeli sig jest Nic:
            # At this point we know, that `obj` jest a class, przy no user-
            # defined '__init__', '__new__', albo class-level '__call__'

            dla base w obj.__mro__[:-1]:
                # Since '__text_signature__' jest implemented jako a
                # descriptor that extracts text signature z the
                # klasa docstring, jeżeli 'obj' jest derived z a builtin
                # class, its own '__text_signature__' may be 'Nic'.
                # Therefore, we go through the MRO (wyjąwszy the last
                # klasa w there, which jest 'object') to find the first
                # klasa przy non-empty text signature.
                spróbuj:
                    text_sig = base.__text_signature__
                wyjąwszy AttributeError:
                    dalej
                inaczej:
                    jeżeli text_sig:
                        # If 'obj' klasa has a __text_signature__ attribute:
                        # zwróć a signature based on it
                        zwróć _signature_fromstr(sigcls, obj, text_sig)

            # No '__text_signature__' was found dla the 'obj' class.
            # Last option jest to check jeżeli its '__init__' jest
            # object.__init__ albo type.__init__.
            jeżeli type nie w obj.__mro__:
                # We have a klasa (nie metaclass), but no user-defined
                # __init__ albo __new__ dla it
                jeżeli (obj.__init__ jest object.__init__ oraz
                    obj.__new__ jest object.__new__):
                    # Return a signature of 'object' builtin.
                    zwróć signature(object)
                inaczej:
                    podnieś ValueError(
                        'no signature found dla builtin type {!r}'.format(obj))

    albo_inaczej nie isinstance(obj, _NonUserDefinedCallables):
        # An object przy __call__
        # We also check that the 'obj' jest nie an instance of
        # _WrapperDescriptor albo _MethodWrapper to avoid
        # infinite recursion (and even potential segfault)
        call = _signature_get_user_defined_method(type(obj), '__call__')
        jeżeli call jest nie Nic:
            spróbuj:
                sig = _signature_from_callable(
                    call,
                    follow_wrapper_chains=follow_wrapper_chains,
                    skip_bound_arg=skip_bound_arg,
                    sigcls=sigcls)
            wyjąwszy ValueError jako ex:
                msg = 'no signature found dla {!r}'.format(obj)
                podnieś ValueError(msg) z ex

    jeżeli sig jest nie Nic:
        # For classes oraz objects we skip the first parameter of their
        # __call__, __new__, albo __init__ methods
        jeżeli skip_bound_arg:
            zwróć _signature_bound_method(sig)
        inaczej:
            zwróć sig

    jeżeli isinstance(obj, types.BuiltinFunctionType):
        # Raise a nicer error message dla builtins
        msg = 'no signature found dla builtin function {!r}'.format(obj)
        podnieś ValueError(msg)

    podnieś ValueError('callable {!r} jest nie supported by signature'.format(obj))


klasa _void:
    """A private marker - used w Parameter & Signature."""


klasa _empty:
    """Marker object dla Signature.empty oraz Parameter.empty."""


klasa _ParameterKind(enum.IntEnum):
    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4

    def __str__(self):
        zwróć self._name_


_POSITIONAL_ONLY         = _ParameterKind.POSITIONAL_ONLY
_POSITIONAL_OR_KEYWORD   = _ParameterKind.POSITIONAL_OR_KEYWORD
_VAR_POSITIONAL          = _ParameterKind.VAR_POSITIONAL
_KEYWORD_ONLY            = _ParameterKind.KEYWORD_ONLY
_VAR_KEYWORD             = _ParameterKind.VAR_KEYWORD


klasa Parameter:
    """Represents a parameter w a function signature.

    Has the following public attributes:

    * name : str
        The name of the parameter jako a string.
    * default : object
        The default value dla the parameter jeżeli specified.  If the
        parameter has no default value, this attribute jest set to
        `Parameter.empty`.
    * annotation
        The annotation dla the parameter jeżeli specified.  If the
        parameter has no annotation, this attribute jest set to
        `Parameter.empty`.
    * kind : str
        Describes how argument values are bound to the parameter.
        Possible values: `Parameter.POSITIONAL_ONLY`,
        `Parameter.POSITIONAL_OR_KEYWORD`, `Parameter.VAR_POSITIONAL`,
        `Parameter.KEYWORD_ONLY`, `Parameter.VAR_KEYWORD`.
    """

    __slots__ = ('_name', '_kind', '_default', '_annotation')

    POSITIONAL_ONLY         = _POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD   = _POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL          = _VAR_POSITIONAL
    KEYWORD_ONLY            = _KEYWORD_ONLY
    VAR_KEYWORD             = _VAR_KEYWORD

    empty = _empty

    def __init__(self, name, kind, *, default=_empty, annotation=_empty):

        jeżeli kind nie w (_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD,
                        _VAR_POSITIONAL, _KEYWORD_ONLY, _VAR_KEYWORD):
            podnieś ValueError("invalid value dla 'Parameter.kind' attribute")
        self._kind = kind

        jeżeli default jest nie _empty:
            jeżeli kind w (_VAR_POSITIONAL, _VAR_KEYWORD):
                msg = '{} parameters cannot have default values'.format(kind)
                podnieś ValueError(msg)
        self._default = default
        self._annotation = annotation

        jeżeli name jest _empty:
            podnieś ValueError('name jest a required attribute dla Parameter')

        jeżeli nie isinstance(name, str):
            podnieś TypeError("name must be a str, nie a {!r}".format(name))

        jeżeli nie name.isidentifier():
            podnieś ValueError('{!r} jest nie a valid parameter name'.format(name))

        self._name = name

    def __reduce__(self):
        zwróć (type(self),
                (self._name, self._kind),
                {'_default': self._default,
                 '_annotation': self._annotation})

    def __setstate__(self, state):
        self._default = state['_default']
        self._annotation = state['_annotation']

    @property
    def name(self):
        zwróć self._name

    @property
    def default(self):
        zwróć self._default

    @property
    def annotation(self):
        zwróć self._annotation

    @property
    def kind(self):
        zwróć self._kind

    def replace(self, *, name=_void, kind=_void,
                annotation=_void, default=_void):
        """Creates a customized copy of the Parameter."""

        jeżeli name jest _void:
            name = self._name

        jeżeli kind jest _void:
            kind = self._kind

        jeżeli annotation jest _void:
            annotation = self._annotation

        jeżeli default jest _void:
            default = self._default

        zwróć type(self)(name, kind, default=default, annotation=annotation)

    def __str__(self):
        kind = self.kind
        formatted = self._name

        # Add annotation oraz default value
        jeżeli self._annotation jest nie _empty:
            formatted = '{}:{}'.format(formatted,
                                       formatannotation(self._annotation))

        jeżeli self._default jest nie _empty:
            formatted = '{}={}'.format(formatted, repr(self._default))

        jeżeli kind == _VAR_POSITIONAL:
            formatted = '*' + formatted
        albo_inaczej kind == _VAR_KEYWORD:
            formatted = '**' + formatted

        zwróć formatted

    def __repr__(self):
        zwróć '<{} "{}">'.format(self.__class__.__name__, self)

    def __hash__(self):
        zwróć hash((self.name, self.kind, self.annotation, self.default))

    def __eq__(self, other):
        jeżeli self jest other:
            zwróć Prawda
        jeżeli nie isinstance(other, Parameter):
            zwróć NotImplemented
        zwróć (self._name == other._name oraz
                self._kind == other._kind oraz
                self._default == other._default oraz
                self._annotation == other._annotation)


klasa BoundArguments:
    """Result of `Signature.bind` call.  Holds the mapping of arguments
    to the function's parameters.

    Has the following public attributes:

    * arguments : OrderedDict
        An ordered mutable mapping of parameters' names to arguments' values.
        Does nie contain arguments' default values.
    * signature : Signature
        The Signature object that created this instance.
    * args : tuple
        Tuple of positional arguments values.
    * kwargs : dict
        Dict of keyword arguments values.
    """

    __slots__ = ('arguments', '_signature', '__weakref__')

    def __init__(self, signature, arguments):
        self.arguments = arguments
        self._signature = signature

    @property
    def signature(self):
        zwróć self._signature

    @property
    def args(self):
        args = []
        dla param_name, param w self._signature.parameters.items():
            jeżeli param.kind w (_VAR_KEYWORD, _KEYWORD_ONLY):
                przerwij

            spróbuj:
                arg = self.arguments[param_name]
            wyjąwszy KeyError:
                # We're done here. Other arguments
                # will be mapped w 'BoundArguments.kwargs'
                przerwij
            inaczej:
                jeżeli param.kind == _VAR_POSITIONAL:
                    # *args
                    args.extend(arg)
                inaczej:
                    # plain argument
                    args.append(arg)

        zwróć tuple(args)

    @property
    def kwargs(self):
        kwargs = {}
        kwargs_started = Nieprawda
        dla param_name, param w self._signature.parameters.items():
            jeżeli nie kwargs_started:
                jeżeli param.kind w (_VAR_KEYWORD, _KEYWORD_ONLY):
                    kwargs_started = Prawda
                inaczej:
                    jeżeli param_name nie w self.arguments:
                        kwargs_started = Prawda
                        kontynuuj

            jeżeli nie kwargs_started:
                kontynuuj

            spróbuj:
                arg = self.arguments[param_name]
            wyjąwszy KeyError:
                dalej
            inaczej:
                jeżeli param.kind == _VAR_KEYWORD:
                    # **kwargs
                    kwargs.update(arg)
                inaczej:
                    # plain keyword argument
                    kwargs[param_name] = arg

        zwróć kwargs

    def apply_defaults(self):
        """Set default values dla missing arguments.

        For variable-positional arguments (*args) the default jest an
        empty tuple.

        For variable-keyword arguments (**kwargs) the default jest an
        empty dict.
        """
        arguments = self.arguments
        jeżeli nie arguments:
            zwróć
        new_arguments = []
        dla name, param w self._signature.parameters.items():
            spróbuj:
                new_arguments.append((name, arguments[name]))
            wyjąwszy KeyError:
                jeżeli param.default jest nie _empty:
                    val = param.default
                albo_inaczej param.kind jest _VAR_POSITIONAL:
                    val = ()
                albo_inaczej param.kind jest _VAR_KEYWORD:
                    val = {}
                inaczej:
                    # This BoundArguments was likely produced by
                    # Signature.bind_partial().
                    kontynuuj
                new_arguments.append((name, val))
        self.arguments = OrderedDict(new_arguments)

    def __eq__(self, other):
        jeżeli self jest other:
            zwróć Prawda
        jeżeli nie isinstance(other, BoundArguments):
            zwróć NotImplemented
        zwróć (self.signature == other.signature oraz
                self.arguments == other.arguments)

    def __setstate__(self, state):
        self._signature = state['_signature']
        self.arguments = state['arguments']

    def __getstate__(self):
        zwróć {'_signature': self._signature, 'arguments': self.arguments}

    def __repr__(self):
        args = []
        dla arg, value w self.arguments.items():
            args.append('{}={!r}'.format(arg, value))
        zwróć '<{} ({})>'.format(self.__class__.__name__, ', '.join(args))


klasa Signature:
    """A Signature object represents the overall signature of a function.
    It stores a Parameter object dla each parameter accepted by the
    function, jako well jako information specific to the function itself.

    A Signature object has the following public attributes oraz methods:

    * parameters : OrderedDict
        An ordered mapping of parameters' names to the corresponding
        Parameter objects (keyword-only arguments are w the same order
        jako listed w `code.co_varnames`).
    * return_annotation : object
        The annotation dla the zwróć type of the function jeżeli specified.
        If the function has no annotation dla its zwróć type, this
        attribute jest set to `Signature.empty`.
    * bind(*args, **kwargs) -> BoundArguments
        Creates a mapping z positional oraz keyword arguments to
        parameters.
    * bind_partial(*args, **kwargs) -> BoundArguments
        Creates a partial mapping z positional oraz keyword arguments
        to parameters (simulating 'functools.partial' behavior.)
    """

    __slots__ = ('_return_annotation', '_parameters')

    _parameter_cls = Parameter
    _bound_arguments_cls = BoundArguments

    empty = _empty

    def __init__(self, parameters=Nic, *, return_annotation=_empty,
                 __validate_parameters__=Prawda):
        """Constructs Signature z the given list of Parameter
        objects oraz 'return_annotation'.  All arguments are optional.
        """

        jeżeli parameters jest Nic:
            params = OrderedDict()
        inaczej:
            jeżeli __validate_parameters__:
                params = OrderedDict()
                top_kind = _POSITIONAL_ONLY
                kind_defaults = Nieprawda

                dla idx, param w enumerate(parameters):
                    kind = param.kind
                    name = param.name

                    jeżeli kind < top_kind:
                        msg = 'wrong parameter order: {!r} before {!r}'
                        msg = msg.format(top_kind, kind)
                        podnieś ValueError(msg)
                    albo_inaczej kind > top_kind:
                        kind_defaults = Nieprawda
                        top_kind = kind

                    jeżeli kind w (_POSITIONAL_ONLY, _POSITIONAL_OR_KEYWORD):
                        jeżeli param.default jest _empty:
                            jeżeli kind_defaults:
                                # No default dla this parameter, but the
                                # previous parameter of the same kind had
                                # a default
                                msg = 'non-default argument follows default ' \
                                      'argument'
                                podnieś ValueError(msg)
                        inaczej:
                            # There jest a default dla this parameter.
                            kind_defaults = Prawda

                    jeżeli name w params:
                        msg = 'duplicate parameter name: {!r}'.format(name)
                        podnieś ValueError(msg)

                    params[name] = param
            inaczej:
                params = OrderedDict(((param.name, param)
                                                dla param w parameters))

        self._parameters = types.MappingProxyType(params)
        self._return_annotation = return_annotation

    @classmethod
    def from_function(cls, func):
        """Constructs Signature dla the given python function."""

        warnings.warn("inspect.Signature.from_function() jest deprecated, "
                      "use Signature.from_callable()",
                      DeprecationWarning, stacklevel=2)
        zwróć _signature_from_function(cls, func)

    @classmethod
    def from_builtin(cls, func):
        """Constructs Signature dla the given builtin function."""

        warnings.warn("inspect.Signature.from_builtin() jest deprecated, "
                      "use Signature.from_callable()",
                      DeprecationWarning, stacklevel=2)
        zwróć _signature_from_builtin(cls, func)

    @classmethod
    def from_callable(cls, obj, *, follow_wrapped=Prawda):
        """Constructs Signature dla the given callable object."""
        zwróć _signature_from_callable(obj, sigcls=cls,
                                        follow_wrapper_chains=follow_wrapped)

    @property
    def parameters(self):
        zwróć self._parameters

    @property
    def return_annotation(self):
        zwróć self._return_annotation

    def replace(self, *, parameters=_void, return_annotation=_void):
        """Creates a customized copy of the Signature.
        Pass 'parameters' and/or 'return_annotation' arguments
        to override them w the new copy.
        """

        jeżeli parameters jest _void:
            parameters = self.parameters.values()

        jeżeli return_annotation jest _void:
            return_annotation = self._return_annotation

        zwróć type(self)(parameters,
                          return_annotation=return_annotation)

    def _hash_basis(self):
        params = tuple(param dla param w self.parameters.values()
                             jeżeli param.kind != _KEYWORD_ONLY)

        kwo_params = {param.name: param dla param w self.parameters.values()
                                        jeżeli param.kind == _KEYWORD_ONLY}

        zwróć params, kwo_params, self.return_annotation

    def __hash__(self):
        params, kwo_params, return_annotation = self._hash_basis()
        kwo_params = frozenset(kwo_params.values())
        zwróć hash((params, kwo_params, return_annotation))

    def __eq__(self, other):
        jeżeli self jest other:
            zwróć Prawda
        jeżeli nie isinstance(other, Signature):
            zwróć NotImplemented
        zwróć self._hash_basis() == other._hash_basis()

    def _bind(self, args, kwargs, *, partial=Nieprawda):
        """Private method. Don't use directly."""

        arguments = OrderedDict()

        parameters = iter(self.parameters.values())
        parameters_ex = ()
        arg_vals = iter(args)

        dopóki Prawda:
            # Let's iterate through the positional arguments oraz corresponding
            # parameters
            spróbuj:
                arg_val = next(arg_vals)
            wyjąwszy StopIteration:
                # No more positional arguments
                spróbuj:
                    param = next(parameters)
                wyjąwszy StopIteration:
                    # No more parameters. That's it. Just need to check that
                    # we have no `kwargs` after this dopóki loop
                    przerwij
                inaczej:
                    jeżeli param.kind == _VAR_POSITIONAL:
                        # That's OK, just empty *args.  Let's start parsing
                        # kwargs
                        przerwij
                    albo_inaczej param.name w kwargs:
                        jeżeli param.kind == _POSITIONAL_ONLY:
                            msg = '{arg!r} parameter jest positional only, ' \
                                  'but was dalejed jako a keyword'
                            msg = msg.format(arg=param.name)
                            podnieś TypeError(msg) z Nic
                        parameters_ex = (param,)
                        przerwij
                    albo_inaczej (param.kind == _VAR_KEYWORD albo
                                                param.default jest nie _empty):
                        # That's fine too - we have a default value dla this
                        # parameter.  So, lets start parsing `kwargs`, starting
                        # przy the current parameter
                        parameters_ex = (param,)
                        przerwij
                    inaczej:
                        # No default, nie VAR_KEYWORD, nie VAR_POSITIONAL,
                        # nie w `kwargs`
                        jeżeli partial:
                            parameters_ex = (param,)
                            przerwij
                        inaczej:
                            msg = 'missing a required argument: {arg!r}'
                            msg = msg.format(arg=param.name)
                            podnieś TypeError(msg) z Nic
            inaczej:
                # We have a positional argument to process
                spróbuj:
                    param = next(parameters)
                wyjąwszy StopIteration:
                    podnieś TypeError('too many positional arguments') z Nic
                inaczej:
                    jeżeli param.kind w (_VAR_KEYWORD, _KEYWORD_ONLY):
                        # Looks like we have no parameter dla this positional
                        # argument
                        podnieś TypeError(
                            'too many positional arguments') z Nic

                    jeżeli param.kind == _VAR_POSITIONAL:
                        # We have an '*args'-like argument, let's fill it with
                        # all positional arguments we have left oraz move on to
                        # the next phase
                        values = [arg_val]
                        values.extend(arg_vals)
                        arguments[param.name] = tuple(values)
                        przerwij

                    jeżeli param.name w kwargs:
                        podnieś TypeError(
                            'multiple values dla argument {arg!r}'.format(
                                arg=param.name)) z Nic

                    arguments[param.name] = arg_val

        # Now, we iterate through the remaining parameters to process
        # keyword arguments
        kwargs_param = Nic
        dla param w itertools.chain(parameters_ex, parameters):
            jeżeli param.kind == _VAR_KEYWORD:
                # Memorize that we have a '**kwargs'-like parameter
                kwargs_param = param
                kontynuuj

            jeżeli param.kind == _VAR_POSITIONAL:
                # Named arguments don't refer to '*args'-like parameters.
                # We only arrive here jeżeli the positional arguments ended
                # before reaching the last parameter before *args.
                kontynuuj

            param_name = param.name
            spróbuj:
                arg_val = kwargs.pop(param_name)
            wyjąwszy KeyError:
                # We have no value dla this parameter.  It's fine though,
                # jeżeli it has a default value, albo it jest an '*args'-like
                # parameter, left alone by the processing of positional
                # arguments.
                jeżeli (nie partial oraz param.kind != _VAR_POSITIONAL oraz
                                                    param.default jest _empty):
                    podnieś TypeError('missing a required argument: {arg!r}'. \
                                    format(arg=param_name)) z Nic

            inaczej:
                jeżeli param.kind == _POSITIONAL_ONLY:
                    # This should never happen w case of a properly built
                    # Signature object (but let's have this check here
                    # to ensure correct behaviour just w case)
                    podnieś TypeError('{arg!r} parameter jest positional only, '
                                    'but was dalejed jako a keyword'. \
                                    format(arg=param.name))

                arguments[param_name] = arg_val

        jeżeli kwargs:
            jeżeli kwargs_param jest nie Nic:
                # Process our '**kwargs'-like parameter
                arguments[kwargs_param.name] = kwargs
            inaczej:
                podnieś TypeError(
                    'got an unexpected keyword argument {arg!r}'.format(
                        arg=next(iter(kwargs))))

        zwróć self._bound_arguments_cls(self, arguments)

    def bind(*args, **kwargs):
        """Get a BoundArguments object, that maps the dalejed `args`
        oraz `kwargs` to the function's signature.  Raises `TypeError`
        jeżeli the dalejed arguments can nie be bound.
        """
        zwróć args[0]._bind(args[1:], kwargs)

    def bind_partial(*args, **kwargs):
        """Get a BoundArguments object, that partially maps the
        dalejed `args` oraz `kwargs` to the function's signature.
        Raises `TypeError` jeżeli the dalejed arguments can nie be bound.
        """
        zwróć args[0]._bind(args[1:], kwargs, partial=Prawda)

    def __reduce__(self):
        zwróć (type(self),
                (tuple(self._parameters.values()),),
                {'_return_annotation': self._return_annotation})

    def __setstate__(self, state):
        self._return_annotation = state['_return_annotation']

    def __repr__(self):
        zwróć '<{} {}>'.format(self.__class__.__name__, self)

    def __str__(self):
        result = []
        render_pos_only_separator = Nieprawda
        render_kw_only_separator = Prawda
        dla param w self.parameters.values():
            formatted = str(param)

            kind = param.kind

            jeżeli kind == _POSITIONAL_ONLY:
                render_pos_only_separator = Prawda
            albo_inaczej render_pos_only_separator:
                # It's nie a positional-only parameter, oraz the flag
                # jest set to 'Prawda' (there were pos-only params before.)
                result.append('/')
                render_pos_only_separator = Nieprawda

            jeżeli kind == _VAR_POSITIONAL:
                # OK, we have an '*args'-like parameter, so we won't need
                # a '*' to separate keyword-only arguments
                render_kw_only_separator = Nieprawda
            albo_inaczej kind == _KEYWORD_ONLY oraz render_kw_only_separator:
                # We have a keyword-only parameter to render oraz we haven't
                # rendered an '*args'-like parameter before, so add a '*'
                # separator to the parameters list ("foo(arg1, *, arg2)" case)
                result.append('*')
                # This condition should be only triggered once, so
                # reset the flag
                render_kw_only_separator = Nieprawda

            result.append(formatted)

        jeżeli render_pos_only_separator:
            # There were only positional-only parameters, hence the
            # flag was nie reset to 'Nieprawda'
            result.append('/')

        rendered = '({})'.format(', '.join(result))

        jeżeli self.return_annotation jest nie _empty:
            anno = formatannotation(self.return_annotation)
            rendered += ' -> {}'.format(anno)

        zwróć rendered


def signature(obj, *, follow_wrapped=Prawda):
    """Get a signature object dla the dalejed callable."""
    zwróć Signature.from_callable(obj, follow_wrapped=follow_wrapped)


def _main():
    """ Logic dla inspecting an object given at command line """
    zaimportuj argparse
    zaimportuj importlib

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'object',
         help="The object to be analysed. "
              "It supports the 'module:qualname' syntax")
    parser.add_argument(
        '-d', '--details', action='store_true',
        help='Display info about the module rather than its source code')

    args = parser.parse_args()

    target = args.object
    mod_name, has_attrs, attrs = target.partition(":")
    spróbuj:
        obj = module = importlib.import_module(mod_name)
    wyjąwszy Exception jako exc:
        msg = "Failed to zaimportuj {} ({}: {})".format(mod_name,
                                                    type(exc).__name__,
                                                    exc)
        print(msg, file=sys.stderr)
        exit(2)

    jeżeli has_attrs:
        parts = attrs.split(".")
        obj = module
        dla part w parts:
            obj = getattr(obj, part)

    jeżeli module.__name__ w sys.builtin_module_names:
        print("Can't get info dla builtin modules.", file=sys.stderr)
        exit(1)

    jeżeli args.details:
        print('Target: {}'.format(target))
        print('Origin: {}'.format(getsourcefile(module)))
        print('Cached: {}'.format(module.__cached__))
        jeżeli obj jest module:
            print('Loader: {}'.format(repr(module.__loader__)))
            jeżeli hasattr(module, '__path__'):
                print('Submodule search path: {}'.format(module.__path__))
        inaczej:
            spróbuj:
                __, lineno = findsource(obj)
            wyjąwszy Exception:
                dalej
            inaczej:
                print('Line: {}'.format(lineno))

        print('\n')
    inaczej:
        print(getsource(obj))


jeżeli __name__ == "__main__":
    _main()
