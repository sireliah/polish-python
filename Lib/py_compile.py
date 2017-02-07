"""Routine to "compile" a .py file to a .pyc file.

This module has intimate knowledge of the format of .pyc files.
"""

zaimportuj importlib._bootstrap_external
zaimportuj importlib.machinery
zaimportuj importlib.util
zaimportuj os
zaimportuj os.path
zaimportuj sys
zaimportuj traceback

__all__ = ["compile", "main", "PyCompileError"]


klasa PyCompileError(Exception):
    """Exception podnieśd when an error occurs dopóki attempting to
    compile the file.

    To podnieś this exception, use

        podnieś PyCompileError(exc_type,exc_value,file[,msg])

    where

        exc_type:   exception type to be used w error message
                    type name can be accesses jako klasa variable
                    'exc_type_name'

        exc_value:  exception value to be used w error message
                    can be accesses jako klasa variable 'exc_value'

        file:       name of file being compiled to be used w error message
                    can be accesses jako klasa variable 'file'

        msg:        string message to be written jako error message
                    If no value jest given, a default exception message will be
                    given, consistent przy 'standard' py_compile output.
                    message (or default) can be accesses jako klasa variable
                    'msg'

    """

    def __init__(self, exc_type, exc_value, file, msg=''):
        exc_type_name = exc_type.__name__
        jeżeli exc_type jest SyntaxError:
            tbtext = ''.join(traceback.format_exception_only(
                exc_type, exc_value))
            errmsg = tbtext.replace('File "<string>"', 'File "%s"' % file)
        inaczej:
            errmsg = "Sorry: %s: %s" % (exc_type_name,exc_value)

        Exception.__init__(self,msg albo errmsg,exc_type_name,exc_value,file)

        self.exc_type_name = exc_type_name
        self.exc_value = exc_value
        self.file = file
        self.msg = msg albo errmsg

    def __str__(self):
        zwróć self.msg


def compile(file, cfile=Nic, dfile=Nic, doraise=Nieprawda, optimize=-1):
    """Byte-compile one Python source file to Python bytecode.

    :param file: The source file name.
    :param cfile: The target byte compiled file name.  When nie given, this
        defaults to the PEP 3147/PEP 488 location.
    :param dfile: Purported file name, i.e. the file name that shows up w
        error messages.  Defaults to the source file name.
    :param doraise: Flag indicating whether albo nie an exception should be
        podnieśd when a compile error jest found.  If an exception occurs oraz this
        flag jest set to Nieprawda, a string indicating the nature of the exception
        will be printed, oraz the function will zwróć to the caller. If an
        exception occurs oraz this flag jest set to Prawda, a PyCompileError
        exception will be podnieśd.
    :param optimize: The optimization level dla the compiler.  Valid values
        are -1, 0, 1 oraz 2.  A value of -1 means to use the optimization
        level of the current interpreter, jako given by -O command line options.

    :return: Path to the resulting byte compiled file.

    Note that it isn't necessary to byte-compile Python modules for
    execution efficiency -- Python itself byte-compiles a module when
    it jest loaded, oraz jeżeli it can, writes out the bytecode to the
    corresponding .pyc file.

    However, jeżeli a Python installation jest shared between users, it jest a
    good idea to byte-compile all modules upon installation, since
    other users may nie be able to write w the source directories,
    oraz thus they won't be able to write the .pyc file, oraz then
    they would be byte-compiling every module each time it jest loaded.
    This can slow down program start-up considerably.

    See compileall.py dla a script/module that uses this module to
    byte-compile all installed files (or all files w selected
    directories).

    Do note that FileExistsError jest podnieśd jeżeli cfile ends up pointing at a
    non-regular file albo symlink. Because the compilation uses a file renaming,
    the resulting file would be regular oraz thus nie the same type of file as
    it was previously.
    """
    jeżeli cfile jest Nic:
        jeżeli optimize >= 0:
            optimization = optimize jeżeli optimize >= 1 inaczej ''
            cfile = importlib.util.cache_from_source(file,
                                                     optimization=optimization)
        inaczej:
            cfile = importlib.util.cache_from_source(file)
    jeżeli os.path.islink(cfile):
        msg = ('{} jest a symlink oraz will be changed into a regular file jeżeli '
               'zaimportuj writes a byte-compiled file to it')
        podnieś FileExistsError(msg.format(cfile))
    albo_inaczej os.path.exists(cfile) oraz nie os.path.isfile(cfile):
        msg = ('{} jest a non-regular file oraz will be changed into a regular '
               'one jeżeli zaimportuj writes a byte-compiled file to it')
        podnieś FileExistsError(msg.format(cfile))
    loader = importlib.machinery.SourceFileLoader('<py_compile>', file)
    source_bytes = loader.get_data(file)
    spróbuj:
        code = loader.source_to_code(source_bytes, dfile albo file,
                                     _optimize=optimize)
    wyjąwszy Exception jako err:
        py_exc = PyCompileError(err.__class__, err, dfile albo file)
        jeżeli doraise:
            podnieś py_exc
        inaczej:
            sys.stderr.write(py_exc.msg + '\n')
            zwróć
    spróbuj:
        dirname = os.path.dirname(cfile)
        jeżeli dirname:
            os.makedirs(dirname)
    wyjąwszy FileExistsError:
        dalej
    source_stats = loader.path_stats(file)
    bytecode = importlib._bootstrap_external._code_to_bytecode(
            code, source_stats['mtime'], source_stats['size'])
    mode = importlib._bootstrap_external._calc_mode(file)
    importlib._bootstrap_external._write_atomic(cfile, bytecode, mode)
    zwróć cfile


def main(args=Nic):
    """Compile several source files.

    The files named w 'args' (or on the command line, jeżeli 'args' jest
    nie specified) are compiled oraz the resulting bytecode jest cached
    w the normal manner.  This function does nie search a directory
    structure to locate source files; it only compiles files named
    explicitly.  If '-' jest the only parameter w args, the list of
    files jest taken z standard input.

    """
    jeżeli args jest Nic:
        args = sys.argv[1:]
    rv = 0
    jeżeli args == ['-']:
        dopóki Prawda:
            filename = sys.stdin.readline()
            jeżeli nie filename:
                przerwij
            filename = filename.rstrip('\n')
            spróbuj:
                compile(filename, doraise=Prawda)
            wyjąwszy PyCompileError jako error:
                rv = 1
                sys.stderr.write("%s\n" % error.msg)
            wyjąwszy OSError jako error:
                rv = 1
                sys.stderr.write("%s\n" % error)
    inaczej:
        dla filename w args:
            spróbuj:
                compile(filename, doraise=Prawda)
            wyjąwszy PyCompileError jako error:
                # zwróć value to indicate at least one failure
                rv = 1
                sys.stderr.write("%s\n" % error.msg)
    zwróć rv

jeżeli __name__ == "__main__":
    sys.exit(main())
