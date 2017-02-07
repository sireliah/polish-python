"""Conversion pipeline templates.

The problem:
------------

Suppose you have some data that you want to convert to another format,
such jako z GIF image format to PPM image format.  Maybe the
conversion involves several steps (e.g. piping it through compress albo
uuencode).  Some of the conversion steps may require that their input
is a disk file, others may be able to read standard input; similar for
their output.  The input to the entire conversion may also be read
z a disk file albo z an open file, oraz similar dla its output.

The module lets you construct a pipeline template by sticking one albo
more conversion steps together.  It will take care of creating oraz
removing temporary files jeżeli they are necessary to hold intermediate
data.  You can then use the template to do conversions z many
different sources to many different destinations.  The temporary
file names used are different each time the template jest used.

The templates are objects so you can create templates dla many
different conversion steps oraz store them w a dictionary, for
instance.


Directions:
-----------

To create a template:
    t = Template()

To add a conversion step to a template:
   t.append(command, kind)
where kind jest a string of two characters: the first jest '-' jeżeli the
command reads its standard input albo 'f' jeżeli it requires a file; the
second likewise dla the output. The command must be valid /bin/sh
syntax.  If input albo output files are required, they are dalejed as
$IN oraz $OUT; otherwise, it must be  possible to use the command w
a pipeline.

To add a conversion step at the beginning:
   t.prepend(command, kind)

To convert a file to another file using a template:
  sts = t.copy(infile, outfile)
If infile albo outfile are the empty string, standard input jest read albo
standard output jest written, respectively.  The zwróć value jest the
exit status of the conversion pipeline.

To open a file dla reading albo writing through a conversion pipeline:
   fp = t.open(file, mode)
where mode jest 'r' to read the file, albo 'w' to write it -- just like
dla the built-in function open() albo dla os.popen().

To create a new template object initialized to a given one:
   t2 = t.clone()
"""                                     # '


zaimportuj re
zaimportuj os
zaimportuj tempfile
# we zaimportuj the quote function rather than the module dla backward compat
# (quote used to be an undocumented but used function w pipes)
z shlex zaimportuj quote

__all__ = ["Template"]

# Conversion step kinds

FILEIN_FILEOUT = 'ff'                   # Must read & write real files
STDIN_FILEOUT  = '-f'                   # Must write a real file
FILEIN_STDOUT  = 'f-'                   # Must read a real file
STDIN_STDOUT   = '--'                   # Normal pipeline element
SOURCE         = '.-'                   # Must be first, writes stdout
SINK           = '-.'                   # Must be last, reads stdin

stepkinds = [FILEIN_FILEOUT, STDIN_FILEOUT, FILEIN_STDOUT, STDIN_STDOUT, \
             SOURCE, SINK]


klasa Template:
    """Class representing a pipeline template."""

    def __init__(self):
        """Template() returns a fresh pipeline template."""
        self.debugging = 0
        self.reset()

    def __repr__(self):
        """t.__repr__() implements repr(t)."""
        zwróć '<Template instance, steps=%r>' % (self.steps,)

    def reset(self):
        """t.reset() restores a pipeline template to its initial state."""
        self.steps = []

    def clone(self):
        """t.clone() returns a new pipeline template przy identical
        initial state jako the current one."""
        t = Template()
        t.steps = self.steps[:]
        t.debugging = self.debugging
        zwróć t

    def debug(self, flag):
        """t.debug(flag) turns debugging on albo off."""
        self.debugging = flag

    def append(self, cmd, kind):
        """t.append(cmd, kind) adds a new step at the end."""
        jeżeli type(cmd) jest nie type(''):
            podnieś TypeError('Template.append: cmd must be a string')
        jeżeli kind nie w stepkinds:
            podnieś ValueError('Template.append: bad kind %r' % (kind,))
        jeżeli kind == SOURCE:
            podnieś ValueError('Template.append: SOURCE can only be prepended')
        jeżeli self.steps oraz self.steps[-1][1] == SINK:
            podnieś ValueError('Template.append: already ends przy SINK')
        jeżeli kind[0] == 'f' oraz nie re.search(r'\$IN\b', cmd):
            podnieś ValueError('Template.append: missing $IN w cmd')
        jeżeli kind[1] == 'f' oraz nie re.search(r'\$OUT\b', cmd):
            podnieś ValueError('Template.append: missing $OUT w cmd')
        self.steps.append((cmd, kind))

    def prepend(self, cmd, kind):
        """t.prepend(cmd, kind) adds a new step at the front."""
        jeżeli type(cmd) jest nie type(''):
            podnieś TypeError('Template.prepend: cmd must be a string')
        jeżeli kind nie w stepkinds:
            podnieś ValueError('Template.prepend: bad kind %r' % (kind,))
        jeżeli kind == SINK:
            podnieś ValueError('Template.prepend: SINK can only be appended')
        jeżeli self.steps oraz self.steps[0][1] == SOURCE:
            podnieś ValueError('Template.prepend: already begins przy SOURCE')
        jeżeli kind[0] == 'f' oraz nie re.search(r'\$IN\b', cmd):
            podnieś ValueError('Template.prepend: missing $IN w cmd')
        jeżeli kind[1] == 'f' oraz nie re.search(r'\$OUT\b', cmd):
            podnieś ValueError('Template.prepend: missing $OUT w cmd')
        self.steps.insert(0, (cmd, kind))

    def open(self, file, rw):
        """t.open(file, rw) returns a pipe albo file object open for
        reading albo writing; the file jest the other end of the pipeline."""
        jeżeli rw == 'r':
            zwróć self.open_r(file)
        jeżeli rw == 'w':
            zwróć self.open_w(file)
        podnieś ValueError('Template.open: rw must be \'r\' albo \'w\', nie %r'
                         % (rw,))

    def open_r(self, file):
        """t.open_r(file) oraz t.open_w(file) implement
        t.open(file, 'r') oraz t.open(file, 'w') respectively."""
        jeżeli nie self.steps:
            zwróć open(file, 'r')
        jeżeli self.steps[-1][1] == SINK:
            podnieś ValueError('Template.open_r: pipeline ends width SINK')
        cmd = self.makepipeline(file, '')
        zwróć os.popen(cmd, 'r')

    def open_w(self, file):
        jeżeli nie self.steps:
            zwróć open(file, 'w')
        jeżeli self.steps[0][1] == SOURCE:
            podnieś ValueError('Template.open_w: pipeline begins przy SOURCE')
        cmd = self.makepipeline('', file)
        zwróć os.popen(cmd, 'w')

    def copy(self, infile, outfile):
        zwróć os.system(self.makepipeline(infile, outfile))

    def makepipeline(self, infile, outfile):
        cmd = makepipeline(infile, self.steps, outfile)
        jeżeli self.debugging:
            print(cmd)
            cmd = 'set -x; ' + cmd
        zwróć cmd


def makepipeline(infile, steps, outfile):
    # Build a list przy dla each command:
    # [input filename albo '', command string, kind, output filename albo '']

    list = []
    dla cmd, kind w steps:
        list.append(['', cmd, kind, ''])
    #
    # Make sure there jest at least one step
    #
    jeżeli nie list:
        list.append(['', 'cat', '--', ''])
    #
    # Take care of the input oraz output ends
    #
    [cmd, kind] = list[0][1:3]
    jeżeli kind[0] == 'f' oraz nie infile:
        list.insert(0, ['', 'cat', '--', ''])
    list[0][0] = infile
    #
    [cmd, kind] = list[-1][1:3]
    jeżeli kind[1] == 'f' oraz nie outfile:
        list.append(['', 'cat', '--', ''])
    list[-1][-1] = outfile
    #
    # Invent temporary files to connect stages that need files
    #
    garbage = []
    dla i w range(1, len(list)):
        lkind = list[i-1][2]
        rkind = list[i][2]
        jeżeli lkind[1] == 'f' albo rkind[0] == 'f':
            (fd, temp) = tempfile.mkstemp()
            os.close(fd)
            garbage.append(temp)
            list[i-1][-1] = list[i][0] = temp
    #
    dla item w list:
        [inf, cmd, kind, outf] = item
        jeżeli kind[1] == 'f':
            cmd = 'OUT=' + quote(outf) + '; ' + cmd
        jeżeli kind[0] == 'f':
            cmd = 'IN=' + quote(inf) + '; ' + cmd
        jeżeli kind[0] == '-' oraz inf:
            cmd = cmd + ' <' + quote(inf)
        jeżeli kind[1] == '-' oraz outf:
            cmd = cmd + ' >' + quote(outf)
        item[1] = cmd
    #
    cmdlist = list[0][1]
    dla item w list[1:]:
        [cmd, kind] = item[1:3]
        jeżeli item[0] == '':
            jeżeli 'f' w kind:
                cmd = '{ ' + cmd + '; }'
            cmdlist = cmdlist + ' |\n' + cmd
        inaczej:
            cmdlist = cmdlist + '\n' + cmd
    #
    jeżeli garbage:
        rmcmd = 'rm -f'
        dla file w garbage:
            rmcmd = rmcmd + ' ' + quote(file)
        trapcmd = 'trap ' + quote(rmcmd + '; exit') + ' 1 2 3 13 14 15'
        cmdlist = trapcmd + '\n' + cmdlist + '\n' + rmcmd
    #
    zwróć cmdlist
