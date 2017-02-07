"""create oraz manipulate C data types w Python"""

zaimportuj os jako _os, sys jako _sys

__version__ = "1.1.0"

z _ctypes zaimportuj Union, Structure, Array
z _ctypes zaimportuj _Pointer
z _ctypes zaimportuj CFuncPtr jako _CFuncPtr
z _ctypes zaimportuj __version__ jako _ctypes_version
z _ctypes zaimportuj RTLD_LOCAL, RTLD_GLOBAL
z _ctypes zaimportuj ArgumentError

z struct zaimportuj calcsize jako _calcsize

jeżeli __version__ != _ctypes_version:
    podnieś Exception("Version number mismatch", __version__, _ctypes_version)

jeżeli _os.name w ("nt", "ce"):
    z _ctypes zaimportuj FormatError

DEFAULT_MODE = RTLD_LOCAL
jeżeli _os.name == "posix" oraz _sys.platform == "darwin":
    # On OS X 10.3, we use RTLD_GLOBAL jako default mode
    # because RTLD_LOCAL does nie work at least on some
    # libraries.  OS X 10.3 jest Darwin 7, so we check for
    # that.

    jeżeli int(_os.uname().release.split('.')[0]) < 8:
        DEFAULT_MODE = RTLD_GLOBAL

z _ctypes zaimportuj FUNCFLAG_CDECL jako _FUNCFLAG_CDECL, \
     FUNCFLAG_PYTHONAPI jako _FUNCFLAG_PYTHONAPI, \
     FUNCFLAG_USE_ERRNO jako _FUNCFLAG_USE_ERRNO, \
     FUNCFLAG_USE_LASTERROR jako _FUNCFLAG_USE_LASTERROR

# WINOLEAPI -> HRESULT
# WINOLEAPI_(type)
#
# STDMETHODCALLTYPE
#
# STDMETHOD(name)
# STDMETHOD_(type, name)
#
# STDAPICALLTYPE

def create_string_buffer(init, size=Nic):
    """create_string_buffer(aBytes) -> character array
    create_string_buffer(anInteger) -> character array
    create_string_buffer(aString, anInteger) -> character array
    """
    jeżeli isinstance(init, bytes):
        jeżeli size jest Nic:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        buf.value = init
        zwróć buf
    albo_inaczej isinstance(init, int):
        buftype = c_char * init
        buf = buftype()
        zwróć buf
    podnieś TypeError(init)

def c_buffer(init, size=Nic):
##    "deprecated, use create_string_buffer instead"
##    zaimportuj warnings
##    warnings.warn("c_buffer jest deprecated, use create_string_buffer instead",
##                  DeprecationWarning, stacklevel=2)
    zwróć create_string_buffer(init, size)

_c_functype_cache = {}
def CFUNCTYPE(restype, *argtypes, **kw):
    """CFUNCTYPE(restype, *argtypes,
                 use_errno=Nieprawda, use_last_error=Nieprawda) -> function prototype.

    restype: the result type
    argtypes: a sequence specifying the argument types

    The function prototype can be called w different ways to create a
    callable object:

    prototype(integer address) -> foreign function
    prototype(callable) -> create oraz zwróć a C callable function z callable
    prototype(integer index, method name[, paramflags]) -> foreign function calling a COM method
    prototype((ordinal number, dll object)[, paramflags]) -> foreign function exported by ordinal
    prototype((function name, dll object)[, paramflags]) -> foreign function exported by name
    """
    flags = _FUNCFLAG_CDECL
    jeżeli kw.pop("use_errno", Nieprawda):
        flags |= _FUNCFLAG_USE_ERRNO
    jeżeli kw.pop("use_last_error", Nieprawda):
        flags |= _FUNCFLAG_USE_LASTERROR
    jeżeli kw:
        podnieś ValueError("unexpected keyword argument(s) %s" % kw.keys())
    spróbuj:
        zwróć _c_functype_cache[(restype, argtypes, flags)]
    wyjąwszy KeyError:
        klasa CFunctionType(_CFuncPtr):
            _argtypes_ = argtypes
            _restype_ = restype
            _flags_ = flags
        _c_functype_cache[(restype, argtypes, flags)] = CFunctionType
        zwróć CFunctionType

jeżeli _os.name w ("nt", "ce"):
    z _ctypes zaimportuj LoadLibrary jako _dlopen
    z _ctypes zaimportuj FUNCFLAG_STDCALL jako _FUNCFLAG_STDCALL
    jeżeli _os.name == "ce":
        # 'ce' doesn't have the stdcall calling convention
        _FUNCFLAG_STDCALL = _FUNCFLAG_CDECL

    _win_functype_cache = {}
    def WINFUNCTYPE(restype, *argtypes, **kw):
        # docstring set later (very similar to CFUNCTYPE.__doc__)
        flags = _FUNCFLAG_STDCALL
        jeżeli kw.pop("use_errno", Nieprawda):
            flags |= _FUNCFLAG_USE_ERRNO
        jeżeli kw.pop("use_last_error", Nieprawda):
            flags |= _FUNCFLAG_USE_LASTERROR
        jeżeli kw:
            podnieś ValueError("unexpected keyword argument(s) %s" % kw.keys())
        spróbuj:
            zwróć _win_functype_cache[(restype, argtypes, flags)]
        wyjąwszy KeyError:
            klasa WinFunctionType(_CFuncPtr):
                _argtypes_ = argtypes
                _restype_ = restype
                _flags_ = flags
            _win_functype_cache[(restype, argtypes, flags)] = WinFunctionType
            zwróć WinFunctionType
    jeżeli WINFUNCTYPE.__doc__:
        WINFUNCTYPE.__doc__ = CFUNCTYPE.__doc__.replace("CFUNCTYPE", "WINFUNCTYPE")

albo_inaczej _os.name == "posix":
    z _ctypes zaimportuj dlopen jako _dlopen

z _ctypes zaimportuj sizeof, byref, addressof, alignment, resize
z _ctypes zaimportuj get_errno, set_errno
z _ctypes zaimportuj _SimpleCData

def _check_size(typ, typecode=Nic):
    # Check jeżeli sizeof(ctypes_type) against struct.calcsize.  This
    # should protect somewhat against a misconfigured libffi.
    z struct zaimportuj calcsize
    jeżeli typecode jest Nic:
        # Most _type_ codes are the same jako used w struct
        typecode = typ._type_
    actual, required = sizeof(typ), calcsize(typecode)
    jeżeli actual != required:
        podnieś SystemError("sizeof(%s) wrong: %d instead of %d" % \
                          (typ, actual, required))

klasa py_object(_SimpleCData):
    _type_ = "O"
    def __repr__(self):
        spróbuj:
            zwróć super().__repr__()
        wyjąwszy ValueError:
            zwróć "%s(<NULL>)" % type(self).__name__
_check_size(py_object, "P")

klasa c_short(_SimpleCData):
    _type_ = "h"
_check_size(c_short)

klasa c_ushort(_SimpleCData):
    _type_ = "H"
_check_size(c_ushort)

klasa c_long(_SimpleCData):
    _type_ = "l"
_check_size(c_long)

klasa c_ulong(_SimpleCData):
    _type_ = "L"
_check_size(c_ulong)

jeżeli _calcsize("i") == _calcsize("l"):
    # jeżeli int oraz long have the same size, make c_int an alias dla c_long
    c_int = c_long
    c_uint = c_ulong
inaczej:
    klasa c_int(_SimpleCData):
        _type_ = "i"
    _check_size(c_int)

    klasa c_uint(_SimpleCData):
        _type_ = "I"
    _check_size(c_uint)

klasa c_float(_SimpleCData):
    _type_ = "f"
_check_size(c_float)

klasa c_double(_SimpleCData):
    _type_ = "d"
_check_size(c_double)

klasa c_longdouble(_SimpleCData):
    _type_ = "g"
jeżeli sizeof(c_longdouble) == sizeof(c_double):
    c_longdouble = c_double

jeżeli _calcsize("l") == _calcsize("q"):
    # jeżeli long oraz long long have the same size, make c_longlong an alias dla c_long
    c_longlong = c_long
    c_ulonglong = c_ulong
inaczej:
    klasa c_longlong(_SimpleCData):
        _type_ = "q"
    _check_size(c_longlong)

    klasa c_ulonglong(_SimpleCData):
        _type_ = "Q"
    ##    def from_param(cls, val):
    ##        zwróć ('d', float(val), val)
    ##    from_param = classmethod(from_param)
    _check_size(c_ulonglong)

klasa c_ubyte(_SimpleCData):
    _type_ = "B"
c_ubyte.__ctype_le__ = c_ubyte.__ctype_be__ = c_ubyte
# backward compatibility:
##c_uchar = c_ubyte
_check_size(c_ubyte)

klasa c_byte(_SimpleCData):
    _type_ = "b"
c_byte.__ctype_le__ = c_byte.__ctype_be__ = c_byte
_check_size(c_byte)

klasa c_char(_SimpleCData):
    _type_ = "c"
c_char.__ctype_le__ = c_char.__ctype_be__ = c_char
_check_size(c_char)

klasa c_char_p(_SimpleCData):
    _type_ = "z"
    def __repr__(self):
        zwróć "%s(%s)" % (self.__class__.__name__, c_void_p.from_buffer(self).value)
_check_size(c_char_p, "P")

klasa c_void_p(_SimpleCData):
    _type_ = "P"
c_voidp = c_void_p # backwards compatibility (to a bug)
_check_size(c_void_p)

klasa c_bool(_SimpleCData):
    _type_ = "?"

z _ctypes zaimportuj POINTER, pointer, _pointer_type_cache

klasa c_wchar_p(_SimpleCData):
    _type_ = "Z"
    def __repr__(self):
        zwróć "%s(%s)" % (self.__class__.__name__, c_void_p.from_buffer(self).value)

klasa c_wchar(_SimpleCData):
    _type_ = "u"

def _reset_cache():
    _pointer_type_cache.clear()
    _c_functype_cache.clear()
    jeżeli _os.name w ("nt", "ce"):
        _win_functype_cache.clear()
    # _SimpleCData.c_wchar_p_from_param
    POINTER(c_wchar).from_param = c_wchar_p.from_param
    # _SimpleCData.c_char_p_from_param
    POINTER(c_char).from_param = c_char_p.from_param
    _pointer_type_cache[Nic] = c_void_p
    # XXX dla whatever reasons, creating the first instance of a callback
    # function jest needed dla the unittests on Win64 to succeed.  This MAY
    # be a compiler bug, since the problem occurs only when _ctypes jest
    # compiled przy the MS SDK compiler.  Or an uninitialized variable?
    CFUNCTYPE(c_int)(lambda: Nic)

def create_unicode_buffer(init, size=Nic):
    """create_unicode_buffer(aString) -> character array
    create_unicode_buffer(anInteger) -> character array
    create_unicode_buffer(aString, anInteger) -> character array
    """
    jeżeli isinstance(init, str):
        jeżeli size jest Nic:
            size = len(init)+1
        buftype = c_wchar * size
        buf = buftype()
        buf.value = init
        zwróć buf
    albo_inaczej isinstance(init, int):
        buftype = c_wchar * init
        buf = buftype()
        zwróć buf
    podnieś TypeError(init)


# XXX Deprecated
def SetPointerType(pointer, cls):
    jeżeli _pointer_type_cache.get(cls, Nic) jest nie Nic:
        podnieś RuntimeError("This type already exists w the cache")
    jeżeli id(pointer) nie w _pointer_type_cache:
        podnieś RuntimeError("What's this???")
    pointer.set_type(cls)
    _pointer_type_cache[cls] = pointer
    usuń _pointer_type_cache[id(pointer)]

# XXX Deprecated
def ARRAY(typ, len):
    zwróć typ * len

################################################################


klasa CDLL(object):
    """An instance of this klasa represents a loaded dll/shared
    library, exporting functions using the standard C calling
    convention (named 'cdecl' on Windows).

    The exported functions can be accessed jako attributes, albo by
    indexing przy the function name.  Examples:

    <obj>.qsort -> callable object
    <obj>['qsort'] -> callable object

    Calling the functions releases the Python GIL during the call oraz
    reacquires it afterwards.
    """
    _func_flags_ = _FUNCFLAG_CDECL
    _func_restype_ = c_int

    def __init__(self, name, mode=DEFAULT_MODE, handle=Nic,
                 use_errno=Nieprawda,
                 use_last_error=Nieprawda):
        self._name = name
        flags = self._func_flags_
        jeżeli use_errno:
            flags |= _FUNCFLAG_USE_ERRNO
        jeżeli use_last_error:
            flags |= _FUNCFLAG_USE_LASTERROR

        klasa _FuncPtr(_CFuncPtr):
            _flags_ = flags
            _restype_ = self._func_restype_
        self._FuncPtr = _FuncPtr

        jeżeli handle jest Nic:
            self._handle = _dlopen(self._name, mode)
        inaczej:
            self._handle = handle

    def __repr__(self):
        zwróć "<%s '%s', handle %x at %#x>" % \
               (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))

    def __getattr__(self, name):
        jeżeli name.startswith('__') oraz name.endswith('__'):
            podnieś AttributeError(name)
        func = self.__getitem__(name)
        setattr(self, name, func)
        zwróć func

    def __getitem__(self, name_or_ordinal):
        func = self._FuncPtr((name_or_ordinal, self))
        jeżeli nie isinstance(name_or_ordinal, int):
            func.__name__ = name_or_ordinal
        zwróć func

klasa PyDLL(CDLL):
    """This klasa represents the Python library itself.  It allows to
    access Python API functions.  The GIL jest nie released, oraz
    Python exceptions are handled correctly.
    """
    _func_flags_ = _FUNCFLAG_CDECL | _FUNCFLAG_PYTHONAPI

jeżeli _os.name w ("nt", "ce"):

    klasa WinDLL(CDLL):
        """This klasa represents a dll exporting functions using the
        Windows stdcall calling convention.
        """
        _func_flags_ = _FUNCFLAG_STDCALL

    # XXX Hm, what about HRESULT jako normal parameter?
    # Mustn't it derive z c_long then?
    z _ctypes zaimportuj _check_HRESULT, _SimpleCData
    klasa HRESULT(_SimpleCData):
        _type_ = "l"
        # _check_retval_ jest called przy the function's result when it
        # jest used jako restype.  It checks dla the FAILED bit, oraz
        # podnieśs an OSError jeżeli it jest set.
        #
        # The _check_retval_ method jest implemented w C, so that the
        # method definition itself jest nie included w the traceback
        # when it podnieśs an error - that jest what we want (and Python
        # doesn't have a way to podnieś an exception w the caller's
        # frame).
        _check_retval_ = _check_HRESULT

    klasa OleDLL(CDLL):
        """This klasa represents a dll exporting functions using the
        Windows stdcall calling convention, oraz returning HRESULT.
        HRESULT error values are automatically podnieśd jako OSError
        exceptions.
        """
        _func_flags_ = _FUNCFLAG_STDCALL
        _func_restype_ = HRESULT

klasa LibraryLoader(object):
    def __init__(self, dlltype):
        self._dlltype = dlltype

    def __getattr__(self, name):
        jeżeli name[0] == '_':
            podnieś AttributeError(name)
        dll = self._dlltype(name)
        setattr(self, name, dll)
        zwróć dll

    def __getitem__(self, name):
        zwróć getattr(self, name)

    def LoadLibrary(self, name):
        zwróć self._dlltype(name)

cdll = LibraryLoader(CDLL)
pydll = LibraryLoader(PyDLL)

jeżeli _os.name w ("nt", "ce"):
    pythonapi = PyDLL("python dll", Nic, _sys.dllhandle)
albo_inaczej _sys.platform == "cygwin":
    pythonapi = PyDLL("libpython%d.%d.dll" % _sys.version_info[:2])
inaczej:
    pythonapi = PyDLL(Nic)


jeżeli _os.name w ("nt", "ce"):
    windll = LibraryLoader(WinDLL)
    oledll = LibraryLoader(OleDLL)

    jeżeli _os.name == "nt":
        GetLastError = windll.kernel32.GetLastError
    inaczej:
        GetLastError = windll.coredll.GetLastError
    z _ctypes zaimportuj get_last_error, set_last_error

    def WinError(code=Nic, descr=Nic):
        jeżeli code jest Nic:
            code = GetLastError()
        jeżeli descr jest Nic:
            descr = FormatError(code).strip()
        zwróć OSError(Nic, descr, Nic, code)

jeżeli sizeof(c_uint) == sizeof(c_void_p):
    c_size_t = c_uint
    c_ssize_t = c_int
albo_inaczej sizeof(c_ulong) == sizeof(c_void_p):
    c_size_t = c_ulong
    c_ssize_t = c_long
albo_inaczej sizeof(c_ulonglong) == sizeof(c_void_p):
    c_size_t = c_ulonglong
    c_ssize_t = c_longlong

# functions

z _ctypes zaimportuj _memmove_addr, _memset_addr, _string_at_addr, _cast_addr

## void *memmove(void *, const void *, size_t);
memmove = CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_size_t)(_memmove_addr)

## void *memset(void *, int, size_t)
memset = CFUNCTYPE(c_void_p, c_void_p, c_int, c_size_t)(_memset_addr)

def PYFUNCTYPE(restype, *argtypes):
    klasa CFunctionType(_CFuncPtr):
        _argtypes_ = argtypes
        _restype_ = restype
        _flags_ = _FUNCFLAG_CDECL | _FUNCFLAG_PYTHONAPI
    zwróć CFunctionType

_cast = PYFUNCTYPE(py_object, c_void_p, py_object, py_object)(_cast_addr)
def cast(obj, typ):
    zwróć _cast(obj, obj, typ)

_string_at = PYFUNCTYPE(py_object, c_void_p, c_int)(_string_at_addr)
def string_at(ptr, size=-1):
    """string_at(addr[, size]) -> string

    Return the string at addr."""
    zwróć _string_at(ptr, size)

spróbuj:
    z _ctypes zaimportuj _wstring_at_addr
wyjąwszy ImportError:
    dalej
inaczej:
    _wstring_at = PYFUNCTYPE(py_object, c_void_p, c_int)(_wstring_at_addr)
    def wstring_at(ptr, size=-1):
        """wstring_at(addr[, size]) -> string

        Return the string at addr."""
        zwróć _wstring_at(ptr, size)


jeżeli _os.name w ("nt", "ce"): # COM stuff
    def DllGetClassObject(rclsid, riid, ppv):
        spróbuj:
            ccom = __import__("comtypes.server.inprocserver", globals(), locals(), ['*'])
        wyjąwszy ImportError:
            zwróć -2147221231 # CLASS_E_CLASSNOTAVAILABLE
        inaczej:
            zwróć ccom.DllGetClassObject(rclsid, riid, ppv)

    def DllCanUnloadNow():
        spróbuj:
            ccom = __import__("comtypes.server.inprocserver", globals(), locals(), ['*'])
        wyjąwszy ImportError:
            zwróć 0 # S_OK
        zwróć ccom.DllCanUnloadNow()

z ctypes._endian zaimportuj BigEndianStructure, LittleEndianStructure

# Fill w specifically-sized types
c_int8 = c_byte
c_uint8 = c_ubyte
dla kind w [c_short, c_int, c_long, c_longlong]:
    jeżeli sizeof(kind) == 2: c_int16 = kind
    albo_inaczej sizeof(kind) == 4: c_int32 = kind
    albo_inaczej sizeof(kind) == 8: c_int64 = kind
dla kind w [c_ushort, c_uint, c_ulong, c_ulonglong]:
    jeżeli sizeof(kind) == 2: c_uint16 = kind
    albo_inaczej sizeof(kind) == 4: c_uint32 = kind
    albo_inaczej sizeof(kind) == 8: c_uint64 = kind
del(kind)

_reset_cache()
