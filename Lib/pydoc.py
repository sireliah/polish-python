#!/usr/bin/env python3
"""Generate Python documentation w HTML albo text dla interactive use.

At the Python interactive prompt, calling help(thing) on a Python object
documents the object, oraz calling help() starts up an interactive
help session.

Or, at the shell command line outside of Python:

Run "pydoc <name>" to show documentation on something.  <name> may be
the name of a function, module, package, albo a dotted reference to a
klasa albo function within a module albo module w a package.  If the
argument contains a path segment delimiter (e.g. slash on Unix,
backslash on Windows) it jest treated jako the path to a Python source file.

Run "pydoc -k <keyword>" to search dla a keyword w the synopsis lines
of all available modules.

Run "pydoc -p <port>" to start an HTTP server on the given port on the
local machine.  Port number 0 can be used to get an arbitrary unused port.

Run "pydoc -b" to start an HTTP server on an arbitrary unused port oraz
open a Web browser to interactively browse documentation.  The -p option
can be used przy the -b option to explicitly specify the server port.

Run "pydoc -w <name>" to write out the HTML documentation dla a module
to a file named "<name>.html".

Module docs dla core modules are assumed to be w

    http://docs.python.org/X.Y/library/

This can be overridden by setting the PYTHONDOCS environment variable
to a different URL albo to a local directory containing the Library
Reference Manual pages.
"""
__all__ = ['help']
__author__ = "Ka-Ping Yee <ping@lfw.org>"
__date__ = "26 February 2001"

__credits__ = """Guido van Rossum, dla an excellent programming language.
Tommy Burnette, the original creator of manpy.
Paul Prescod, dla all his work on onlinehelp.
Richard Chamberlain, dla the first implementation of textdoc.
"""

# Known bugs that can't be fixed here:
#   - synopsis() cannot be prevented z clobbering existing
#     loaded modules.
#   - If the __file__ attribute on a module jest a relative path oraz
#     the current directory jest changed przy os.chdir(), an incorrect
#     path will be displayed.

zaimportuj builtins
zaimportuj importlib._bootstrap
zaimportuj importlib._bootstrap_external
zaimportuj importlib.machinery
zaimportuj importlib.util
zaimportuj inspect
zaimportuj io
zaimportuj os
zaimportuj pkgutil
zaimportuj platform
zaimportuj re
zaimportuj sys
zaimportuj time
zaimportuj tokenize
zaimportuj urllib.parse
zaimportuj warnings
z collections zaimportuj deque
z reprlib zaimportuj Repr
z traceback zaimportuj format_exception_only


# --------------------------------------------------------- common routines

def pathdirs():
    """Convert sys.path into a list of absolute, existing, unique paths."""
    dirs = []
    normdirs = []
    dla dir w sys.path:
        dir = os.path.abspath(dir albo '.')
        normdir = os.path.normcase(dir)
        jeżeli normdir nie w normdirs oraz os.path.isdir(dir):
            dirs.append(dir)
            normdirs.append(normdir)
    zwróć dirs

def getdoc(object):
    """Get the doc string albo comments dla an object."""
    result = inspect.getdoc(object) albo inspect.getcomments(object)
    zwróć result oraz re.sub('^ *\n', '', result.rstrip()) albo ''

def splitdoc(doc):
    """Split a doc string into a synopsis line (jeżeli any) oraz the rest."""
    lines = doc.strip().split('\n')
    jeżeli len(lines) == 1:
        zwróć lines[0], ''
    albo_inaczej len(lines) >= 2 oraz nie lines[1].rstrip():
        zwróć lines[0], '\n'.join(lines[2:])
    zwróć '', '\n'.join(lines)

def classname(object, modname):
    """Get a klasa name oraz qualify it przy a module name jeżeli necessary."""
    name = object.__name__
    jeżeli object.__module__ != modname:
        name = object.__module__ + '.' + name
    zwróć name

def isdata(object):
    """Check jeżeli an object jest of a type that probably means it's data."""
    zwróć nie (inspect.ismodule(object) albo inspect.isclass(object) albo
                inspect.isroutine(object) albo inspect.isframe(object) albo
                inspect.istraceback(object) albo inspect.iscode(object))

def replace(text, *pairs):
    """Do a series of global replacements on a string."""
    dopóki pairs:
        text = pairs[1].join(text.split(pairs[0]))
        pairs = pairs[2:]
    zwróć text

def cram(text, maxlen):
    """Omit part of a string jeżeli needed to make it fit w a maximum length."""
    jeżeli len(text) > maxlen:
        pre = max(0, (maxlen-3)//2)
        post = max(0, maxlen-3-pre)
        zwróć text[:pre] + '...' + text[len(text)-post:]
    zwróć text

_re_stripid = re.compile(r' at 0x[0-9a-f]{6,16}(>+)$', re.IGNORECASE)
def stripid(text):
    """Remove the hexadecimal id z a Python object representation."""
    # The behaviour of %p jest implementation-dependent w terms of case.
    zwróć _re_stripid.sub(r'\1', text)

def _is_some_method(obj):
    zwróć (inspect.isfunction(obj) albo
            inspect.ismethod(obj) albo
            inspect.isbuiltin(obj) albo
            inspect.ismethoddescriptor(obj))

def _is_bound_method(fn):
    """
    Returns Prawda jeżeli fn jest a bound method, regardless of whether
    fn was implemented w Python albo w C.
    """
    jeżeli inspect.ismethod(fn):
        zwróć Prawda
    jeżeli inspect.isbuiltin(fn):
        self = getattr(fn, '__self__', Nic)
        zwróć nie (inspect.ismodule(self) albo (self jest Nic))
    zwróć Nieprawda


def allmethods(cl):
    methods = {}
    dla key, value w inspect.getmembers(cl, _is_some_method):
        methods[key] = 1
    dla base w cl.__bases__:
        methods.update(allmethods(base)) # all your base are belong to us
    dla key w methods.keys():
        methods[key] = getattr(cl, key)
    zwróć methods

def _split_list(s, predicate):
    """Split sequence s via predicate, oraz zwróć pair ([true], [false]).

    The zwróć value jest a 2-tuple of lists,
        ([x dla x w s jeżeli predicate(x)],
         [x dla x w s jeżeli nie predicate(x)])
    """

    yes = []
    no = []
    dla x w s:
        jeżeli predicate(x):
            yes.append(x)
        inaczej:
            no.append(x)
    zwróć yes, no

def visiblename(name, all=Nic, obj=Nic):
    """Decide whether to show documentation on a variable."""
    # Certain special names are redundant albo internal.
    # XXX Remove __initializing__?
    jeżeli name w {'__author__', '__builtins__', '__cached__', '__credits__',
                '__date__', '__doc__', '__file__', '__spec__',
                '__loader__', '__module__', '__name__', '__package__',
                '__path__', '__qualname__', '__slots__', '__version__'}:
        zwróć 0
    # Private names are hidden, but special names are displayed.
    jeżeli name.startswith('__') oraz name.endswith('__'): zwróć 1
    # Namedtuples have public fields oraz methods przy a single leading underscore
    jeżeli name.startswith('_') oraz hasattr(obj, '_fields'):
        zwróć Prawda
    jeżeli all jest nie Nic:
        # only document that which the programmer exported w __all__
        zwróć name w all
    inaczej:
        zwróć nie name.startswith('_')

def classify_class_attrs(object):
    """Wrap inspect.classify_class_attrs, przy fixup dla data descriptors."""
    results = []
    dla (name, kind, cls, value) w inspect.classify_class_attrs(object):
        jeżeli inspect.isdatadescriptor(value):
            kind = 'data descriptor'
        results.append((name, kind, cls, value))
    zwróć results

# ----------------------------------------------------- module manipulation

def ispackage(path):
    """Guess whether a path refers to a package directory."""
    jeżeli os.path.isdir(path):
        dla ext w ('.py', '.pyc'):
            jeżeli os.path.isfile(os.path.join(path, '__init__' + ext)):
                zwróć Prawda
    zwróć Nieprawda

def source_synopsis(file):
    line = file.readline()
    dopóki line[:1] == '#' albo nie line.strip():
        line = file.readline()
        jeżeli nie line: przerwij
    line = line.strip()
    jeżeli line[:4] == 'r"""': line = line[1:]
    jeżeli line[:3] == '"""':
        line = line[3:]
        jeżeli line[-1:] == '\\': line = line[:-1]
        dopóki nie line.strip():
            line = file.readline()
            jeżeli nie line: przerwij
        result = line.split('"""')[0].strip()
    inaczej: result = Nic
    zwróć result

def synopsis(filename, cache={}):
    """Get the one-line summary out of a module file."""
    mtime = os.stat(filename).st_mtime
    lastupdate, result = cache.get(filename, (Nic, Nic))
    jeżeli lastupdate jest Nic albo lastupdate < mtime:
        # Look dla binary suffixes first, falling back to source.
        jeżeli filename.endswith(tuple(importlib.machinery.BYTECODE_SUFFIXES)):
            loader_cls = importlib.machinery.SourcelessFileLoader
        albo_inaczej filename.endswith(tuple(importlib.machinery.EXTENSION_SUFFIXES)):
            loader_cls = importlib.machinery.ExtensionFileLoader
        inaczej:
            loader_cls = Nic
        # Now handle the choice.
        jeżeli loader_cls jest Nic:
            # Must be a source file.
            spróbuj:
                file = tokenize.open(filename)
            wyjąwszy OSError:
                # module can't be opened, so skip it
                zwróć Nic
            # text modules can be directly examined
            przy file:
                result = source_synopsis(file)
        inaczej:
            # Must be a binary module, which has to be imported.
            loader = loader_cls('__temp__', filename)
            # XXX We probably don't need to dalej w the loader here.
            spec = importlib.util.spec_from_file_location('__temp__', filename,
                                                          loader=loader)
            spróbuj:
                module = importlib._bootstrap._load(spec)
            wyjąwszy:
                zwróć Nic
            usuń sys.modules['__temp__']
            result = module.__doc__.splitlines()[0] jeżeli module.__doc__ inaczej Nic
        # Cache the result.
        cache[filename] = (mtime, result)
    zwróć result

klasa ErrorDuringImport(Exception):
    """Errors that occurred dopóki trying to zaimportuj something to document it."""
    def __init__(self, filename, exc_info):
        self.filename = filename
        self.exc, self.value, self.tb = exc_info

    def __str__(self):
        exc = self.exc.__name__
        zwróć 'problem w %s - %s: %s' % (self.filename, exc, self.value)

def importfile(path):
    """Import a Python source file albo compiled file given its path."""
    magic = importlib.util.MAGIC_NUMBER
    przy open(path, 'rb') jako file:
        is_bytecode = magic == file.read(len(magic))
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    jeżeli is_bytecode:
        loader = importlib._bootstrap_external.SourcelessFileLoader(name, path)
    inaczej:
        loader = importlib._bootstrap_external.SourceFileLoader(name, path)
    # XXX We probably don't need to dalej w the loader here.
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    spróbuj:
        zwróć importlib._bootstrap._load(spec)
    wyjąwszy:
        podnieś ErrorDuringImport(path, sys.exc_info())

def safeimport(path, forceload=0, cache={}):
    """Import a module; handle errors; zwróć Nic jeżeli the module isn't found.

    If the module *is* found but an exception occurs, it's wrapped w an
    ErrorDuringImport exception oraz reraised.  Unlike __import__, jeżeli a
    package path jest specified, the module at the end of the path jest returned,
    nie the package at the beginning.  If the optional 'forceload' argument
    jest 1, we reload the module z disk (unless it's a dynamic extension)."""
    spróbuj:
        # If forceload jest 1 oraz the module has been previously loaded from
        # disk, we always have to reload the module.  Checking the file's
        # mtime isn't good enough (e.g. the module could contain a class
        # that inherits z another module that has changed).
        jeżeli forceload oraz path w sys.modules:
            jeżeli path nie w sys.builtin_module_names:
                # Remove the module z sys.modules oraz re-zaimportuj to try
                # oraz avoid problems przy partially loaded modules.
                # Also remove any submodules because they won't appear
                # w the newly loaded module's namespace jeżeli they're already
                # w sys.modules.
                subs = [m dla m w sys.modules jeżeli m.startswith(path + '.')]
                dla key w [path] + subs:
                    # Prevent garbage collection.
                    cache[key] = sys.modules[key]
                    usuń sys.modules[key]
        module = __import__(path)
    wyjąwszy:
        # Did the error occur before albo after the module was found?
        (exc, value, tb) = info = sys.exc_info()
        jeżeli path w sys.modules:
            # An error occurred dopóki executing the imported module.
            podnieś ErrorDuringImport(sys.modules[path].__file__, info)
        albo_inaczej exc jest SyntaxError:
            # A SyntaxError occurred before we could execute the module.
            podnieś ErrorDuringImport(value.filename, info)
        albo_inaczej exc jest ImportError oraz value.name == path:
            # No such module w the path.
            zwróć Nic
        inaczej:
            # Some other error occurred during the importing process.
            podnieś ErrorDuringImport(path, sys.exc_info())
    dla part w path.split('.')[1:]:
        spróbuj: module = getattr(module, part)
        wyjąwszy AttributeError: zwróć Nic
    zwróć module

# ---------------------------------------------------- formatter base class

klasa Doc:

    PYTHONDOCS = os.environ.get("PYTHONDOCS",
                                "http://docs.python.org/%d.%d/library"
                                % sys.version_info[:2])

    def document(self, object, name=Nic, *args):
        """Generate documentation dla an object."""
        args = (object, name) + args
        # 'try' clause jest to attempt to handle the possibility that inspect
        # identifies something w a way that pydoc itself has issues handling;
        # think 'super' oraz how it jest a descriptor (which podnieśs the exception
        # by lacking a __name__ attribute) oraz an instance.
        jeżeli inspect.isgetsetdescriptor(object): zwróć self.docdata(*args)
        jeżeli inspect.ismemberdescriptor(object): zwróć self.docdata(*args)
        spróbuj:
            jeżeli inspect.ismodule(object): zwróć self.docmodule(*args)
            jeżeli inspect.isclass(object): zwróć self.docclass(*args)
            jeżeli inspect.isroutine(object): zwróć self.docroutine(*args)
        wyjąwszy AttributeError:
            dalej
        jeżeli isinstance(object, property): zwróć self.docproperty(*args)
        zwróć self.docother(*args)

    def fail(self, object, name=Nic, *args):
        """Raise an exception dla unimplemented types."""
        message = "don't know how to document object%s of type %s" % (
            name oraz ' ' + repr(name), type(object).__name__)
        podnieś TypeError(message)

    docmodule = docclass = docroutine = docother = docproperty = docdata = fail

    def getdocloc(self, object):
        """Return the location of module docs albo Nic"""

        spróbuj:
            file = inspect.getabsfile(object)
        wyjąwszy TypeError:
            file = '(built-in)'

        docloc = os.environ.get("PYTHONDOCS", self.PYTHONDOCS)

        basedir = os.path.join(sys.base_exec_prefix, "lib",
                               "python%d.%d" %  sys.version_info[:2])
        jeżeli (isinstance(object, type(os)) oraz
            (object.__name__ w ('errno', 'exceptions', 'gc', 'imp',
                                 'marshal', 'posix', 'signal', 'sys',
                                 '_thread', 'zipimport') albo
             (file.startswith(basedir) oraz
              nie file.startswith(os.path.join(basedir, 'site-packages')))) oraz
            object.__name__ nie w ('xml.etree', 'test.pydoc_mod')):
            jeżeli docloc.startswith("http://"):
                docloc = "%s/%s" % (docloc.rstrip("/"), object.__name__)
            inaczej:
                docloc = os.path.join(docloc, object.__name__ + ".html")
        inaczej:
            docloc = Nic
        zwróć docloc

# -------------------------------------------- HTML documentation generator

klasa HTMLRepr(Repr):
    """Class dla safely making an HTML representation of a Python object."""
    def __init__(self):
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    def escape(self, text):
        zwróć replace(text, '&', '&amp;', '<', '&lt;', '>', '&gt;')

    def repr(self, object):
        zwróć Repr.repr(self, object)

    def repr1(self, x, level):
        jeżeli hasattr(type(x), '__name__'):
            methodname = 'repr_' + '_'.join(type(x).__name__.split())
            jeżeli hasattr(self, methodname):
                zwróć getattr(self, methodname)(x, level)
        zwróć self.escape(cram(stripid(repr(x)), self.maxother))

    def repr_string(self, x, level):
        test = cram(x, self.maxstring)
        testrepr = repr(test)
        jeżeli '\\' w test oraz '\\' nie w replace(testrepr, r'\\', ''):
            # Backslashes are only literal w the string oraz are never
            # needed to make any special characters, so show a raw string.
            zwróć 'r' + testrepr[0] + self.escape(test) + testrepr[0]
        zwróć re.sub(r'((\\[\\abfnrtv\'"]|\\[0-9]..|\\x..|\\u....)+)',
                      r'<font color="#c040c0">\1</font>',
                      self.escape(testrepr))

    repr_str = repr_string

    def repr_instance(self, x, level):
        spróbuj:
            zwróć self.escape(cram(stripid(repr(x)), self.maxstring))
        wyjąwszy:
            zwróć self.escape('<%s instance>' % x.__class__.__name__)

    repr_unicode = repr_string

klasa HTMLDoc(Doc):
    """Formatter klasa dla HTML documentation."""

    # ------------------------------------------- HTML formatting utilities

    _repr_instance = HTMLRepr()
    repr = _repr_instance.repr
    escape = _repr_instance.escape

    def page(self, title, contents):
        """Format an HTML page."""
        zwróć '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Python: %s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body bgcolor="#f0f0f8">
%s
</body></html>''' % (title, contents)

    def heading(self, title, fgcol, bgcol, extras=''):
        """Format a page heading."""
        zwróć '''
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="%s">
<td valign=bottom>&nbsp;<br>
<font color="%s" face="helvetica, arial">&nbsp;<br>%s</font></td
><td align=right valign=bottom
><font color="%s" face="helvetica, arial">%s</font></td></tr></table>
    ''' % (bgcol, fgcol, title, fgcol, extras albo '&nbsp;')

    def section(self, title, fgcol, bgcol, contents, width=6,
                prelude='', marginalia=Nic, gap='&nbsp;'):
        """Format a section przy a heading."""
        jeżeli marginalia jest Nic:
            marginalia = '<tt>' + '&nbsp;' * width + '</tt>'
        result = '''<p>
<table width="100%%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="%s">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="%s" face="helvetica, arial">%s</font></td></tr>
    ''' % (bgcol, fgcol, title)
        jeżeli prelude:
            result = result + '''
<tr bgcolor="%s"><td rowspan=2>%s</td>
<td colspan=2>%s</td></tr>
<tr><td>%s</td>''' % (bgcol, marginalia, prelude, gap)
        inaczej:
            result = result + '''
<tr><td bgcolor="%s">%s</td><td>%s</td>''' % (bgcol, marginalia, gap)

        zwróć result + '\n<td width="100%%">%s</td></tr></table>' % contents

    def bigsection(self, title, *args):
        """Format a section przy a big heading."""
        title = '<big><strong>%s</strong></big>' % title
        zwróć self.section(title, *args)

    def preformat(self, text):
        """Format literal preformatted text."""
        text = self.escape(text.expandtabs())
        zwróć replace(text, '\n\n', '\n \n', '\n\n', '\n \n',
                             ' ', '&nbsp;', '\n', '<br>\n')

    def multicolumn(self, list, format, cols=4):
        """Format a list of items into a multi-column list."""
        result = ''
        rows = (len(list)+cols-1)//cols
        dla col w range(cols):
            result = result + '<td width="%d%%" valign=top>' % (100//cols)
            dla i w range(rows*col, rows*col+rows):
                jeżeli i < len(list):
                    result = result + format(list[i]) + '<br>\n'
            result = result + '</td>'
        zwróć '<table width="100%%" summary="list"><tr>%s</tr></table>' % result

    def grey(self, text): zwróć '<font color="#909090">%s</font>' % text

    def namelink(self, name, *dicts):
        """Make a link dla an identifier, given name-to-URL mappings."""
        dla dict w dicts:
            jeżeli name w dict:
                zwróć '<a href="%s">%s</a>' % (dict[name], name)
        zwróć name

    def classlink(self, object, modname):
        """Make a link dla a class."""
        name, module = object.__name__, sys.modules.get(object.__module__)
        jeżeli hasattr(module, name) oraz getattr(module, name) jest object:
            zwróć '<a href="%s.html#%s">%s</a>' % (
                module.__name__, name, classname(object, modname))
        zwróć classname(object, modname)

    def modulelink(self, object):
        """Make a link dla a module."""
        zwróć '<a href="%s.html">%s</a>' % (object.__name__, object.__name__)

    def modpkglink(self, modpkginfo):
        """Make a link dla a module albo package to display w an index."""
        name, path, ispackage, shadowed = modpkginfo
        jeżeli shadowed:
            zwróć self.grey(name)
        jeżeli path:
            url = '%s.%s.html' % (path, name)
        inaczej:
            url = '%s.html' % name
        jeżeli ispackage:
            text = '<strong>%s</strong>&nbsp;(package)' % name
        inaczej:
            text = name
        zwróć '<a href="%s">%s</a>' % (url, text)

    def filelink(self, url, path):
        """Make a link to source file."""
        zwróć '<a href="file:%s">%s</a>' % (url, path)

    def markup(self, text, escape=Nic, funcs={}, classes={}, methods={}):
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape = escape albo self.escape
        results = []
        here = 0
        pattern = re.compile(r'\b((http|ftp)://\S+[\w/]|'
                                r'RFC[- ]?(\d+)|'
                                r'PEP[- ]?(\d+)|'
                                r'(self\.)?(\w+))')
        dopóki Prawda:
            match = pattern.search(text, here)
            jeżeli nie match: przerwij
            start, end = match.span()
            results.append(escape(text[here:start]))

            all, scheme, rfc, pep, selfdot, name = match.groups()
            jeżeli scheme:
                url = escape(all).replace('"', '&quot;')
                results.append('<a href="%s">%s</a>' % (url, url))
            albo_inaczej rfc:
                url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            albo_inaczej pep:
                url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                results.append('<a href="%s">%s</a>' % (url, escape(all)))
            albo_inaczej selfdot:
                # Create a link dla methods like 'self.method(...)'
                # oraz use <strong> dla attributes like 'self.attr'
                jeżeli text[end:end+1] == '(':
                    results.append('self.' + self.namelink(name, methods))
                inaczej:
                    results.append('self.<strong>%s</strong>' % name)
            albo_inaczej text[end:end+1] == '(':
                results.append(self.namelink(name, methods, funcs, classes))
            inaczej:
                results.append(self.namelink(name, classes))
            here = end
        results.append(escape(text[here:]))
        zwróć ''.join(results)

    # ---------------------------------------------- type-specific routines

    def formattree(self, tree, modname, parent=Nic):
        """Produce HTML dla a klasa tree jako given by inspect.getclasstree()."""
        result = ''
        dla entry w tree:
            jeżeli type(entry) jest type(()):
                c, bases = entry
                result = result + '<dt><font face="helvetica, arial">'
                result = result + self.classlink(c, modname)
                jeżeli bases oraz bases != (parent,):
                    parents = []
                    dla base w bases:
                        parents.append(self.classlink(base, modname))
                    result = result + '(' + ', '.join(parents) + ')'
                result = result + '\n</font></dt>'
            albo_inaczej type(entry) jest type([]):
                result = result + '<dd>\n%s</dd>\n' % self.formattree(
                    entry, modname, c)
        zwróć '<dl>\n%s</dl>\n' % result

    def docmodule(self, object, name=Nic, mod=Nic, *ignored):
        """Produce HTML documentation dla a module object."""
        name = object.__name__ # ignore the dalejed-in name
        spróbuj:
            all = object.__all__
        wyjąwszy AttributeError:
            all = Nic
        parts = name.split('.')
        links = []
        dla i w range(len(parts)-1):
            links.append(
                '<a href="%s.html"><font color="#ffffff">%s</font></a>' %
                ('.'.join(parts[:i+1]), parts[i]))
        linkedname = '.'.join(links + parts[-1:])
        head = '<big><big><strong>%s</strong></big></big>' % linkedname
        spróbuj:
            path = inspect.getabsfile(object)
            url = urllib.parse.quote(path)
            filelink = self.filelink(url, path)
        wyjąwszy TypeError:
            filelink = '(built-in)'
        info = []
        jeżeli hasattr(object, '__version__'):
            version = str(object.__version__)
            jeżeli version[:11] == '$' + 'Revision: ' oraz version[-1:] == '$':
                version = version[11:-1].strip()
            info.append('version %s' % self.escape(version))
        jeżeli hasattr(object, '__date__'):
            info.append(self.escape(str(object.__date__)))
        jeżeli info:
            head = head + ' (%s)' % ', '.join(info)
        docloc = self.getdocloc(object)
        jeżeli docloc jest nie Nic:
            docloc = '<br><a href="%(docloc)s">Module Reference</a>' % locals()
        inaczej:
            docloc = ''
        result = self.heading(
            head, '#ffffff', '#7799ee',
            '<a href=".">index</a><br>' + filelink + docloc)

        modules = inspect.getmembers(object, inspect.ismodule)

        classes, cdict = [], {}
        dla key, value w inspect.getmembers(object, inspect.isclass):
            # jeżeli __all__ exists, believe it.  Otherwise use old heuristic.
            jeżeli (all jest nie Nic albo
                (inspect.getmodule(value) albo object) jest object):
                jeżeli visiblename(key, all, object):
                    classes.append((key, value))
                    cdict[key] = cdict[value] = '#' + key
        dla key, value w classes:
            dla base w value.__bases__:
                key, modname = base.__name__, base.__module__
                module = sys.modules.get(modname)
                jeżeli modname != name oraz module oraz hasattr(module, key):
                    jeżeli getattr(module, key) jest base:
                        jeżeli nie key w cdict:
                            cdict[key] = cdict[base] = modname + '.html#' + key
        funcs, fdict = [], {}
        dla key, value w inspect.getmembers(object, inspect.isroutine):
            # jeżeli __all__ exists, believe it.  Otherwise use old heuristic.
            jeżeli (all jest nie Nic albo
                inspect.isbuiltin(value) albo inspect.getmodule(value) jest object):
                jeżeli visiblename(key, all, object):
                    funcs.append((key, value))
                    fdict[key] = '#-' + key
                    jeżeli inspect.isfunction(value): fdict[value] = fdict[key]
        data = []
        dla key, value w inspect.getmembers(object, isdata):
            jeżeli visiblename(key, all, object):
                data.append((key, value))

        doc = self.markup(getdoc(object), self.preformat, fdict, cdict)
        doc = doc oraz '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc

        jeżeli hasattr(object, '__path__'):
            modpkgs = []
            dla importer, modname, ispkg w pkgutil.iter_modules(object.__path__):
                modpkgs.append((modname, name, ispkg, 0))
            modpkgs.sort()
            contents = self.multicolumn(modpkgs, self.modpkglink)
            result = result + self.bigsection(
                'Package Contents', '#ffffff', '#aa55cc', contents)
        albo_inaczej modules:
            contents = self.multicolumn(
                modules, lambda t: self.modulelink(t[1]))
            result = result + self.bigsection(
                'Modules', '#ffffff', '#aa55cc', contents)

        jeżeli classes:
            classlist = [value dla (key, value) w classes]
            contents = [
                self.formattree(inspect.getclasstree(classlist, 1), name)]
            dla key, value w classes:
                contents.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                'Classes', '#ffffff', '#ee77aa', ' '.join(contents))
        jeżeli funcs:
            contents = []
            dla key, value w funcs:
                contents.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                'Functions', '#ffffff', '#eeaa77', ' '.join(contents))
        jeżeli data:
            contents = []
            dla key, value w data:
                contents.append(self.document(value, key))
            result = result + self.bigsection(
                'Data', '#ffffff', '#55aa55', '<br>\n'.join(contents))
        jeżeli hasattr(object, '__author__'):
            contents = self.markup(str(object.__author__), self.preformat)
            result = result + self.bigsection(
                'Author', '#ffffff', '#7799ee', contents)
        jeżeli hasattr(object, '__credits__'):
            contents = self.markup(str(object.__credits__), self.preformat)
            result = result + self.bigsection(
                'Credits', '#ffffff', '#7799ee', contents)

        zwróć result

    def docclass(self, object, name=Nic, mod=Nic, funcs={}, classes={},
                 *ignored):
        """Produce HTML documentation dla a klasa object."""
        realname = object.__name__
        name = name albo realname
        bases = object.__bases__

        contents = []
        push = contents.append

        # Cute little klasa to pump out a horizontal rule between sections.
        klasa HorizontalRule:
            def __init__(self):
                self.needone = 0
            def maybe(self):
                jeżeli self.needone:
                    push('<hr>\n')
                self.needone = 1
        hr = HorizontalRule()

        # List the mro, jeżeli non-trivial.
        mro = deque(inspect.getmro(object))
        jeżeli len(mro) > 2:
            hr.maybe()
            push('<dl><dt>Method resolution order:</dt>\n')
            dla base w mro:
                push('<dd>%s</dd>\n' % self.classlink(base,
                                                      object.__module__))
            push('</dl>\n')

        def spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    spróbuj:
                        value = getattr(object, name)
                    wyjąwszy Exception:
                        # Some descriptors may meet a failure w their __get__.
                        # (bug #1785)
                        push(self._docdescriptor(name, value, mod))
                    inaczej:
                        push(self.document(value, name, mod,
                                        funcs, classes, mdict, object))
                    push('\n')
            zwróć attrs

        def spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    push(self._docdescriptor(name, value, mod))
            zwróć attrs

        def spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    base = self.docother(getattr(object, name), name, mod)
                    jeżeli callable(value) albo inspect.isdatadescriptor(value):
                        doc = getattr(value, "__doc__", Nic)
                    inaczej:
                        doc = Nic
                    jeżeli doc jest Nic:
                        push('<dl><dt>%s</dl>\n' % base)
                    inaczej:
                        doc = self.markup(getdoc(value), self.preformat,
                                          funcs, classes, mdict)
                        doc = '<dd><tt>%s</tt>' % doc
                        push('<dl><dt>%s%s</dl>\n' % (base, doc))
                    push('\n')
            zwróć attrs

        attrs = [(name, kind, cls, value)
                 dla name, kind, cls, value w classify_class_attrs(object)
                 jeżeli visiblename(name, obj=object)]

        mdict = {}
        dla key, kind, homecls, value w attrs:
            mdict[key] = anchor = '#' + name + '-' + key
            spróbuj:
                value = getattr(object, name)
            wyjąwszy Exception:
                # Some descriptors may meet a failure w their __get__.
                # (bug #1785)
                dalej
            spróbuj:
                # The value may nie be hashable (e.g., a data attr with
                # a dict albo list value).
                mdict[value] = anchor
            wyjąwszy TypeError:
                dalej

        dopóki attrs:
            jeżeli mro:
                thisclass = mro.popleft()
            inaczej:
                thisclass = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] jest thisclass)

            jeżeli thisclass jest builtins.object:
                attrs = inherited
                kontynuuj
            albo_inaczej thisclass jest object:
                tag = 'defined here'
            inaczej:
                tag = 'inherited z %s' % self.classlink(thisclass,
                                                           object.__module__)
            tag += ':<br>\n'

            # Sort attrs by name.
            attrs.sort(key=lambda t: t[0])

            # Pump out the attrs, segregated by kind.
            attrs = spill('Methods %s' % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill('Class methods %s' % tag, attrs,
                          lambda t: t[1] == 'class method')
            attrs = spill('Static methods %s' % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors('Data descriptors %s' % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata('Data oraz other attributes %s' % tag, attrs,
                              lambda t: t[1] == 'data')
            assert attrs == []
            attrs = inherited

        contents = ''.join(contents)

        jeżeli name == realname:
            title = '<a name="%s">class <strong>%s</strong></a>' % (
                name, realname)
        inaczej:
            title = '<strong>%s</strong> = <a name="%s">class %s</a>' % (
                name, name, realname)
        jeżeli bases:
            parents = []
            dla base w bases:
                parents.append(self.classlink(base, object.__module__))
            title = title + '(%s)' % ', '.join(parents)
        doc = self.markup(getdoc(object), self.preformat, funcs, classes, mdict)
        doc = doc oraz '<tt>%s<br>&nbsp;</tt>' % doc

        zwróć self.section(title, '#000000', '#ffc8d8', contents, 3, doc)

    def formatvalue(self, object):
        """Format an argument default value jako text."""
        zwróć self.grey('=' + self.repr(object))

    def docroutine(self, object, name=Nic, mod=Nic,
                   funcs={}, classes={}, methods={}, cl=Nic):
        """Produce HTML documentation dla a function albo method object."""
        realname = object.__name__
        name = name albo realname
        anchor = (cl oraz cl.__name__ albo '') + '-' + name
        note = ''
        skipdocs = 0
        jeżeli _is_bound_method(object):
            imclass = object.__self__.__class__
            jeżeli cl:
                jeżeli imclass jest nie cl:
                    note = ' z ' + self.classlink(imclass, mod)
            inaczej:
                jeżeli object.__self__ jest nie Nic:
                    note = ' method of %s instance' % self.classlink(
                        object.__self__.__class__, mod)
                inaczej:
                    note = ' unbound %s method' % self.classlink(imclass,mod)

        jeżeli name == realname:
            title = '<a name="%s"><strong>%s</strong></a>' % (anchor, realname)
        inaczej:
            jeżeli (cl oraz realname w cl.__dict__ oraz
                cl.__dict__[realname] jest object):
                reallink = '<a href="#%s">%s</a>' % (
                    cl.__name__ + '-' + realname, realname)
                skipdocs = 1
            inaczej:
                reallink = realname
            title = '<a name="%s"><strong>%s</strong></a> = %s' % (
                anchor, name, reallink)
        argspec = Nic
        jeżeli inspect.isroutine(object):
            spróbuj:
                signature = inspect.signature(object)
            wyjąwszy (ValueError, TypeError):
                signature = Nic
            jeżeli signature:
                argspec = str(signature)
                jeżeli realname == '<lambda>':
                    title = '<strong>%s</strong> <em>lambda</em> ' % name
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it jest possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1] # remove parentheses
        jeżeli nie argspec:
            argspec = '(...)'

        decl = title + self.escape(argspec) + (niee oraz self.grey(
               '<font face="helvetica, arial">%s</font>' % note))

        jeżeli skipdocs:
            zwróć '<dl><dt>%s</dt></dl>\n' % decl
        inaczej:
            doc = self.markup(
                getdoc(object), self.preformat, funcs, classes, methods)
            doc = doc oraz '<dd><tt>%s</tt></dd>' % doc
            zwróć '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    def _docdescriptor(self, name, value, mod):
        results = []
        push = results.append

        jeżeli name:
            push('<dl><dt><strong>%s</strong></dt>\n' % name)
        jeżeli value.__doc__ jest nie Nic:
            doc = self.markup(getdoc(value), self.preformat)
            push('<dd><tt>%s</tt></dd>\n' % doc)
        push('</dl>\n')

        zwróć ''.join(results)

    def docproperty(self, object, name=Nic, mod=Nic, cl=Nic):
        """Produce html documentation dla a property."""
        zwróć self._docdescriptor(name, object, mod)

    def docother(self, object, name=Nic, mod=Nic, *ignored):
        """Produce HTML documentation dla a data object."""
        lhs = name oraz '<strong>%s</strong> = ' % name albo ''
        zwróć lhs + self.repr(object)

    def docdata(self, object, name=Nic, mod=Nic, cl=Nic):
        """Produce html documentation dla a data descriptor."""
        zwróć self._docdescriptor(name, object, mod)

    def index(self, dir, shadowed=Nic):
        """Generate an HTML index dla a directory of modules."""
        modpkgs = []
        jeżeli shadowed jest Nic: shadowed = {}
        dla importer, name, ispkg w pkgutil.iter_modules([dir]):
            jeżeli any((0xD800 <= ord(ch) <= 0xDFFF) dla ch w name):
                # ignore a module jeżeli its name contains a surrogate character
                kontynuuj
            modpkgs.append((name, '', ispkg, name w shadowed))
            shadowed[name] = 1

        modpkgs.sort()
        contents = self.multicolumn(modpkgs, self.modpkglink)
        zwróć self.bigsection(dir, '#ffffff', '#ee77aa', contents)

# -------------------------------------------- text documentation generator

klasa TextRepr(Repr):
    """Class dla safely making a text representation of a Python object."""
    def __init__(self):
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    def repr1(self, x, level):
        jeżeli hasattr(type(x), '__name__'):
            methodname = 'repr_' + '_'.join(type(x).__name__.split())
            jeżeli hasattr(self, methodname):
                zwróć getattr(self, methodname)(x, level)
        zwróć cram(stripid(repr(x)), self.maxother)

    def repr_string(self, x, level):
        test = cram(x, self.maxstring)
        testrepr = repr(test)
        jeżeli '\\' w test oraz '\\' nie w replace(testrepr, r'\\', ''):
            # Backslashes are only literal w the string oraz are never
            # needed to make any special characters, so show a raw string.
            zwróć 'r' + testrepr[0] + test + testrepr[0]
        zwróć testrepr

    repr_str = repr_string

    def repr_instance(self, x, level):
        spróbuj:
            zwróć cram(stripid(repr(x)), self.maxstring)
        wyjąwszy:
            zwróć '<%s instance>' % x.__class__.__name__

klasa TextDoc(Doc):
    """Formatter klasa dla text documentation."""

    # ------------------------------------------- text formatting utilities

    _repr_instance = TextRepr()
    repr = _repr_instance.repr

    def bold(self, text):
        """Format a string w bold by overstriking."""
        zwróć ''.join(ch + '\b' + ch dla ch w text)

    def indent(self, text, prefix='    '):
        """Indent text by prepending a given prefix to each line."""
        jeżeli nie text: zwróć ''
        lines = [prefix + line dla line w text.split('\n')]
        jeżeli lines: lines[-1] = lines[-1].rstrip()
        zwróć '\n'.join(lines)

    def section(self, title, contents):
        """Format a section przy a given heading."""
        clean_contents = self.indent(contents).rstrip()
        zwróć self.bold(title) + '\n' + clean_contents + '\n\n'

    # ---------------------------------------------- type-specific routines

    def formattree(self, tree, modname, parent=Nic, prefix=''):
        """Render w text a klasa tree jako returned by inspect.getclasstree()."""
        result = ''
        dla entry w tree:
            jeżeli type(entry) jest type(()):
                c, bases = entry
                result = result + prefix + classname(c, modname)
                jeżeli bases oraz bases != (parent,):
                    parents = (classname(c, modname) dla c w bases)
                    result = result + '(%s)' % ', '.join(parents)
                result = result + '\n'
            albo_inaczej type(entry) jest type([]):
                result = result + self.formattree(
                    entry, modname, c, prefix + '    ')
        zwróć result

    def docmodule(self, object, name=Nic, mod=Nic):
        """Produce text documentation dla a given module object."""
        name = object.__name__ # ignore the dalejed-in name
        synop, desc = splitdoc(getdoc(object))
        result = self.section('NAME', name + (synop oraz ' - ' + synop))
        all = getattr(object, '__all__', Nic)
        docloc = self.getdocloc(object)
        jeżeli docloc jest nie Nic:
            result = result + self.section('MODULE REFERENCE', docloc + """

The following documentation jest automatically generated z the Python
source files.  It may be incomplete, incorrect albo include features that
are considered implementation detail oraz may vary between Python
implementations.  When w doubt, consult the module reference at the
location listed above.
""")

        jeżeli desc:
            result = result + self.section('DESCRIPTION', desc)

        classes = []
        dla key, value w inspect.getmembers(object, inspect.isclass):
            # jeżeli __all__ exists, believe it.  Otherwise use old heuristic.
            jeżeli (all jest nie Nic
                albo (inspect.getmodule(value) albo object) jest object):
                jeżeli visiblename(key, all, object):
                    classes.append((key, value))
        funcs = []
        dla key, value w inspect.getmembers(object, inspect.isroutine):
            # jeżeli __all__ exists, believe it.  Otherwise use old heuristic.
            jeżeli (all jest nie Nic albo
                inspect.isbuiltin(value) albo inspect.getmodule(value) jest object):
                jeżeli visiblename(key, all, object):
                    funcs.append((key, value))
        data = []
        dla key, value w inspect.getmembers(object, isdata):
            jeżeli visiblename(key, all, object):
                data.append((key, value))

        modpkgs = []
        modpkgs_names = set()
        jeżeli hasattr(object, '__path__'):
            dla importer, modname, ispkg w pkgutil.iter_modules(object.__path__):
                modpkgs_names.add(modname)
                jeżeli ispkg:
                    modpkgs.append(modname + ' (package)')
                inaczej:
                    modpkgs.append(modname)

            modpkgs.sort()
            result = result + self.section(
                'PACKAGE CONTENTS', '\n'.join(modpkgs))

        # Detect submodules jako sometimes created by C extensions
        submodules = []
        dla key, value w inspect.getmembers(object, inspect.ismodule):
            jeżeli value.__name__.startswith(name + '.') oraz key nie w modpkgs_names:
                submodules.append(key)
        jeżeli submodules:
            submodules.sort()
            result = result + self.section(
                'SUBMODULES', '\n'.join(submodules))

        jeżeli classes:
            classlist = [value dla key, value w classes]
            contents = [self.formattree(
                inspect.getclasstree(classlist, 1), name)]
            dla key, value w classes:
                contents.append(self.document(value, key, name))
            result = result + self.section('CLASSES', '\n'.join(contents))

        jeżeli funcs:
            contents = []
            dla key, value w funcs:
                contents.append(self.document(value, key, name))
            result = result + self.section('FUNCTIONS', '\n'.join(contents))

        jeżeli data:
            contents = []
            dla key, value w data:
                contents.append(self.docother(value, key, name, maxlen=70))
            result = result + self.section('DATA', '\n'.join(contents))

        jeżeli hasattr(object, '__version__'):
            version = str(object.__version__)
            jeżeli version[:11] == '$' + 'Revision: ' oraz version[-1:] == '$':
                version = version[11:-1].strip()
            result = result + self.section('VERSION', version)
        jeżeli hasattr(object, '__date__'):
            result = result + self.section('DATE', str(object.__date__))
        jeżeli hasattr(object, '__author__'):
            result = result + self.section('AUTHOR', str(object.__author__))
        jeżeli hasattr(object, '__credits__'):
            result = result + self.section('CREDITS', str(object.__credits__))
        spróbuj:
            file = inspect.getabsfile(object)
        wyjąwszy TypeError:
            file = '(built-in)'
        result = result + self.section('FILE', file)
        zwróć result

    def docclass(self, object, name=Nic, mod=Nic, *ignored):
        """Produce text documentation dla a given klasa object."""
        realname = object.__name__
        name = name albo realname
        bases = object.__bases__

        def makename(c, m=object.__module__):
            zwróć classname(c, m)

        jeżeli name == realname:
            title = 'class ' + self.bold(realname)
        inaczej:
            title = self.bold(name) + ' = klasa ' + realname
        jeżeli bases:
            parents = map(makename, bases)
            title = title + '(%s)' % ', '.join(parents)

        doc = getdoc(object)
        contents = doc oraz [doc + '\n'] albo []
        push = contents.append

        # List the mro, jeżeli non-trivial.
        mro = deque(inspect.getmro(object))
        jeżeli len(mro) > 2:
            push("Method resolution order:")
            dla base w mro:
                push('    ' + makename(base))
            push('')

        # Cute little klasa to pump out a horizontal rule between sections.
        klasa HorizontalRule:
            def __init__(self):
                self.needone = 0
            def maybe(self):
                jeżeli self.needone:
                    push('-' * 70)
                self.needone = 1
        hr = HorizontalRule()

        def spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    spróbuj:
                        value = getattr(object, name)
                    wyjąwszy Exception:
                        # Some descriptors may meet a failure w their __get__.
                        # (bug #1785)
                        push(self._docdescriptor(name, value, mod))
                    inaczej:
                        push(self.document(value,
                                        name, mod, object))
            zwróć attrs

        def spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    push(self._docdescriptor(name, value, mod))
            zwróć attrs

        def spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            jeżeli ok:
                hr.maybe()
                push(msg)
                dla name, kind, homecls, value w ok:
                    jeżeli callable(value) albo inspect.isdatadescriptor(value):
                        doc = getdoc(value)
                    inaczej:
                        doc = Nic
                    spróbuj:
                        obj = getattr(object, name)
                    wyjąwszy AttributeError:
                        obj = homecls.__dict__[name]
                    push(self.docother(obj, name, mod, maxlen=70, doc=doc) +
                         '\n')
            zwróć attrs

        attrs = [(name, kind, cls, value)
                 dla name, kind, cls, value w classify_class_attrs(object)
                 jeżeli visiblename(name, obj=object)]

        dopóki attrs:
            jeżeli mro:
                thisclass = mro.popleft()
            inaczej:
                thisclass = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] jest thisclass)

            jeżeli thisclass jest builtins.object:
                attrs = inherited
                kontynuuj
            albo_inaczej thisclass jest object:
                tag = "defined here"
            inaczej:
                tag = "inherited z %s" % classname(thisclass,
                                                      object.__module__)
            # Sort attrs by name.
            attrs.sort()

            # Pump out the attrs, segregated by kind.
            attrs = spill("Methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill("Class methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'class method')
            attrs = spill("Static methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors("Data descriptors %s:\n" % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata("Data oraz other attributes %s:\n" % tag, attrs,
                              lambda t: t[1] == 'data')

            assert attrs == []
            attrs = inherited

        contents = '\n'.join(contents)
        jeżeli nie contents:
            zwróć title + '\n'
        zwróć title + '\n' + self.indent(contents.rstrip(), ' |  ') + '\n'

    def formatvalue(self, object):
        """Format an argument default value jako text."""
        zwróć '=' + self.repr(object)

    def docroutine(self, object, name=Nic, mod=Nic, cl=Nic):
        """Produce text documentation dla a function albo method object."""
        realname = object.__name__
        name = name albo realname
        note = ''
        skipdocs = 0
        jeżeli _is_bound_method(object):
            imclass = object.__self__.__class__
            jeżeli cl:
                jeżeli imclass jest nie cl:
                    note = ' z ' + classname(imclass, mod)
            inaczej:
                jeżeli object.__self__ jest nie Nic:
                    note = ' method of %s instance' % classname(
                        object.__self__.__class__, mod)
                inaczej:
                    note = ' unbound %s method' % classname(imclass,mod)

        jeżeli name == realname:
            title = self.bold(realname)
        inaczej:
            jeżeli (cl oraz realname w cl.__dict__ oraz
                cl.__dict__[realname] jest object):
                skipdocs = 1
            title = self.bold(name) + ' = ' + realname
        argspec = Nic

        jeżeli inspect.isroutine(object):
            spróbuj:
                signature = inspect.signature(object)
            wyjąwszy (ValueError, TypeError):
                signature = Nic
            jeżeli signature:
                argspec = str(signature)
                jeżeli realname == '<lambda>':
                    title = self.bold(name) + ' lambda '
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it jest possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1] # remove parentheses
        jeżeli nie argspec:
            argspec = '(...)'
        decl = title + argspec + note

        jeżeli skipdocs:
            zwróć decl + '\n'
        inaczej:
            doc = getdoc(object) albo ''
            zwróć decl + '\n' + (doc oraz self.indent(doc).rstrip() + '\n')

    def _docdescriptor(self, name, value, mod):
        results = []
        push = results.append

        jeżeli name:
            push(self.bold(name))
            push('\n')
        doc = getdoc(value) albo ''
        jeżeli doc:
            push(self.indent(doc))
            push('\n')
        zwróć ''.join(results)

    def docproperty(self, object, name=Nic, mod=Nic, cl=Nic):
        """Produce text documentation dla a property."""
        zwróć self._docdescriptor(name, object, mod)

    def docdata(self, object, name=Nic, mod=Nic, cl=Nic):
        """Produce text documentation dla a data descriptor."""
        zwróć self._docdescriptor(name, object, mod)

    def docother(self, object, name=Nic, mod=Nic, parent=Nic, maxlen=Nic, doc=Nic):
        """Produce text documentation dla a data object."""
        repr = self.repr(object)
        jeżeli maxlen:
            line = (name oraz name + ' = ' albo '') + repr
            chop = maxlen - len(line)
            jeżeli chop < 0: repr = repr[:chop] + '...'
        line = (name oraz self.bold(name) + ' = ' albo '') + repr
        jeżeli doc jest nie Nic:
            line += '\n' + self.indent(str(doc))
        zwróć line

klasa _PlainTextDoc(TextDoc):
    """Subclass of TextDoc which overrides string styling"""
    def bold(self, text):
        zwróć text

# --------------------------------------------------------- user interfaces

def pager(text):
    """The first time this jest called, determine what kind of pager to use."""
    global pager
    pager = getpager()
    pager(text)

def getpager():
    """Decide what method to use dla paging through text."""
    jeżeli nie hasattr(sys.stdin, "isatty"):
        zwróć plainpager
    jeżeli nie hasattr(sys.stdout, "isatty"):
        zwróć plainpager
    jeżeli nie sys.stdin.isatty() albo nie sys.stdout.isatty():
        zwróć plainpager
    jeżeli 'PAGER' w os.environ:
        jeżeli sys.platform == 'win32': # pipes completely broken w Windows
            zwróć lambda text: tempfilepager(plain(text), os.environ['PAGER'])
        albo_inaczej os.environ.get('TERM') w ('dumb', 'emacs'):
            zwróć lambda text: pipepager(plain(text), os.environ['PAGER'])
        inaczej:
            zwróć lambda text: pipepager(text, os.environ['PAGER'])
    jeżeli os.environ.get('TERM') w ('dumb', 'emacs'):
        zwróć plainpager
    jeżeli sys.platform == 'win32':
        zwróć lambda text: tempfilepager(plain(text), 'more <')
    jeżeli hasattr(os, 'system') oraz os.system('(less) 2>/dev/null') == 0:
        zwróć lambda text: pipepager(text, 'less')

    zaimportuj tempfile
    (fd, filename) = tempfile.mkstemp()
    os.close(fd)
    spróbuj:
        jeżeli hasattr(os, 'system') oraz os.system('more "%s"' % filename) == 0:
            zwróć lambda text: pipepager(text, 'more')
        inaczej:
            zwróć ttypager
    w_końcu:
        os.unlink(filename)

def plain(text):
    """Remove boldface formatting z text."""
    zwróć re.sub('.\b', '', text)

def pipepager(text, cmd):
    """Page through text by feeding it to another program."""
    zaimportuj subprocess
    proc = subprocess.Popen(cmd, shell=Prawda, stdin=subprocess.PIPE)
    spróbuj:
        przy io.TextIOWrapper(proc.stdin, errors='backslashreplace') jako pipe:
            spróbuj:
                pipe.write(text)
            wyjąwszy KeyboardInterrupt:
                # We've hereby abandoned whatever text hasn't been written,
                # but the pager jest still w control of the terminal.
                dalej
    wyjąwszy OSError:
        dalej # Ignore broken pipes caused by quitting the pager program.
    dopóki Prawda:
        spróbuj:
            proc.wait()
            przerwij
        wyjąwszy KeyboardInterrupt:
            # Ignore ctl-c like the pager itself does.  Otherwise the pager jest
            # left running oraz the terminal jest w raw mode oraz unusable.
            dalej

def tempfilepager(text, cmd):
    """Page through text by invoking a program on a temporary file."""
    zaimportuj tempfile
    filename = tempfile.mktemp()
    przy open(filename, 'w', errors='backslashreplace') jako file:
        file.write(text)
    spróbuj:
        os.system(cmd + ' "' + filename + '"')
    w_końcu:
        os.unlink(filename)

def _escape_stdout(text):
    # Escape non-encodable characters to avoid encoding errors later
    encoding = getattr(sys.stdout, 'encoding', Nic) albo 'utf-8'
    zwróć text.encode(encoding, 'backslashreplace').decode(encoding)

def ttypager(text):
    """Page through text on a text terminal."""
    lines = plain(_escape_stdout(text)).split('\n')
    spróbuj:
        zaimportuj tty
        fd = sys.stdin.fileno()
        old = tty.tcgetattr(fd)
        tty.setcbreak(fd)
        getchar = lambda: sys.stdin.read(1)
    wyjąwszy (ImportError, AttributeError, io.UnsupportedOperation):
        tty = Nic
        getchar = lambda: sys.stdin.readline()[:-1][:1]

    spróbuj:
        spróbuj:
            h = int(os.environ.get('LINES', 0))
        wyjąwszy ValueError:
            h = 0
        jeżeli h <= 1:
            h = 25
        r = inc = h - 1
        sys.stdout.write('\n'.join(lines[:inc]) + '\n')
        dopóki lines[r:]:
            sys.stdout.write('-- more --')
            sys.stdout.flush()
            c = getchar()

            jeżeli c w ('q', 'Q'):
                sys.stdout.write('\r          \r')
                przerwij
            albo_inaczej c w ('\r', '\n'):
                sys.stdout.write('\r          \r' + lines[r] + '\n')
                r = r + 1
                kontynuuj
            jeżeli c w ('b', 'B', '\x1b'):
                r = r - inc - inc
                jeżeli r < 0: r = 0
            sys.stdout.write('\n' + '\n'.join(lines[r:r+inc]) + '\n')
            r = r + inc

    w_końcu:
        jeżeli tty:
            tty.tcsetattr(fd, tty.TCSAFLUSH, old)

def plainpager(text):
    """Simply print unformatted text.  This jest the ultimate fallback."""
    sys.stdout.write(plain(_escape_stdout(text)))

def describe(thing):
    """Produce a short description of the given thing."""
    jeżeli inspect.ismodule(thing):
        jeżeli thing.__name__ w sys.builtin_module_names:
            zwróć 'built-in module ' + thing.__name__
        jeżeli hasattr(thing, '__path__'):
            zwróć 'package ' + thing.__name__
        inaczej:
            zwróć 'module ' + thing.__name__
    jeżeli inspect.isbuiltin(thing):
        zwróć 'built-in function ' + thing.__name__
    jeżeli inspect.isgetsetdescriptor(thing):
        zwróć 'getset descriptor %s.%s.%s' % (
            thing.__objclass__.__module__, thing.__objclass__.__name__,
            thing.__name__)
    jeżeli inspect.ismemberdescriptor(thing):
        zwróć 'member descriptor %s.%s.%s' % (
            thing.__objclass__.__module__, thing.__objclass__.__name__,
            thing.__name__)
    jeżeli inspect.isclass(thing):
        zwróć 'class ' + thing.__name__
    jeżeli inspect.isfunction(thing):
        zwróć 'function ' + thing.__name__
    jeżeli inspect.ismethod(thing):
        zwróć 'method ' + thing.__name__
    zwróć type(thing).__name__

def locate(path, forceload=0):
    """Locate an object by name albo dotted path, importing jako necessary."""
    parts = [part dla part w path.split('.') jeżeli part]
    module, n = Nic, 0
    dopóki n < len(parts):
        nextmodule = safeimport('.'.join(parts[:n+1]), forceload)
        jeżeli nextmodule: module, n = nextmodule, n + 1
        inaczej: przerwij
    jeżeli module:
        object = module
    inaczej:
        object = builtins
    dla part w parts[n:]:
        spróbuj:
            object = getattr(object, part)
        wyjąwszy AttributeError:
            zwróć Nic
    zwróć object

# --------------------------------------- interactive interpreter interface

text = TextDoc()
plaintext = _PlainTextDoc()
html = HTMLDoc()

def resolve(thing, forceload=0):
    """Given an object albo a path to an object, get the object oraz its name."""
    jeżeli isinstance(thing, str):
        object = locate(thing, forceload)
        jeżeli object jest Nic:
            podnieś ImportError('''\
No Python documentation found dla %r.
Use help() to get the interactive help utility.
Use help(str) dla help on the str class.''' % thing)
        zwróć object, thing
    inaczej:
        name = getattr(thing, '__name__', Nic)
        zwróć thing, name jeżeli isinstance(name, str) inaczej Nic

def render_doc(thing, title='Python Library Documentation: %s', forceload=0,
        renderer=Nic):
    """Render text documentation, given an object albo a path to an object."""
    jeżeli renderer jest Nic:
        renderer = text
    object, name = resolve(thing, forceload)
    desc = describe(object)
    module = inspect.getmodule(object)
    jeżeli name oraz '.' w name:
        desc += ' w ' + name[:name.rfind('.')]
    albo_inaczej module oraz module jest nie object:
        desc += ' w module ' + module.__name__

    jeżeli nie (inspect.ismodule(object) albo
              inspect.isclass(object) albo
              inspect.isroutine(object) albo
              inspect.isgetsetdescriptor(object) albo
              inspect.ismemberdescriptor(object) albo
              isinstance(object, property)):
        # If the dalejed object jest a piece of data albo an instance,
        # document its available methods instead of its value.
        object = type(object)
        desc += ' object'
    zwróć title % desc + '\n\n' + renderer.document(object, name)

def doc(thing, title='Python Library Documentation: %s', forceload=0,
        output=Nic):
    """Display text documentation, given an object albo a path to an object."""
    spróbuj:
        jeżeli output jest Nic:
            pager(render_doc(thing, title, forceload))
        inaczej:
            output.write(render_doc(thing, title, forceload, plaintext))
    wyjąwszy (ImportError, ErrorDuringImport) jako value:
        print(value)

def writedoc(thing, forceload=0):
    """Write HTML documentation to a file w the current directory."""
    spróbuj:
        object, name = resolve(thing, forceload)
        page = html.page(describe(object), html.document(object, name))
        przy open(name + '.html', 'w', encoding='utf-8') jako file:
            file.write(page)
        print('wrote', name + '.html')
    wyjąwszy (ImportError, ErrorDuringImport) jako value:
        print(value)

def writedocs(dir, pkgpath='', done=Nic):
    """Write out HTML documentation dla all modules w a directory tree."""
    jeżeli done jest Nic: done = {}
    dla importer, modname, ispkg w pkgutil.walk_packages([dir], pkgpath):
        writedoc(modname)
    zwróć

klasa Helper:

    # These dictionaries map a topic name to either an alias, albo a tuple
    # (label, seealso-items).  The "label" jest the label of the corresponding
    # section w the .rst file under Doc/ oraz an index into the dictionary
    # w pydoc_data/topics.py.
    #
    # CAUTION: jeżeli you change one of these dictionaries, be sure to adapt the
    #          list of needed labels w Doc/tools/pyspecific.py oraz
    #          regenerate the pydoc_data/topics.py file by running
    #              make pydoc-topics
    #          w Doc/ oraz copying the output file into the Lib/ directory.

    keywords = {
        'Nieprawda': '',
        'Nic': '',
        'Prawda': '',
        'and': 'BOOLEAN',
        'as': 'przy',
        'assert': ('assert', ''),
        'break': ('break', 'dopóki for'),
        'class': ('class', 'CLASSES SPECIALMETHODS'),
        'continue': ('continue', 'dopóki for'),
        'def': ('function', ''),
        'del': ('del', 'BASICMETHODS'),
        'elif': 'if',
        'inaczej': ('inaczej', 'dopóki for'),
        'wyjąwszy': 'try',
        'w_końcu': 'try',
        'for': ('for', 'break continue while'),
        'from': 'import',
        'global': ('global', 'nonlocal NAMESPACES'),
        'if': ('if', 'TRUTHVALUE'),
        'import': ('import', 'MODULES'),
        'in': ('in', 'SEQUENCEMETHODS'),
        'is': 'COMPARISON',
        'lambda': ('lambda', 'FUNCTIONS'),
        'nonlocal': ('nonlocal', 'global NAMESPACES'),
        'not': 'BOOLEAN',
        'or': 'BOOLEAN',
        'pass': ('pass', ''),
        'raise': ('raise', 'EXCEPTIONS'),
        'return': ('return', 'FUNCTIONS'),
        'try': ('try', 'EXCEPTIONS'),
        'while': ('while', 'break continue jeżeli TRUTHVALUE'),
        'przy': ('przy', 'CONTEXTMANAGERS EXCEPTIONS uzyskaj'),
        'uzyskaj': ('uzyskaj', ''),
    }
    # Either add symbols to this dictionary albo to the symbols dictionary
    # directly: Whichever jest easier. They are merged later.
    _symbols_inverse = {
        'STRINGS' : ("'", "'''", "r'", "b'", '"""', '"', 'r"', 'b"'),
        'OPERATORS' : ('+', '-', '*', '**', '/', '//', '%', '<<', '>>', '&',
                       '|', '^', '~', '<', '>', '<=', '>=', '==', '!=', '<>'),
        'COMPARISON' : ('<', '>', '<=', '>=', '==', '!=', '<>'),
        'UNARY' : ('-', '~'),
        'AUGMENTEDASSIGNMENT' : ('+=', '-=', '*=', '/=', '%=', '&=', '|=',
                                '^=', '<<=', '>>=', '**=', '//='),
        'BITWISE' : ('<<', '>>', '&', '|', '^', '~'),
        'COMPLEX' : ('j', 'J')
    }
    symbols = {
        '%': 'OPERATORS FORMATTING',
        '**': 'POWER',
        ',': 'TUPLES LISTS FUNCTIONS',
        '.': 'ATTRIBUTES FLOAT MODULES OBJECTS',
        '...': 'ELLIPSIS',
        ':': 'SLICINGS DICTIONARYLITERALS',
        '@': 'def class',
        '\\': 'STRINGS',
        '_': 'PRIVATENAMES',
        '__': 'PRIVATENAMES SPECIALMETHODS',
        '`': 'BACKQUOTES',
        '(': 'TUPLES FUNCTIONS CALLS',
        ')': 'TUPLES FUNCTIONS CALLS',
        '[': 'LISTS SUBSCRIPTS SLICINGS',
        ']': 'LISTS SUBSCRIPTS SLICINGS'
    }
    dla topic, symbols_ w _symbols_inverse.items():
        dla symbol w symbols_:
            topics = symbols.get(symbol, topic)
            jeżeli topic nie w topics:
                topics = topics + ' ' + topic
            symbols[symbol] = topics

    topics = {
        'TYPES': ('types', 'STRINGS UNICODE NUMBERS SEQUENCES MAPPINGS '
                  'FUNCTIONS CLASSES MODULES FILES inspect'),
        'STRINGS': ('strings', 'str UNICODE SEQUENCES STRINGMETHODS '
                    'FORMATTING TYPES'),
        'STRINGMETHODS': ('string-methods', 'STRINGS FORMATTING'),
        'FORMATTING': ('formatstrings', 'OPERATORS'),
        'UNICODE': ('strings', 'encodings unicode SEQUENCES STRINGMETHODS '
                    'FORMATTING TYPES'),
        'NUMBERS': ('numbers', 'INTEGER FLOAT COMPLEX TYPES'),
        'INTEGER': ('integers', 'int range'),
        'FLOAT': ('floating', 'float math'),
        'COMPLEX': ('imaginary', 'complex cmath'),
        'SEQUENCES': ('typesseq', 'STRINGMETHODS FORMATTING range LISTS'),
        'MAPPINGS': 'DICTIONARIES',
        'FUNCTIONS': ('typesfunctions', 'def TYPES'),
        'METHODS': ('typesmethods', 'class def CLASSES TYPES'),
        'CODEOBJECTS': ('bltin-code-objects', 'compile FUNCTIONS TYPES'),
        'TYPEOBJECTS': ('bltin-type-objects', 'types TYPES'),
        'FRAMEOBJECTS': 'TYPES',
        'TRACEBACKS': 'TYPES',
        'NONE': ('bltin-null-object', ''),
        'ELLIPSIS': ('bltin-ellipsis-object', 'SLICINGS'),
        'SPECIALATTRIBUTES': ('specialattrs', ''),
        'CLASSES': ('types', 'class SPECIALMETHODS PRIVATENAMES'),
        'MODULES': ('typesmodules', 'import'),
        'PACKAGES': 'import',
        'EXPRESSIONS': ('operator-summary', 'lambda albo oraz nie w jest BOOLEAN '
                        'COMPARISON BITWISE SHIFTING BINARY FORMATTING POWER '
                        'UNARY ATTRIBUTES SUBSCRIPTS SLICINGS CALLS TUPLES '
                        'LISTS DICTIONARIES'),
        'OPERATORS': 'EXPRESSIONS',
        'PRECEDENCE': 'EXPRESSIONS',
        'OBJECTS': ('objects', 'TYPES'),
        'SPECIALMETHODS': ('specialnames', 'BASICMETHODS ATTRIBUTEMETHODS '
                           'CALLABLEMETHODS SEQUENCEMETHODS MAPPINGMETHODS '
                           'NUMBERMETHODS CLASSES'),
        'BASICMETHODS': ('customization', 'hash repr str SPECIALMETHODS'),
        'ATTRIBUTEMETHODS': ('attribute-access', 'ATTRIBUTES SPECIALMETHODS'),
        'CALLABLEMETHODS': ('callable-types', 'CALLS SPECIALMETHODS'),
        'SEQUENCEMETHODS': ('sequence-types', 'SEQUENCES SEQUENCEMETHODS '
                             'SPECIALMETHODS'),
        'MAPPINGMETHODS': ('sequence-types', 'MAPPINGS SPECIALMETHODS'),
        'NUMBERMETHODS': ('numeric-types', 'NUMBERS AUGMENTEDASSIGNMENT '
                          'SPECIALMETHODS'),
        'EXECUTION': ('execmodel', 'NAMESPACES DYNAMICFEATURES EXCEPTIONS'),
        'NAMESPACES': ('naming', 'global nonlocal ASSIGNMENT DELETION DYNAMICFEATURES'),
        'DYNAMICFEATURES': ('dynamic-features', ''),
        'SCOPING': 'NAMESPACES',
        'FRAMES': 'NAMESPACES',
        'EXCEPTIONS': ('exceptions', 'try wyjąwszy finally podnieś'),
        'CONVERSIONS': ('conversions', ''),
        'IDENTIFIERS': ('identifiers', 'keywords SPECIALIDENTIFIERS'),
        'SPECIALIDENTIFIERS': ('id-classes', ''),
        'PRIVATENAMES': ('atom-identifiers', ''),
        'LITERALS': ('atom-literals', 'STRINGS NUMBERS TUPLELITERALS '
                     'LISTLITERALS DICTIONARYLITERALS'),
        'TUPLES': 'SEQUENCES',
        'TUPLELITERALS': ('exprlists', 'TUPLES LITERALS'),
        'LISTS': ('typesseq-mutable', 'LISTLITERALS'),
        'LISTLITERALS': ('lists', 'LISTS LITERALS'),
        'DICTIONARIES': ('typesmapping', 'DICTIONARYLITERALS'),
        'DICTIONARYLITERALS': ('dict', 'DICTIONARIES LITERALS'),
        'ATTRIBUTES': ('attribute-references', 'getattr hasattr setattr ATTRIBUTEMETHODS'),
        'SUBSCRIPTS': ('subscriptions', 'SEQUENCEMETHODS'),
        'SLICINGS': ('slicings', 'SEQUENCEMETHODS'),
        'CALLS': ('calls', 'EXPRESSIONS'),
        'POWER': ('power', 'EXPRESSIONS'),
        'UNARY': ('unary', 'EXPRESSIONS'),
        'BINARY': ('binary', 'EXPRESSIONS'),
        'SHIFTING': ('shifting', 'EXPRESSIONS'),
        'BITWISE': ('bitwise', 'EXPRESSIONS'),
        'COMPARISON': ('comparisons', 'EXPRESSIONS BASICMETHODS'),
        'BOOLEAN': ('booleans', 'EXPRESSIONS TRUTHVALUE'),
        'ASSERTION': 'assert',
        'ASSIGNMENT': ('assignment', 'AUGMENTEDASSIGNMENT'),
        'AUGMENTEDASSIGNMENT': ('augassign', 'NUMBERMETHODS'),
        'DELETION': 'del',
        'RETURNING': 'return',
        'IMPORTING': 'import',
        'CONDITIONAL': 'if',
        'LOOPING': ('compound', 'dla dopóki przerwij continue'),
        'TRUTHVALUE': ('truth', 'jeżeli dopóki oraz albo nie BASICMETHODS'),
        'DEBUGGING': ('debugger', 'pdb'),
        'CONTEXTMANAGERS': ('context-managers', 'przy'),
    }

    def __init__(self, input=Nic, output=Nic):
        self._input = input
        self._output = output

    input  = property(lambda self: self._input albo sys.stdin)
    output = property(lambda self: self._output albo sys.stdout)

    def __repr__(self):
        jeżeli inspect.stack()[1][3] == '?':
            self()
            zwróć ''
        zwróć '<%s.%s instance>' % (self.__class__.__module__,
                                     self.__class__.__qualname__)

    _GoInteractive = object()
    def __call__(self, request=_GoInteractive):
        jeżeli request jest nie self._GoInteractive:
            self.help(request)
        inaczej:
            self.intro()
            self.interact()
            self.output.write('''
You are now leaving help oraz returning to the Python interpreter.
If you want to ask dla help on a particular object directly z the
interpreter, you can type "help(object)".  Executing "help('string')"
has the same effect jako typing a particular string at the help> prompt.
''')

    def interact(self):
        self.output.write('\n')
        dopóki Prawda:
            spróbuj:
                request = self.getline('help> ')
                jeżeli nie request: przerwij
            wyjąwszy (KeyboardInterrupt, EOFError):
                przerwij
            request = replace(request, '"', '', "'", '').strip()
            jeżeli request.lower() w ('q', 'quit'): przerwij
            jeżeli request == 'help':
                self.intro()
            inaczej:
                self.help(request)

    def getline(self, prompt):
        """Read one line, using input() when appropriate."""
        jeżeli self.input jest sys.stdin:
            zwróć input(prompt)
        inaczej:
            self.output.write(prompt)
            self.output.flush()
            zwróć self.input.readline()

    def help(self, request):
        jeżeli type(request) jest type(''):
            request = request.strip()
            jeżeli request == 'keywords': self.listkeywords()
            albo_inaczej request == 'symbols': self.listsymbols()
            albo_inaczej request == 'topics': self.listtopics()
            albo_inaczej request == 'modules': self.listmodules()
            albo_inaczej request[:8] == 'modules ':
                self.listmodules(request.split()[1])
            albo_inaczej request w self.symbols: self.showsymbol(request)
            albo_inaczej request w ['Prawda', 'Nieprawda', 'Nic']:
                # special case these keywords since they are objects too
                doc(eval(request), 'Help on %s:')
            albo_inaczej request w self.keywords: self.showtopic(request)
            albo_inaczej request w self.topics: self.showtopic(request)
            albo_inaczej request: doc(request, 'Help on %s:', output=self._output)
            inaczej: doc(str, 'Help on %s:', output=self._output)
        albo_inaczej isinstance(request, Helper): self()
        inaczej: doc(request, 'Help on %s:', output=self._output)
        self.output.write('\n')

    def intro(self):
        self.output.write('''
Welcome to Python %s's help utility!

If this jest your first time using Python, you should definitely check out
the tutorial on the Internet at http://docs.python.org/%s/tutorial/.

Enter the name of any module, keyword, albo topic to get help on writing
Python programs oraz using Python modules.  To quit this help utility oraz
return to the interpreter, just type "quit".

To get a list of available modules, keywords, symbols, albo topics, type
"modules", "keywords", "symbols", albo "topics".  Each module also comes
przy a one-line summary of what it does; to list the modules whose name
or summary contain a given string such jako "spam", type "modules spam".
''' % tuple([sys.version[:3]]*2))

    def list(self, items, columns=4, width=80):
        items = list(sorted(items))
        colw = width // columns
        rows = (len(items) + columns - 1) // columns
        dla row w range(rows):
            dla col w range(columns):
                i = col * rows + row
                jeżeli i < len(items):
                    self.output.write(items[i])
                    jeżeli col < columns - 1:
                        self.output.write(' ' + ' ' * (colw - 1 - len(items[i])))
            self.output.write('\n')

    def listkeywords(self):
        self.output.write('''
Here jest a list of the Python keywords.  Enter any keyword to get more help.

''')
        self.list(self.keywords.keys())

    def listsymbols(self):
        self.output.write('''
Here jest a list of the punctuation symbols which Python assigns special meaning
to. Enter any symbol to get more help.

''')
        self.list(self.symbols.keys())

    def listtopics(self):
        self.output.write('''
Here jest a list of available topics.  Enter any topic name to get more help.

''')
        self.list(self.topics.keys())

    def showtopic(self, topic, more_xrefs=''):
        spróbuj:
            zaimportuj pydoc_data.topics
        wyjąwszy ImportError:
            self.output.write('''
Sorry, topic oraz keyword documentation jest nie available because the
module "pydoc_data.topics" could nie be found.
''')
            zwróć
        target = self.topics.get(topic, self.keywords.get(topic))
        jeżeli nie target:
            self.output.write('no documentation found dla %s\n' % repr(topic))
            zwróć
        jeżeli type(target) jest type(''):
            zwróć self.showtopic(target, more_xrefs)

        label, xrefs = target
        spróbuj:
            doc = pydoc_data.topics.topics[label]
        wyjąwszy KeyError:
            self.output.write('no documentation found dla %s\n' % repr(topic))
            zwróć
        pager(doc.strip() + '\n')
        jeżeli more_xrefs:
            xrefs = (xrefs albo '') + ' ' + more_xrefs
        jeżeli xrefs:
            zaimportuj textwrap
            text = 'Related help topics: ' + ', '.join(xrefs.split()) + '\n'
            wrapped_text = textwrap.wrap(text, 72)
            self.output.write('\n%s\n' % ''.join(wrapped_text))

    def _gettopic(self, topic, more_xrefs=''):
        """Return unbuffered tuple of (topic, xrefs).

        If an error occurs here, the exception jest caught oraz displayed by
        the url handler.

        This function duplicates the showtopic method but returns its
        result directly so it can be formatted dla display w an html page.
        """
        spróbuj:
            zaimportuj pydoc_data.topics
        wyjąwszy ImportError:
            return('''
Sorry, topic oraz keyword documentation jest nie available because the
module "pydoc_data.topics" could nie be found.
''' , '')
        target = self.topics.get(topic, self.keywords.get(topic))
        jeżeli nie target:
            podnieś ValueError('could nie find topic')
        jeżeli isinstance(target, str):
            zwróć self._gettopic(target, more_xrefs)
        label, xrefs = target
        doc = pydoc_data.topics.topics[label]
        jeżeli more_xrefs:
            xrefs = (xrefs albo '') + ' ' + more_xrefs
        zwróć doc, xrefs

    def showsymbol(self, symbol):
        target = self.symbols[symbol]
        topic, _, xrefs = target.partition(' ')
        self.showtopic(topic, xrefs)

    def listmodules(self, key=''):
        jeżeli key:
            self.output.write('''
Here jest a list of modules whose name albo summary contains '{}'.
If there are any, enter a module name to get more help.

'''.format(key))
            apropos(key)
        inaczej:
            self.output.write('''
Please wait a moment dopóki I gather a list of all available modules...

''')
            modules = {}
            def callback(path, modname, desc, modules=modules):
                jeżeli modname oraz modname[-9:] == '.__init__':
                    modname = modname[:-9] + ' (package)'
                jeżeli modname.find('.') < 0:
                    modules[modname] = 1
            def onerror(modname):
                callback(Nic, modname, Nic)
            ModuleScanner().run(callback, onerror=onerror)
            self.list(modules.keys())
            self.output.write('''
Enter any module name to get more help.  Or, type "modules spam" to search
dla modules whose name albo summary contain the string "spam".
''')

help = Helper()

klasa ModuleScanner:
    """An interruptible scanner that searches module synopses."""

    def run(self, callback, key=Nic, completer=Nic, onerror=Nic):
        jeżeli key: key = key.lower()
        self.quit = Nieprawda
        seen = {}

        dla modname w sys.builtin_module_names:
            jeżeli modname != '__main__':
                seen[modname] = 1
                jeżeli key jest Nic:
                    callback(Nic, modname, '')
                inaczej:
                    name = __import__(modname).__doc__ albo ''
                    desc = name.split('\n')[0]
                    name = modname + ' - ' + desc
                    jeżeli name.lower().find(key) >= 0:
                        callback(Nic, modname, desc)

        dla importer, modname, ispkg w pkgutil.walk_packages(onerror=onerror):
            jeżeli self.quit:
                przerwij

            jeżeli key jest Nic:
                callback(Nic, modname, '')
            inaczej:
                spróbuj:
                    spec = pkgutil._get_spec(importer, modname)
                wyjąwszy SyntaxError:
                    # podnieśd by tests dla bad coding cookies albo BOM
                    kontynuuj
                loader = spec.loader
                jeżeli hasattr(loader, 'get_source'):
                    spróbuj:
                        source = loader.get_source(modname)
                    wyjąwszy Exception:
                        jeżeli onerror:
                            onerror(modname)
                        kontynuuj
                    desc = source_synopsis(io.StringIO(source)) albo ''
                    jeżeli hasattr(loader, 'get_filename'):
                        path = loader.get_filename(modname)
                    inaczej:
                        path = Nic
                inaczej:
                    spróbuj:
                        module = importlib._bootstrap._load(spec)
                    wyjąwszy ImportError:
                        jeżeli onerror:
                            onerror(modname)
                        kontynuuj
                    desc = module.__doc__.splitlines()[0] jeżeli module.__doc__ inaczej ''
                    path = getattr(module,'__file__',Nic)
                name = modname + ' - ' + desc
                jeżeli name.lower().find(key) >= 0:
                    callback(path, modname, desc)

        jeżeli completer:
            completer()

def apropos(key):
    """Print all the one-line module summaries that contain a substring."""
    def callback(path, modname, desc):
        jeżeli modname[-9:] == '.__init__':
            modname = modname[:-9] + ' (package)'
        print(modname, desc oraz '- ' + desc)
    def onerror(modname):
        dalej
    przy warnings.catch_warnings():
        warnings.filterwarnings('ignore') # ignore problems during import
        ModuleScanner().run(callback, key, onerror=onerror)

# --------------------------------------- enhanced Web browser interface

def _start_server(urlhandler, port):
    """Start an HTTP server thread on a specific port.

    Start an HTML/text server thread, so HTML albo text documents can be
    browsed dynamically oraz interactively przy a Web browser.  Example use:

        >>> zaimportuj time
        >>> zaimportuj pydoc

        Define a URL handler.  To determine what the client jest asking
        for, check the URL oraz content_type.

        Then get albo generate some text albo HTML code oraz zwróć it.

        >>> def my_url_handler(url, content_type):
        ...     text = 'the URL sent was: (%s, %s)' % (url, content_type)
        ...     zwróć text

        Start server thread on port 0.
        If you use port 0, the server will pick a random port number.
        You can then use serverthread.port to get the port number.

        >>> port = 0
        >>> serverthread = pydoc._start_server(my_url_handler, port)

        Check that the server jest really started.  If it is, open browser
        oraz get first page.  Use serverthread.url jako the starting page.

        >>> jeżeli serverthread.serving:
        ...    zaimportuj webbrowser

        The next two lines are commented out so a browser doesn't open if
        doctest jest run on this module.

        #...    webbrowser.open(serverthread.url)
        #Prawda

        Let the server do its thing. We just need to monitor its status.
        Use time.sleep so the loop doesn't hog the CPU.

        >>> starttime = time.time()
        >>> timeout = 1                    #seconds

        This jest a short timeout dla testing purposes.

        >>> dopóki serverthread.serving:
        ...     time.sleep(.01)
        ...     jeżeli serverthread.serving oraz time.time() - starttime > timeout:
        ...          serverthread.stop()
        ...          przerwij

        Print any errors that may have occurred.

        >>> print(serverthread.error)
        Nic
   """
    zaimportuj http.server
    zaimportuj email.message
    zaimportuj select
    zaimportuj threading

    klasa DocHandler(http.server.BaseHTTPRequestHandler):

        def do_GET(self):
            """Process a request z an HTML browser.

            The URL received jest w self.path.
            Get an HTML page z self.urlhandler oraz send it.
            """
            jeżeli self.path.endswith('.css'):
                content_type = 'text/css'
            inaczej:
                content_type = 'text/html'
            self.send_response(200)
            self.send_header('Content-Type', '%s; charset=UTF-8' % content_type)
            self.end_headers()
            self.wfile.write(self.urlhandler(
                self.path, content_type).encode('utf-8'))

        def log_message(self, *args):
            # Don't log messages.
            dalej

    klasa DocServer(http.server.HTTPServer):

        def __init__(self, port, callback):
            self.host = 'localhost'
            self.address = (self.host, port)
            self.callback = callback
            self.base.__init__(self, self.address, self.handler)
            self.quit = Nieprawda

        def serve_until_quit(self):
            dopóki nie self.quit:
                rd, wr, ex = select.select([self.socket.fileno()], [], [], 1)
                jeżeli rd:
                    self.handle_request()
            self.server_close()

        def server_activate(self):
            self.base.server_activate(self)
            jeżeli self.callback:
                self.callback(self)

    klasa ServerThread(threading.Thread):

        def __init__(self, urlhandler, port):
            self.urlhandler = urlhandler
            self.port = int(port)
            threading.Thread.__init__(self)
            self.serving = Nieprawda
            self.error = Nic

        def run(self):
            """Start the server."""
            spróbuj:
                DocServer.base = http.server.HTTPServer
                DocServer.handler = DocHandler
                DocHandler.MessageClass = email.message.Message
                DocHandler.urlhandler = staticmethod(self.urlhandler)
                docsvr = DocServer(self.port, self.ready)
                self.docserver = docsvr
                docsvr.serve_until_quit()
            wyjąwszy Exception jako e:
                self.error = e

        def ready(self, server):
            self.serving = Prawda
            self.host = server.host
            self.port = server.server_port
            self.url = 'http://%s:%d/' % (self.host, self.port)

        def stop(self):
            """Stop the server oraz this thread nicely"""
            self.docserver.quit = Prawda
            self.serving = Nieprawda
            self.url = Nic

    thread = ServerThread(urlhandler, port)
    thread.start()
    # Wait until thread.serving jest Prawda to make sure we are
    # really up before returning.
    dopóki nie thread.error oraz nie thread.serving:
        time.sleep(.01)
    zwróć thread


def _url_handler(url, content_type="text/html"):
    """The pydoc url handler dla use przy the pydoc server.

    If the content_type jest 'text/css', the _pydoc.css style
    sheet jest read oraz returned jeżeli it exits.

    If the content_type jest 'text/html', then the result of
    get_html_page(url) jest returned.
    """
    klasa _HTMLDoc(HTMLDoc):

        def page(self, title, contents):
            """Format an HTML page."""
            css_path = "pydoc_data/_pydoc.css"
            css_link = (
                '<link rel="stylesheet" type="text/css" href="%s">' %
                css_path)
            zwróć '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Pydoc: %s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
%s</head><body bgcolor="#f0f0f8">%s<div style="clear:both;padding-top:.5em;">%s</div>
</body></html>''' % (title, css_link, html_navbar(), contents)

        def filelink(self, url, path):
            zwróć '<a href="getfile?key=%s">%s</a>' % (url, path)


    html = _HTMLDoc()

    def html_navbar():
        version = html.escape("%s [%s, %s]" % (platform.python_version(),
                                               platform.python_build()[0],
                                               platform.python_compiler()))
        zwróć """
            <div style='float:left'>
                Python %s<br>%s
            </div>
            <div style='float:right'>
                <div style='text-align:center'>
                  <a href="index.html">Module Index</a>
                  : <a href="topics.html">Topics</a>
                  : <a href="keywords.html">Keywords</a>
                </div>
                <div>
                    <form action="get" style='display:inline;'>
                      <input type=text name=key size=15>
                      <input type=submit value="Get">
                    </form>&nbsp;
                    <form action="search" style='display:inline;'>
                      <input type=text name=key size=15>
                      <input type=submit value="Search">
                    </form>
                </div>
            </div>
            """ % (version, html.escape(platform.platform(terse=Prawda)))

    def html_index():
        """Module Index page."""

        def bltinlink(name):
            zwróć '<a href="%s.html">%s</a>' % (name, name)

        heading = html.heading(
            '<big><big><strong>Index of Modules</strong></big></big>',
            '#ffffff', '#7799ee')
        names = [name dla name w sys.builtin_module_names
                 jeżeli name != '__main__']
        contents = html.multicolumn(names, bltinlink)
        contents = [heading, '<p>' + html.bigsection(
            'Built-in Modules', '#ffffff', '#ee77aa', contents)]

        seen = {}
        dla dir w sys.path:
            contents.append(html.index(dir, seen))

        contents.append(
            '<p align=right><font color="#909090" face="helvetica,'
            'arial"><strong>pydoc</strong> by Ka-Ping Yee'
            '&lt;ping@lfw.org&gt;</font>')
        zwróć 'Index of Modules', ''.join(contents)

    def html_search(key):
        """Search results page."""
        # scan dla modules
        search_result = []

        def callback(path, modname, desc):
            jeżeli modname[-9:] == '.__init__':
                modname = modname[:-9] + ' (package)'
            search_result.append((modname, desc oraz '- ' + desc))

        przy warnings.catch_warnings():
            warnings.filterwarnings('ignore') # ignore problems during import
            ModuleScanner().run(callback, key)

        # format page
        def bltinlink(name):
            zwróć '<a href="%s.html">%s</a>' % (name, name)

        results = []
        heading = html.heading(
            '<big><big><strong>Search Results</strong></big></big>',
            '#ffffff', '#7799ee')
        dla name, desc w search_result:
            results.append(bltinlink(name) + desc)
        contents = heading + html.bigsection(
            'key = %s' % key, '#ffffff', '#ee77aa', '<br>'.join(results))
        zwróć 'Search Results', contents

    def html_getfile(path):
        """Get oraz display a source file listing safely."""
        path = urllib.parse.unquote(path)
        przy tokenize.open(path) jako fp:
            lines = html.escape(fp.read())
        body = '<pre>%s</pre>' % lines
        heading = html.heading(
            '<big><big><strong>File Listing</strong></big></big>',
            '#ffffff', '#7799ee')
        contents = heading + html.bigsection(
            'File: %s' % path, '#ffffff', '#ee77aa', body)
        zwróć 'getfile %s' % path, contents

    def html_topics():
        """Index of topic texts available."""

        def bltinlink(name):
            zwróć '<a href="topic?key=%s">%s</a>' % (name, name)

        heading = html.heading(
            '<big><big><strong>INDEX</strong></big></big>',
            '#ffffff', '#7799ee')
        names = sorted(Helper.topics.keys())

        contents = html.multicolumn(names, bltinlink)
        contents = heading + html.bigsection(
            'Topics', '#ffffff', '#ee77aa', contents)
        zwróć 'Topics', contents

    def html_keywords():
        """Index of keywords."""
        heading = html.heading(
            '<big><big><strong>INDEX</strong></big></big>',
            '#ffffff', '#7799ee')
        names = sorted(Helper.keywords.keys())

        def bltinlink(name):
            zwróć '<a href="topic?key=%s">%s</a>' % (name, name)

        contents = html.multicolumn(names, bltinlink)
        contents = heading + html.bigsection(
            'Keywords', '#ffffff', '#ee77aa', contents)
        zwróć 'Keywords', contents

    def html_topicpage(topic):
        """Topic albo keyword help page."""
        buf = io.StringIO()
        htmlhelp = Helper(buf, buf)
        contents, xrefs = htmlhelp._gettopic(topic)
        jeżeli topic w htmlhelp.keywords:
            title = 'KEYWORD'
        inaczej:
            title = 'TOPIC'
        heading = html.heading(
            '<big><big><strong>%s</strong></big></big>' % title,
            '#ffffff', '#7799ee')
        contents = '<pre>%s</pre>' % html.markup(contents)
        contents = html.bigsection(topic , '#ffffff','#ee77aa', contents)
        jeżeli xrefs:
            xrefs = sorted(xrefs.split())

            def bltinlink(name):
                zwróć '<a href="topic?key=%s">%s</a>' % (name, name)

            xrefs = html.multicolumn(xrefs, bltinlink)
            xrefs = html.section('Related help topics: ',
                                 '#ffffff', '#ee77aa', xrefs)
        zwróć ('%s %s' % (title, topic),
                ''.join((heading, contents, xrefs)))

    def html_getobj(url):
        obj = locate(url, forceload=1)
        jeżeli obj jest Nic oraz url != 'Nic':
            podnieś ValueError('could nie find object')
        title = describe(obj)
        content = html.document(obj, url)
        zwróć title, content

    def html_error(url, exc):
        heading = html.heading(
            '<big><big><strong>Error</strong></big></big>',
            '#ffffff', '#7799ee')
        contents = '<br>'.join(html.escape(line) dla line w
                               format_exception_only(type(exc), exc))
        contents = heading + html.bigsection(url, '#ffffff', '#bb0000',
                                             contents)
        zwróć "Error - %s" % url, contents

    def get_html_page(url):
        """Generate an HTML page dla url."""
        complete_url = url
        jeżeli url.endswith('.html'):
            url = url[:-5]
        spróbuj:
            jeżeli url w ("", "index"):
                title, content = html_index()
            albo_inaczej url == "topics":
                title, content = html_topics()
            albo_inaczej url == "keywords":
                title, content = html_keywords()
            albo_inaczej '=' w url:
                op, _, url = url.partition('=')
                jeżeli op == "search?key":
                    title, content = html_search(url)
                albo_inaczej op == "getfile?key":
                    title, content = html_getfile(url)
                albo_inaczej op == "topic?key":
                    # try topics first, then objects.
                    spróbuj:
                        title, content = html_topicpage(url)
                    wyjąwszy ValueError:
                        title, content = html_getobj(url)
                albo_inaczej op == "get?key":
                    # try objects first, then topics.
                    jeżeli url w ("", "index"):
                        title, content = html_index()
                    inaczej:
                        spróbuj:
                            title, content = html_getobj(url)
                        wyjąwszy ValueError:
                            title, content = html_topicpage(url)
                inaczej:
                    podnieś ValueError('bad pydoc url')
            inaczej:
                title, content = html_getobj(url)
        wyjąwszy Exception jako exc:
            # Catch any errors oraz display them w an error page.
            title, content = html_error(complete_url, exc)
        zwróć html.page(title, content)

    jeżeli url.startswith('/'):
        url = url[1:]
    jeżeli content_type == 'text/css':
        path_here = os.path.dirname(os.path.realpath(__file__))
        css_path = os.path.join(path_here, url)
        przy open(css_path) jako fp:
            zwróć ''.join(fp.readlines())
    albo_inaczej content_type == 'text/html':
        zwróć get_html_page(url)
    # Errors outside the url handler are caught by the server.
    podnieś TypeError('unknown content type %r dla url %s' % (content_type, url))


def browse(port=0, *, open_browser=Prawda):
    """Start the enhanced pydoc Web server oraz open a Web browser.

    Use port '0' to start the server on an arbitrary port.
    Set open_browser to Nieprawda to suppress opening a browser.
    """
    zaimportuj webbrowser
    serverthread = _start_server(_url_handler, port)
    jeżeli serverthread.error:
        print(serverthread.error)
        zwróć
    jeżeli serverthread.serving:
        server_help_msg = 'Server commands: [b]rowser, [q]uit'
        jeżeli open_browser:
            webbrowser.open(serverthread.url)
        spróbuj:
            print('Server ready at', serverthread.url)
            print(server_help_msg)
            dopóki serverthread.serving:
                cmd = input('server> ')
                cmd = cmd.lower()
                jeżeli cmd == 'q':
                    przerwij
                albo_inaczej cmd == 'b':
                    webbrowser.open(serverthread.url)
                inaczej:
                    print(server_help_msg)
        wyjąwszy (KeyboardInterrupt, EOFError):
            print()
        w_końcu:
            jeżeli serverthread.serving:
                serverthread.stop()
                print('Server stopped')


# -------------------------------------------------- command-line interface

def ispath(x):
    zwróć isinstance(x, str) oraz x.find(os.sep) >= 0

def cli():
    """Command-line interface (looks at sys.argv to decide what to do)."""
    zaimportuj getopt
    klasa BadUsage(Exception): dalej

    # Scripts don't get the current directory w their path by default
    # unless they are run przy the '-m' switch
    jeżeli '' nie w sys.path:
        scriptdir = os.path.dirname(sys.argv[0])
        jeżeli scriptdir w sys.path:
            sys.path.remove(scriptdir)
        sys.path.insert(0, '.')

    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'bk:p:w')
        writing = Nieprawda
        start_server = Nieprawda
        open_browser = Nieprawda
        port = Nic
        dla opt, val w opts:
            jeżeli opt == '-b':
                start_server = Prawda
                open_browser = Prawda
            jeżeli opt == '-k':
                apropos(val)
                zwróć
            jeżeli opt == '-p':
                start_server = Prawda
                port = val
            jeżeli opt == '-w':
                writing = Prawda

        jeżeli start_server:
            jeżeli port jest Nic:
                port = 0
            browse(port, open_browser=open_browser)
            zwróć

        jeżeli nie args: podnieś BadUsage
        dla arg w args:
            jeżeli ispath(arg) oraz nie os.path.exists(arg):
                print('file %r does nie exist' % arg)
                przerwij
            spróbuj:
                jeżeli ispath(arg) oraz os.path.isfile(arg):
                    arg = importfile(arg)
                jeżeli writing:
                    jeżeli ispath(arg) oraz os.path.isdir(arg):
                        writedocs(arg)
                    inaczej:
                        writedoc(arg)
                inaczej:
                    help.help(arg)
            wyjąwszy ErrorDuringImport jako value:
                print(value)

    wyjąwszy (getopt.error, BadUsage):
        cmd = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        print("""pydoc - the Python documentation tool

{cmd} <name> ...
    Show text documentation on something.  <name> may be the name of a
    Python keyword, topic, function, module, albo package, albo a dotted
    reference to a klasa albo function within a module albo module w a
    package.  If <name> contains a '{sep}', it jest used jako the path to a
    Python source file to document. If name jest 'keywords', 'topics',
    albo 'modules', a listing of these things jest displayed.

{cmd} -k <keyword>
    Search dla a keyword w the synopsis lines of all available modules.

{cmd} -p <port>
    Start an HTTP server on the given port on the local machine.  Port
    number 0 can be used to get an arbitrary unused port.

{cmd} -b
    Start an HTTP server on an arbitrary unused port oraz open a Web browser
    to interactively browse documentation.  The -p option can be used with
    the -b option to explicitly specify the server port.

{cmd} -w <name> ...
    Write out the HTML documentation dla a module to a file w the current
    directory.  If <name> contains a '{sep}', it jest treated jako a filename; if
    it names a directory, documentation jest written dla all the contents.
""".format(cmd=cmd, sep=os.sep))

jeżeli __name__ == '__main__':
    cli()
