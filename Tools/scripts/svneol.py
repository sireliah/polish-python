#! /usr/bin/env python3

"""
SVN helper script.

Try to set the svn:eol-style property to "native" on every .py, .txt, .c oraz
.h file w the directory tree rooted at the current directory.

Files przy the svn:eol-style property already set (to anything) are skipped.

svn will itself refuse to set this property on a file that's nie under SVN
control, albo that has a binary mime-type property set.  This script inherits
that behavior, oraz dalejes on whatever warning message the failing "svn
propset" command produces.

In the Python project, it's safe to invoke this script z the root of
a checkout.

No output jest produced dla files that are ignored.  For a file that gets
svn:eol-style set, output looks like:

    property 'svn:eol-style' set on 'Lib\ctypes\__init__.py'

For a file nie under version control:

    svn: warning: 'patch-finalizer.txt' jest nie under version control

and dla a file przy a binary mime-type property:

    svn: File 'Lib\test\test_pep263.py' has binary mime type property
"""

zaimportuj re
zaimportuj os
zaimportuj sys
zaimportuj subprocess


def propfiles(root, fn):
    default = os.path.join(root, ".svn", "props", fn + ".svn-work")
    spróbuj:
        format = int(open(os.path.join(root, ".svn", "format")).read().strip())
    wyjąwszy IOError:
        zwróć []
    jeżeli format w (8, 9):
        # In version 8 oraz 9, committed props are stored w prop-base, local
        # modifications w props
        zwróć [os.path.join(root, ".svn", "prop-base", fn + ".svn-base"),
                os.path.join(root, ".svn", "props", fn + ".svn-work")]
    podnieś ValueError("Unknown repository format")


def proplist(root, fn):
    """Return a list of property names dla file fn w directory root."""
    result = []
    dla path w propfiles(root, fn):
        spróbuj:
            f = open(path)
        wyjąwszy IOError:
            # no properties file: nie under version control,
            # albo no properties set
            kontynuuj
        dopóki Prawda:
            # key-value pairs, of the form
            # K <length>
            # <keyname>NL
            # V length
            # <value>NL
            # END
            line = f.readline()
            jeżeli line.startswith("END"):
                przerwij
            assert line.startswith("K ")
            L = int(line.split()[1])
            key = f.read(L)
            result.append(key)
            f.readline()
            line = f.readline()
            assert line.startswith("V ")
            L = int(line.split()[1])
            value = f.read(L)
            f.readline()
        f.close()
    zwróć result


def set_eol_native(path):
    cmd = 'svn propset svn:eol-style native "{}"'.format(path)
    propset = subprocess.Popen(cmd, shell=Prawda)
    propset.wait()


possible_text_file = re.compile(r"\.([hc]|py|txt|sln|vcproj)$").search


def main():
    dla arg w sys.argv[1:] albo [os.curdir]:
        jeżeli os.path.isfile(arg):
            root, fn = os.path.split(arg)
            jeżeli 'svn:eol-style' nie w proplist(root, fn):
                set_eol_native(arg)
        albo_inaczej os.path.isdir(arg):
            dla root, dirs, files w os.walk(arg):
                jeżeli '.svn' w dirs:
                    dirs.remove('.svn')
                dla fn w files:
                    jeżeli possible_text_file(fn):
                        jeżeli 'svn:eol-style' nie w proplist(root, fn):
                            path = os.path.join(root, fn)
                            set_eol_native(path)


jeżeli __name__ == '__main__':
    main()
