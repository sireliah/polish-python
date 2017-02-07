#! /usr/bin/env python3

"""
"PYSTONE" Benchmark Program

Version:        Python/1.2 (corresponds to C/1.1 plus 3 Pystone fixes)

Author:         Reinhold P. Weicker,  CACM Vol 27, No 10, 10/84 pg. 1013.

                Translated z ADA to C by Rick Richardson.
                Every method to preserve ADA-likeness has been used,
                at the expense of C-ness.

                Translated z C to Python by Guido van Rossum.

Version History:

                Version 1.1 corrects two bugs w version 1.0:

                First, it leaked memory: w Proc1(), NextRecord ends
                up having a pointer to itself.  I have corrected this
                by zapping NextRecord.PtrComp at the end of Proc1().

                Second, Proc3() used the operator != to compare a
                record to Nic.  This jest rather inefficient oraz nie
                true to the intention of the original benchmark (where
                a pointer comparison to Nic jest intended; the !=
                operator attempts to find a method __cmp__ to do value
                comparison of the record).  Version 1.1 runs 5-10
                percent faster than version 1.0, so benchmark figures
                of different versions can't be compared directly.

                Version 1.2 changes the division to floor division.

                Under Python 3 version 1.1 would use the normal division
                operator, resulting w some of the operations mistakenly
                uzyskajing floats. Version 1.2 instead uses floor division
                making the benchmark a integer benchmark again.

"""

LOOPS = 50000

z time zaimportuj time

__version__ = "1.2"

[Ident1, Ident2, Ident3, Ident4, Ident5] = range(1, 6)

klasa Record:

    def __init__(self, PtrComp = Nic, Discr = 0, EnumComp = 0,
                       IntComp = 0, StringComp = 0):
        self.PtrComp = PtrComp
        self.Discr = Discr
        self.EnumComp = EnumComp
        self.IntComp = IntComp
        self.StringComp = StringComp

    def copy(self):
        zwróć Record(self.PtrComp, self.Discr, self.EnumComp,
                      self.IntComp, self.StringComp)

TRUE = 1
FALSE = 0

def main(loops=LOOPS):
    benchtime, stones = pystones(loops)
    print("Pystone(%s) time dla %d dalejes = %g" % \
          (__version__, loops, benchtime))
    print("This machine benchmarks at %g pystones/second" % stones)


def pystones(loops=LOOPS):
    zwróć Proc0(loops)

IntGlob = 0
BoolGlob = FALSE
Char1Glob = '\0'
Char2Glob = '\0'
Array1Glob = [0]*51
Array2Glob = [x[:] dla x w [Array1Glob]*51]
PtrGlb = Nic
PtrGlbNext = Nic

def Proc0(loops=LOOPS):
    global IntGlob
    global BoolGlob
    global Char1Glob
    global Char2Glob
    global Array1Glob
    global Array2Glob
    global PtrGlb
    global PtrGlbNext

    starttime = time()
    dla i w range(loops):
        dalej
    nulltime = time() - starttime

    PtrGlbNext = Record()
    PtrGlb = Record()
    PtrGlb.PtrComp = PtrGlbNext
    PtrGlb.Discr = Ident1
    PtrGlb.EnumComp = Ident3
    PtrGlb.IntComp = 40
    PtrGlb.StringComp = "DHRYSTONE PROGRAM, SOME STRING"
    String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING"
    Array2Glob[8][7] = 10

    starttime = time()

    dla i w range(loops):
        Proc5()
        Proc4()
        IntLoc1 = 2
        IntLoc2 = 3
        String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING"
        EnumLoc = Ident2
        BoolGlob = nie Func2(String1Loc, String2Loc)
        dopóki IntLoc1 < IntLoc2:
            IntLoc3 = 5 * IntLoc1 - IntLoc2
            IntLoc3 = Proc7(IntLoc1, IntLoc2)
            IntLoc1 = IntLoc1 + 1
        Proc8(Array1Glob, Array2Glob, IntLoc1, IntLoc3)
        PtrGlb = Proc1(PtrGlb)
        CharIndex = 'A'
        dopóki CharIndex <= Char2Glob:
            jeżeli EnumLoc == Func1(CharIndex, 'C'):
                EnumLoc = Proc6(Ident1)
            CharIndex = chr(ord(CharIndex)+1)
        IntLoc3 = IntLoc2 * IntLoc1
        IntLoc2 = IntLoc3 // IntLoc1
        IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1
        IntLoc1 = Proc2(IntLoc1)

    benchtime = time() - starttime - nulltime
    jeżeli benchtime == 0.0:
        loopsPerBenchtime = 0.0
    inaczej:
        loopsPerBenchtime = (loops / benchtime)
    zwróć benchtime, loopsPerBenchtime

def Proc1(PtrParIn):
    PtrParIn.PtrComp = NextRecord = PtrGlb.copy()
    PtrParIn.IntComp = 5
    NextRecord.IntComp = PtrParIn.IntComp
    NextRecord.PtrComp = PtrParIn.PtrComp
    NextRecord.PtrComp = Proc3(NextRecord.PtrComp)
    jeżeli NextRecord.Discr == Ident1:
        NextRecord.IntComp = 6
        NextRecord.EnumComp = Proc6(PtrParIn.EnumComp)
        NextRecord.PtrComp = PtrGlb.PtrComp
        NextRecord.IntComp = Proc7(NextRecord.IntComp, 10)
    inaczej:
        PtrParIn = NextRecord.copy()
    NextRecord.PtrComp = Nic
    zwróć PtrParIn

def Proc2(IntParIO):
    IntLoc = IntParIO + 10
    dopóki 1:
        jeżeli Char1Glob == 'A':
            IntLoc = IntLoc - 1
            IntParIO = IntLoc - IntGlob
            EnumLoc = Ident1
        jeżeli EnumLoc == Ident1:
            przerwij
    zwróć IntParIO

def Proc3(PtrParOut):
    global IntGlob

    jeżeli PtrGlb jest nie Nic:
        PtrParOut = PtrGlb.PtrComp
    inaczej:
        IntGlob = 100
    PtrGlb.IntComp = Proc7(10, IntGlob)
    zwróć PtrParOut

def Proc4():
    global Char2Glob

    BoolLoc = Char1Glob == 'A'
    BoolLoc = BoolLoc albo BoolGlob
    Char2Glob = 'B'

def Proc5():
    global Char1Glob
    global BoolGlob

    Char1Glob = 'A'
    BoolGlob = FALSE

def Proc6(EnumParIn):
    EnumParOut = EnumParIn
    jeżeli nie Func3(EnumParIn):
        EnumParOut = Ident4
    jeżeli EnumParIn == Ident1:
        EnumParOut = Ident1
    albo_inaczej EnumParIn == Ident2:
        jeżeli IntGlob > 100:
            EnumParOut = Ident1
        inaczej:
            EnumParOut = Ident4
    albo_inaczej EnumParIn == Ident3:
        EnumParOut = Ident2
    albo_inaczej EnumParIn == Ident4:
        dalej
    albo_inaczej EnumParIn == Ident5:
        EnumParOut = Ident3
    zwróć EnumParOut

def Proc7(IntParI1, IntParI2):
    IntLoc = IntParI1 + 2
    IntParOut = IntParI2 + IntLoc
    zwróć IntParOut

def Proc8(Array1Par, Array2Par, IntParI1, IntParI2):
    global IntGlob

    IntLoc = IntParI1 + 5
    Array1Par[IntLoc] = IntParI2
    Array1Par[IntLoc+1] = Array1Par[IntLoc]
    Array1Par[IntLoc+30] = IntLoc
    dla IntIndex w range(IntLoc, IntLoc+2):
        Array2Par[IntLoc][IntIndex] = IntLoc
    Array2Par[IntLoc][IntLoc-1] = Array2Par[IntLoc][IntLoc-1] + 1
    Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc]
    IntGlob = 5

def Func1(CharPar1, CharPar2):
    CharLoc1 = CharPar1
    CharLoc2 = CharLoc1
    jeżeli CharLoc2 != CharPar2:
        zwróć Ident1
    inaczej:
        zwróć Ident2

def Func2(StrParI1, StrParI2):
    IntLoc = 1
    dopóki IntLoc <= 1:
        jeżeli Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1:
            CharLoc = 'A'
            IntLoc = IntLoc + 1
    jeżeli CharLoc >= 'W' oraz CharLoc <= 'Z':
        IntLoc = 7
    jeżeli CharLoc == 'X':
        zwróć TRUE
    inaczej:
        jeżeli StrParI1 > StrParI2:
            IntLoc = IntLoc + 7
            zwróć TRUE
        inaczej:
            zwróć FALSE

def Func3(EnumParIn):
    EnumLoc = EnumParIn
    jeżeli EnumLoc == Ident3: zwróć TRUE
    zwróć FALSE

jeżeli __name__ == '__main__':
    zaimportuj sys
    def error(msg):
        print(msg, end=' ', file=sys.stderr)
        print("usage: %s [number_of_loops]" % sys.argv[0], file=sys.stderr)
        sys.exit(100)
    nargs = len(sys.argv) - 1
    jeżeli nargs > 1:
        error("%d arguments are too many;" % nargs)
    albo_inaczej nargs == 1:
        spróbuj: loops = int(sys.argv[1])
        wyjąwszy ValueError:
            error("Invalid argument %r;" % sys.argv[1])
    inaczej:
        loops = LOOPS
    main(loops)
