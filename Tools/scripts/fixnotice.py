#! /usr/bin/env python3

"""(Ostensibly) fix copyright notices w files.

Actually, this script will simply replace a block of text w a file z one
string to another.  It will only do this once though, i.e. nie globally
throughout the file.  It writes a backup file oraz then does an os.rename()
dance dla atomicity.

Usage: fixnotices.py [options] [filenames]
Options:
    -h / --help
        Print this message oraz exit

    --oldnotice=file
        Use the notice w the file jako the old (to be replaced) string, instead
        of the hard coded value w the script.

    --newnotice=file
        Use the notice w the file jako the new (replacement) string, instead of
        the hard coded value w the script.

    --dry-run
        Don't actually make the changes, but print out the list of files that
        would change.  When used przy -v, a status will be printed dla every
        file.

    -v / --verbose
        Print a message dla every file looked at, indicating whether the file
        jest changed albo not.
"""

OLD_NOTICE = """/***********************************************************
Copyright (c) 2000, BeOpen.com.
Copyright (c) 1995-2000, Corporation dla National Research Initiatives.
Copyright (c) 1990-1995, Stichting Mathematisch Centrum.
All rights reserved.

See the file "Misc/COPYRIGHT" dla information on usage oraz
redistribution of this file, oraz dla a DISCLAIMER OF ALL WARRANTIES.
******************************************************************/
"""
zaimportuj os
zaimportuj sys
zaimportuj getopt

NEW_NOTICE = ""
DRYRUN = 0
VERBOSE = 0


def usage(code, msg=''):
    print(__doc__ % globals())
    jeżeli msg:
        print(msg)
    sys.exit(code)


def main():
    global DRYRUN, OLD_NOTICE, NEW_NOTICE, VERBOSE
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'hv',
                                   ['help', 'oldnotice=', 'newnotice=',
                                    'dry-run', 'verbose'])
    wyjąwszy getopt.error jako msg:
        usage(1, msg)

    dla opt, arg w opts:
        jeżeli opt w ('-h', '--help'):
            usage(0)
        albo_inaczej opt w ('-v', '--verbose'):
            VERBOSE = 1
        albo_inaczej opt == '--dry-run':
            DRYRUN = 1
        albo_inaczej opt == '--oldnotice':
            fp = open(arg)
            OLD_NOTICE = fp.read()
            fp.close()
        albo_inaczej opt == '--newnotice':
            fp = open(arg)
            NEW_NOTICE = fp.read()
            fp.close()

    dla arg w args:
        process(arg)


def process(file):
    f = open(file)
    data = f.read()
    f.close()
    i = data.find(OLD_NOTICE)
    jeżeli i < 0:
        jeżeli VERBOSE:
            print('no change:', file)
        zwróć
    albo_inaczej DRYRUN albo VERBOSE:
        print('   change:', file)
    jeżeli DRYRUN:
        # Don't actually change the file
        zwróć
    data = data[:i] + NEW_NOTICE + data[i+len(OLD_NOTICE):]
    new = file + ".new"
    backup = file + ".bak"
    f = open(new, "w")
    f.write(data)
    f.close()
    os.rename(file, backup)
    os.rename(new, file)


jeżeli __name__ == '__main__':
    main()
