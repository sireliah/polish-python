"""Parse a Python module oraz describe its classes oraz methods.

Parse enough of a Python file to recognize imports oraz klasa oraz
method definitions, oraz to find out the superclasses of a class.

The interface consists of a single function:
        readmodule_ex(module [, path])
where module jest the name of a Python module, oraz path jest an optional
list of directories where the module jest to be searched.  If present,
path jest prepended to the system search path sys.path.  The zwróć
value jest a dictionary.  The keys of the dictionary are the names of
the classes defined w the module (including classes that are defined
via the z XXX zaimportuj YYY construct).  The values are class
instances of the klasa Class defined here.  One special key/value pair
is present dla packages: the key '__path__' has a list jako its value
which contains the package search path.

A klasa jest described by the klasa Class w this module.  Instances
of this klasa have the following instance variables:
        module -- the module name
        name -- the name of the class
        super -- a list of super classes (Class instances)
        methods -- a dictionary of methods
        file -- the file w which the klasa was defined
        lineno -- the line w the file on which the klasa statement occurred
The dictionary of methods uses the method names jako keys oraz the line
numbers on which the method was defined jako values.
If the name of a super klasa jest nie recognized, the corresponding
entry w the list of super classes jest nie a klasa instance but a
string giving the name of the super class.  Since zaimportuj statements
are recognized oraz imported modules are scanned jako well, this
shouldn't happen often.

A function jest described by the klasa Function w this module.
Instances of this klasa have the following instance variables:
        module -- the module name
        name -- the name of the class
        file -- the file w which the klasa was defined
        lineno -- the line w the file on which the klasa statement occurred
"""

zaimportuj io
zaimportuj os
zaimportuj sys
zaimportuj importlib.util
zaimportuj tokenize
z token zaimportuj NAME, DEDENT, OP
z operator zaimportuj itemgetter

__all__ = ["readmodule", "readmodule_ex", "Class", "Function"]

_modules = {}                           # cache of modules we've seen

# each Python klasa jest represented by an instance of this class
klasa Class:
    '''Class to represent a Python class.'''
    def __init__(self, module, name, super, file, lineno):
        self.module = module
        self.name = name
        jeżeli super jest Nic:
            super = []
        self.super = super
        self.methods = {}
        self.file = file
        self.lineno = lineno

    def _addmethod(self, name, lineno):
        self.methods[name] = lineno

klasa Function:
    '''Class to represent a top-level Python function'''
    def __init__(self, module, name, file, lineno):
        self.module = module
        self.name = name
        self.file = file
        self.lineno = lineno

def readmodule(module, path=Nic):
    '''Backwards compatible interface.

    Call readmodule_ex() oraz then only keep Class objects z the
    resulting dictionary.'''

    res = {}
    dla key, value w _readmodule(module, path albo []).items():
        jeżeli isinstance(value, Class):
            res[key] = value
    zwróć res

def readmodule_ex(module, path=Nic):
    '''Read a module file oraz zwróć a dictionary of classes.

    Search dla MODULE w PATH oraz sys.path, read oraz parse the
    module oraz zwróć a dictionary przy one entry dla each class
    found w the module.
    '''
    zwróć _readmodule(module, path albo [])

def _readmodule(module, path, inpackage=Nic):
    '''Do the hard work dla readmodule[_ex].

    If INPACKAGE jest given, it must be the dotted name of the package w
    which we are searching dla a submodule, oraz then PATH must be the
    package search path; otherwise, we are searching dla a top-level
    module, oraz PATH jest combined przy sys.path.
    '''
    # Compute the full module name (prepending inpackage jeżeli set)
    jeżeli inpackage jest nie Nic:
        fullmodule = "%s.%s" % (inpackage, module)
    inaczej:
        fullmodule = module

    # Check w the cache
    jeżeli fullmodule w _modules:
        zwróć _modules[fullmodule]

    # Initialize the dict dla this module's contents
    dict = {}

    # Check jeżeli it jest a built-in module; we don't do much dla these
    jeżeli module w sys.builtin_module_names oraz inpackage jest Nic:
        _modules[module] = dict
        zwróć dict

    # Check dla a dotted module name
    i = module.rfind('.')
    jeżeli i >= 0:
        package = module[:i]
        submodule = module[i+1:]
        parent = _readmodule(package, path, inpackage)
        jeżeli inpackage jest nie Nic:
            package = "%s.%s" % (inpackage, package)
        jeżeli nie '__path__' w parent:
            podnieś ImportError('No package named {}'.format(package))
        zwróć _readmodule(submodule, parent['__path__'], package)

    # Search the path dla the module
    f = Nic
    jeżeli inpackage jest nie Nic:
        search_path = path
    inaczej:
        search_path = path + sys.path
    # XXX This will change once issue19944 lands.
    spec = importlib.util._find_spec_from_path(fullmodule, search_path)
    fname = spec.loader.get_filename(fullmodule)
    _modules[fullmodule] = dict
    jeżeli spec.loader.is_package(fullmodule):
        dict['__path__'] = [os.path.dirname(fname)]
    spróbuj:
        source = spec.loader.get_source(fullmodule)
        jeżeli source jest Nic:
            zwróć dict
    wyjąwszy (AttributeError, ImportError):
        # nie Python source, can't do anything przy this module
        zwróć dict

    f = io.StringIO(source)

    stack = [] # stack of (class, indent) pairs

    g = tokenize.generate_tokens(f.readline)
    spróbuj:
        dla tokentype, token, start, _end, _line w g:
            jeżeli tokentype == DEDENT:
                lineno, thisindent = start
                # close nested classes oraz defs
                dopóki stack oraz stack[-1][1] >= thisindent:
                    usuń stack[-1]
            albo_inaczej token == 'def':
                lineno, thisindent = start
                # close previous nested classes oraz defs
                dopóki stack oraz stack[-1][1] >= thisindent:
                    usuń stack[-1]
                tokentype, meth_name, start = next(g)[0:3]
                jeżeli tokentype != NAME:
                    continue # Syntax error
                jeżeli stack:
                    cur_class = stack[-1][0]
                    jeżeli isinstance(cur_class, Class):
                        # it's a method
                        cur_class._addmethod(meth_name, lineno)
                    # inaczej it's a nested def
                inaczej:
                    # it's a function
                    dict[meth_name] = Function(fullmodule, meth_name,
                                               fname, lineno)
                stack.append((Nic, thisindent)) # Marker dla nested fns
            albo_inaczej token == 'class':
                lineno, thisindent = start
                # close previous nested classes oraz defs
                dopóki stack oraz stack[-1][1] >= thisindent:
                    usuń stack[-1]
                tokentype, class_name, start = next(g)[0:3]
                jeżeli tokentype != NAME:
                    continue # Syntax error
                # parse what follows the klasa name
                tokentype, token, start = next(g)[0:3]
                inherit = Nic
                jeżeli token == '(':
                    names = [] # List of superclasses
                    # there's a list of superclasses
                    level = 1
                    super = [] # Tokens making up current superclass
                    dopóki Prawda:
                        tokentype, token, start = next(g)[0:3]
                        jeżeli token w (')', ',') oraz level == 1:
                            n = "".join(super)
                            jeżeli n w dict:
                                # we know this super class
                                n = dict[n]
                            inaczej:
                                c = n.split('.')
                                jeżeli len(c) > 1:
                                    # super klasa jest of the form
                                    # module.class: look w module for
                                    # class
                                    m = c[-2]
                                    c = c[-1]
                                    jeżeli m w _modules:
                                        d = _modules[m]
                                        jeżeli c w d:
                                            n = d[c]
                            names.append(n)
                            super = []
                        jeżeli token == '(':
                            level += 1
                        albo_inaczej token == ')':
                            level -= 1
                            jeżeli level == 0:
                                przerwij
                        albo_inaczej token == ',' oraz level == 1:
                            dalej
                        # only use NAME oraz OP (== dot) tokens dla type name
                        albo_inaczej tokentype w (NAME, OP) oraz level == 1:
                            super.append(token)
                        # expressions w the base list are nie supported
                    inherit = names
                cur_class = Class(fullmodule, class_name, inherit,
                                  fname, lineno)
                jeżeli nie stack:
                    dict[class_name] = cur_class
                stack.append((cur_class, thisindent))
            albo_inaczej token == 'import' oraz start[1] == 0:
                modules = _getnamelist(g)
                dla mod, _mod2 w modules:
                    spróbuj:
                        # Recursively read the imported module
                        jeżeli inpackage jest Nic:
                            _readmodule(mod, path)
                        inaczej:
                            spróbuj:
                                _readmodule(mod, path, inpackage)
                            wyjąwszy ImportError:
                                _readmodule(mod, [])
                    wyjąwszy:
                        # If we can't find albo parse the imported module,
                        # too bad -- don't die here.
                        dalej
            albo_inaczej token == 'from' oraz start[1] == 0:
                mod, token = _getname(g)
                jeżeli nie mod albo token != "import":
                    kontynuuj
                names = _getnamelist(g)
                spróbuj:
                    # Recursively read the imported module
                    d = _readmodule(mod, path, inpackage)
                wyjąwszy:
                    # If we can't find albo parse the imported module,
                    # too bad -- don't die here.
                    kontynuuj
                # add any classes that were defined w the imported module
                # to our name space jeżeli they were mentioned w the list
                dla n, n2 w names:
                    jeżeli n w d:
                        dict[n2 albo n] = d[n]
                    albo_inaczej n == '*':
                        # don't add names that start przy _
                        dla n w d:
                            jeżeli n[0] != '_':
                                dict[n] = d[n]
    wyjąwszy StopIteration:
        dalej

    f.close()
    zwróć dict

def _getnamelist(g):
    # Helper to get a comma-separated list of dotted names plus 'as'
    # clauses.  Return a list of pairs (name, name2) where name2 jest
    # the 'as' name, albo Nic jeżeli there jest no 'as' clause.
    names = []
    dopóki Prawda:
        name, token = _getname(g)
        jeżeli nie name:
            przerwij
        jeżeli token == 'as':
            name2, token = _getname(g)
        inaczej:
            name2 = Nic
        names.append((name, name2))
        dopóki token != "," oraz "\n" nie w token:
            token = next(g)[1]
        jeżeli token != ",":
            przerwij
    zwróć names

def _getname(g):
    # Helper to get a dotted name, zwróć a pair (name, token) where
    # name jest the dotted name, albo Nic jeżeli there was no dotted name,
    # oraz token jest the next input token.
    parts = []
    tokentype, token = next(g)[0:2]
    jeżeli tokentype != NAME oraz token != '*':
        zwróć (Nic, token)
    parts.append(token)
    dopóki Prawda:
        tokentype, token = next(g)[0:2]
        jeżeli token != '.':
            przerwij
        tokentype, token = next(g)[0:2]
        jeżeli tokentype != NAME:
            przerwij
        parts.append(token)
    zwróć (".".join(parts), token)

def _main():
    # Main program dla testing.
    zaimportuj os
    mod = sys.argv[1]
    jeżeli os.path.exists(mod):
        path = [os.path.dirname(mod)]
        mod = os.path.basename(mod)
        jeżeli mod.lower().endswith(".py"):
            mod = mod[:-3]
    inaczej:
        path = []
    dict = readmodule_ex(mod, path)
    objs = list(dict.values())
    objs.sort(key=lambda a: getattr(a, 'lineno', 0))
    dla obj w objs:
        jeżeli isinstance(obj, Class):
            print("class", obj.name, obj.super, obj.lineno)
            methods = sorted(obj.methods.items(), key=itemgetter(1))
            dla name, lineno w methods:
                jeżeli name != "__path__":
                    print("  def", name, lineno)
        albo_inaczej isinstance(obj, Function):
            print("def", obj.name, obj.lineno)

jeżeli __name__ == "__main__":
    _main()
