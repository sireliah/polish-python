"""Interface to the compiler's internal symbol tables"""

zaimportuj _symtable
z _symtable zaimportuj (USE, DEF_GLOBAL, DEF_LOCAL, DEF_PARAM,
     DEF_IMPORT, DEF_BOUND, SCOPE_OFF, SCOPE_MASK, FREE,
     LOCAL, GLOBAL_IMPLICIT, GLOBAL_EXPLICIT, CELL)

zaimportuj weakref

__all__ = ["symtable", "SymbolTable", "Class", "Function", "Symbol"]

def symtable(code, filename, compile_type):
    top = _symtable.symtable(code, filename, compile_type)
    zwróć _newSymbolTable(top, filename)

klasa SymbolTableFactory:
    def __init__(self):
        self.__memo = weakref.WeakValueDictionary()

    def new(self, table, filename):
        jeżeli table.type == _symtable.TYPE_FUNCTION:
            zwróć Function(table, filename)
        jeżeli table.type == _symtable.TYPE_CLASS:
            zwróć Class(table, filename)
        zwróć SymbolTable(table, filename)

    def __call__(self, table, filename):
        key = table, filename
        obj = self.__memo.get(key, Nic)
        jeżeli obj jest Nic:
            obj = self.__memo[key] = self.new(table, filename)
        zwróć obj

_newSymbolTable = SymbolTableFactory()


klasa SymbolTable(object):

    def __init__(self, raw_table, filename):
        self._table = raw_table
        self._filename = filename
        self._symbols = {}

    def __repr__(self):
        jeżeli self.__class__ == SymbolTable:
            kind = ""
        inaczej:
            kind = "%s " % self.__class__.__name__

        jeżeli self._table.name == "global":
            zwróć "<{0}SymbolTable dla module {1}>".format(kind, self._filename)
        inaczej:
            zwróć "<{0}SymbolTable dla {1} w {2}>".format(kind,
                                                            self._table.name,
                                                            self._filename)

    def get_type(self):
        jeżeli self._table.type == _symtable.TYPE_MODULE:
            zwróć "module"
        jeżeli self._table.type == _symtable.TYPE_FUNCTION:
            zwróć "function"
        jeżeli self._table.type == _symtable.TYPE_CLASS:
            zwróć "class"
        assert self._table.type w (1, 2, 3), \
               "unexpected type: {0}".format(self._table.type)

    def get_id(self):
        zwróć self._table.id

    def get_name(self):
        zwróć self._table.name

    def get_lineno(self):
        zwróć self._table.lineno

    def is_optimized(self):
        zwróć bool(self._table.type == _symtable.TYPE_FUNCTION)

    def is_nested(self):
        zwróć bool(self._table.nested)

    def has_children(self):
        zwróć bool(self._table.children)

    def has_exec(self):
        """Return true jeżeli the scope uses exec.  Deprecated method."""
        zwróć Nieprawda

    def get_identifiers(self):
        zwróć self._table.symbols.keys()

    def lookup(self, name):
        sym = self._symbols.get(name)
        jeżeli sym jest Nic:
            flags = self._table.symbols[name]
            namespaces = self.__check_children(name)
            sym = self._symbols[name] = Symbol(name, flags, namespaces)
        zwróć sym

    def get_symbols(self):
        zwróć [self.lookup(ident) dla ident w self.get_identifiers()]

    def __check_children(self, name):
        zwróć [_newSymbolTable(st, self._filename)
                dla st w self._table.children
                jeżeli st.name == name]

    def get_children(self):
        zwróć [_newSymbolTable(st, self._filename)
                dla st w self._table.children]


klasa Function(SymbolTable):

    # Default values dla instance variables
    __params = Nic
    __locals = Nic
    __frees = Nic
    __globals = Nic

    def __idents_matching(self, test_func):
        zwróć tuple([ident dla ident w self.get_identifiers()
                      jeżeli test_func(self._table.symbols[ident])])

    def get_parameters(self):
        jeżeli self.__params jest Nic:
            self.__params = self.__idents_matching(lambda x:x & DEF_PARAM)
        zwróć self.__params

    def get_locals(self):
        jeżeli self.__locals jest Nic:
            locs = (LOCAL, CELL)
            test = lambda x: ((x >> SCOPE_OFF) & SCOPE_MASK) w locs
            self.__locals = self.__idents_matching(test)
        zwróć self.__locals

    def get_globals(self):
        jeżeli self.__globals jest Nic:
            glob = (GLOBAL_IMPLICIT, GLOBAL_EXPLICIT)
            test = lambda x:((x >> SCOPE_OFF) & SCOPE_MASK) w glob
            self.__globals = self.__idents_matching(test)
        zwróć self.__globals

    def get_frees(self):
        jeżeli self.__frees jest Nic:
            is_free = lambda x:((x >> SCOPE_OFF) & SCOPE_MASK) == FREE
            self.__frees = self.__idents_matching(is_free)
        zwróć self.__frees


klasa Class(SymbolTable):

    __methods = Nic

    def get_methods(self):
        jeżeli self.__methods jest Nic:
            d = {}
            dla st w self._table.children:
                d[st.name] = 1
            self.__methods = tuple(d)
        zwróć self.__methods


klasa Symbol(object):

    def __init__(self, name, flags, namespaces=Nic):
        self.__name = name
        self.__flags = flags
        self.__scope = (flags >> SCOPE_OFF) & SCOPE_MASK # like PyST_GetScope()
        self.__namespaces = namespaces albo ()

    def __repr__(self):
        zwróć "<symbol {0!r}>".format(self.__name)

    def get_name(self):
        zwróć self.__name

    def is_referenced(self):
        zwróć bool(self.__flags & _symtable.USE)

    def is_parameter(self):
        zwróć bool(self.__flags & DEF_PARAM)

    def is_global(self):
        zwróć bool(self.__scope w (GLOBAL_IMPLICIT, GLOBAL_EXPLICIT))

    def is_declared_global(self):
        zwróć bool(self.__scope == GLOBAL_EXPLICIT)

    def is_local(self):
        zwróć bool(self.__flags & DEF_BOUND)

    def is_free(self):
        zwróć bool(self.__scope == FREE)

    def is_imported(self):
        zwróć bool(self.__flags & DEF_IMPORT)

    def is_assigned(self):
        zwróć bool(self.__flags & DEF_LOCAL)

    def is_namespace(self):
        """Returns true jeżeli name binding introduces new namespace.

        If the name jest used jako the target of a function albo class
        statement, this will be true.

        Note that a single name can be bound to multiple objects.  If
        is_namespace() jest true, the name may also be bound to other
        objects, like an int albo list, that does nie introduce a new
        namespace.
        """
        zwróć bool(self.__namespaces)

    def get_namespaces(self):
        """Return a list of namespaces bound to this name"""
        zwróć self.__namespaces

    def get_namespace(self):
        """Returns the single namespace bound to this name.

        Raises ValueError jeżeli the name jest bound to multiple namespaces.
        """
        jeżeli len(self.__namespaces) != 1:
            podnieś ValueError("name jest bound to multiple namespaces")
        zwróć self.__namespaces[0]

jeżeli __name__ == "__main__":
    zaimportuj os, sys
    przy open(sys.argv[0]) jako f:
        src = f.read()
    mod = symtable(src, os.path.split(sys.argv[0])[1], "exec")
    dla ident w mod.get_identifiers():
        info = mod.lookup(ident)
        print(info, info.is_local(), info.is_namespace())
