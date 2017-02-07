#!/usr/bin/python
'''
From gdb 7 onwards, gdb's build can be configured --with-python, allowing gdb
to be extended przy Python code e.g. dla library-specific data visualizations,
such jako dla the C++ STL types.  Documentation on this API can be seen at:
http://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html


This python module deals przy the case when the process being debugged (the
"inferior process" w gdb parlance) jest itself python, albo more specifically,
linked against libpython.  In this situation, almost every item of data jest a
(PyObject*), oraz having the debugger merely print their addresses jest nie very
enlightening.

This module embeds knowledge about the implementation details of libpython so
that we can emit useful visualizations e.g. a string, a list, a dict, a frame
giving file/line information oraz the state of local variables

In particular, given a gdb.Value corresponding to a PyObject* w the inferior
process, we can generate a "proxy value" within the gdb process.  For example,
given a PyObject* w the inferior process that jest w fact a PyListObject*
holding three PyObject* that turn out to be PyBytesObject* instances, we can
generate a proxy value within the gdb process that jest a list of bytes
instances:
  [b"foo", b"bar", b"baz"]

Doing so can be expensive dla complicated graphs of objects, oraz could take
some time, so we also have a "write_repr" method that writes a representation
of the data to a file-like object.  This allows us to stop the traversal by
having the file-like object podnieś an exception jeżeli it gets too much data.

With both "proxyval" oraz "write_repr" we keep track of the set of all addresses
visited so far w the traversal, to avoid infinite recursion due to cycles w
the graph of object references.

We try to defer gdb.lookup_type() invocations dla python types until jako late as
possible: dla a dynamically linked python binary, when the process starts w
the debugger, the libpython.so hasn't been dynamically loaded yet, so none of
the type names are known to the debugger

The module also extends gdb przy some python-specific commands.
'''

# NOTE: some gdbs are linked przy Python 3, so this file should be dual-syntax
# compatible (2.6+ oraz 3.0+).  See #19308.

z __future__ zaimportuj print_function, with_statement
zaimportuj gdb
zaimportuj os
zaimportuj locale
zaimportuj sys

jeżeli sys.version_info[0] >= 3:
    unichr = chr
    xrange = range
    long = int

# Look up the gdb.Type dla some standard types:
_type_char_ptr = gdb.lookup_type('char').pointer() # char*
_type_unsigned_char_ptr = gdb.lookup_type('unsigned char').pointer() # unsigned char*
_type_void_ptr = gdb.lookup_type('void').pointer() # void*
_type_unsigned_short_ptr = gdb.lookup_type('unsigned short').pointer()
_type_unsigned_int_ptr = gdb.lookup_type('unsigned int').pointer()

# value computed later, see PyUnicodeObjectPtr.proxy()
_is_pep393 = Nic

SIZEOF_VOID_P = _type_void_ptr.sizeof


Py_TPFLAGS_HEAPTYPE = (1 << 9)

Py_TPFLAGS_LONG_SUBCLASS     = (1 << 24)
Py_TPFLAGS_LIST_SUBCLASS     = (1 << 25)
Py_TPFLAGS_TUPLE_SUBCLASS    = (1 << 26)
Py_TPFLAGS_BYTES_SUBCLASS    = (1 << 27)
Py_TPFLAGS_UNICODE_SUBCLASS  = (1 << 28)
Py_TPFLAGS_DICT_SUBCLASS     = (1 << 29)
Py_TPFLAGS_BASE_EXC_SUBCLASS = (1 << 30)
Py_TPFLAGS_TYPE_SUBCLASS     = (1 << 31)


MAX_OUTPUT_LEN=1024

hexdigits = "0123456789abcdef"

ENCODING = locale.getpreferredencoding()

klasa NullPyObjectPtr(RuntimeError):
    dalej


def safety_limit(val):
    # Given a integer value z the process being debugged, limit it to some
    # safety threshold so that arbitrary przerwijage within said process doesn't
    # przerwij the gdb process too much (e.g. sizes of iterations, sizes of lists)
    zwróć min(val, 1000)


def safe_range(val):
    # As per range, but don't trust the value too much: cap it to a safety
    # threshold w case the data was corrupted
    zwróć xrange(safety_limit(int(val)))

jeżeli sys.version_info[0] >= 3:
    def write_unicode(file, text):
        file.write(text)
inaczej:
    def write_unicode(file, text):
        # Write a byte albo unicode string to file. Unicode strings are encoded to
        # ENCODING encoding przy 'backslashreplace' error handler to avoid
        # UnicodeEncodeError.
        jeżeli isinstance(text, unicode):
            text = text.encode(ENCODING, 'backslashreplace')
        file.write(text)

spróbuj:
    os_fsencode = os.fsencode
wyjąwszy AttributeError:
    def os_fsencode(filename):
        jeżeli nie isinstance(filename, unicode):
            zwróć filename
        encoding = sys.getfilesystemencoding()
        jeżeli encoding == 'mbcs':
            # mbcs doesn't support surrogateescape
            zwróć filename.encode(encoding)
        encoded = []
        dla char w filename:
            # surrogateescape error handler
            jeżeli 0xDC80 <= ord(char) <= 0xDCFF:
                byte = chr(ord(char) - 0xDC00)
            inaczej:
                byte = char.encode(encoding)
            encoded.append(byte)
        zwróć ''.join(encoded)

klasa StringTruncated(RuntimeError):
    dalej

klasa TruncatedStringIO(object):
    '''Similar to io.StringIO, but can truncate the output by raising a
    StringTruncated exception'''
    def __init__(self, maxlen=Nic):
        self._val = ''
        self.maxlen = maxlen

    def write(self, data):
        jeżeli self.maxlen:
            jeżeli len(data) + len(self._val) > self.maxlen:
                # Truncation:
                self._val += data[0:self.maxlen - len(self._val)]
                podnieś StringTruncated()

        self._val += data

    def getvalue(self):
        zwróć self._val

klasa PyObjectPtr(object):
    """
    Class wrapping a gdb.Value that's a either a (PyObject*) within the
    inferior process, albo some subclass pointer e.g. (PyBytesObject*)

    There will be a subclass dla every refined PyObject type that we care
    about.

    Note that at every stage the underlying pointer could be NULL, point
    to corrupt data, etc; this jest the debugger, after all.
    """
    _typename = 'PyObject'

    def __init__(self, gdbval, cast_to=Nic):
        jeżeli cast_to:
            self._gdbval = gdbval.cast(cast_to)
        inaczej:
            self._gdbval = gdbval

    def field(self, name):
        '''
        Get the gdb.Value dla the given field within the PyObject, coping with
        some python 2 versus python 3 differences.

        Various libpython types are defined using the "PyObject_HEAD" oraz
        "PyObject_VAR_HEAD" macros.

        In Python 2, this these are defined so that "ob_type" oraz (dla a var
        object) "ob_size" are fields of the type w question.

        In Python 3, this jest defined jako an embedded PyVarObject type thus:
           PyVarObject ob_base;
        so that the "ob_size" field jest located insize the "ob_base" field, oraz
        the "ob_type" jest most easily accessed by casting back to a (PyObject*).
        '''
        jeżeli self.is_null():
            podnieś NullPyObjectPtr(self)

        jeżeli name == 'ob_type':
            pyo_ptr = self._gdbval.cast(PyObjectPtr.get_gdb_type())
            zwróć pyo_ptr.dereference()[name]

        jeżeli name == 'ob_size':
            pyo_ptr = self._gdbval.cast(PyVarObjectPtr.get_gdb_type())
            zwróć pyo_ptr.dereference()[name]

        # General case: look it up inside the object:
        zwróć self._gdbval.dereference()[name]

    def pyop_field(self, name):
        '''
        Get a PyObjectPtr dla the given PyObject* field within this PyObject,
        coping przy some python 2 versus python 3 differences.
        '''
        zwróć PyObjectPtr.from_pyobject_ptr(self.field(name))

    def write_field_repr(self, name, out, visited):
        '''
        Extract the PyObject* field named "name", oraz write its representation
        to file-like object "out"
        '''
        field_obj = self.pyop_field(name)
        field_obj.write_repr(out, visited)

    def get_truncated_repr(self, maxlen):
        '''
        Get a repr-like string dla the data, but truncate it at "maxlen" bytes
        (ending the object graph traversal jako soon jako you do)
        '''
        out = TruncatedStringIO(maxlen)
        spróbuj:
            self.write_repr(out, set())
        wyjąwszy StringTruncated:
            # Truncation occurred:
            zwróć out.getvalue() + '...(truncated)'

        # No truncation occurred:
        zwróć out.getvalue()

    def type(self):
        zwróć PyTypeObjectPtr(self.field('ob_type'))

    def is_null(self):
        zwróć 0 == long(self._gdbval)

    def is_optimized_out(self):
        '''
        Is the value of the underlying PyObject* visible to the debugger?

        This can vary przy the precise version of the compiler used to build
        Python, oraz the precise version of gdb.

        See e.g. https://bugzilla.redhat.com/show_bug.cgi?id=556975 with
        PyEval_EvalFrameEx's "f"
        '''
        zwróć self._gdbval.is_optimized_out

    def safe_tp_name(self):
        spróbuj:
            zwróć self.type().field('tp_name').string()
        wyjąwszy NullPyObjectPtr:
            # NULL tp_name?
            zwróć 'unknown'
        wyjąwszy RuntimeError:
            # Can't even read the object at all?
            zwróć 'unknown'

    def proxyval(self, visited):
        '''
        Scrape a value z the inferior process, oraz try to represent it
        within the gdb process, whilst (hopefully) avoiding crashes when
        the remote data jest corrupt.

        Derived classes will override this.

        For example, a PyIntObject* przy ob_ival 42 w the inferior process
        should result w an int(42) w this process.

        visited: a set of all gdb.Value pyobject pointers already visited
        whilst generating this value (to guard against infinite recursion when
        visiting object graphs przy loops).  Analogous to Py_ReprEnter oraz
        Py_ReprLeave
        '''

        klasa FakeRepr(object):
            """
            Class representing a non-descript PyObject* value w the inferior
            process dla when we don't have a custom scraper, intended to have
            a sane repr().
            """

            def __init__(self, tp_name, address):
                self.tp_name = tp_name
                self.address = address

            def __repr__(self):
                # For the NULL pointer, we have no way of knowing a type, so
                # special-case it jako per
                # http://bugs.python.org/issue8032#msg100882
                jeżeli self.address == 0:
                    zwróć '0x0'
                zwróć '<%s at remote 0x%x>' % (self.tp_name, self.address)

        zwróć FakeRepr(self.safe_tp_name(),
                        long(self._gdbval))

    def write_repr(self, out, visited):
        '''
        Write a string representation of the value scraped z the inferior
        process to "out", a file-like object.
        '''
        # Default implementation: generate a proxy value oraz write its repr
        # However, this could involve a lot of work dla complicated objects,
        # so dla derived classes we specialize this
        zwróć out.write(repr(self.proxyval(visited)))

    @classmethod
    def subclass_from_type(cls, t):
        '''
        Given a PyTypeObjectPtr instance wrapping a gdb.Value that's a
        (PyTypeObject*), determine the corresponding subclass of PyObjectPtr
        to use

        Ideally, we would look up the symbols dla the global types, but that
        isn't working yet:
          (gdb) python print gdb.lookup_symbol('PyList_Type')[0].value
          Traceback (most recent call last):
            File "<string>", line 1, w <module>
          NotImplementedError: Symbol type nie yet supported w Python scripts.
          Error dopóki executing Python code.

        For now, we use tp_flags, after doing some string comparisons on the
        tp_name dla some special-cases that don't seem to be visible through
        flags
        '''
        spróbuj:
            tp_name = t.field('tp_name').string()
            tp_flags = int(t.field('tp_flags'))
        wyjąwszy RuntimeError:
            # Handle any kind of error e.g. NULL ptrs by simply using the base
            # class
            zwróć cls

        #print('tp_flags = 0x%08x' % tp_flags)
        #print('tp_name = %r' % tp_name)

        name_map = {'bool': PyBoolObjectPtr,
                    'classobj': PyClassObjectPtr,
                    'NicType': PyNicStructPtr,
                    'frame': PyFrameObjectPtr,
                    'set' : PySetObjectPtr,
                    'frozenset' : PySetObjectPtr,
                    'builtin_function_or_method' : PyCFunctionObjectPtr,
                    }
        jeżeli tp_name w name_map:
            zwróć name_map[tp_name]

        jeżeli tp_flags & Py_TPFLAGS_HEAPTYPE:
            zwróć HeapTypeObjectPtr

        jeżeli tp_flags & Py_TPFLAGS_LONG_SUBCLASS:
            zwróć PyLongObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_LIST_SUBCLASS:
            zwróć PyListObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_TUPLE_SUBCLASS:
            zwróć PyTupleObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_BYTES_SUBCLASS:
            zwróć PyBytesObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS:
            zwróć PyUnicodeObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_DICT_SUBCLASS:
            zwróć PyDictObjectPtr
        jeżeli tp_flags & Py_TPFLAGS_BASE_EXC_SUBCLASS:
            zwróć PyBaseExceptionObjectPtr
        #jeżeli tp_flags & Py_TPFLAGS_TYPE_SUBCLASS:
        #    zwróć PyTypeObjectPtr

        # Use the base class:
        zwróć cls

    @classmethod
    def from_pyobject_ptr(cls, gdbval):
        '''
        Try to locate the appropriate derived klasa dynamically, oraz cast
        the pointer accordingly.
        '''
        spróbuj:
            p = PyObjectPtr(gdbval)
            cls = cls.subclass_from_type(p.type())
            zwróć cls(gdbval, cast_to=cls.get_gdb_type())
        wyjąwszy RuntimeError:
            # Handle any kind of error e.g. NULL ptrs by simply using the base
            # class
            dalej
        zwróć cls(gdbval)

    @classmethod
    def get_gdb_type(cls):
        zwróć gdb.lookup_type(cls._typename).pointer()

    def as_address(self):
        zwróć long(self._gdbval)

klasa PyVarObjectPtr(PyObjectPtr):
    _typename = 'PyVarObject'

klasa ProxyAlreadyVisited(object):
    '''
    Placeholder proxy to use when protecting against infinite recursion due to
    loops w the object graph.

    Analogous to the values emitted by the users of Py_ReprEnter oraz Py_ReprLeave
    '''
    def __init__(self, rep):
        self._rep = rep

    def __repr__(self):
        zwróć self._rep


def _write_instance_repr(out, visited, name, pyop_attrdict, address):
    '''Shared code dla use by all classes:
    write a representation to file-like object "out"'''
    out.write('<')
    out.write(name)

    # Write dictionary of instance attributes:
    jeżeli isinstance(pyop_attrdict, PyDictObjectPtr):
        out.write('(')
        first = Prawda
        dla pyop_arg, pyop_val w pyop_attrdict.iteritems():
            jeżeli nie first:
                out.write(', ')
            first = Nieprawda
            out.write(pyop_arg.proxyval(visited))
            out.write('=')
            pyop_val.write_repr(out, visited)
        out.write(')')
    out.write(' at remote 0x%x>' % address)


klasa InstanceProxy(object):

    def __init__(self, cl_name, attrdict, address):
        self.cl_name = cl_name
        self.attrdict = attrdict
        self.address = address

    def __repr__(self):
        jeżeli isinstance(self.attrdict, dict):
            kwargs = ', '.join(["%s=%r" % (arg, val)
                                dla arg, val w self.attrdict.iteritems()])
            zwróć '<%s(%s) at remote 0x%x>' % (self.cl_name,
                                                kwargs, self.address)
        inaczej:
            zwróć '<%s at remote 0x%x>' % (self.cl_name,
                                            self.address)

def _PyObject_VAR_SIZE(typeobj, nitems):
    jeżeli _PyObject_VAR_SIZE._type_size_t jest Nic:
        _PyObject_VAR_SIZE._type_size_t = gdb.lookup_type('size_t')

    zwróć ( ( typeobj.field('tp_basicsize') +
               nitems * typeobj.field('tp_itemsize') +
               (SIZEOF_VOID_P - 1)
             ) & ~(SIZEOF_VOID_P - 1)
           ).cast(_PyObject_VAR_SIZE._type_size_t)
_PyObject_VAR_SIZE._type_size_t = Nic

klasa HeapTypeObjectPtr(PyObjectPtr):
    _typename = 'PyObject'

    def get_attr_dict(self):
        '''
        Get the PyDictObject ptr representing the attribute dictionary
        (or Nic jeżeli there's a problem)
        '''
        spróbuj:
            typeobj = self.type()
            dictoffset = int_from_int(typeobj.field('tp_dictoffset'))
            jeżeli dictoffset != 0:
                jeżeli dictoffset < 0:
                    type_PyVarObject_ptr = gdb.lookup_type('PyVarObject').pointer()
                    tsize = int_from_int(self._gdbval.cast(type_PyVarObject_ptr)['ob_size'])
                    jeżeli tsize < 0:
                        tsize = -tsize
                    size = _PyObject_VAR_SIZE(typeobj, tsize)
                    dictoffset += size
                    assert dictoffset > 0
                    assert dictoffset % SIZEOF_VOID_P == 0

                dictptr = self._gdbval.cast(_type_char_ptr) + dictoffset
                PyObjectPtrPtr = PyObjectPtr.get_gdb_type().pointer()
                dictptr = dictptr.cast(PyObjectPtrPtr)
                zwróć PyObjectPtr.from_pyobject_ptr(dictptr.dereference())
        wyjąwszy RuntimeError:
            # Corrupt data somewhere; fail safe
            dalej

        # Not found, albo some kind of error:
        zwróć Nic

    def proxyval(self, visited):
        '''
        Support dla classes.

        Currently we just locate the dictionary using a transliteration to
        python of _PyObject_GetDictPtr, ignoring descriptors
        '''
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('<...>')
        visited.add(self.as_address())

        pyop_attr_dict = self.get_attr_dict()
        jeżeli pyop_attr_dict:
            attr_dict = pyop_attr_dict.proxyval(visited)
        inaczej:
            attr_dict = {}
        tp_name = self.safe_tp_name()

        # Class:
        zwróć InstanceProxy(tp_name, attr_dict, long(self._gdbval))

    def write_repr(self, out, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('<...>')
            zwróć
        visited.add(self.as_address())

        pyop_attrdict = self.get_attr_dict()
        _write_instance_repr(out, visited,
                             self.safe_tp_name(), pyop_attrdict, self.as_address())

klasa ProxyException(Exception):
    def __init__(self, tp_name, args):
        self.tp_name = tp_name
        self.args = args

    def __repr__(self):
        zwróć '%s%r' % (self.tp_name, self.args)

klasa PyBaseExceptionObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyBaseExceptionObject* i.e. an exception
    within the process being debugged.
    """
    _typename = 'PyBaseExceptionObject'

    def proxyval(self, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('(...)')
        visited.add(self.as_address())
        arg_proxy = self.pyop_field('args').proxyval(visited)
        zwróć ProxyException(self.safe_tp_name(),
                              arg_proxy)

    def write_repr(self, out, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('(...)')
            zwróć
        visited.add(self.as_address())

        out.write(self.safe_tp_name())
        self.write_field_repr('args', out, visited)

klasa PyClassObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyClassObject* i.e. a <classobj>
    instance within the process being debugged.
    """
    _typename = 'PyClassObject'


klasa BuiltInFunctionProxy(object):
    def __init__(self, ml_name):
        self.ml_name = ml_name

    def __repr__(self):
        zwróć "<built-in function %s>" % self.ml_name

klasa BuiltInMethodProxy(object):
    def __init__(self, ml_name, pyop_m_self):
        self.ml_name = ml_name
        self.pyop_m_self = pyop_m_self

    def __repr__(self):
        zwróć ('<built-in method %s of %s object at remote 0x%x>'
                % (self.ml_name,
                   self.pyop_m_self.safe_tp_name(),
                   self.pyop_m_self.as_address())
                )

klasa PyCFunctionObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyCFunctionObject*
    (see Include/methodobject.h oraz Objects/methodobject.c)
    """
    _typename = 'PyCFunctionObject'

    def proxyval(self, visited):
        m_ml = self.field('m_ml') # m_ml jest a (PyMethodDef*)
        ml_name = m_ml['ml_name'].string()

        pyop_m_self = self.pyop_field('m_self')
        jeżeli pyop_m_self.is_null():
            zwróć BuiltInFunctionProxy(ml_name)
        inaczej:
            zwróć BuiltInMethodProxy(ml_name, pyop_m_self)


klasa PyCodeObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyCodeObject* i.e. a <code> instance
    within the process being debugged.
    """
    _typename = 'PyCodeObject'

    def addr2line(self, addrq):
        '''
        Get the line number dla a given bytecode offset

        Analogous to PyCode_Addr2Line; translated z pseudocode w
        Objects/lnotab_notes.txt
        '''
        co_lnotab = self.pyop_field('co_lnotab').proxyval(set())

        # Initialize lineno to co_firstlineno jako per PyCode_Addr2Line
        # nie 0, jako lnotab_notes.txt has it:
        lineno = int_from_int(self.field('co_firstlineno'))

        addr = 0
        dla addr_incr, line_incr w zip(co_lnotab[::2], co_lnotab[1::2]):
            addr += ord(addr_incr)
            jeżeli addr > addrq:
                zwróć lineno
            lineno += ord(line_incr)
        zwróć lineno


klasa PyDictObjectPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyDictObject* i.e. a dict instance
    within the process being debugged.
    """
    _typename = 'PyDictObject'

    def iteritems(self):
        '''
        Yields a sequence of (PyObjectPtr key, PyObjectPtr value) pairs,
        analogous to dict.iteritems()
        '''
        keys = self.field('ma_keys')
        values = self.field('ma_values')
        dla i w safe_range(keys['dk_size']):
            ep = keys['dk_entries'].address + i
            jeżeli long(values):
                pyop_value = PyObjectPtr.from_pyobject_ptr(values[i])
            inaczej:
                pyop_value = PyObjectPtr.from_pyobject_ptr(ep['me_value'])
            jeżeli nie pyop_value.is_null():
                pyop_key = PyObjectPtr.from_pyobject_ptr(ep['me_key'])
                uzyskaj (pyop_key, pyop_value)

    def proxyval(self, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('{...}')
        visited.add(self.as_address())

        result = {}
        dla pyop_key, pyop_value w self.iteritems():
            proxy_key = pyop_key.proxyval(visited)
            proxy_value = pyop_value.proxyval(visited)
            result[proxy_key] = proxy_value
        zwróć result

    def write_repr(self, out, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('{...}')
            zwróć
        visited.add(self.as_address())

        out.write('{')
        first = Prawda
        dla pyop_key, pyop_value w self.iteritems():
            jeżeli nie first:
                out.write(', ')
            first = Nieprawda
            pyop_key.write_repr(out, visited)
            out.write(': ')
            pyop_value.write_repr(out, visited)
        out.write('}')

klasa PyListObjectPtr(PyObjectPtr):
    _typename = 'PyListObject'

    def __getitem__(self, i):
        # Get the gdb.Value dla the (PyObject*) przy the given index:
        field_ob_item = self.field('ob_item')
        zwróć field_ob_item[i]

    def proxyval(self, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('[...]')
        visited.add(self.as_address())

        result = [PyObjectPtr.from_pyobject_ptr(self[i]).proxyval(visited)
                  dla i w safe_range(int_from_int(self.field('ob_size')))]
        zwróć result

    def write_repr(self, out, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('[...]')
            zwróć
        visited.add(self.as_address())

        out.write('[')
        dla i w safe_range(int_from_int(self.field('ob_size'))):
            jeżeli i > 0:
                out.write(', ')
            element = PyObjectPtr.from_pyobject_ptr(self[i])
            element.write_repr(out, visited)
        out.write(']')

klasa PyLongObjectPtr(PyObjectPtr):
    _typename = 'PyLongObject'

    def proxyval(self, visited):
        '''
        Python's Include/longobjrep.h has this declaration:
           struct _longobject {
               PyObject_VAR_HEAD
               digit ob_digit[1];
           };

        przy this description:
            The absolute value of a number jest equal to
                 SUM(dla i=0 through abs(ob_size)-1) ob_digit[i] * 2**(SHIFT*i)
            Negative numbers are represented przy ob_size < 0;
            zero jest represented by ob_size == 0.

        where SHIFT can be either:
            #define PyLong_SHIFT        30
            #define PyLong_SHIFT        15
        '''
        ob_size = long(self.field('ob_size'))
        jeżeli ob_size == 0:
            zwróć 0

        ob_digit = self.field('ob_digit')

        jeżeli gdb.lookup_type('digit').sizeof == 2:
            SHIFT = 15
        inaczej:
            SHIFT = 30

        digits = [long(ob_digit[i]) * 2**(SHIFT*i)
                  dla i w safe_range(abs(ob_size))]
        result = sum(digits)
        jeżeli ob_size < 0:
            result = -result
        zwróć result

    def write_repr(self, out, visited):
        # Write this out jako a Python 3 int literal, i.e. without the "L" suffix
        proxy = self.proxyval(visited)
        out.write("%s" % proxy)


klasa PyBoolObjectPtr(PyLongObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyBoolObject* i.e. one of the two
    <bool> instances (Py_Prawda/Py_Nieprawda) within the process being debugged.
    """
    def proxyval(self, visited):
        jeżeli PyLongObjectPtr.proxyval(self, visited):
            zwróć Prawda
        inaczej:
            zwróć Nieprawda

klasa PyNicStructPtr(PyObjectPtr):
    """
    Class wrapping a gdb.Value that's a PyObject* pointing to the
    singleton (we hope) _Py_NicStruct przy ob_type PyNic_Type
    """
    _typename = 'PyObject'

    def proxyval(self, visited):
        zwróć Nic


klasa PyFrameObjectPtr(PyObjectPtr):
    _typename = 'PyFrameObject'

    def __init__(self, gdbval, cast_to=Nic):
        PyObjectPtr.__init__(self, gdbval, cast_to)

        jeżeli nie self.is_optimized_out():
            self.co = PyCodeObjectPtr.from_pyobject_ptr(self.field('f_code'))
            self.co_name = self.co.pyop_field('co_name')
            self.co_filename = self.co.pyop_field('co_filename')

            self.f_lineno = int_from_int(self.field('f_lineno'))
            self.f_lasti = int_from_int(self.field('f_lasti'))
            self.co_nlocals = int_from_int(self.co.field('co_nlocals'))
            self.co_varnames = PyTupleObjectPtr.from_pyobject_ptr(self.co.field('co_varnames'))

    def iter_locals(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the local variables of this frame
        '''
        jeżeli self.is_optimized_out():
            zwróć

        f_localsplus = self.field('f_localsplus')
        dla i w safe_range(self.co_nlocals):
            pyop_value = PyObjectPtr.from_pyobject_ptr(f_localsplus[i])
            jeżeli nie pyop_value.is_null():
                pyop_name = PyObjectPtr.from_pyobject_ptr(self.co_varnames[i])
                uzyskaj (pyop_name, pyop_value)

    def iter_globals(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the global variables of this frame
        '''
        jeżeli self.is_optimized_out():
            zwróć ()

        pyop_globals = self.pyop_field('f_globals')
        zwróć pyop_globals.iteritems()

    def iter_builtins(self):
        '''
        Yield a sequence of (name,value) pairs of PyObjectPtr instances, for
        the builtin variables
        '''
        jeżeli self.is_optimized_out():
            zwróć ()

        pyop_builtins = self.pyop_field('f_builtins')
        zwróć pyop_builtins.iteritems()

    def get_var_by_name(self, name):
        '''
        Look dla the named local variable, returning a (PyObjectPtr, scope) pair
        where scope jest a string 'local', 'global', 'builtin'

        If nie found, zwróć (Nic, Nic)
        '''
        dla pyop_name, pyop_value w self.iter_locals():
            jeżeli name == pyop_name.proxyval(set()):
                zwróć pyop_value, 'local'
        dla pyop_name, pyop_value w self.iter_globals():
            jeżeli name == pyop_name.proxyval(set()):
                zwróć pyop_value, 'global'
        dla pyop_name, pyop_value w self.iter_builtins():
            jeżeli name == pyop_name.proxyval(set()):
                zwróć pyop_value, 'builtin'
        zwróć Nic, Nic

    def filename(self):
        '''Get the path of the current Python source file, jako a string'''
        jeżeli self.is_optimized_out():
            zwróć '(frame information optimized out)'
        zwróć self.co_filename.proxyval(set())

    def current_line_num(self):
        '''Get current line number jako an integer (1-based)

        Translated z PyFrame_GetLineNumber oraz PyCode_Addr2Line

        See Objects/lnotab_notes.txt
        '''
        jeżeli self.is_optimized_out():
            zwróć Nic
        f_trace = self.field('f_trace')
        jeżeli long(f_trace) != 0:
            # we have a non-NULL f_trace:
            zwróć self.f_lineno
        inaczej:
            #spróbuj:
            zwróć self.co.addr2line(self.f_lasti)
            #wyjąwszy ValueError:
            #    zwróć self.f_lineno

    def current_line(self):
        '''Get the text of the current source line jako a string, przy a trailing
        newline character'''
        jeżeli self.is_optimized_out():
            zwróć '(frame information optimized out)'
        filename = self.filename()
        spróbuj:
            f = open(os_fsencode(filename), 'r')
        wyjąwszy IOError:
            zwróć Nic
        przy f:
            all_lines = f.readlines()
            # Convert z 1-based current_line_num to 0-based list offset:
            zwróć all_lines[self.current_line_num()-1]

    def write_repr(self, out, visited):
        jeżeli self.is_optimized_out():
            out.write('(frame information optimized out)')
            zwróć
        out.write('Frame 0x%x, dla file %s, line %i, w %s ('
                  % (self.as_address(),
                     self.co_filename.proxyval(visited),
                     self.current_line_num(),
                     self.co_name.proxyval(visited)))
        first = Prawda
        dla pyop_name, pyop_value w self.iter_locals():
            jeżeli nie first:
                out.write(', ')
            first = Nieprawda

            out.write(pyop_name.proxyval(visited))
            out.write('=')
            pyop_value.write_repr(out, visited)

        out.write(')')

    def print_traceback(self):
        jeżeli self.is_optimized_out():
            sys.stdout.write('  (frame information optimized out)\n')
            zwróć
        visited = set()
        sys.stdout.write('  File "%s", line %i, w %s\n'
                  % (self.co_filename.proxyval(visited),
                     self.current_line_num(),
                     self.co_name.proxyval(visited)))

klasa PySetObjectPtr(PyObjectPtr):
    _typename = 'PySetObject'

    @classmethod
    def _dummy_key(self):
        zwróć gdb.lookup_global_symbol('_PySet_Dummy').value()

    def __iter__(self):
        dummy_ptr = self._dummy_key()
        table = self.field('table')
        dla i w safe_range(self.field('mask') + 1):
            setentry = table[i]
            key = setentry['key']
            jeżeli key != 0 oraz key != dummy_ptr:
                uzyskaj PyObjectPtr.from_pyobject_ptr(key)

    def proxyval(self, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('%s(...)' % self.safe_tp_name())
        visited.add(self.as_address())

        members = (key.proxyval(visited) dla key w self)
        jeżeli self.safe_tp_name() == 'frozenset':
            zwróć frozenset(members)
        inaczej:
            zwróć set(members)

    def write_repr(self, out, visited):
        # Emulate Python 3's set_repr
        tp_name = self.safe_tp_name()

        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('(...)')
            zwróć
        visited.add(self.as_address())

        # Python 3's set_repr special-cases the empty set:
        jeżeli nie self.field('used'):
            out.write(tp_name)
            out.write('()')
            zwróć

        # Python 3 uses {} dla set literals:
        jeżeli tp_name != 'set':
            out.write(tp_name)
            out.write('(')

        out.write('{')
        first = Prawda
        dla key w self:
            jeżeli nie first:
                out.write(', ')
            first = Nieprawda
            key.write_repr(out, visited)
        out.write('}')

        jeżeli tp_name != 'set':
            out.write(')')


klasa PyBytesObjectPtr(PyObjectPtr):
    _typename = 'PyBytesObject'

    def __str__(self):
        field_ob_size = self.field('ob_size')
        field_ob_sval = self.field('ob_sval')
        char_ptr = field_ob_sval.address.cast(_type_unsigned_char_ptr)
        zwróć ''.join([chr(char_ptr[i]) dla i w safe_range(field_ob_size)])

    def proxyval(self, visited):
        zwróć str(self)

    def write_repr(self, out, visited):
        # Write this out jako a Python 3 bytes literal, i.e. przy a "b" prefix

        # Get a PyStringObject* within the Python 2 gdb process:
        proxy = self.proxyval(visited)

        # Transliteration of Python 3's Objects/bytesobject.c:PyBytes_Repr
        # to Python 2 code:
        quote = "'"
        jeżeli "'" w proxy oraz nie '"' w proxy:
            quote = '"'
        out.write('b')
        out.write(quote)
        dla byte w proxy:
            jeżeli byte == quote albo byte == '\\':
                out.write('\\')
                out.write(byte)
            albo_inaczej byte == '\t':
                out.write('\\t')
            albo_inaczej byte == '\n':
                out.write('\\n')
            albo_inaczej byte == '\r':
                out.write('\\r')
            albo_inaczej byte < ' ' albo ord(byte) >= 0x7f:
                out.write('\\x')
                out.write(hexdigits[(ord(byte) & 0xf0) >> 4])
                out.write(hexdigits[ord(byte) & 0xf])
            inaczej:
                out.write(byte)
        out.write(quote)

klasa PyTupleObjectPtr(PyObjectPtr):
    _typename = 'PyTupleObject'

    def __getitem__(self, i):
        # Get the gdb.Value dla the (PyObject*) przy the given index:
        field_ob_item = self.field('ob_item')
        zwróć field_ob_item[i]

    def proxyval(self, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            zwróć ProxyAlreadyVisited('(...)')
        visited.add(self.as_address())

        result = tuple([PyObjectPtr.from_pyobject_ptr(self[i]).proxyval(visited)
                        dla i w safe_range(int_from_int(self.field('ob_size')))])
        zwróć result

    def write_repr(self, out, visited):
        # Guard against infinite loops:
        jeżeli self.as_address() w visited:
            out.write('(...)')
            zwróć
        visited.add(self.as_address())

        out.write('(')
        dla i w safe_range(int_from_int(self.field('ob_size'))):
            jeżeli i > 0:
                out.write(', ')
            element = PyObjectPtr.from_pyobject_ptr(self[i])
            element.write_repr(out, visited)
        jeżeli self.field('ob_size') == 1:
            out.write(',)')
        inaczej:
            out.write(')')

klasa PyTypeObjectPtr(PyObjectPtr):
    _typename = 'PyTypeObject'


def _unichr_is_printable(char):
    # Logic adapted z Python 3's Tools/unicode/makeunicodedata.py
    jeżeli char == u" ":
        zwróć Prawda
    zaimportuj unicodedata
    zwróć unicodedata.category(char) nie w ("C", "Z")

jeżeli sys.maxunicode >= 0x10000:
    _unichr = unichr
inaczej:
    # Needed dla proper surrogate support jeżeli sizeof(Py_UNICODE) jest 2 w gdb
    def _unichr(x):
        jeżeli x < 0x10000:
            zwróć unichr(x)
        x -= 0x10000
        ch1 = 0xD800 | (x >> 10)
        ch2 = 0xDC00 | (x & 0x3FF)
        zwróć unichr(ch1) + unichr(ch2)


klasa PyUnicodeObjectPtr(PyObjectPtr):
    _typename = 'PyUnicodeObject'

    def char_width(self):
        _type_Py_UNICODE = gdb.lookup_type('Py_UNICODE')
        zwróć _type_Py_UNICODE.sizeof

    def proxyval(self, visited):
        global _is_pep393
        jeżeli _is_pep393 jest Nic:
            fields = gdb.lookup_type('PyUnicodeObject').target().fields()
            _is_pep393 = 'data' w [f.name dla f w fields]
        jeżeli _is_pep393:
            # Python 3.3 oraz newer
            may_have_surrogates = Nieprawda
            compact = self.field('_base')
            ascii = compact['_base']
            state = ascii['state']
            is_compact_ascii = (int(state['ascii']) oraz int(state['compact']))
            jeżeli nie int(state['ready']):
                # string jest nie ready
                field_length = long(compact['wstr_length'])
                may_have_surrogates = Prawda
                field_str = ascii['wstr']
            inaczej:
                field_length = long(ascii['length'])
                jeżeli is_compact_ascii:
                    field_str = ascii.address + 1
                albo_inaczej int(state['compact']):
                    field_str = compact.address + 1
                inaczej:
                    field_str = self.field('data')['any']
                repr_kind = int(state['kind'])
                jeżeli repr_kind == 1:
                    field_str = field_str.cast(_type_unsigned_char_ptr)
                albo_inaczej repr_kind == 2:
                    field_str = field_str.cast(_type_unsigned_short_ptr)
                albo_inaczej repr_kind == 4:
                    field_str = field_str.cast(_type_unsigned_int_ptr)
        inaczej:
            # Python 3.2 oraz earlier
            field_length = long(self.field('length'))
            field_str = self.field('str')
            may_have_surrogates = self.char_width() == 2

        # Gather a list of ints z the Py_UNICODE array; these are either
        # UCS-1, UCS-2 albo UCS-4 code points:
        jeżeli nie may_have_surrogates:
            Py_UNICODEs = [int(field_str[i]) dla i w safe_range(field_length)]
        inaczej:
            # A more elaborate routine jeżeli sizeof(Py_UNICODE) jest 2 w the
            # inferior process: we must join surrogate pairs.
            Py_UNICODEs = []
            i = 0
            limit = safety_limit(field_length)
            dopóki i < limit:
                ucs = int(field_str[i])
                i += 1
                jeżeli ucs < 0xD800 albo ucs >= 0xDC00 albo i == field_length:
                    Py_UNICODEs.append(ucs)
                    kontynuuj
                # This could be a surrogate pair.
                ucs2 = int(field_str[i])
                jeżeli ucs2 < 0xDC00 albo ucs2 > 0xDFFF:
                    kontynuuj
                code = (ucs & 0x03FF) << 10
                code |= ucs2 & 0x03FF
                code += 0x00010000
                Py_UNICODEs.append(code)
                i += 1

        # Convert the int code points to unicode characters, oraz generate a
        # local unicode instance.
        # This splits surrogate pairs jeżeli sizeof(Py_UNICODE) jest 2 here (in gdb).
        result = u''.join([
            (_unichr(ucs) jeżeli ucs <= 0x10ffff inaczej '\ufffd')
            dla ucs w Py_UNICODEs])
        zwróć result

    def write_repr(self, out, visited):
        # Write this out jako a Python 3 str literal, i.e. without a "u" prefix

        # Get a PyUnicodeObject* within the Python 2 gdb process:
        proxy = self.proxyval(visited)

        # Transliteration of Python 3's Object/unicodeobject.c:unicode_repr
        # to Python 2:
        jeżeli "'" w proxy oraz '"' nie w proxy:
            quote = '"'
        inaczej:
            quote = "'"
        out.write(quote)

        i = 0
        dopóki i < len(proxy):
            ch = proxy[i]
            i += 1

            # Escape quotes oraz backslashes
            jeżeli ch == quote albo ch == '\\':
                out.write('\\')
                out.write(ch)

            #  Map special whitespace to '\t', \n', '\r'
            albo_inaczej ch == '\t':
                out.write('\\t')
            albo_inaczej ch == '\n':
                out.write('\\n')
            albo_inaczej ch == '\r':
                out.write('\\r')

            # Map non-printable US ASCII to '\xhh' */
            albo_inaczej ch < ' ' albo ch == 0x7F:
                out.write('\\x')
                out.write(hexdigits[(ord(ch) >> 4) & 0x000F])
                out.write(hexdigits[ord(ch) & 0x000F])

            # Copy ASCII characters as-is
            albo_inaczej ord(ch) < 0x7F:
                out.write(ch)

            # Non-ASCII characters
            inaczej:
                ucs = ch
                ch2 = Nic
                jeżeli sys.maxunicode < 0x10000:
                    # If sizeof(Py_UNICODE) jest 2 here (in gdb), join
                    # surrogate pairs before calling _unichr_is_printable.
                    jeżeli (i < len(proxy)
                    oraz 0xD800 <= ord(ch) < 0xDC00 \
                    oraz 0xDC00 <= ord(proxy[i]) <= 0xDFFF):
                        ch2 = proxy[i]
                        ucs = ch + ch2
                        i += 1

                # Unfortuately, Python 2's unicode type doesn't seem
                # to expose the "isprintable" method
                printable = _unichr_is_printable(ucs)
                jeżeli printable:
                    spróbuj:
                        ucs.encode(ENCODING)
                    wyjąwszy UnicodeEncodeError:
                        printable = Nieprawda

                # Map Unicode whitespace oraz control characters
                # (categories Z* oraz C* wyjąwszy ASCII space)
                jeżeli nie printable:
                    jeżeli ch2 jest nie Nic:
                        # Match Python 3's representation of non-printable
                        # wide characters.
                        code = (ord(ch) & 0x03FF) << 10
                        code |= ord(ch2) & 0x03FF
                        code += 0x00010000
                    inaczej:
                        code = ord(ucs)

                    # Map 8-bit characters to '\\xhh'
                    jeżeli code <= 0xff:
                        out.write('\\x')
                        out.write(hexdigits[(code >> 4) & 0x000F])
                        out.write(hexdigits[code & 0x000F])
                    # Map 21-bit characters to '\U00xxxxxx'
                    albo_inaczej code >= 0x10000:
                        out.write('\\U')
                        out.write(hexdigits[(code >> 28) & 0x0000000F])
                        out.write(hexdigits[(code >> 24) & 0x0000000F])
                        out.write(hexdigits[(code >> 20) & 0x0000000F])
                        out.write(hexdigits[(code >> 16) & 0x0000000F])
                        out.write(hexdigits[(code >> 12) & 0x0000000F])
                        out.write(hexdigits[(code >> 8) & 0x0000000F])
                        out.write(hexdigits[(code >> 4) & 0x0000000F])
                        out.write(hexdigits[code & 0x0000000F])
                    # Map 16-bit characters to '\uxxxx'
                    inaczej:
                        out.write('\\u')
                        out.write(hexdigits[(code >> 12) & 0x000F])
                        out.write(hexdigits[(code >> 8) & 0x000F])
                        out.write(hexdigits[(code >> 4) & 0x000F])
                        out.write(hexdigits[code & 0x000F])
                inaczej:
                    # Copy characters as-is
                    out.write(ch)
                    jeżeli ch2 jest nie Nic:
                        out.write(ch2)

        out.write(quote)




def int_from_int(gdbval):
    zwróć int(str(gdbval))


def stringify(val):
    # TODO: repr() puts everything on one line; pformat can be nicer, but
    # can lead to v.long results; this function isolates the choice
    jeżeli Prawda:
        zwróć repr(val)
    inaczej:
        z pprint zaimportuj pformat
        zwróć pformat(val)


klasa PyObjectPtrPrinter:
    "Prints a (PyObject*)"

    def __init__ (self, gdbval):
        self.gdbval = gdbval

    def to_string (self):
        pyop = PyObjectPtr.from_pyobject_ptr(self.gdbval)
        jeżeli Prawda:
            zwróć pyop.get_truncated_repr(MAX_OUTPUT_LEN)
        inaczej:
            # Generate full proxy value then stringify it.
            # Doing so could be expensive
            proxyval = pyop.proxyval(set())
            zwróć stringify(proxyval)

def pretty_printer_lookup(gdbval):
    type = gdbval.type.unqualified()
    jeżeli type.code == gdb.TYPE_CODE_PTR:
        type = type.target().unqualified()
        t = str(type)
        jeżeli t w ("PyObject", "PyFrameObject", "PyUnicodeObject"):
            zwróć PyObjectPtrPrinter(gdbval)

"""
During development, I've been manually invoking the code w this way:
(gdb) python

zaimportuj sys
sys.path.append('/home/david/coding/python-gdb')
zaimportuj libpython
end

then reloading it after each edit like this:
(gdb) python reload(libpython)

The following code should ensure that the prettyprinter jest registered
jeżeli the code jest autoloaded by gdb when visiting libpython.so, provided
that this python file jest installed to the same path jako the library (or its
.debug file) plus a "-gdb.py" suffix, e.g:
  /usr/lib/libpython2.6.so.1.0-gdb.py
  /usr/lib/debug/usr/lib/libpython2.6.so.1.0.debug-gdb.py
"""
def register (obj):
    jeżeli obj jest Nic:
        obj = gdb

    # Wire up the pretty-printer
    obj.pretty_printers.append(pretty_printer_lookup)

register (gdb.current_objfile ())



# Unfortunately, the exact API exposed by the gdb module varies somewhat
# z build to build
# See http://bugs.python.org/issue8279?#msg102276

klasa Frame(object):
    '''
    Wrapper dla gdb.Frame, adding various methods
    '''
    def __init__(self, gdbframe):
        self._gdbframe = gdbframe

    def older(self):
        older = self._gdbframe.older()
        jeżeli older:
            zwróć Frame(older)
        inaczej:
            zwróć Nic

    def newer(self):
        newer = self._gdbframe.newer()
        jeżeli newer:
            zwróć Frame(newer)
        inaczej:
            zwróć Nic

    def select(self):
        '''If supported, select this frame oraz zwróć Prawda; zwróć Nieprawda jeżeli unsupported

        Not all builds have a gdb.Frame.select method; seems to be present on Fedora 12
        onwards, but absent on Ubuntu buildbot'''
        jeżeli nie hasattr(self._gdbframe, 'select'):
            print ('Unable to select frame: '
                   'this build of gdb does nie expose a gdb.Frame.select method')
            zwróć Nieprawda
        self._gdbframe.select()
        zwróć Prawda

    def get_index(self):
        '''Calculate index of frame, starting at 0 dla the newest frame within
        this thread'''
        index = 0
        # Go down until you reach the newest frame:
        iter_frame = self
        dopóki iter_frame.newer():
            index += 1
            iter_frame = iter_frame.newer()
        zwróć index

    # We divide frames into:
    #   - "python frames":
    #       - "bytecode frames" i.e. PyEval_EvalFrameEx
    #       - "other python frames": things that are of interest z a python
    #         POV, but aren't bytecode (e.g. GC, GIL)
    #   - everything inaczej

    def is_python_frame(self):
        '''Is this a PyEval_EvalFrameEx frame, albo some other important
        frame? (see is_other_python_frame dla what "important" means w this
        context)'''
        jeżeli self.is_evalframeex():
            zwróć Prawda
        jeżeli self.is_other_python_frame():
            zwróć Prawda
        zwróć Nieprawda

    def is_evalframeex(self):
        '''Is this a PyEval_EvalFrameEx frame?'''
        jeżeli self._gdbframe.name() == 'PyEval_EvalFrameEx':
            '''
            I believe we also need to filter on the inline
            struct frame_id.inline_depth, only regarding frames with
            an inline depth of 0 jako actually being this function

            So we reject those przy type gdb.INLINE_FRAME
            '''
            jeżeli self._gdbframe.type() == gdb.NORMAL_FRAME:
                # We have a PyEval_EvalFrameEx frame:
                zwróć Prawda

        zwróć Nieprawda

    def is_other_python_frame(self):
        '''Is this frame worth displaying w python backtraces?
        Examples:
          - waiting on the GIL
          - garbage-collecting
          - within a CFunction
         If it is, zwróć a descriptive string
         For other frames, zwróć Nieprawda
         '''
        jeżeli self.is_waiting_for_gil():
            zwróć 'Waiting dla the GIL'
        albo_inaczej self.is_gc_collect():
            zwróć 'Garbage-collecting'
        inaczej:
            # Detect invocations of PyCFunction instances:
            older = self.older()
            jeżeli older oraz older._gdbframe.name() == 'PyCFunction_Call':
                # Within that frame:
                #   "func" jest the local containing the PyObject* of the
                # PyCFunctionObject instance
                #   "f" jest the same value, but cast to (PyCFunctionObject*)
                #   "self" jest the (PyObject*) of the 'self'
                spróbuj:
                    # Use the prettyprinter dla the func:
                    func = older._gdbframe.read_var('func')
                    zwróć str(func)
                wyjąwszy RuntimeError:
                    zwróć 'PyCFunction invocation (unable to read "func")'

        # This frame isn't worth reporting:
        zwróć Nieprawda

    def is_waiting_for_gil(self):
        '''Is this frame waiting on the GIL?'''
        # This assumes the _POSIX_THREADS version of Python/ceval_gil.h:
        name = self._gdbframe.name()
        jeżeli name:
            zwróć 'pthread_cond_timedwait' w name

    def is_gc_collect(self):
        '''Is this frame "collect" within the garbage-collector?'''
        zwróć self._gdbframe.name() == 'collect'

    def get_pyop(self):
        spróbuj:
            f = self._gdbframe.read_var('f')
            frame = PyFrameObjectPtr.from_pyobject_ptr(f)
            jeżeli nie frame.is_optimized_out():
                zwróć frame
            # gdb jest unable to get the "f" argument of PyEval_EvalFrameEx()
            # because it was "optimized out". Try to get "f" z the frame
            # of the caller, PyEval_EvalCodeEx().
            orig_frame = frame
            caller = self._gdbframe.older()
            jeżeli caller:
                f = caller.read_var('f')
                frame = PyFrameObjectPtr.from_pyobject_ptr(f)
                jeżeli nie frame.is_optimized_out():
                    zwróć frame
            zwróć orig_frame
        wyjąwszy ValueError:
            zwróć Nic

    @classmethod
    def get_selected_frame(cls):
        _gdbframe = gdb.selected_frame()
        jeżeli _gdbframe:
            zwróć Frame(_gdbframe)
        zwróć Nic

    @classmethod
    def get_selected_python_frame(cls):
        '''Try to obtain the Frame dla the python-related code w the selected
        frame, albo Nic'''
        frame = cls.get_selected_frame()

        dopóki frame:
            jeżeli frame.is_python_frame():
                zwróć frame
            frame = frame.older()

        # Not found:
        zwróć Nic

    @classmethod
    def get_selected_bytecode_frame(cls):
        '''Try to obtain the Frame dla the python bytecode interpreter w the
        selected GDB frame, albo Nic'''
        frame = cls.get_selected_frame()

        dopóki frame:
            jeżeli frame.is_evalframeex():
                zwróć frame
            frame = frame.older()

        # Not found:
        zwróć Nic

    def print_summary(self):
        jeżeli self.is_evalframeex():
            pyop = self.get_pyop()
            jeżeli pyop:
                line = pyop.get_truncated_repr(MAX_OUTPUT_LEN)
                write_unicode(sys.stdout, '#%i %s\n' % (self.get_index(), line))
                jeżeli nie pyop.is_optimized_out():
                    line = pyop.current_line()
                    jeżeli line jest nie Nic:
                        sys.stdout.write('    %s\n' % line.strip())
            inaczej:
                sys.stdout.write('#%i (unable to read python frame information)\n' % self.get_index())
        inaczej:
            info = self.is_other_python_frame()
            jeżeli info:
                sys.stdout.write('#%i %s\n' % (self.get_index(), info))
            inaczej:
                sys.stdout.write('#%i\n' % self.get_index())

    def print_traceback(self):
        jeżeli self.is_evalframeex():
            pyop = self.get_pyop()
            jeżeli pyop:
                pyop.print_traceback()
                jeżeli nie pyop.is_optimized_out():
                    line = pyop.current_line()
                    jeżeli line jest nie Nic:
                        sys.stdout.write('    %s\n' % line.strip())
            inaczej:
                sys.stdout.write('  (unable to read python frame information)\n')
        inaczej:
            info = self.is_other_python_frame()
            jeżeli info:
                sys.stdout.write('  %s\n' % info)
            inaczej:
                sys.stdout.write('  (nie a python frame)\n')

klasa PyList(gdb.Command):
    '''List the current Python source code, jeżeli any

    Use
       py-list START
    to list at a different line number within the python source.

    Use
       py-list START, END
    to list a specific range of lines within the python source.
    '''

    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-list",
                              gdb.COMMAND_FILES,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        zaimportuj re

        start = Nic
        end = Nic

        m = re.match(r'\s*(\d+)\s*', args)
        jeżeli m:
            start = int(m.group(0))
            end = start + 10

        m = re.match(r'\s*(\d+)\s*,\s*(\d+)\s*', args)
        jeżeli m:
            start, end = map(int, m.groups())

        # py-list requires an actual PyEval_EvalFrameEx frame:
        frame = Frame.get_selected_bytecode_frame()
        jeżeli nie frame:
            print('Unable to locate gdb frame dla python bytecode interpreter')
            zwróć

        pyop = frame.get_pyop()
        jeżeli nie pyop albo pyop.is_optimized_out():
            print('Unable to read information on python frame')
            zwróć

        filename = pyop.filename()
        lineno = pyop.current_line_num()

        jeżeli start jest Nic:
            start = lineno - 5
            end = lineno + 5

        jeżeli start<1:
            start = 1

        spróbuj:
            f = open(os_fsencode(filename), 'r')
        wyjąwszy IOError jako err:
            sys.stdout.write('Unable to open %s: %s\n'
                             % (filename, err))
            zwróć
        przy f:
            all_lines = f.readlines()
            # start oraz end are 1-based, all_lines jest 0-based;
            # so [start-1:end] jako a python slice gives us [start, end] jako a
            # closed interval
            dla i, line w enumerate(all_lines[start-1:end]):
                linestr = str(i+start)
                # Highlight current line:
                jeżeli i + start == lineno:
                    linestr = '>' + linestr
                sys.stdout.write('%4s    %s' % (linestr, line))


# ...and register the command:
PyList()

def move_in_stack(move_up):
    '''Move up albo down the stack (dla the py-up/py-down command)'''
    frame = Frame.get_selected_python_frame()
    dopóki frame:
        jeżeli move_up:
            iter_frame = frame.older()
        inaczej:
            iter_frame = frame.newer()

        jeżeli nie iter_frame:
            przerwij

        jeżeli iter_frame.is_python_frame():
            # Result:
            jeżeli iter_frame.select():
                iter_frame.print_summary()
            zwróć

        frame = iter_frame

    jeżeli move_up:
        print('Unable to find an older python frame')
    inaczej:
        print('Unable to find a newer python frame')

klasa PyUp(gdb.Command):
    'Select oraz print the python stack frame that called this one (jeżeli any)'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-up",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        move_in_stack(move_up=Prawda)

klasa PyDown(gdb.Command):
    'Select oraz print the python stack frame called by this one (jeżeli any)'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-down",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        move_in_stack(move_up=Nieprawda)

# Not all builds of gdb have gdb.Frame.select
jeżeli hasattr(gdb.Frame, 'select'):
    PyUp()
    PyDown()

klasa PyBacktraceFull(gdb.Command):
    'Display the current python frame oraz all the frames within its call stack (jeżeli any)'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-bt-full",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        frame = Frame.get_selected_python_frame()
        dopóki frame:
            jeżeli frame.is_python_frame():
                frame.print_summary()
            frame = frame.older()

PyBacktraceFull()

klasa PyBacktrace(gdb.Command):
    'Display the current python frame oraz all the frames within its call stack (jeżeli any)'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-bt",
                              gdb.COMMAND_STACK,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        sys.stdout.write('Traceback (most recent call first):\n')
        frame = Frame.get_selected_python_frame()
        dopóki frame:
            jeżeli frame.is_python_frame():
                frame.print_traceback()
            frame = frame.older()

PyBacktrace()

klasa PyPrint(gdb.Command):
    'Look up the given python variable name, oraz print it'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-print",
                              gdb.COMMAND_DATA,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        name = str(args)

        frame = Frame.get_selected_python_frame()
        jeżeli nie frame:
            print('Unable to locate python frame')
            zwróć

        pyop_frame = frame.get_pyop()
        jeżeli nie pyop_frame:
            print('Unable to read information on python frame')
            zwróć

        pyop_var, scope = pyop_frame.get_var_by_name(name)

        jeżeli pyop_var:
            print('%s %r = %s'
                   % (scope,
                      name,
                      pyop_var.get_truncated_repr(MAX_OUTPUT_LEN)))
        inaczej:
            print('%r nie found' % name)

PyPrint()

klasa PyLocals(gdb.Command):
    'Look up the given python variable name, oraz print it'
    def __init__(self):
        gdb.Command.__init__ (self,
                              "py-locals",
                              gdb.COMMAND_DATA,
                              gdb.COMPLETE_NONE)


    def invoke(self, args, from_tty):
        name = str(args)

        frame = Frame.get_selected_python_frame()
        jeżeli nie frame:
            print('Unable to locate python frame')
            zwróć

        pyop_frame = frame.get_pyop()
        jeżeli nie pyop_frame:
            print('Unable to read information on python frame')
            zwróć

        dla pyop_name, pyop_value w pyop_frame.iter_locals():
            print('%s = %s'
                   % (pyop_name.proxyval(set()),
                      pyop_value.get_truncated_repr(MAX_OUTPUT_LEN)))

PyLocals()
