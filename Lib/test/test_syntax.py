"""This module tests SyntaxErrors.

Here's an example of the sort of thing that jest tested.

>>> def f(x):
...     global x
Traceback (most recent call last):
SyntaxError: name 'x' jest parameter oraz global

The tests are all podnieś SyntaxErrors.  They were created by checking
each C call that podnieśs SyntaxError.  There are several modules that
raise these exceptions-- ast.c, compile.c, future.c, pythonrun.c, oraz
symtable.c.

The parser itself outlaws a lot of invalid syntax.  Nic of these
errors are tested here at the moment.  We should add some tests; since
there are infinitely many programs przy invalid syntax, we would need
to be judicious w selecting some.

The compiler generates a synthetic module name dla code executed by
doctest.  Since all the code comes z the same module, a suffix like
[1] jest appended to the module name, As a consequence, changing the
order of tests w this module means renumbering all the errors after
it.  (Maybe we should enable the ellipsis option dla these tests.)

In ast.c, syntax errors are podnieśd by calling ast_error().

Errors z set_context():

>>> obj.Nic = 1
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> Nic = 1
Traceback (most recent call last):
SyntaxError: can't assign to keyword

It's a syntax error to assign to the empty tuple.  Why isn't it an
error to assign to the empty list?  It will always podnieś some error at
runtime.

>>> () = 1
Traceback (most recent call last):
SyntaxError: can't assign to ()

>>> f() = 1
Traceback (most recent call last):
SyntaxError: can't assign to function call

>>> usuń f()
Traceback (most recent call last):
SyntaxError: can't delete function call

>>> a + 1 = 2
Traceback (most recent call last):
SyntaxError: can't assign to operator

>>> (x dla x w x) = 1
Traceback (most recent call last):
SyntaxError: can't assign to generator expression

>>> 1 = 1
Traceback (most recent call last):
SyntaxError: can't assign to literal

>>> "abc" = 1
Traceback (most recent call last):
SyntaxError: can't assign to literal

>>> b"" = 1
Traceback (most recent call last):
SyntaxError: can't assign to literal

>>> `1` = 1
Traceback (most recent call last):
SyntaxError: invalid syntax

If the left-hand side of an assignment jest a list albo tuple, an illegal
expression inside that contain should still cause a syntax error.
This test just checks a couple of cases rather than enumerating all of
them.

>>> (a, "b", c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: can't assign to literal

>>> [a, b, c + 1] = [1, 2, 3]
Traceback (most recent call last):
SyntaxError: can't assign to operator

>>> a jeżeli 1 inaczej b = 1
Traceback (most recent call last):
SyntaxError: can't assign to conditional expression

From compiler_complex_args():

>>> def f(Nic=1):
...     dalej
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_arguments():

>>> def f(x, y=1, z):
...     dalej
Traceback (most recent call last):
SyntaxError: non-default argument follows default argument

>>> def f(x, Nic):
...     dalej
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> def f(*Nic):
...     dalej
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> def f(**Nic):
...     dalej
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_funcdef():

>>> def Nic(x):
...     dalej
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_call():

>>> def f(it, *varargs):
...     zwróć list(it)
>>> L = range(10)
>>> f(x dla x w L)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> f(x dla x w L, 1)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized jeżeli nie sole argument
>>> f(x dla x w L, y dla y w L)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized jeżeli nie sole argument
>>> f((x dla x w L), 1)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> f(i0,  i1,  i2,  i3,  i4,  i5,  i6,  i7,  i8,  i9,  i10,  i11,
...   i12,  i13,  i14,  i15,  i16,  i17,  i18,  i19,  i20,  i21,  i22,
...   i23,  i24,  i25,  i26,  i27,  i28,  i29,  i30,  i31,  i32,  i33,
...   i34,  i35,  i36,  i37,  i38,  i39,  i40,  i41,  i42,  i43,  i44,
...   i45,  i46,  i47,  i48,  i49,  i50,  i51,  i52,  i53,  i54,  i55,
...   i56,  i57,  i58,  i59,  i60,  i61,  i62,  i63,  i64,  i65,  i66,
...   i67,  i68,  i69,  i70,  i71,  i72,  i73,  i74,  i75,  i76,  i77,
...   i78,  i79,  i80,  i81,  i82,  i83,  i84,  i85,  i86,  i87,  i88,
...   i89,  i90,  i91,  i92,  i93,  i94,  i95,  i96,  i97,  i98,  i99,
...   i100,  i101,  i102,  i103,  i104,  i105,  i106,  i107,  i108,
...   i109,  i110,  i111,  i112,  i113,  i114,  i115,  i116,  i117,
...   i118,  i119,  i120,  i121,  i122,  i123,  i124,  i125,  i126,
...   i127,  i128,  i129,  i130,  i131,  i132,  i133,  i134,  i135,
...   i136,  i137,  i138,  i139,  i140,  i141,  i142,  i143,  i144,
...   i145,  i146,  i147,  i148,  i149,  i150,  i151,  i152,  i153,
...   i154,  i155,  i156,  i157,  i158,  i159,  i160,  i161,  i162,
...   i163,  i164,  i165,  i166,  i167,  i168,  i169,  i170,  i171,
...   i172,  i173,  i174,  i175,  i176,  i177,  i178,  i179,  i180,
...   i181,  i182,  i183,  i184,  i185,  i186,  i187,  i188,  i189,
...   i190,  i191,  i192,  i193,  i194,  i195,  i196,  i197,  i198,
...   i199,  i200,  i201,  i202,  i203,  i204,  i205,  i206,  i207,
...   i208,  i209,  i210,  i211,  i212,  i213,  i214,  i215,  i216,
...   i217,  i218,  i219,  i220,  i221,  i222,  i223,  i224,  i225,
...   i226,  i227,  i228,  i229,  i230,  i231,  i232,  i233,  i234,
...   i235,  i236,  i237,  i238,  i239,  i240,  i241,  i242,  i243,
...   i244,  i245,  i246,  i247,  i248,  i249,  i250,  i251,  i252,
...   i253,  i254,  i255)
Traceback (most recent call last):
SyntaxError: more than 255 arguments

The actual error cases counts positional arguments, keyword arguments,
and generator expression arguments separately.  This test combines the
three.

>>> f(i0,  i1,  i2,  i3,  i4,  i5,  i6,  i7,  i8,  i9,  i10,  i11,
...   i12,  i13,  i14,  i15,  i16,  i17,  i18,  i19,  i20,  i21,  i22,
...   i23,  i24,  i25,  i26,  i27,  i28,  i29,  i30,  i31,  i32,  i33,
...   i34,  i35,  i36,  i37,  i38,  i39,  i40,  i41,  i42,  i43,  i44,
...   i45,  i46,  i47,  i48,  i49,  i50,  i51,  i52,  i53,  i54,  i55,
...   i56,  i57,  i58,  i59,  i60,  i61,  i62,  i63,  i64,  i65,  i66,
...   i67,  i68,  i69,  i70,  i71,  i72,  i73,  i74,  i75,  i76,  i77,
...   i78,  i79,  i80,  i81,  i82,  i83,  i84,  i85,  i86,  i87,  i88,
...   i89,  i90,  i91,  i92,  i93,  i94,  i95,  i96,  i97,  i98,  i99,
...   i100,  i101,  i102,  i103,  i104,  i105,  i106,  i107,  i108,
...   i109,  i110,  i111,  i112,  i113,  i114,  i115,  i116,  i117,
...   i118,  i119,  i120,  i121,  i122,  i123,  i124,  i125,  i126,
...   i127,  i128,  i129,  i130,  i131,  i132,  i133,  i134,  i135,
...   i136,  i137,  i138,  i139,  i140,  i141,  i142,  i143,  i144,
...   i145,  i146,  i147,  i148,  i149,  i150,  i151,  i152,  i153,
...   i154,  i155,  i156,  i157,  i158,  i159,  i160,  i161,  i162,
...   i163,  i164,  i165,  i166,  i167,  i168,  i169,  i170,  i171,
...   i172,  i173,  i174,  i175,  i176,  i177,  i178,  i179,  i180,
...   i181,  i182,  i183,  i184,  i185,  i186,  i187,  i188,  i189,
...   i190,  i191,  i192,  i193,  i194,  i195,  i196,  i197,  i198,
...   i199,  i200,  i201,  i202,  i203,  i204,  i205,  i206,  i207,
...   i208,  i209,  i210,  i211,  i212,  i213,  i214,  i215,  i216,
...   i217,  i218,  i219,  i220,  i221,  i222,  i223,  i224,  i225,
...   i226,  i227,  i228,  i229,  i230,  i231,  i232,  i233,  i234,
...   i235, i236,  i237,  i238,  i239,  i240,  i241,  i242,  i243,
...   (x dla x w i244),  i245,  i246,  i247,  i248,  i249,  i250,  i251,
...    i252=1, i253=1,  i254=1,  i255=1)
Traceback (most recent call last):
SyntaxError: more than 255 arguments

>>> f(lambda x: x[0] = 3)
Traceback (most recent call last):
SyntaxError: lambda cannot contain assignment

The grammar accepts any test (basically, any expression) w the
keyword slot of a call site.  Test a few different options.

>>> f(x()=2)
Traceback (most recent call last):
SyntaxError: keyword can't be an expression
>>> f(a albo b=1)
Traceback (most recent call last):
SyntaxError: keyword can't be an expression
>>> f(x.y=1)
Traceback (most recent call last):
SyntaxError: keyword can't be an expression


More set_context():

>>> (x dla x w x) += 1
Traceback (most recent call last):
SyntaxError: can't assign to generator expression
>>> Nic += 1
Traceback (most recent call last):
SyntaxError: can't assign to keyword
>>> f() += 1
Traceback (most recent call last):
SyntaxError: can't assign to function call


Test continue w finally w weird combinations.

continue w dla loop under finally should be ok.

    >>> def test():
    ...     spróbuj:
    ...         dalej
    ...     w_końcu:
    ...         dla abc w range(10):
    ...             kontynuuj
    ...     print(abc)
    >>> test()
    9

Start simple, a continue w a finally should nie be allowed.

    >>> def test():
    ...    dla abc w range(10):
    ...        spróbuj:
    ...            dalej
    ...        w_końcu:
    ...            kontynuuj
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

This jest essentially a continue w a finally which should nie be allowed.

    >>> def test():
    ...    dla abc w range(10):
    ...        spróbuj:
    ...            dalej
    ...        w_końcu:
    ...            spróbuj:
    ...                kontynuuj
    ...            wyjąwszy:
    ...                dalej
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

    >>> def foo():
    ...     spróbuj:
    ...         dalej
    ...     w_końcu:
    ...         kontynuuj
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

    >>> def foo():
    ...     dla a w ():
    ...       spróbuj:
    ...           dalej
    ...       w_końcu:
    ...           kontynuuj
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

    >>> def foo():
    ...     dla a w ():
    ...         spróbuj:
    ...             dalej
    ...         w_końcu:
    ...             spróbuj:
    ...                 kontynuuj
    ...             w_końcu:
    ...                 dalej
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

    >>> def foo():
    ...  dla a w ():
    ...   spróbuj: dalej
    ...   w_końcu:
    ...    spróbuj:
    ...     dalej
    ...    wyjąwszy:
    ...     kontynuuj
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' nie supported inside 'finally' clause

There jest one test dla a przerwij that jest nie w a loop.  The compiler
uses a single data structure to keep track of try-finally oraz loops,
so we need to be sure that a przerwij jest actually inside a loop.  If it
isn't, there should be a syntax error.

   >>> spróbuj:
   ...     print(1)
   ...     przerwij
   ...     print(2)
   ... w_końcu:
   ...     print(3)
   Traceback (most recent call last):
     ...
   SyntaxError: 'break' outside loop

This should probably podnieś a better error than a SystemError (or none at all).
In 2.5 there was a missing exception oraz an assert was triggered w a debug
build.  The number of blocks must be greater than CO_MAXBLOCKS.  SF #1565514

   >>> dopóki 1:
   ...  dopóki 2:
   ...   dopóki 3:
   ...    dopóki 4:
   ...     dopóki 5:
   ...      dopóki 6:
   ...       dopóki 8:
   ...        dopóki 9:
   ...         dopóki 10:
   ...          dopóki 11:
   ...           dopóki 12:
   ...            dopóki 13:
   ...             dopóki 14:
   ...              dopóki 15:
   ...               dopóki 16:
   ...                dopóki 17:
   ...                 dopóki 18:
   ...                  dopóki 19:
   ...                   dopóki 20:
   ...                    dopóki 21:
   ...                     dopóki 22:
   ...                      przerwij
   Traceback (most recent call last):
     ...
   SystemError: too many statically nested blocks

Misuse of the nonlocal statement can lead to a few unique syntax errors.

   >>> def f(x):
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' jest parameter oraz nonlocal

   >>> def f():
   ...     global x
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' jest nonlocal oraz global

   >>> def f():
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: no binding dla nonlocal 'x' found

From SF bug #1705365
   >>> nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: nonlocal declaration nie allowed at module level

TODO(jhylton): Figure out how to test SyntaxWarning przy doctest.

##   >>> def f(x):
##   ...     def f():
##   ...         print(x)
##   ...         nonlocal x
##   Traceback (most recent call last):
##     ...
##   SyntaxWarning: name 'x' jest assigned to before nonlocal declaration

##   >>> def f():
##   ...     x = 1
##   ...     nonlocal x
##   Traceback (most recent call last):
##     ...
##   SyntaxWarning: name 'x' jest assigned to before nonlocal declaration


This tests assignment-context; there was a bug w Python 2.5 where compiling
a complex 'if' (one przy 'elif') would fail to notice an invalid suite,
leading to spurious errors.

   >>> jeżeli 1:
   ...   x() = 1
   ... albo_inaczej 1:
   ...   dalej
   Traceback (most recent call last):
     ...
   SyntaxError: can't assign to function call

   >>> jeżeli 1:
   ...   dalej
   ... albo_inaczej 1:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: can't assign to function call

   >>> jeżeli 1:
   ...   x() = 1
   ... albo_inaczej 1:
   ...   dalej
   ... inaczej:
   ...   dalej
   Traceback (most recent call last):
     ...
   SyntaxError: can't assign to function call

   >>> jeżeli 1:
   ...   dalej
   ... albo_inaczej 1:
   ...   x() = 1
   ... inaczej:
   ...   dalej
   Traceback (most recent call last):
     ...
   SyntaxError: can't assign to function call

   >>> jeżeli 1:
   ...   dalej
   ... albo_inaczej 1:
   ...   dalej
   ... inaczej:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: can't assign to function call

Make sure that the old "raise X, Y[, Z]" form jest gone:
   >>> podnieś X, Y
   Traceback (most recent call last):
     ...
   SyntaxError: invalid syntax
   >>> podnieś X, Y, Z
   Traceback (most recent call last):
     ...
   SyntaxError: invalid syntax


>>> f(a=23, a=234)
Traceback (most recent call last):
   ...
SyntaxError: keyword argument repeated

>>> usuń ()
Traceback (most recent call last):
SyntaxError: can't delete ()

>>> {1, 2, 3} = 42
Traceback (most recent call last):
SyntaxError: can't assign to literal

Corner-cases that used to fail to podnieś the correct error:

    >>> def f(*, x=lambda __debug__:0): dalej
    Traceback (most recent call last):
    SyntaxError: assignment to keyword

    >>> def f(*args:(lambda __debug__:0)): dalej
    Traceback (most recent call last):
    SyntaxError: assignment to keyword

    >>> def f(**kwargs:(lambda __debug__:0)): dalej
    Traceback (most recent call last):
    SyntaxError: assignment to keyword

    >>> przy (lambda *:0): dalej
    Traceback (most recent call last):
    SyntaxError: named arguments must follow bare *

Corner-cases that used to crash:

    >>> def f(**__debug__): dalej
    Traceback (most recent call last):
    SyntaxError: assignment to keyword

    >>> def f(*xx, __debug__): dalej
    Traceback (most recent call last):
    SyntaxError: assignment to keyword

"""

zaimportuj re
zaimportuj unittest
zaimportuj warnings

z test zaimportuj support

klasa SyntaxTestCase(unittest.TestCase):

    def _check_error(self, code, errtext,
                     filename="<testcase>", mode="exec", subclass=Nic):
        """Check that compiling code podnieśs SyntaxError przy errtext.

        errtest jest a regular expression that must be present w the
        test of the exception podnieśd.  If subclass jest specified it
        jest the expected subclass of SyntaxError (e.g. IndentationError).
        """
        spróbuj:
            compile(code, filename, mode)
        wyjąwszy SyntaxError jako err:
            jeżeli subclass oraz nie isinstance(err, subclass):
                self.fail("SyntaxError jest nie a %s" % subclass.__name__)
            mo = re.search(errtext, str(err))
            jeżeli mo jest Nic:
                self.fail("SyntaxError did nie contain '%r'" % (errtext,))
        inaczej:
            self.fail("compile() did nie podnieś SyntaxError")

    def test_assign_call(self):
        self._check_error("f() = 1", "assign")

    def test_assign_del(self):
        self._check_error("usuń f()", "delete")

    def test_global_err_then_warn(self):
        # Bug tickler:  The SyntaxError podnieśd dla one global statement
        # shouldn't be clobbered by a SyntaxWarning issued dla a later one.
        source = """jeżeli 1:
            def error(a):
                global a  # SyntaxError
            def warning():
                b = 1
                global b  # SyntaxWarning
            """
        warnings.filterwarnings(action='ignore', category=SyntaxWarning)
        self._check_error(source, "global")
        warnings.filters.pop(0)

    def test_break_outside_loop(self):
        self._check_error("break", "outside loop")

    def test_unexpected_indent(self):
        self._check_error("foo()\n bar()\n", "unexpected indent",
                          subclass=IndentationError)

    def test_no_indent(self):
        self._check_error("jeżeli 1:\nfoo()", "expected an indented block",
                          subclass=IndentationError)

    def test_bad_outdent(self):
        self._check_error("jeżeli 1:\n  foo()\n bar()",
                          "unindent does nie match .* level",
                          subclass=IndentationError)

    def test_kwargs_last(self):
        self._check_error("int(base=10, '2')",
                          "positional argument follows keyword argument")

    def test_kwargs_last2(self):
        self._check_error("int(**{base: 10}, '2')",
                          "positional argument follows "
                          "keyword argument unpacking")

    def test_kwargs_last3(self):
        self._check_error("int(**{base: 10}, *['2'])",
                          "iterable argument unpacking follows "
                          "keyword argument unpacking")

def test_main():
    support.run_unittest(SyntaxTestCase)
    z test zaimportuj test_syntax
    support.run_doctest(test_syntax, verbosity=Prawda)

jeżeli __name__ == "__main__":
    test_main()
