"""Find modules used by a script, using introspection."""

zaimportuj dis
zaimportuj importlib._bootstrap_external
zaimportuj importlib.machinery
zaimportuj marshal
zaimportuj os
zaimportuj sys
zaimportuj types
zaimportuj struct
zaimportuj warnings
przy warnings.catch_warnings():
    warnings.simplefilter('ignore', PendingDeprecationWarning)
    zaimportuj imp

# XXX Clean up once str8's cstor matches bytes.
LOAD_CONST = bytes([dis.opname.index('LOAD_CONST')])
IMPORT_NAME = bytes([dis.opname.index('IMPORT_NAME')])
STORE_NAME = bytes([dis.opname.index('STORE_NAME')])
STORE_GLOBAL = bytes([dis.opname.index('STORE_GLOBAL')])
STORE_OPS = [STORE_NAME, STORE_GLOBAL]
HAVE_ARGUMENT = bytes([dis.HAVE_ARGUMENT])

# Modulefinder does a good job at simulating Python's, but it can nie
# handle __path__ modifications packages make at runtime.  Therefore there
# jest a mechanism whereby you can register extra paths w this map dla a
# package, oraz it will be honored.

# Note this jest a mapping jest lists of paths.
packagePathMap = {}

# A Public interface
def AddPackagePath(packagename, path):
    packagePathMap.setdefault(packagename, []).append(path)

replacePackageMap = {}

# This ReplacePackage mechanism allows modulefinder to work around
# situations w which a package injects itself under the name
# of another package into sys.modules at runtime by calling
# ReplacePackage("real_package_name", "faked_package_name")
# before running ModuleFinder.

def ReplacePackage(oldname, newname):
    replacePackageMap[oldname] = newname


klasa Module:

    def __init__(self, name, file=Nic, path=Nic):
        self.__name__ = name
        self.__file__ = file
        self.__path__ = path
        self.__code__ = Nic
        # The set of global names that are assigned to w the module.
        # This includes those names imported through starimports of
        # Python modules.
        self.globalnames = {}
        # The set of starimports this module did that could nie be
        # resolved, ie. a starzaimportuj z a non-Python module.
        self.starimports = {}

    def __repr__(self):
        s = "Module(%r" % (self.__name__,)
        jeżeli self.__file__ jest nie Nic:
            s = s + ", %r" % (self.__file__,)
        jeżeli self.__path__ jest nie Nic:
            s = s + ", %r" % (self.__path__,)
        s = s + ")"
        zwróć s

klasa ModuleFinder:

    def __init__(self, path=Nic, debug=0, excludes=[], replace_paths=[]):
        jeżeli path jest Nic:
            path = sys.path
        self.path = path
        self.modules = {}
        self.badmodules = {}
        self.debug = debug
        self.indent = 0
        self.excludes = excludes
        self.replace_paths = replace_paths
        self.processed_paths = []   # Used w debugging only

    def msg(self, level, str, *args):
        jeżeli level <= self.debug:
            dla i w range(self.indent):
                print("   ", end=' ')
            print(str, end=' ')
            dla arg w args:
                print(repr(arg), end=' ')
            print()

    def msgin(self, *args):
        level = args[0]
        jeżeli level <= self.debug:
            self.indent = self.indent + 1
            self.msg(*args)

    def msgout(self, *args):
        level = args[0]
        jeżeli level <= self.debug:
            self.indent = self.indent - 1
            self.msg(*args)

    def run_script(self, pathname):
        self.msg(2, "run_script", pathname)
        przy open(pathname) jako fp:
            stuff = ("", "r", imp.PY_SOURCE)
            self.load_module('__main__', fp, pathname, stuff)

    def load_file(self, pathname):
        dir, name = os.path.split(pathname)
        name, ext = os.path.splitext(name)
        przy open(pathname) jako fp:
            stuff = (ext, "r", imp.PY_SOURCE)
            self.load_module(name, fp, pathname, stuff)

    def import_hook(self, name, caller=Nic, fromlist=Nic, level=-1):
        self.msg(3, "import_hook", name, caller, fromlist, level)
        parent = self.determine_parent(caller, level=level)
        q, tail = self.find_head_package(parent, name)
        m = self.load_tail(q, tail)
        jeżeli nie fromlist:
            zwróć q
        jeżeli m.__path__:
            self.ensure_fromlist(m, fromlist)
        zwróć Nic

    def determine_parent(self, caller, level=-1):
        self.msgin(4, "determine_parent", caller, level)
        jeżeli nie caller albo level == 0:
            self.msgout(4, "determine_parent -> Nic")
            zwróć Nic
        pname = caller.__name__
        jeżeli level >= 1: # relative import
            jeżeli caller.__path__:
                level -= 1
            jeżeli level == 0:
                parent = self.modules[pname]
                assert parent jest caller
                self.msgout(4, "determine_parent ->", parent)
                zwróć parent
            jeżeli pname.count(".") < level:
                podnieś ImportError("relative importpath too deep")
            pname = ".".join(pname.split(".")[:-level])
            parent = self.modules[pname]
            self.msgout(4, "determine_parent ->", parent)
            zwróć parent
        jeżeli caller.__path__:
            parent = self.modules[pname]
            assert caller jest parent
            self.msgout(4, "determine_parent ->", parent)
            zwróć parent
        jeżeli '.' w pname:
            i = pname.rfind('.')
            pname = pname[:i]
            parent = self.modules[pname]
            assert parent.__name__ == pname
            self.msgout(4, "determine_parent ->", parent)
            zwróć parent
        self.msgout(4, "determine_parent -> Nic")
        zwróć Nic

    def find_head_package(self, parent, name):
        self.msgin(4, "find_head_package", parent, name)
        jeżeli '.' w name:
            i = name.find('.')
            head = name[:i]
            tail = name[i+1:]
        inaczej:
            head = name
            tail = ""
        jeżeli parent:
            qname = "%s.%s" % (parent.__name__, head)
        inaczej:
            qname = head
        q = self.import_module(head, qname, parent)
        jeżeli q:
            self.msgout(4, "find_head_package ->", (q, tail))
            zwróć q, tail
        jeżeli parent:
            qname = head
            parent = Nic
            q = self.import_module(head, qname, parent)
            jeżeli q:
                self.msgout(4, "find_head_package ->", (q, tail))
                zwróć q, tail
        self.msgout(4, "raise ImportError: No module named", qname)
        podnieś ImportError("No module named " + qname)

    def load_tail(self, q, tail):
        self.msgin(4, "load_tail", q, tail)
        m = q
        dopóki tail:
            i = tail.find('.')
            jeżeli i < 0: i = len(tail)
            head, tail = tail[:i], tail[i+1:]
            mname = "%s.%s" % (m.__name__, head)
            m = self.import_module(head, mname, m)
            jeżeli nie m:
                self.msgout(4, "raise ImportError: No module named", mname)
                podnieś ImportError("No module named " + mname)
        self.msgout(4, "load_tail ->", m)
        zwróć m

    def ensure_fromlist(self, m, fromlist, recursive=0):
        self.msg(4, "ensure_fromlist", m, fromlist, recursive)
        dla sub w fromlist:
            jeżeli sub == "*":
                jeżeli nie recursive:
                    all = self.find_all_submodules(m)
                    jeżeli all:
                        self.ensure_fromlist(m, all, 1)
            albo_inaczej nie hasattr(m, sub):
                subname = "%s.%s" % (m.__name__, sub)
                submod = self.import_module(sub, subname, m)
                jeżeli nie submod:
                    podnieś ImportError("No module named " + subname)

    def find_all_submodules(self, m):
        jeżeli nie m.__path__:
            zwróć
        modules = {}
        # 'suffixes' used to be a list hardcoded to [".py", ".pyc"].
        # But we must also collect Python extension modules - although
        # we cannot separate normal dlls z Python extensions.
        suffixes = []
        suffixes += importlib.machinery.EXTENSION_SUFFIXES[:]
        suffixes += importlib.machinery.SOURCE_SUFFIXES[:]
        suffixes += importlib.machinery.BYTECODE_SUFFIXES[:]
        dla dir w m.__path__:
            spróbuj:
                names = os.listdir(dir)
            wyjąwszy OSError:
                self.msg(2, "can't list directory", dir)
                kontynuuj
            dla name w names:
                mod = Nic
                dla suff w suffixes:
                    n = len(suff)
                    jeżeli name[-n:] == suff:
                        mod = name[:-n]
                        przerwij
                jeżeli mod oraz mod != "__init__":
                    modules[mod] = mod
        zwróć modules.keys()

    def import_module(self, partname, fqname, parent):
        self.msgin(3, "import_module", partname, fqname, parent)
        spróbuj:
            m = self.modules[fqname]
        wyjąwszy KeyError:
            dalej
        inaczej:
            self.msgout(3, "import_module ->", m)
            zwróć m
        jeżeli fqname w self.badmodules:
            self.msgout(3, "import_module -> Nic")
            zwróć Nic
        jeżeli parent oraz parent.__path__ jest Nic:
            self.msgout(3, "import_module -> Nic")
            zwróć Nic
        spróbuj:
            fp, pathname, stuff = self.find_module(partname,
                                                   parent oraz parent.__path__, parent)
        wyjąwszy ImportError:
            self.msgout(3, "import_module ->", Nic)
            zwróć Nic
        spróbuj:
            m = self.load_module(fqname, fp, pathname, stuff)
        w_końcu:
            jeżeli fp:
                fp.close()
        jeżeli parent:
            setattr(parent, partname, m)
        self.msgout(3, "import_module ->", m)
        zwróć m

    def load_module(self, fqname, fp, pathname, file_info):
        suffix, mode, type = file_info
        self.msgin(2, "load_module", fqname, fp oraz "fp", pathname)
        jeżeli type == imp.PKG_DIRECTORY:
            m = self.load_package(fqname, pathname)
            self.msgout(2, "load_module ->", m)
            zwróć m
        jeżeli type == imp.PY_SOURCE:
            co = compile(fp.read()+'\n', pathname, 'exec')
        albo_inaczej type == imp.PY_COMPILED:
            spróbuj:
                marshal_data = importlib._bootstrap_external._validate_bytecode_header(fp.read())
            wyjąwszy ImportError jako exc:
                self.msgout(2, "raise ImportError: " + str(exc), pathname)
                podnieś
            co = marshal.loads(marshal_data)
        inaczej:
            co = Nic
        m = self.add_module(fqname)
        m.__file__ = pathname
        jeżeli co:
            jeżeli self.replace_paths:
                co = self.replace_paths_in_code(co)
            m.__code__ = co
            self.scan_code(co, m)
        self.msgout(2, "load_module ->", m)
        zwróć m

    def _add_badmodule(self, name, caller):
        jeżeli name nie w self.badmodules:
            self.badmodules[name] = {}
        jeżeli caller:
            self.badmodules[name][caller.__name__] = 1
        inaczej:
            self.badmodules[name]["-"] = 1

    def _safe_import_hook(self, name, caller, fromlist, level=-1):
        # wrapper dla self.import_hook() that won't podnieś ImportError
        jeżeli name w self.badmodules:
            self._add_badmodule(name, caller)
            zwróć
        spróbuj:
            self.import_hook(name, caller, level=level)
        wyjąwszy ImportError jako msg:
            self.msg(2, "ImportError:", str(msg))
            self._add_badmodule(name, caller)
        inaczej:
            jeżeli fromlist:
                dla sub w fromlist:
                    jeżeli sub w self.badmodules:
                        self._add_badmodule(sub, caller)
                        kontynuuj
                    spróbuj:
                        self.import_hook(name, caller, [sub], level=level)
                    wyjąwszy ImportError jako msg:
                        self.msg(2, "ImportError:", str(msg))
                        fullname = name + "." + sub
                        self._add_badmodule(fullname, caller)

    def scan_opcodes_25(self, co,
                     unpack = struct.unpack):
        # Scan the code, oraz uzyskaj 'interesting' opcode combinations
        # Python 2.5 version (has absolute oraz relative imports)
        code = co.co_code
        names = co.co_names
        consts = co.co_consts
        LOAD_LOAD_AND_IMPORT = LOAD_CONST + LOAD_CONST + IMPORT_NAME
        dopóki code:
            c = bytes([code[0]])
            jeżeli c w STORE_OPS:
                oparg, = unpack('<H', code[1:3])
                uzyskaj "store", (names[oparg],)
                code = code[3:]
                kontynuuj
            jeżeli code[:9:3] == LOAD_LOAD_AND_IMPORT:
                oparg_1, oparg_2, oparg_3 = unpack('<xHxHxH', code[:9])
                level = consts[oparg_1]
                jeżeli level == 0: # absolute import
                    uzyskaj "absolute_import", (consts[oparg_2], names[oparg_3])
                inaczej: # relative import
                    uzyskaj "relative_import", (level, consts[oparg_2], names[oparg_3])
                code = code[9:]
                kontynuuj
            jeżeli c >= HAVE_ARGUMENT:
                code = code[3:]
            inaczej:
                code = code[1:]

    def scan_code(self, co, m):
        code = co.co_code
        scanner = self.scan_opcodes_25
        dla what, args w scanner(co):
            jeżeli what == "store":
                name, = args
                m.globalnames[name] = 1
            albo_inaczej what == "absolute_import":
                fromlist, name = args
                have_star = 0
                jeżeli fromlist jest nie Nic:
                    jeżeli "*" w fromlist:
                        have_star = 1
                    fromlist = [f dla f w fromlist jeżeli f != "*"]
                self._safe_import_hook(name, m, fromlist, level=0)
                jeżeli have_star:
                    # We've encountered an "zaimportuj *". If it jest a Python module,
                    # the code has already been parsed oraz we can suck out the
                    # global names.
                    mm = Nic
                    jeżeli m.__path__:
                        # At this point we don't know whether 'name' jest a
                        # submodule of 'm' albo a global module. Let's just try
                        # the full name first.
                        mm = self.modules.get(m.__name__ + "." + name)
                    jeżeli mm jest Nic:
                        mm = self.modules.get(name)
                    jeżeli mm jest nie Nic:
                        m.globalnames.update(mm.globalnames)
                        m.starimports.update(mm.starimports)
                        jeżeli mm.__code__ jest Nic:
                            m.starimports[name] = 1
                    inaczej:
                        m.starimports[name] = 1
            albo_inaczej what == "relative_import":
                level, fromlist, name = args
                jeżeli name:
                    self._safe_import_hook(name, m, fromlist, level=level)
                inaczej:
                    parent = self.determine_parent(m, level=level)
                    self._safe_import_hook(parent.__name__, Nic, fromlist, level=0)
            inaczej:
                # We don't expect anything inaczej z the generator.
                podnieś RuntimeError(what)

        dla c w co.co_consts:
            jeżeli isinstance(c, type(co)):
                self.scan_code(c, m)

    def load_package(self, fqname, pathname):
        self.msgin(2, "load_package", fqname, pathname)
        newname = replacePackageMap.get(fqname)
        jeżeli newname:
            fqname = newname
        m = self.add_module(fqname)
        m.__file__ = pathname
        m.__path__ = [pathname]

        # As per comment at top of file, simulate runtime __path__ additions.
        m.__path__ = m.__path__ + packagePathMap.get(fqname, [])

        fp, buf, stuff = self.find_module("__init__", m.__path__)
        spróbuj:
            self.load_module(fqname, fp, buf, stuff)
            self.msgout(2, "load_package ->", m)
            zwróć m
        w_końcu:
            jeżeli fp:
                fp.close()

    def add_module(self, fqname):
        jeżeli fqname w self.modules:
            zwróć self.modules[fqname]
        self.modules[fqname] = m = Module(fqname)
        zwróć m

    def find_module(self, name, path, parent=Nic):
        jeżeli parent jest nie Nic:
            # assert path jest nie Nic
            fullname = parent.__name__+'.'+name
        inaczej:
            fullname = name
        jeżeli fullname w self.excludes:
            self.msgout(3, "find_module -> Excluded", fullname)
            podnieś ImportError(name)

        jeżeli path jest Nic:
            jeżeli name w sys.builtin_module_names:
                zwróć (Nic, Nic, ("", "", imp.C_BUILTIN))

            path = self.path
        zwróć imp.find_module(name, path)

    def report(self):
        """Print a report to stdout, listing the found modules przy their
        paths, jako well jako modules that are missing, albo seem to be missing.
        """
        print()
        print("  %-25s %s" % ("Name", "File"))
        print("  %-25s %s" % ("----", "----"))
        # Print modules found
        keys = sorted(self.modules.keys())
        dla key w keys:
            m = self.modules[key]
            jeżeli m.__path__:
                print("P", end=' ')
            inaczej:
                print("m", end=' ')
            print("%-25s" % key, m.__file__ albo "")

        # Print missing modules
        missing, maybe = self.any_missing_maybe()
        jeżeli missing:
            print()
            print("Missing modules:")
            dla name w missing:
                mods = sorted(self.badmodules[name].keys())
                print("?", name, "imported from", ', '.join(mods))
        # Print modules that may be missing, but then again, maybe not...
        jeżeli maybe:
            print()
            print("Submodules that appear to be missing, but could also be", end=' ')
            print("global names w the parent package:")
            dla name w maybe:
                mods = sorted(self.badmodules[name].keys())
                print("?", name, "imported from", ', '.join(mods))

    def any_missing(self):
        """Return a list of modules that appear to be missing. Use
        any_missing_maybe() jeżeli you want to know which modules are
        certain to be missing, oraz which *may* be missing.
        """
        missing, maybe = self.any_missing_maybe()
        zwróć missing + maybe

    def any_missing_maybe(self):
        """Return two lists, one przy modules that are certainly missing
        oraz one przy modules that *may* be missing. The latter names could
        either be submodules *or* just global names w the package.

        The reason it can't always be determined jest that it's impossible to
        tell which names are imported when "z module zaimportuj *" jest done
        przy an extension module, short of actually importing it.
        """
        missing = []
        maybe = []
        dla name w self.badmodules:
            jeżeli name w self.excludes:
                kontynuuj
            i = name.rfind(".")
            jeżeli i < 0:
                missing.append(name)
                kontynuuj
            subname = name[i+1:]
            pkgname = name[:i]
            pkg = self.modules.get(pkgname)
            jeżeli pkg jest nie Nic:
                jeżeli pkgname w self.badmodules[name]:
                    # The package tried to zaimportuj this module itself oraz
                    # failed. It's definitely missing.
                    missing.append(name)
                albo_inaczej subname w pkg.globalnames:
                    # It's a global w the package: definitely nie missing.
                    dalej
                albo_inaczej pkg.starimports:
                    # It could be missing, but the package did an "zaimportuj *"
                    # z a non-Python module, so we simply can't be sure.
                    maybe.append(name)
                inaczej:
                    # It's nie a global w the package, the package didn't
                    # do funny star imports, it's very likely to be missing.
                    # The symbol could be inserted into the package z the
                    # outside, but since that's nie good style we simply list
                    # it missing.
                    missing.append(name)
            inaczej:
                missing.append(name)
        missing.sort()
        maybe.sort()
        zwróć missing, maybe

    def replace_paths_in_code(self, co):
        new_filename = original_filename = os.path.normpath(co.co_filename)
        dla f, r w self.replace_paths:
            jeżeli original_filename.startswith(f):
                new_filename = r + original_filename[len(f):]
                przerwij

        jeżeli self.debug oraz original_filename nie w self.processed_paths:
            jeżeli new_filename != original_filename:
                self.msgout(2, "co_filename %r changed to %r" \
                                    % (original_filename,new_filename,))
            inaczej:
                self.msgout(2, "co_filename %r remains unchanged" \
                                    % (original_filename,))
            self.processed_paths.append(original_filename)

        consts = list(co.co_consts)
        dla i w range(len(consts)):
            jeżeli isinstance(consts[i], type(co)):
                consts[i] = self.replace_paths_in_code(consts[i])

        zwróć types.CodeType(co.co_argcount, co.co_kwonlyargcount,
                              co.co_nlocals, co.co_stacksize, co.co_flags,
                              co.co_code, tuple(consts), co.co_names,
                              co.co_varnames, new_filename, co.co_name,
                              co.co_firstlineno, co.co_lnotab, co.co_freevars,
                              co.co_cellvars)


def test():
    # Parse command line
    zaimportuj getopt
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], "dmp:qx:")
    wyjąwszy getopt.error jako msg:
        print(msg)
        zwróć

    # Process options
    debug = 1
    domods = 0
    addpath = []
    exclude = []
    dla o, a w opts:
        jeżeli o == '-d':
            debug = debug + 1
        jeżeli o == '-m':
            domods = 1
        jeżeli o == '-p':
            addpath = addpath + a.split(os.pathsep)
        jeżeli o == '-q':
            debug = 0
        jeżeli o == '-x':
            exclude.append(a)

    # Provide default arguments
    jeżeli nie args:
        script = "hello.py"
    inaczej:
        script = args[0]

    # Set the path based on sys.path oraz the script directory
    path = sys.path[:]
    path[0] = os.path.dirname(script)
    path = addpath + path
    jeżeli debug > 1:
        print("path:")
        dla item w path:
            print("   ", repr(item))

    # Create the module finder oraz turn its crank
    mf = ModuleFinder(path, debug, exclude)
    dla arg w args[1:]:
        jeżeli arg == '-m':
            domods = 1
            kontynuuj
        jeżeli domods:
            jeżeli arg[-2:] == '.*':
                mf.import_hook(arg[:-2], Nic, ["*"])
            inaczej:
                mf.import_hook(arg)
        inaczej:
            mf.load_file(arg)
    mf.run_script(script)
    mf.report()
    zwróć mf  # dla -i debugging


jeżeli __name__ == '__main__':
    spróbuj:
        mf = test()
    wyjąwszy KeyboardInterrupt:
        print("\n[interrupted]")
