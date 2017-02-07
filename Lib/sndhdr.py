"""Routines to help recognizing sound files.

Function whathdr() recognizes various types of sound file headers.
It understands almost all headers that SOX can decode.

The zwróć tuple contains the following items, w this order:
- file type (as SOX understands it)
- sampling rate (0 jeżeli unknown albo hard to decode)
- number of channels (0 jeżeli unknown albo hard to decode)
- number of frames w the file (-1 jeżeli unknown albo hard to decode)
- number of bits/sample, albo 'U' dla U-LAW, albo 'A' dla A-LAW

If the file doesn't have a recognizable type, it returns Nic.
If the file can't be opened, OSError jest podnieśd.

To compute the total time, divide the number of frames by the
sampling rate (a frame contains a sample dla each channel).

Function what() calls whathdr().  (It used to also use some
heuristics dla raw data, but this doesn't work very well.)

Finally, the function test() jest a simple main program that calls
what() dla all files mentioned on the argument list.  For directory
arguments it calls what() dla all files w that directory.  Default
argument jest "." (testing all files w the current directory).  The
option -r tells it to recurse down directories found inside
explicitly given directories.
"""

# The file structure jest top-down wyjąwszy that the test program oraz its
# subroutine come last.

__all__ = ['what', 'whathdr']

z collections zaimportuj namedtuple

SndHeaders = namedtuple('SndHeaders',
                        'filetype framerate nchannels nframes sampwidth')

def what(filename):
    """Guess the type of a sound file."""
    res = whathdr(filename)
    zwróć res


def whathdr(filename):
    """Recognize sound headers."""
    przy open(filename, 'rb') jako f:
        h = f.read(512)
        dla tf w tests:
            res = tf(h, f)
            jeżeli res:
                zwróć SndHeaders(*res)
        zwróć Nic


#-----------------------------------#
# Subroutines per sound header type #
#-----------------------------------#

tests = []

def test_aifc(h, f):
    zaimportuj aifc
    jeżeli nie h.startswith(b'FORM'):
        zwróć Nic
    jeżeli h[8:12] == b'AIFC':
        fmt = 'aifc'
    albo_inaczej h[8:12] == b'AIFF':
        fmt = 'aiff'
    inaczej:
        zwróć Nic
    f.seek(0)
    spróbuj:
        a = aifc.open(f, 'r')
    wyjąwszy (EOFError, aifc.Error):
        zwróć Nic
    zwróć (fmt, a.getframerate(), a.getnchannels(),
            a.getnframes(), 8 * a.getsampwidth())

tests.append(test_aifc)


def test_au(h, f):
    jeżeli h.startswith(b'.snd'):
        func = get_long_be
    albo_inaczej h[:4] w (b'\0ds.', b'dns.'):
        func = get_long_le
    inaczej:
        zwróć Nic
    filetype = 'au'
    hdr_size = func(h[4:8])
    data_size = func(h[8:12])
    encoding = func(h[12:16])
    rate = func(h[16:20])
    nchannels = func(h[20:24])
    sample_size = 1 # default
    jeżeli encoding == 1:
        sample_bits = 'U'
    albo_inaczej encoding == 2:
        sample_bits = 8
    albo_inaczej encoding == 3:
        sample_bits = 16
        sample_size = 2
    inaczej:
        sample_bits = '?'
    frame_size = sample_size * nchannels
    jeżeli frame_size:
        nframe = data_size / frame_size
    inaczej:
        nframe = -1
    zwróć filetype, rate, nchannels, nframe, sample_bits

tests.append(test_au)


def test_hcom(h, f):
    jeżeli h[65:69] != b'FSSD' albo h[128:132] != b'HCOM':
        zwróć Nic
    divisor = get_long_be(h[144:148])
    jeżeli divisor:
        rate = 22050 / divisor
    inaczej:
        rate = 0
    zwróć 'hcom', rate, 1, -1, 8

tests.append(test_hcom)


def test_voc(h, f):
    jeżeli nie h.startswith(b'Creative Voice File\032'):
        zwróć Nic
    sbseek = get_short_le(h[20:22])
    rate = 0
    jeżeli 0 <= sbseek < 500 oraz h[sbseek] == 1:
        ratecode = 256 - h[sbseek+4]
        jeżeli ratecode:
            rate = int(1000000.0 / ratecode)
    zwróć 'voc', rate, 1, -1, 8

tests.append(test_voc)


def test_wav(h, f):
    zaimportuj wave
    # 'RIFF' <len> 'WAVE' 'fmt ' <len>
    jeżeli nie h.startswith(b'RIFF') albo h[8:12] != b'WAVE' albo h[12:16] != b'fmt ':
        zwróć Nic
    f.seek(0)
    spróbuj:
        w = wave.openfp(f, 'r')
    wyjąwszy (EOFError, wave.Error):
        zwróć Nic
    zwróć ('wav', w.getframerate(), w.getnchannels(),
                   w.getnframes(), 8*w.getsampwidth())

tests.append(test_wav)


def test_8svx(h, f):
    jeżeli nie h.startswith(b'FORM') albo h[8:12] != b'8SVX':
        zwróć Nic
    # Should decode it to get #channels -- assume always 1
    zwróć '8svx', 0, 1, 0, 8

tests.append(test_8svx)


def test_sndt(h, f):
    jeżeli h.startswith(b'SOUND'):
        nsamples = get_long_le(h[8:12])
        rate = get_short_le(h[20:22])
        zwróć 'sndt', rate, 1, nsamples, 8

tests.append(test_sndt)


def test_sndr(h, f):
    jeżeli h.startswith(b'\0\0'):
        rate = get_short_le(h[2:4])
        jeżeli 4000 <= rate <= 25000:
            zwróć 'sndr', rate, 1, -1, 8

tests.append(test_sndr)


#-------------------------------------------#
# Subroutines to extract numbers z bytes #
#-------------------------------------------#

def get_long_be(b):
    zwróć (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]

def get_long_le(b):
    zwróć (b[3] << 24) | (b[2] << 16) | (b[1] << 8) | b[0]

def get_short_be(b):
    zwróć (b[0] << 8) | b[1]

def get_short_le(b):
    zwróć (b[1] << 8) | b[0]


#--------------------#
# Small test program #
#--------------------#

def test():
    zaimportuj sys
    recursive = 0
    jeżeli sys.argv[1:] oraz sys.argv[1] == '-r':
        usuń sys.argv[1:2]
        recursive = 1
    spróbuj:
        jeżeli sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        inaczej:
            testall(['.'], recursive, 1)
    wyjąwszy KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)

def testall(list, recursive, toplevel):
    zaimportuj sys
    zaimportuj os
    dla filename w list:
        jeżeli os.path.isdir(filename):
            print(filename + '/:', end=' ')
            jeżeli recursive albo toplevel:
                print('recursing down:')
                zaimportuj glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            inaczej:
                print('*** directory (use -r) ***')
        inaczej:
            print(filename + ':', end=' ')
            sys.stdout.flush()
            spróbuj:
                print(what(filename))
            wyjąwszy OSError:
                print('*** nie found ***')

jeżeli __name__ == '__main__':
    test()
