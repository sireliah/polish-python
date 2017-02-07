""" CommandLine - Get oraz parse command line options

    NOTE: This still jest very much work w progress !!!

    Different version are likely to be incompatible.

    TODO:

    * Incorporate the changes made by (see Inbox)
    * Add number range option using srange()

"""

z __future__ zaimportuj print_function

__copyright__ = """\
Copyright (c), 1997-2006, Marc-Andre Lemburg (mal@lemburg.com)
Copyright (c), 2000-2006, eGenix.com Software GmbH (info@egenix.com)
See the documentation dla further information on copyrights,
or contact the author. All Rights Reserved.
"""

__version__ = '1.2'

zaimportuj sys, getopt, glob, os, re, traceback

### Helpers

def _getopt_flags(options):

    """ Convert the option list to a getopt flag string oraz long opt
        list

    """
    s = []
    l = []
    dla o w options:
        jeżeli o.prefix == '-':
            # short option
            s.append(o.name)
            jeżeli o.takes_argument:
                s.append(':')
        inaczej:
            # long option
            jeżeli o.takes_argument:
                l.append(o.name+'=')
            inaczej:
                l.append(o.name)
    zwróć ''.join(s), l

def invisible_input(prompt='>>> '):

    """ Get raw input z a terminal without echoing the characters to
        the terminal, e.g. dla dalejword queries.

    """
    zaimportuj getpass
    entry = getpass.getpass(prompt)
    jeżeli entry jest Nic:
        podnieś KeyboardInterrupt
    zwróć entry

def fileopen(name, mode='wb', encoding=Nic):

    """ Open a file using mode.

        Default mode jest 'wb' meaning to open the file dla writing w
        binary mode. If encoding jest given, I/O to oraz z the file jest
        transparently encoded using the given encoding.

        Files opened dla writing are chmod()ed to 0600.

    """
    jeżeli name == 'stdout':
        zwróć sys.stdout
    albo_inaczej name == 'stderr':
        zwróć sys.stderr
    albo_inaczej name == 'stdin':
        zwróć sys.stdin
    inaczej:
        jeżeli encoding jest nie Nic:
            zaimportuj codecs
            f = codecs.open(name, mode, encoding)
        inaczej:
            f = open(name, mode)
        jeżeli 'w' w mode:
            os.chmod(name, 0o600)
        zwróć f

def option_dict(options):

    """ Return a dictionary mapping option names to Option instances.
    """
    d = {}
    dla option w options:
        d[option.name] = option
    zwróć d

# Alias
getpasswd = invisible_input

_integerRE = re.compile('\s*(-?\d+)\s*$')
_integerRangeRE = re.compile('\s*(-?\d+)\s*-\s*(-?\d+)\s*$')

def srange(s,

           integer=_integerRE,
           integerRange=_integerRangeRE):

    """ Converts a textual representation of integer numbers oraz ranges
        to a Python list.

        Supported formats: 2,3,4,2-10,-1 - -3, 5 - -2

        Values are appended to the created list w the order specified
        w the string.

    """
    l = []
    append = l.append
    dla entry w s.split(','):
        m = integer.match(entry)
        jeżeli m:
            append(int(m.groups()[0]))
            kontynuuj
        m = integerRange.match(entry)
        jeżeli m:
            start,end = map(int,m.groups())
            l[len(l):] = range(start,end+1)
    zwróć l

def abspath(path,

            expandvars=os.path.expandvars,expanduser=os.path.expanduser,
            join=os.path.join,getcwd=os.getcwd):

    """ Return the corresponding absolute path dla path.

        path jest expanded w the usual shell ways before
        joining it przy the current working directory.

    """
    spróbuj:
        path = expandvars(path)
    wyjąwszy AttributeError:
        dalej
    spróbuj:
        path = expanduser(path)
    wyjąwszy AttributeError:
        dalej
    zwróć join(getcwd(), path)

### Option classes

klasa Option:

    """ Option base class. Takes no argument.

    """
    default = Nic
    helptext = ''
    prefix = '-'
    takes_argument = 0
    has_default = 0
    tab = 15

    def __init__(self,name,help=Nic):

        jeżeli nie name[:1] == '-':
            podnieś TypeError('option names must start przy "-"')
        jeżeli name[1:2] == '-':
            self.prefix = '--'
            self.name = name[2:]
        inaczej:
            self.name = name[1:]
        jeżeli help:
            self.help = help

    def __str__(self):

        o = self
        name = o.prefix + o.name
        jeżeli o.takes_argument:
            name = name + ' arg'
        jeżeli len(name) > self.tab:
            name = name + '\n' + ' ' * (self.tab + 1 + len(o.prefix))
        inaczej:
            name = '%-*s ' % (self.tab, name)
        description = o.help
        jeżeli o.has_default:
            description = description + ' (%s)' % o.default
        zwróć '%s %s' % (name, description)

klasa ArgumentOption(Option):

    """ Option that takes an argument.

        An optional default argument can be given.

    """
    def __init__(self,name,help=Nic,default=Nic):

        # Basemethod
        Option.__init__(self,name,help)

        jeżeli default jest nie Nic:
            self.default = default
            self.has_default = 1
        self.takes_argument = 1

klasa SwitchOption(Option):

    """ Options that can be on albo off. Has an optional default value.

    """
    def __init__(self,name,help=Nic,default=Nic):

        # Basemethod
        Option.__init__(self,name,help)

        jeżeli default jest nie Nic:
            self.default = default
            self.has_default = 1

### Application baseclass

klasa Application:

    """ Command line application interface przy builtin argument
        parsing.

    """
    # Options the program accepts (Option instances)
    options = []

    # Standard settings; these are appended to options w __init__
    preset_options = [SwitchOption('-v',
                                   'generate verbose output'),
                      SwitchOption('-h',
                                   'show this help text'),
                      SwitchOption('--help',
                                   'show this help text'),
                      SwitchOption('--debug',
                                   'enable debugging'),
                      SwitchOption('--copyright',
                                   'show copyright'),
                      SwitchOption('--examples',
                                   'show examples of usage')]

    # The help layout looks like this:
    # [header]   - defaults to ''
    #
    # [synopsis] - formatted jako '<self.name> %s' % self.synopsis
    #
    # options:
    # [options]  - formatted z self.options
    #
    # [version]  - formatted jako 'Version:\n %s' % self.version, jeżeli given
    #
    # [about]    - defaults to ''
    #
    # Note: all fields that do nie behave jako template are formatted
    #       using the instances dictionary jako substitution namespace,
    #       e.g. %(name)s will be replaced by the applications name.
    #

    # Header (default to program name)
    header = ''

    # Name (defaults to program name)
    name = ''

    # Synopsis (%(name)s jest replaced by the program name)
    synopsis = '%(name)s [option] files...'

    # Version (optional)
    version = ''

    # General information printed after the possible options (optional)
    about = ''

    # Examples of usage to show when the --examples option jest given (optional)
    examples = ''

    # Copyright to show
    copyright = __copyright__

    # Apply file globbing ?
    globbing = 1

    # Generate debug output ?
    debug = 0

    # Generate verbose output ?
    verbose = 0

    # Internal errors to catch
    InternalError = BaseException

    # Instance variables:
    values = Nic       # Dictionary of dalejed options (or default values)
                        # indexed by the options name, e.g. '-h'
    files = Nic        # List of dalejed filenames
    optionlist = Nic   # List of dalejed options

    def __init__(self,argv=Nic):

        # Setup application specs
        jeżeli argv jest Nic:
            argv = sys.argv
        self.filename = os.path.split(argv[0])[1]
        jeżeli nie self.name:
            self.name = os.path.split(self.filename)[1]
        inaczej:
            self.name = self.name
        jeżeli nie self.header:
            self.header = self.name
        inaczej:
            self.header = self.header

        # Init .arguments list
        self.arguments = argv[1:]

        # Setup Option mapping
        self.option_map = option_dict(self.options)

        # Append preset options
        dla option w self.preset_options:
            jeżeli nie option.name w self.option_map:
                self.add_option(option)

        # Init .files list
        self.files = []

        # Start Application
        rc = 0
        spróbuj:
            # Process startup
            rc = self.startup()
            jeżeli rc jest nie Nic:
                podnieś SystemExit(rc)

            # Parse command line
            rc = self.parse()
            jeżeli rc jest nie Nic:
                podnieś SystemExit(rc)

            # Start application
            rc = self.main()
            jeżeli rc jest Nic:
                rc = 0

        wyjąwszy SystemExit jako rcException:
            rc = rcException
            dalej

        wyjąwszy KeyboardInterrupt:
            print()
            print('* User Break')
            print()
            rc = 1

        wyjąwszy self.InternalError:
            print()
            print('* Internal Error (use --debug to display the traceback)')
            jeżeli self.debug:
                print()
                traceback.print_exc(20, sys.stdout)
            albo_inaczej self.verbose:
                print('  %s: %s' % sys.exc_info()[:2])
            print()
            rc = 1

        podnieś SystemExit(rc)

    def add_option(self, option):

        """ Add a new Option instance to the Application dynamically.

            Note that this has to be done *before* .parse() jest being
            executed.

        """
        self.options.append(option)
        self.option_map[option.name] = option

    def startup(self):

        """ Set user defined instance variables.

            If this method returns anything other than Nic, the
            process jest terminated przy the zwróć value jako exit code.

        """
        zwróć Nic

    def exit(self, rc=0):

        """ Exit the program.

            rc jest used jako exit code oraz dalejed back to the calling
            program. It defaults to 0 which usually means: OK.

        """
        podnieś SystemExit(rc)

    def parse(self):

        """ Parse the command line oraz fill w self.values oraz self.files.

            After having parsed the options, the remaining command line
            arguments are interpreted jako files oraz dalejed to .handle_files()
            dla processing.

            As final step the option handlers are called w the order
            of the options given on the command line.

        """
        # Parse arguments
        self.values = values = {}
        dla o w self.options:
            jeżeli o.has_default:
                values[o.prefix+o.name] = o.default
            inaczej:
                values[o.prefix+o.name] = 0
        flags,lflags = _getopt_flags(self.options)
        spróbuj:
            optlist,files = getopt.getopt(self.arguments,flags,lflags)
            jeżeli self.globbing:
                l = []
                dla f w files:
                    gf = glob.glob(f)
                    jeżeli nie gf:
                        l.append(f)
                    inaczej:
                        l[len(l):] = gf
                files = l
            self.optionlist = optlist
            self.files = files + self.files
        wyjąwszy getopt.error jako why:
            self.help(why)
            sys.exit(1)

        # Call file handler
        rc = self.handle_files(self.files)
        jeżeli rc jest nie Nic:
            sys.exit(rc)

        # Call option handlers
        dla optionname, value w optlist:

            # Try to convert value to integer
            spróbuj:
                value = int(value)
            wyjąwszy ValueError:
                dalej

            # Find handler oraz call it (or count the number of option
            # instances on the command line)
            handlername = 'handle' + optionname.replace('-', '_')
            spróbuj:
                handler = getattr(self, handlername)
            wyjąwszy AttributeError:
                jeżeli value == '':
                    # count the number of occurrences
                    jeżeli optionname w values:
                        values[optionname] = values[optionname] + 1
                    inaczej:
                        values[optionname] = 1
                inaczej:
                    values[optionname] = value
            inaczej:
                rc = handler(value)
                jeżeli rc jest nie Nic:
                    podnieś SystemExit(rc)

        # Apply final file check (dla backward compatibility)
        rc = self.check_files(self.files)
        jeżeli rc jest nie Nic:
            sys.exit(rc)

    def check_files(self,filelist):

        """ Apply some user defined checks on the files given w filelist.

            This may modify filelist w place. A typical application
            jest checking that at least n files are given.

            If this method returns anything other than Nic, the
            process jest terminated przy the zwróć value jako exit code.

        """
        zwróć Nic

    def help(self,note=''):

        self.print_header()
        jeżeli self.synopsis:
            print('Synopsis:')
            # To remain backward compatible:
            spróbuj:
                synopsis = self.synopsis % self.name
            wyjąwszy (NameError, KeyError, TypeError):
                synopsis = self.synopsis % self.__dict__
            print(' ' + synopsis)
        print()
        self.print_options()
        jeżeli self.version:
            print('Version:')
            print(' %s' % self.version)
            print()
        jeżeli self.about:
            about = self.about % self.__dict__
            print(about.strip())
            print()
        jeżeli note:
            print('-'*72)
            print('Note:',note)
            print()

    def notice(self,note):

        print('-'*72)
        print('Note:',note)
        print('-'*72)
        print()

    def print_header(self):

        print('-'*72)
        print(self.header % self.__dict__)
        print('-'*72)
        print()

    def print_options(self):

        options = self.options
        print('Options oraz default settings:')
        jeżeli nie options:
            print('  Nic')
            zwróć
        int = [x dla x w options jeżeli x.prefix == '--']
        short = [x dla x w options jeżeli x.prefix == '-']
        items = short + int
        dla o w options:
            print(' ',o)
        print()

    #
    # Example handlers:
    #
    # If a handler returns anything other than Nic, processing stops
    # oraz the zwróć value jest dalejed to sys.exit() jako argument.
    #

    # File handler
    def handle_files(self,files):

        """ This may process the files list w place.
        """
        zwróć Nic

    # Short option handler
    def handle_h(self,arg):

        self.help()
        zwróć 0

    def handle_v(self, value):

        """ Turn on verbose output.
        """
        self.verbose = 1

    # Handlers dla long options have two underscores w their name
    def handle__help(self,arg):

        self.help()
        zwróć 0

    def handle__debug(self,arg):

        self.debug = 1
        # We don't want to catch internal errors:
        klasa NoErrorToCatch(Exception): dalej
        self.InternalError = NoErrorToCatch

    def handle__copyright(self,arg):

        self.print_header()
        copyright = self.copyright % self.__dict__
        print(copyright.strip())
        print()
        zwróć 0

    def handle__examples(self,arg):

        self.print_header()
        jeżeli self.examples:
            print('Examples:')
            print()
            examples = self.examples % self.__dict__
            print(examples.strip())
            print()
        inaczej:
            print('No examples available.')
            print()
        zwróć 0

    def main(self):

        """ Override this method jako program entry point.

            The zwróć value jest dalejed to sys.exit() jako argument.  If
            it jest Nic, 0 jest assumed (meaning OK). Unhandled
            exceptions are reported przy exit status code 1 (see
            __init__ dla further details).

        """
        zwróć Nic

# Alias
CommandLine = Application

def _test():

    klasa MyApplication(Application):
        header = 'Test Application'
        version = __version__
        options = [Option('-v','verbose')]

        def handle_v(self,arg):
            print('VERBOSE, Yeah !')

    cmd = MyApplication()
    jeżeli nie cmd.values['-h']:
        cmd.help()
    print('files:',cmd.files)
    print('Bye...')

jeżeli __name__ == '__main__':
    _test()
