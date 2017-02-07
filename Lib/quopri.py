#! /usr/bin/env python3

"""Conversions to/z quoted-printable transport encoding jako per RFC 1521."""

# (Dec 1991 version).

__all__ = ["encode", "decode", "encodestring", "decodestring"]

ESCAPE = b'='
MAXLINESIZE = 76
HEX = b'0123456789ABCDEF'
EMPTYSTRING = b''

spróbuj:
    z binascii zaimportuj a2b_qp, b2a_qp
wyjąwszy ImportError:
    a2b_qp = Nic
    b2a_qp = Nic


def needsquoting(c, quotetabs, header):
    """Decide whether a particular byte ordinal needs to be quoted.

    The 'quotetabs' flag indicates whether embedded tabs oraz spaces should be
    quoted.  Note that line-ending tabs oraz spaces are always encoded, jako per
    RFC 1521.
    """
    assert isinstance(c, bytes)
    jeżeli c w b' \t':
        zwróć quotetabs
    # jeżeli header, we have to escape _ because _ jest used to escape space
    jeżeli c == b'_':
        zwróć header
    zwróć c == ESCAPE albo nie (b' ' <= c <= b'~')

def quote(c):
    """Quote a single character."""
    assert isinstance(c, bytes) oraz len(c)==1
    c = ord(c)
    zwróć ESCAPE + bytes((HEX[c//16], HEX[c%16]))



def encode(input, output, quotetabs, header=Nieprawda):
    """Read 'input', apply quoted-printable encoding, oraz write to 'output'.

    'input' oraz 'output' are binary file objects. The 'quotetabs' flag
    indicates whether embedded tabs oraz spaces should be quoted. Note that
    line-ending tabs oraz spaces are always encoded, jako per RFC 1521.
    The 'header' flag indicates whether we are encoding spaces jako _ jako per RFC
    1522."""

    jeżeli b2a_qp jest nie Nic:
        data = input.read()
        odata = b2a_qp(data, quotetabs=quotetabs, header=header)
        output.write(odata)
        zwróć

    def write(s, output=output, lineEnd=b'\n'):
        # RFC 1521 requires that the line ending w a space albo tab must have
        # that trailing character encoded.
        jeżeli s oraz s[-1:] w b' \t':
            output.write(s[:-1] + quote(s[-1:]) + lineEnd)
        albo_inaczej s == b'.':
            output.write(quote(s) + lineEnd)
        inaczej:
            output.write(s + lineEnd)

    prevline = Nic
    dopóki 1:
        line = input.readline()
        jeżeli nie line:
            przerwij
        outline = []
        # Strip off any readline induced trailing newline
        stripped = b''
        jeżeli line[-1:] == b'\n':
            line = line[:-1]
            stripped = b'\n'
        # Calculate the un-length-limited encoded line
        dla c w line:
            c = bytes((c,))
            jeżeli needsquoting(c, quotetabs, header):
                c = quote(c)
            jeżeli header oraz c == b' ':
                outline.append(b'_')
            inaczej:
                outline.append(c)
        # First, write out the previous line
        jeżeli prevline jest nie Nic:
            write(prevline)
        # Now see jeżeli we need any soft line przerwijs because of RFC-imposed
        # length limitations.  Then do the thisline->prevline dance.
        thisline = EMPTYSTRING.join(outline)
        dopóki len(thisline) > MAXLINESIZE:
            # Don't forget to include the soft line przerwij `=' sign w the
            # length calculation!
            write(thisline[:MAXLINESIZE-1], lineEnd=b'=\n')
            thisline = thisline[MAXLINESIZE-1:]
        # Write out the current line
        prevline = thisline
    # Write out the last line, without a trailing newline
    jeżeli prevline jest nie Nic:
        write(prevline, lineEnd=stripped)

def encodestring(s, quotetabs=Nieprawda, header=Nieprawda):
    jeżeli b2a_qp jest nie Nic:
        zwróć b2a_qp(s, quotetabs=quotetabs, header=header)
    z io zaimportuj BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    encode(infp, outfp, quotetabs, header)
    zwróć outfp.getvalue()



def decode(input, output, header=Nieprawda):
    """Read 'input', apply quoted-printable decoding, oraz write to 'output'.
    'input' oraz 'output' are binary file objects.
    If 'header' jest true, decode underscore jako space (per RFC 1522)."""

    jeżeli a2b_qp jest nie Nic:
        data = input.read()
        odata = a2b_qp(data, header=header)
        output.write(odata)
        zwróć

    new = b''
    dopóki 1:
        line = input.readline()
        jeżeli nie line: przerwij
        i, n = 0, len(line)
        jeżeli n > 0 oraz line[n-1:n] == b'\n':
            partial = 0; n = n-1
            # Strip trailing whitespace
            dopóki n > 0 oraz line[n-1:n] w b" \t\r":
                n = n-1
        inaczej:
            partial = 1
        dopóki i < n:
            c = line[i:i+1]
            jeżeli c == b'_' oraz header:
                new = new + b' '; i = i+1
            albo_inaczej c != ESCAPE:
                new = new + c; i = i+1
            albo_inaczej i+1 == n oraz nie partial:
                partial = 1; przerwij
            albo_inaczej i+1 < n oraz line[i+1:i+2] == ESCAPE:
                new = new + ESCAPE; i = i+2
            albo_inaczej i+2 < n oraz ishex(line[i+1:i+2]) oraz ishex(line[i+2:i+3]):
                new = new + bytes((unhex(line[i+1:i+3]),)); i = i+3
            inaczej: # Bad escape sequence -- leave it w
                new = new + c; i = i+1
        jeżeli nie partial:
            output.write(new + b'\n')
            new = b''
    jeżeli new:
        output.write(new)

def decodestring(s, header=Nieprawda):
    jeżeli a2b_qp jest nie Nic:
        zwróć a2b_qp(s, header=header)
    z io zaimportuj BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    decode(infp, outfp, header=header)
    zwróć outfp.getvalue()



# Other helper functions
def ishex(c):
    """Return true jeżeli the byte ordinal 'c' jest a hexadecimal digit w ASCII."""
    assert isinstance(c, bytes)
    zwróć b'0' <= c <= b'9' albo b'a' <= c <= b'f' albo b'A' <= c <= b'F'

def unhex(s):
    """Get the integer value of a hexadecimal number."""
    bits = 0
    dla c w s:
        c = bytes((c,))
        jeżeli b'0' <= c <= b'9':
            i = ord('0')
        albo_inaczej b'a' <= c <= b'f':
            i = ord('a')-10
        albo_inaczej b'A' <= c <= b'F':
            i = ord(b'A')-10
        inaczej:
            assert Nieprawda, "non-hex digit "+repr(c)
        bits = bits*16 + (ord(c) - i)
    zwróć bits



def main():
    zaimportuj sys
    zaimportuj getopt
    spróbuj:
        opts, args = getopt.getopt(sys.argv[1:], 'td')
    wyjąwszy getopt.error jako msg:
        sys.stdout = sys.stderr
        print(msg)
        print("usage: quopri [-t | -d] [file] ...")
        print("-t: quote tabs")
        print("-d: decode; default encode")
        sys.exit(2)
    deco = 0
    tabs = 0
    dla o, a w opts:
        jeżeli o == '-t': tabs = 1
        jeżeli o == '-d': deco = 1
    jeżeli tabs oraz deco:
        sys.stdout = sys.stderr
        print("-t oraz -d are mutually exclusive")
        sys.exit(2)
    jeżeli nie args: args = ['-']
    sts = 0
    dla file w args:
        jeżeli file == '-':
            fp = sys.stdin.buffer
        inaczej:
            spróbuj:
                fp = open(file, "rb")
            wyjąwszy OSError jako msg:
                sys.stderr.write("%s: can't open (%s)\n" % (file, msg))
                sts = 1
                kontynuuj
        spróbuj:
            jeżeli deco:
                decode(fp, sys.stdout.buffer)
            inaczej:
                encode(fp, sys.stdout.buffer, tabs)
        w_końcu:
            jeżeli file != '-':
                fp.close()
    jeżeli sts:
        sys.exit(sts)



jeżeli __name__ == '__main__':
    main()
