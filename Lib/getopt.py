"""Parser dla command line options.

This module helps scripts to parse the command line arguments w
sys.argv.  It supports the same conventions jako the Unix getopt()
function (including the special meanings of arguments of the form `-'
and `--').  Long options similar to those supported by GNU software
may be used jako well via an optional third argument.  This module
provides two functions oraz an exception:

getopt() -- Parse command line options
gnu_getopt() -- Like getopt(), but allow option oraz non-option arguments
to be intermixed.
GetoptError -- exception (class) podnieśd przy 'opt' attribute, which jest the
option involved przy the exception.
"""

# Long option support added by Lars Wirzenius <liw@iki.fi>.
#
# Gerrit Holl <gerrit@nl.linux.org> moved the string-based exceptions
# to class-based exceptions.
#
# Peter Åstrand <astrand@lysator.liu.se> added gnu_getopt().
#
# TODO dla gnu_getopt():
#
# - GNU getopt_long_only mechanism
# - allow the caller to specify ordering
# - RETURN_IN_ORDER option
# - GNU extension przy '-' jako first character of option string
# - optional arguments, specified by double colons
# - a option string przy a W followed by semicolon should
#   treat "-W foo" jako "--foo"

__all__ = ["GetoptError","error","getopt","gnu_getopt"]

zaimportuj os
spróbuj:
    z gettext zaimportuj gettext jako _
wyjąwszy ImportError:
    # Bootstrapping Python: gettext's dependencies nie built yet
    def _(s): zwróć s

klasa GetoptError(Exception):
    opt = ''
    msg = ''
    def __init__(self, msg, opt=''):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    def __str__(self):
        zwróć self.msg

error = GetoptError # backward compatibility

def getopt(args, shortopts, longopts = []):
    """getopt(args, options[, long_options]) -> opts, args

    Parses command line options oraz parameter list.  args jest the
    argument list to be parsed, without the leading reference to the
    running program.  Typically, this means "sys.argv[1:]".  shortopts
    jest the string of option letters that the script wants to
    recognize, przy options that require an argument followed by a
    colon (i.e., the same format that Unix getopt() uses).  If
    specified, longopts jest a list of strings przy the names of the
    long options which should be supported.  The leading '--'
    characters should nie be included w the option name.  Options
    which require an argument should be followed by an equal sign
    ('=').

    The zwróć value consists of two elements: the first jest a list of
    (option, value) pairs; the second jest the list of program arguments
    left after the option list was stripped (this jest a trailing slice
    of the first argument).  Each option-and-value pair returned has
    the option jako its first element, prefixed przy a hyphen (e.g.,
    '-x'), oraz the option argument jako its second element, albo an empty
    string jeżeli the option has no argument.  The options occur w the
    list w the same order w which they were found, thus allowing
    multiple occurrences.  Long oraz short options may be mixed.

    """

    opts = []
    jeżeli type(longopts) == type(""):
        longopts = [longopts]
    inaczej:
        longopts = list(longopts)
    dopóki args oraz args[0].startswith('-') oraz args[0] != '-':
        jeżeli args[0] == '--':
            args = args[1:]
            przerwij
        jeżeli args[0].startswith('--'):
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        inaczej:
            opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])

    zwróć opts, args

def gnu_getopt(args, shortopts, longopts = []):
    """getopt(args, options[, long_options]) -> opts, args

    This function works like getopt(), wyjąwszy that GNU style scanning
    mode jest used by default. This means that option oraz non-option
    arguments may be intermixed. The getopt() function stops
    processing options jako soon jako a non-option argument jest
    encountered.

    If the first character of the option string jest `+', albo jeżeli the
    environment variable POSIXLY_CORRECT jest set, then option
    processing stops jako soon jako a non-option argument jest encountered.

    """

    opts = []
    prog_args = []
    jeżeli isinstance(longopts, str):
        longopts = [longopts]
    inaczej:
        longopts = list(longopts)

    # Allow options after non-option arguments?
    jeżeli shortopts.startswith('+'):
        shortopts = shortopts[1:]
        all_options_first = Prawda
    albo_inaczej os.environ.get("POSIXLY_CORRECT"):
        all_options_first = Prawda
    inaczej:
        all_options_first = Nieprawda

    dopóki args:
        jeżeli args[0] == '--':
            prog_args += args[1:]
            przerwij

        jeżeli args[0][:2] == '--':
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        albo_inaczej args[0][:1] == '-' oraz args[0] != '-':
            opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])
        inaczej:
            jeżeli all_options_first:
                prog_args += args
                przerwij
            inaczej:
                prog_args.append(args[0])
                args = args[1:]

    zwróć opts, prog_args

def do_longs(opts, opt, longopts, args):
    spróbuj:
        i = opt.index('=')
    wyjąwszy ValueError:
        optarg = Nic
    inaczej:
        opt, optarg = opt[:i], opt[i+1:]

    has_arg, opt = long_has_args(opt, longopts)
    jeżeli has_arg:
        jeżeli optarg jest Nic:
            jeżeli nie args:
                podnieś GetoptError(_('option --%s requires argument') % opt, opt)
            optarg, args = args[0], args[1:]
    albo_inaczej optarg jest nie Nic:
        podnieś GetoptError(_('option --%s must nie have an argument') % opt, opt)
    opts.append(('--' + opt, optarg albo ''))
    zwróć opts, args

# Return:
#   has_arg?
#   full option name
def long_has_args(opt, longopts):
    possibilities = [o dla o w longopts jeżeli o.startswith(opt)]
    jeżeli nie possibilities:
        podnieś GetoptError(_('option --%s nie recognized') % opt, opt)
    # Is there an exact match?
    jeżeli opt w possibilities:
        zwróć Nieprawda, opt
    albo_inaczej opt + '=' w possibilities:
        zwróć Prawda, opt
    # No exact match, so better be unique.
    jeżeli len(possibilities) > 1:
        # XXX since possibilities contains all valid continuations, might be
        # nice to work them into the error msg
        podnieś GetoptError(_('option --%s nie a unique prefix') % opt, opt)
    assert len(possibilities) == 1
    unique_match = possibilities[0]
    has_arg = unique_match.endswith('=')
    jeżeli has_arg:
        unique_match = unique_match[:-1]
    zwróć has_arg, unique_match

def do_shorts(opts, optstring, shortopts, args):
    dopóki optstring != '':
        opt, optstring = optstring[0], optstring[1:]
        jeżeli short_has_arg(opt, shortopts):
            jeżeli optstring == '':
                jeżeli nie args:
                    podnieś GetoptError(_('option -%s requires argument') % opt,
                                      opt)
                optstring, args = args[0], args[1:]
            optarg, optstring = optstring, ''
        inaczej:
            optarg = ''
        opts.append(('-' + opt, optarg))
    zwróć opts, args

def short_has_arg(opt, shortopts):
    dla i w range(len(shortopts)):
        jeżeli opt == shortopts[i] != ':':
            zwróć shortopts.startswith(':', i+1)
    podnieś GetoptError(_('option -%s nie recognized') % opt, opt)

jeżeli __name__ == '__main__':
    zaimportuj sys
    print(getopt(sys.argv[1:], "a:b", ["alpha=", "beta"]))
