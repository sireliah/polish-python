#! /usr/bin/env python3

# This file contains a klasa oraz a main program that perform three
# related (though complimentary) formatting operations on Python
# programs.  When called jako "pindent -c", it takes a valid Python
# program jako input oraz outputs a version augmented przy block-closing
# comments.  When called jako "pindent -d", it assumes its input jest a
# Python program przy block-closing comments oraz outputs a commentless
# version.   When called jako "pindent -r" it assumes its input jest a
# Python program przy block-closing comments but przy its indentation
# messed up, oraz outputs a properly indented version.

# A "block-closing comment" jest a comment of the form '# end <keyword>'
# where <keyword> jest the keyword that opened the block.  If the
# opening keyword jest 'def' albo 'class', the function albo klasa name may
# be repeated w the block-closing comment jako well.  Here jest an
# example of a program fully augmented przy block-closing comments:

# def foobar(a, b):
#    jeżeli a == b:
#        a = a+1
#    albo_inaczej a < b:
#        b = b-1
#        jeżeli b > a: a = a-1
#        # end if
#    inaczej:
#        print 'oops!'
#    # end if
# # end def foobar

# Note that only the last part of an if...elif...inaczej... block needs a
# block-closing comment; the same jest true dla other compound
# statements (e.g. try...except).  Also note that "short-form" blocks
# like the second 'if' w the example must be closed jako well;
# otherwise the 'inaczej' w the example would be ambiguous (remember
# that indentation jest nie significant when interpreting block-closing
# comments).

# The operations are idempotent (i.e. applied to their own output
# they uzyskaj an identical result).  Running first "pindent -c" oraz
# then "pindent -r" on a valid Python program produces a program that
# jest semantically identical to the input (though its indentation may
# be different). Running "pindent -e" on that output produces a
# program that only differs z the original w indentation.

# Other options:
# -s stepsize: set the indentation step size (default 8)
# -t tabsize : set the number of spaces a tab character jest worth (default 8)
# -e         : expand TABs into spaces
# file ...   : input file(s) (default standard input)
# The results always go to standard output

# Caveats:
# - comments ending w a backslash will be mistaken dla continued lines
# - continuations using backslash are always left unchanged
# - continuations inside parentheses are nie extra indented by -r
#   but must be indented dla -c to work correctly (this przerwijs
#   idempotency!)
# - continued lines inside triple-quoted strings are totally garbled

# Secret feature:
# - On input, a block may also be closed przy an "end statement" --
#   this jest a block-closing comment without the '#' sign.

# Possible improvements:
# - check syntax based on transitions w 'next' table
# - better error reporting
# - better error recovery
# - check identifier after class/def

# The following wishes need a more complete tokenization of the source:
# - Don't get fooled by comments ending w backslash
# - reindent continuation lines indicated by backslash
# - handle continuation lines inside parentheses/braces/brackets
# - handle triple quoted strings spanning lines
# - realign comments
# - optionally do much more thorough reformatting, a la C indent

# Defaults
STEPSIZE = 8
TABSIZE = 8
EXPANDTABS = Nieprawda

zaimportuj io
zaimportuj re
zaimportuj sys

next = {}
next['jeżeli'] = next['albo_inaczej'] = 'albo_inaczej', 'inaczej', 'end'
next['dopóki'] = next['dla'] = 'inaczej', 'end'
next['spróbuj'] = 'wyjąwszy', 'w_końcu'
next['wyjąwszy'] = 'wyjąwszy', 'inaczej', 'w_końcu', 'end'
next['inaczej'] = next['w_końcu'] = next['z'] = \
    next['def'] = next['class'] = 'end'
next['end'] = ()
start = 'jeżeli', 'dopóki', 'dla', 'spróbuj', 'z', 'def', 'class'

klasa PythonIndenter:

    def __init__(self, fpi = sys.stdin, fpo = sys.stdout,
                 indentsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
        self.fpi = fpi
        self.fpo = fpo
        self.indentsize = indentsize
        self.tabsize = tabsize
        self.lineno = 0
        self.expandtabs = expandtabs
        self._write = fpo.write
        self.kwprog = re.compile(
                r'^(?:\s|\\\n)*(?P<kw>[a-z]+)'
                r'((?:\s|\\\n)+(?P<id>[a-zA-Z_]\w*))?'
                r'[^\w]')
        self.endprog = re.compile(
                r'^(?:\s|\\\n)*#?\s*end\s+(?P<kw>[a-z]+)'
                r'(\s+(?P<id>[a-zA-Z_]\w*))?'
                r'[^\w]')
        self.wsprog = re.compile(r'^[ \t]*')
    # end def __init__

    def write(self, line):
        jeżeli self.expandtabs:
            self._write(line.expandtabs(self.tabsize))
        inaczej:
            self._write(line)
        # end if
    # end def write

    def readline(self):
        line = self.fpi.readline()
        jeżeli line: self.lineno += 1
        # end if
        zwróć line
    # end def readline

    def error(self, fmt, *args):
        jeżeli args: fmt = fmt % args
        # end if
        sys.stderr.write('Error at line %d: %s\n' % (self.lineno, fmt))
        self.write('### %s ###\n' % fmt)
    # end def error

    def getline(self):
        line = self.readline()
        dopóki line[-2:] == '\\\n':
            line2 = self.readline()
            jeżeli nie line2: przerwij
            # end if
            line += line2
        # end while
        zwróć line
    # end def getline

    def putline(self, line, indent):
        tabs, spaces = divmod(indent*self.indentsize, self.tabsize)
        i = self.wsprog.match(line).end()
        line = line[i:]
        jeżeli line[:1] nie w ('\n', '\r', ''):
            line = '\t'*tabs + ' '*spaces + line
        # end if
        self.write(line)
    # end def putline

    def reformat(self):
        stack = []
        dopóki Prawda:
            line = self.getline()
            jeżeli nie line: przerwij      # EOF
            # end if
            m = self.endprog.match(line)
            jeżeli m:
                kw = 'end'
                kw2 = m.group('kw')
                jeżeli nie stack:
                    self.error('unexpected end')
                albo_inaczej stack.pop()[0] != kw2:
                    self.error('unmatched end')
                # end if
                self.putline(line, len(stack))
                kontynuuj
            # end if
            m = self.kwprog.match(line)
            jeżeli m:
                kw = m.group('kw')
                jeżeli kw w start:
                    self.putline(line, len(stack))
                    stack.append((kw, kw))
                    kontynuuj
                # end if
                jeżeli kw w next oraz stack:
                    self.putline(line, len(stack)-1)
                    kwa, kwb = stack[-1]
                    stack[-1] = kwa, kw
                    kontynuuj
                # end if
            # end if
            self.putline(line, len(stack))
        # end while
        jeżeli stack:
            self.error('unterminated keywords')
            dla kwa, kwb w stack:
                self.write('\t%s\n' % kwa)
            # end for
        # end if
    # end def reformat

    def delete(self):
        begin_counter = 0
        end_counter = 0
        dopóki Prawda:
            line = self.getline()
            jeżeli nie line: przerwij      # EOF
            # end if
            m = self.endprog.match(line)
            jeżeli m:
                end_counter += 1
                kontynuuj
            # end if
            m = self.kwprog.match(line)
            jeżeli m:
                kw = m.group('kw')
                jeżeli kw w start:
                    begin_counter += 1
                # end if
            # end if
            self.write(line)
        # end while
        jeżeli begin_counter - end_counter < 0:
            sys.stderr.write('Warning: input contained more end tags than expected\n')
        albo_inaczej begin_counter - end_counter > 0:
            sys.stderr.write('Warning: input contained less end tags than expected\n')
        # end if
    # end def delete

    def complete(self):
        stack = []
        todo = []
        currentws = thisid = firstkw = lastkw = topid = ''
        dopóki Prawda:
            line = self.getline()
            i = self.wsprog.match(line).end()
            m = self.endprog.match(line)
            jeżeli m:
                thiskw = 'end'
                endkw = m.group('kw')
                thisid = m.group('id')
            inaczej:
                m = self.kwprog.match(line)
                jeżeli m:
                    thiskw = m.group('kw')
                    jeżeli thiskw nie w next:
                        thiskw = ''
                    # end if
                    jeżeli thiskw w ('def', 'class'):
                        thisid = m.group('id')
                    inaczej:
                        thisid = ''
                    # end if
                albo_inaczej line[i:i+1] w ('\n', '#'):
                    todo.append(line)
                    kontynuuj
                inaczej:
                    thiskw = ''
                # end if
            # end if
            indentws = line[:i]
            indent = len(indentws.expandtabs(self.tabsize))
            current = len(currentws.expandtabs(self.tabsize))
            dopóki indent < current:
                jeżeli firstkw:
                    jeżeli topid:
                        s = '# end %s %s\n' % (
                                firstkw, topid)
                    inaczej:
                        s = '# end %s\n' % firstkw
                    # end if
                    self.write(currentws + s)
                    firstkw = lastkw = ''
                # end if
                currentws, firstkw, lastkw, topid = stack.pop()
                current = len(currentws.expandtabs(self.tabsize))
            # end while
            jeżeli indent == current oraz firstkw:
                jeżeli thiskw == 'end':
                    jeżeli endkw != firstkw:
                        self.error('mismatched end')
                    # end if
                    firstkw = lastkw = ''
                albo_inaczej nie thiskw albo thiskw w start:
                    jeżeli topid:
                        s = '# end %s %s\n' % (
                                firstkw, topid)
                    inaczej:
                        s = '# end %s\n' % firstkw
                    # end if
                    self.write(currentws + s)
                    firstkw = lastkw = topid = ''
                # end if
            # end if
            jeżeli indent > current:
                stack.append((currentws, firstkw, lastkw, topid))
                jeżeli thiskw oraz thiskw nie w start:
                    # error
                    thiskw = ''
                # end if
                currentws, firstkw, lastkw, topid = \
                          indentws, thiskw, thiskw, thisid
            # end if
            jeżeli thiskw:
                jeżeli thiskw w start:
                    firstkw = lastkw = thiskw
                    topid = thisid
                inaczej:
                    lastkw = thiskw
                # end if
            # end if
            dla l w todo: self.write(l)
            # end for
            todo = []
            jeżeli nie line: przerwij
            # end if
            self.write(line)
        # end while
    # end def complete
# end klasa PythonIndenter

# Simplified user interface
# - xxx_filter(input, output): read oraz write file objects
# - xxx_string(s): take oraz zwróć string object
# - xxx_file(filename): process file w place, zwróć true iff changed

def complete_filter(input = sys.stdin, output = sys.stdout,
                    stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.complete()
# end def complete_filter

def delete_filter(input= sys.stdin, output = sys.stdout,
                        stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.delete()
# end def delete_filter

def reformat_filter(input = sys.stdin, output = sys.stdout,
                    stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.reformat()
# end def reformat_filter

def complete_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.complete()
    zwróć output.getvalue()
# end def complete_string

def delete_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.delete()
    zwróć output.getvalue()
# end def delete_string

def reformat_string(source, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    input = io.StringIO(source)
    output = io.StringIO()
    pi = PythonIndenter(input, output, stepsize, tabsize, expandtabs)
    pi.reformat()
    zwróć output.getvalue()
# end def reformat_string

def make_backup(filename):
    zaimportuj os, os.path
    backup = filename + '~'
    jeżeli os.path.lexists(backup):
        spróbuj:
            os.remove(backup)
        wyjąwszy OSError:
            print("Can't remove backup %r" % (backup,), file=sys.stderr)
        # end try
    # end if
    spróbuj:
        os.rename(filename, backup)
    wyjąwszy OSError:
        print("Can't rename %r to %r" % (filename, backup), file=sys.stderr)
    # end try
# end def make_backup

def complete_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    przy open(filename, 'r') jako f:
        source = f.read()
    # end with
    result = complete_string(source, stepsize, tabsize, expandtabs)
    jeżeli source == result: zwróć 0
    # end if
    make_backup(filename)
    przy open(filename, 'w') jako f:
        f.write(result)
    # end with
    zwróć 1
# end def complete_file

def delete_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    przy open(filename, 'r') jako f:
        source = f.read()
    # end with
    result = delete_string(source, stepsize, tabsize, expandtabs)
    jeżeli source == result: zwróć 0
    # end if
    make_backup(filename)
    przy open(filename, 'w') jako f:
        f.write(result)
    # end with
    zwróć 1
# end def delete_file

def reformat_file(filename, stepsize = STEPSIZE, tabsize = TABSIZE, expandtabs = EXPANDTABS):
    przy open(filename, 'r') jako f:
        source = f.read()
    # end with
    result = reformat_string(source, stepsize, tabsize, expandtabs)
    jeżeli source == result: zwróć 0
    # end if
    make_backup(filename)
    przy open(filename, 'w') jako f:
        f.write(result)
    # end with
    zwróć 1
# end def reformat_file

# Test program when called jako a script

usage = """
usage: pindent (-c|-d|-r) [-s stepsize] [-t tabsize] [-e] [file] ...
-c         : complete a correctly indented program (add #end directives)
-d         : delete #end directives
-r         : reformat a completed program (use #end directives)
-s stepsize: indentation step (default %(STEPSIZE)d)
-t tabsize : the worth w spaces of a tab (default %(TABSIZE)d)
-e         : expand TABs into spaces (default OFF)
[file] ... : files are changed w place, przy backups w file~
If no files are specified albo a single - jest given,
the program acts jako a filter (reads stdin, writes stdout).
""" % vars()

def error_both(op1, op2):
    sys.stderr.write('Error: You can nie specify both '+op1+' oraz -'+op2[0]+' at the same time\n')
    sys.stderr.write(usage)
    sys.exit(2)
# end def error_both

def test():
    zaimportuj getopt
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'cdrs:t:e')
    wyjąwszy getopt.error jako msg:
        sys.stderr.write('Error: %s\n' % msg)
        sys.stderr.write(usage)
        sys.exit(2)
    # end try
    action = Nic
    stepsize = STEPSIZE
    tabsize = TABSIZE
    expandtabs = EXPANDTABS
    dla o, a w opts:
        jeżeli o == '-c':
            jeżeli action: error_both(o, action)
            # end if
            action = 'complete'
        albo_inaczej o == '-d':
            jeżeli action: error_both(o, action)
            # end if
            action = 'delete'
        albo_inaczej o == '-r':
            jeżeli action: error_both(o, action)
            # end if
            action = 'reformat'
        albo_inaczej o == '-s':
            stepsize = int(a)
        albo_inaczej o == '-t':
            tabsize = int(a)
        albo_inaczej o == '-e':
            expandtabs = Prawda
        # end if
    # end for
    jeżeli nie action:
        sys.stderr.write(
                'You must specify -c(omplete), -d(elete) albo -r(eformat)\n')
        sys.stderr.write(usage)
        sys.exit(2)
    # end if
    jeżeli nie args albo args == ['-']:
        action = eval(action + '_filter')
        action(sys.stdin, sys.stdout, stepsize, tabsize, expandtabs)
    inaczej:
        action = eval(action + '_file')
        dla filename w args:
            action(filename, stepsize, tabsize, expandtabs)
        # end for
    # end if
# end def test

jeżeli __name__ == '__main__':
    test()
# end if
