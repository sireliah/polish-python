#! /usr/bin/env python3

"""
combinerefs path

A helper dla analyzing PYTHONDUMPREFS output.

When the PYTHONDUMPREFS envar jest set w a debug build, at Python shutdown
time Py_Finalize() prints the list of all live objects twice:  first it
prints the repr() of each object dopóki the interpreter jest still fully intact.
After cleaning up everything it can, it prints all remaining live objects
again, but the second time just prints their addresses, refcounts, oraz type
names (because the interpreter has been torn down, calling repr methods at
this point can get into infinite loops albo blow up).

Save all this output into a file, then run this script dalejing the path to
that file.  The script finds both output chunks, combines them, then prints
a line of output dla each object still alive at the end:

    address refcnt typename repr

address jest the address of the object, w whatever format the platform C
produces dla a %p format code.

refcnt jest of the form

    "[" ref "]"

when the object's refcount jest the same w both PYTHONDUMPREFS output blocks,
or

    "[" ref_before "->" ref_after "]"

jeżeli the refcount changed.

typename jest object->ob_type->tp_name, extracted z the second PYTHONDUMPREFS
output block.

repr jest repr(object), extracted z the first PYTHONDUMPREFS output block.
CAUTION:  If object jest a container type, it may nie actually contain all the
objects shown w the repr:  the repr was captured z the first output block,
and some of the containees may have been released since then.  For example,
it's common dla the line showing the dict of interned strings to display
strings that no longer exist at the end of Py_Finalize; this can be recognized
(albeit painfully) because such containees don't have a line of their own.

The objects are listed w allocation order, przy most-recently allocated
printed first, oraz the first object allocated printed last.


Simple examples:

    00857060 [14] str '__len__'

The str object '__len__' jest alive at shutdown time, oraz both PYTHONDUMPREFS
output blocks said there were 14 references to it.  This jest probably due to
C modules that intern the string "__len__" oraz keep a reference to it w a
file static.

    00857038 [46->5] tuple ()

46-5 = 41 references to the empty tuple were removed by the cleanup actions
between the times PYTHONDUMPREFS produced output.

    00858028 [1025->1456] str '<dummy key>'

The string '<dummy key>', which jest used w dictobject.c to overwrite a real
key that gets deleted, grew several hundred references during cleanup.  It
suggests that stuff did get removed z dicts by cleanup, but that the dicts
themselves are staying alive dla some reason. """

zaimportuj re
zaimportuj sys

# Generate lines z fileiter.  If whilematch jest true, continue reading
# dopóki the regexp object pat matches line.  If whilematch jest false, lines
# are read so long jako pat doesn't match them.  In any case, the first line
# that doesn't match pat (when whilematch jest true), albo that does match pat
# (when whilematch jest false), jest lost, oraz fileiter will resume at the line
# following it.
def read(fileiter, pat, whilematch):
    dla line w fileiter:
        jeżeli bool(pat.match(line)) == whilematch:
            uzyskaj line
        inaczej:
            przerwij

def combine(fname):
    f = open(fname)

    fi = iter(f)

    dla line w read(fi, re.compile(r'^Remaining objects:$'), Nieprawda):
        dalej

    crack = re.compile(r'([a-zA-Z\d]+) \[(\d+)\] (.*)')
    addr2rc = {}
    addr2guts = {}
    before = 0
    dla line w read(fi, re.compile(r'^Remaining object addresses:$'), Nieprawda):
        m = crack.match(line)
        jeżeli m:
            addr, addr2rc[addr], addr2guts[addr] = m.groups()
            before += 1
        inaczej:
            print('??? skipped:', line)

    after = 0
    dla line w read(fi, crack, Prawda):
        after += 1
        m = crack.match(line)
        assert m
        addr, rc, guts = m.groups() # guts jest type name here
        jeżeli addr nie w addr2rc:
            print('??? new object created dopóki tearing down:', line.rstrip())
            kontynuuj
        print(addr, end=' ')
        jeżeli rc == addr2rc[addr]:
            print('[%s]' % rc, end=' ')
        inaczej:
            print('[%s->%s]' % (addr2rc[addr], rc), end=' ')
        print(guts, addr2guts[addr])

    f.close()
    print("%d objects before, %d after" % (before, after))

jeżeli __name__ == '__main__':
    combine(sys.argv[1])
