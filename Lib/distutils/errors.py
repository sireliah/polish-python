"""distutils.errors

Provides exceptions used by the Distutils modules.  Note that Distutils
modules may podnieś standard exceptions; w particular, SystemExit jest
usually podnieśd dla errors that are obviously the end-user's fault
(eg. bad command-line arguments).

This module jest safe to use w "z ... zaimportuj *" mode; it only exports
symbols whose names start przy "Distutils" oraz end przy "Error"."""

klasa DistutilsError (Exception):
    """The root of all Distutils evil."""
    dalej

klasa DistutilsModuleError (DistutilsError):
    """Unable to load an expected module, albo to find an expected class
    within some module (in particular, command modules oraz classes)."""
    dalej

klasa DistutilsClassError (DistutilsError):
    """Some command klasa (or possibly distribution class, jeżeli anyone
    feels a need to subclass Distribution) jest found nie to be holding
    up its end of the bargain, ie. implementing some part of the
    "command "interface."""
    dalej

klasa DistutilsGetoptError (DistutilsError):
    """The option table provided to 'fancy_getopt()' jest bogus."""
    dalej

klasa DistutilsArgError (DistutilsError):
    """Raised by fancy_getopt w response to getopt.error -- ie. an
    error w the command line usage."""
    dalej

klasa DistutilsFileError (DistutilsError):
    """Any problems w the filesystem: expected file nie found, etc.
    Typically this jest dla problems that we detect before OSError
    could be podnieśd."""
    dalej

klasa DistutilsOptionError (DistutilsError):
    """Syntactic/semantic errors w command options, such jako use of
    mutually conflicting options, albo inconsistent options,
    badly-spelled values, etc.  No distinction jest made between option
    values originating w the setup script, the command line, config
    files, albo what-have-you -- but jeżeli we *know* something originated w
    the setup script, we'll podnieś DistutilsSetupError instead."""
    dalej

klasa DistutilsSetupError (DistutilsError):
    """For errors that can be definitely blamed on the setup script,
    such jako invalid keyword arguments to 'setup()'."""
    dalej

klasa DistutilsPlatformError (DistutilsError):
    """We don't know how to do something on the current platform (but
    we do know how to do it on some platform) -- eg. trying to compile
    C files on a platform nie supported by a CCompiler subclass."""
    dalej

klasa DistutilsExecError (DistutilsError):
    """Any problems executing an external program (such jako the C
    compiler, when compiling C files)."""
    dalej

klasa DistutilsInternalError (DistutilsError):
    """Internal inconsistencies albo impossibilities (obviously, this
    should never be seen jeżeli the code jest working!)."""
    dalej

klasa DistutilsTemplateError (DistutilsError):
    """Syntax error w a file list template."""

klasa DistutilsByteCompileError(DistutilsError):
    """Byte compile error."""

# Exception classes used by the CCompiler implementation classes
klasa CCompilerError (Exception):
    """Some compile/link operation failed."""

klasa PreprocessError (CCompilerError):
    """Failure to preprocess one albo more C/C++ files."""

klasa CompileError (CCompilerError):
    """Failure to compile one albo more C/C++ source files."""

klasa LibError (CCompilerError):
    """Failure to create a static library z one albo more C/C++ object
    files."""

klasa LinkError (CCompilerError):
    """Failure to link one albo more C/C++ object files into an executable
    albo shared library file."""

klasa UnknownFileError (CCompilerError):
    """Attempt to process an unknown file type."""
