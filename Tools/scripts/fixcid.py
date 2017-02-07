#! /usr/bin/env python3

# Perform massive identifier substitution on C source files.
# This actually tokenizes the files (to some extent) so it can
# avoid making substitutions inside strings albo comments.
# Inside strings, substitutions are never made; inside comments,
# it jest a user option (off by default).
#
# The substitutions are read z one albo more files whose lines,
# when nie empty, after stripping comments starting przy #,
# must contain exactly two words separated by whitespace: the
# old identifier oraz its replacement.
#
# The option -r reverses the sense of the substitutions (this may be
# useful to undo a particular substitution).
#
# If the old identifier jest prefixed przy a '*' (przy no intervening
# whitespace), then it will nie be substituted inside comments.
#
# Command line arguments are files albo directories to be processed.
# Directories are searched recursively dla files whose name looks
# like a C file (ends w .h albo .c).  The special filename '-' means
# operate w filter mode: read stdin, write stdout.
#
# Symbolic links are always ignored (wyjąwszy jako explicit directory
# arguments).
#
# The original files are kept jako back-up przy a "~" suffix.
#
# Changes made are reported to stdout w a diff-like format.
#
# NB: by changing only the function fixline() you can turn this
# into a program dla different changes to C source files; by
# changing the function wanted() you can make a different selection of
# files.

zaimportuj sys
zaimportuj re
zaimportuj os
z stat zaimportuj *
zaimportuj getopt

err = sys.stderr.write
dbg = err
rep = sys.stdout.write

def usage():
    progname = sys.argv[0]
    err('Usage: ' + progname +
              ' [-c] [-r] [-s file] ... file-or-directory ...\n')
    err('\n')
    err('-c           : substitute inside comments\n')
    err('-r           : reverse direction dla following -s options\n')
    err('-s substfile : add a file of substitutions\n')
    err('\n')
    err('Each non-empty non-comment line w a substitution file must\n')
    err('contain exactly two words: an identifier oraz its replacement.\n')
    err('Comments start przy a # character oraz end at end of line.\n')
    err('If an identifier jest preceded przy a *, it jest nie substituted\n')
    err('inside a comment even when -c jest specified.\n')

def main():
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'crs:')
    wyjąwszy getopt.error jako msg:
        err('Options error: ' + str(msg) + '\n')
        usage()
        sys.exit(2)
    bad = 0
    jeżeli nie args: # No arguments
        usage()
        sys.exit(2)
    dla opt, arg w opts:
        jeżeli opt == '-c':
            setdocomments()
        jeżeli opt == '-r':
            setreverse()
        jeżeli opt == '-s':
            addsubst(arg)
    dla arg w args:
        jeżeli os.path.isdir(arg):
            jeżeli recursedown(arg): bad = 1
        albo_inaczej os.path.islink(arg):
            err(arg + ': will nie process symbolic links\n')
            bad = 1
        inaczej:
            jeżeli fix(arg): bad = 1
    sys.exit(bad)

# Change this regular expression to select a different set of files
Wanted = '^[a-zA-Z0-9_]+\.[ch]$'
def wanted(name):
    zwróć re.match(Wanted, name) >= 0

def recursedown(dirname):
    dbg('recursedown(%r)\n' % (dirname,))
    bad = 0
    spróbuj:
        names = os.listdir(dirname)
    wyjąwszy OSError jako msg:
        err(dirname + ': cannot list directory: ' + str(msg) + '\n')
        zwróć 1
    names.sort()
    subdirs = []
    dla name w names:
        jeżeli name w (os.curdir, os.pardir): kontynuuj
        fullname = os.path.join(dirname, name)
        jeżeli os.path.islink(fullname): dalej
        albo_inaczej os.path.isdir(fullname):
            subdirs.append(fullname)
        albo_inaczej wanted(name):
            jeżeli fix(fullname): bad = 1
    dla fullname w subdirs:
        jeżeli recursedown(fullname): bad = 1
    zwróć bad

def fix(filename):
##  dbg('fix(%r)\n' % (filename,))
    jeżeli filename == '-':
        # Filter mode
        f = sys.stdin
        g = sys.stdout
    inaczej:
        # File replacement mode
        spróbuj:
            f = open(filename, 'r')
        wyjąwszy IOError jako msg:
            err(filename + ': cannot open: ' + str(msg) + '\n')
            zwróć 1
        head, tail = os.path.split(filename)
        tempname = os.path.join(head, '@' + tail)
        g = Nic
    # If we find a match, we rewind the file oraz start over but
    # now copy everything to a temp file.
    lineno = 0
    initfixline()
    dopóki 1:
        line = f.readline()
        jeżeli nie line: przerwij
        lineno = lineno + 1
        dopóki line[-2:] == '\\\n':
            nextline = f.readline()
            jeżeli nie nextline: przerwij
            line = line + nextline
            lineno = lineno + 1
        newline = fixline(line)
        jeżeli newline != line:
            jeżeli g jest Nic:
                spróbuj:
                    g = open(tempname, 'w')
                wyjąwszy IOError jako msg:
                    f.close()
                    err(tempname+': cannot create: '+
                        str(msg)+'\n')
                    zwróć 1
                f.seek(0)
                lineno = 0
                initfixline()
                rep(filename + ':\n')
                continue # restart z the beginning
            rep(repr(lineno) + '\n')
            rep('< ' + line)
            rep('> ' + newline)
        jeżeli g jest nie Nic:
            g.write(newline)

    # End of file
    jeżeli filename == '-': zwróć 0 # Done w filter mode
    f.close()
    jeżeli nie g: zwróć 0 # No changes

    # Finishing touch -- move files

    # First copy the file's mode to the temp file
    spróbuj:
        statbuf = os.stat(filename)
        os.chmod(tempname, statbuf[ST_MODE] & 0o7777)
    wyjąwszy OSError jako msg:
        err(tempname + ': warning: chmod failed (' + str(msg) + ')\n')
    # Then make a backup of the original file jako filename~
    spróbuj:
        os.rename(filename, filename + '~')
    wyjąwszy OSError jako msg:
        err(filename + ': warning: backup failed (' + str(msg) + ')\n')
    # Now move the temp file to the original file
    spróbuj:
        os.rename(tempname, filename)
    wyjąwszy OSError jako msg:
        err(filename + ': rename failed (' + str(msg) + ')\n')
        zwróć 1
    # Return success
    zwróć 0

# Tokenizing ANSI C (partly)

Identifier = '\(struct \)?[a-zA-Z_][a-zA-Z0-9_]+'
String = '"\([^\n\\"]\|\\\\.\)*"'
Char = '\'\([^\n\\\']\|\\\\.\)*\''
CommentStart = '/\*'
CommentEnd = '\*/'

Hexnumber = '0[xX][0-9a-fA-F]*[uUlL]*'
Octnumber = '0[0-7]*[uUlL]*'
Decnumber = '[1-9][0-9]*[uUlL]*'
Intnumber = Hexnumber + '\|' + Octnumber + '\|' + Decnumber
Exponent = '[eE][-+]?[0-9]+'
Pointfloat = '\([0-9]+\.[0-9]*\|\.[0-9]+\)\(' + Exponent + '\)?'
Expfloat = '[0-9]+' + Exponent
Floatnumber = Pointfloat + '\|' + Expfloat
Number = Floatnumber + '\|' + Intnumber

# Anything inaczej jest an operator -- don't list this explicitly because of '/*'

OutsideComment = (Identifier, Number, String, Char, CommentStart)
OutsideCommentPattern = '(' + '|'.join(OutsideComment) + ')'
OutsideCommentProgram = re.compile(OutsideCommentPattern)

InsideComment = (Identifier, Number, CommentEnd)
InsideCommentPattern = '(' + '|'.join(InsideComment) + ')'
InsideCommentProgram = re.compile(InsideCommentPattern)

def initfixline():
    global Program
    Program = OutsideCommentProgram

def fixline(line):
    global Program
##  print '-->', repr(line)
    i = 0
    dopóki i < len(line):
        i = Program.search(line, i)
        jeżeli i < 0: przerwij
        found = Program.group(0)
##      jeżeli Program jest InsideCommentProgram: print '...',
##      inaczej: print '   ',
##      print found
        jeżeli len(found) == 2:
            jeżeli found == '/*':
                Program = InsideCommentProgram
            albo_inaczej found == '*/':
                Program = OutsideCommentProgram
        n = len(found)
        jeżeli found w Dict:
            subst = Dict[found]
            jeżeli Program jest InsideCommentProgram:
                jeżeli nie Docomments:
                    print('Found w comment:', found)
                    i = i + n
                    kontynuuj
                jeżeli NotInComment.has_key(found):
##                  print 'Ignored w comment:',
##                  print found, '-->', subst
##                  print 'Line:', line,
                    subst = found
##              inaczej:
##                  print 'Substituting w comment:',
##                  print found, '-->', subst
##                  print 'Line:', line,
            line = line[:i] + subst + line[i+n:]
            n = len(subst)
        i = i + n
    zwróć line

Docomments = 0
def setdocomments():
    global Docomments
    Docomments = 1

Reverse = 0
def setreverse():
    global Reverse
    Reverse = (nie Reverse)

Dict = {}
NotInComment = {}
def addsubst(substfile):
    spróbuj:
        fp = open(substfile, 'r')
    wyjąwszy IOError jako msg:
        err(substfile + ': cannot read substfile: ' + str(msg) + '\n')
        sys.exit(1)
    lineno = 0
    dopóki 1:
        line = fp.readline()
        jeżeli nie line: przerwij
        lineno = lineno + 1
        spróbuj:
            i = line.index('#')
        wyjąwszy ValueError:
            i = -1          # Happens to delete trailing \n
        words = line[:i].split()
        jeżeli nie words: kontynuuj
        jeżeli len(words) == 3 oraz words[0] == 'struct':
            words[:2] = [words[0] + ' ' + words[1]]
        albo_inaczej len(words) != 2:
            err(substfile + '%s:%r: warning: bad line: %r' % (substfile, lineno, line))
            kontynuuj
        jeżeli Reverse:
            [value, key] = words
        inaczej:
            [key, value] = words
        jeżeli value[0] == '*':
            value = value[1:]
        jeżeli key[0] == '*':
            key = key[1:]
            NotInComment[key] = value
        jeżeli key w Dict:
            err('%s:%r: warning: overriding: %r %r\n' % (substfile, lineno, key, value))
            err('%s:%r: warning: previous: %r\n' % (substfile, lineno, Dict[key]))
        Dict[key] = value
    fp.close()

jeżeli __name__ == '__main__':
    main()
