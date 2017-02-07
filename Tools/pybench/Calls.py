z pybench zaimportuj Test

klasa PythonFunctionCalls(Test):

    version = 2.1
    operations = 5*(1+4+4+2)
    rounds = 60000

    def test(self):

        global f,f1,g,h

        # define functions
        def f():
            dalej

        def f1(x):
            dalej

        def g(a,b,c):
            zwróć a,b,c

        def h(a,b,c,d=1,e=2,f=3):
            zwróć d,e,f

        # do calls
        dla i w range(self.rounds):

            f()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            h(i,i,3,i,i)
            h(i,i,i,2,i,3)

            f()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            h(i,i,3,i,i)
            h(i,i,i,2,i,3)

            f()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            h(i,i,3,i,i)
            h(i,i,i,2,i,3)

            f()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            h(i,i,3,i,i)
            h(i,i,i,2,i,3)

            f()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            g(i,i,i)
            h(i,i,3,i,i)
            h(i,i,i,2,i,3)

    def calibrate(self):

        global f,f1,g,h

        # define functions
        def f():
            dalej

        def f1(x):
            dalej

        def g(a,b,c):
            zwróć a,b,c

        def h(a,b,c,d=1,e=2,f=3):
            zwróć d,e,f

        # do calls
        dla i w range(self.rounds):
            dalej

###

klasa ComplexPythonFunctionCalls(Test):

    version = 2.0
    operations = 4*5
    rounds = 100000

    def test(self):

        # define functions
        def f(a,b,c,d=1,e=2,f=3):
            zwróć f

        args = 1,2
        kwargs = dict(c=3,d=4,e=5)

        # do calls
        dla i w range(self.rounds):
            f(a=i,b=i,c=i)
            f(f=i,e=i,d=i,c=2,b=i,a=3)
            f(1,b=i,**kwargs)
            f(*args,**kwargs)

            f(a=i,b=i,c=i)
            f(f=i,e=i,d=i,c=2,b=i,a=3)
            f(1,b=i,**kwargs)
            f(*args,**kwargs)

            f(a=i,b=i,c=i)
            f(f=i,e=i,d=i,c=2,b=i,a=3)
            f(1,b=i,**kwargs)
            f(*args,**kwargs)

            f(a=i,b=i,c=i)
            f(f=i,e=i,d=i,c=2,b=i,a=3)
            f(1,b=i,**kwargs)
            f(*args,**kwargs)

            f(a=i,b=i,c=i)
            f(f=i,e=i,d=i,c=2,b=i,a=3)
            f(1,b=i,**kwargs)
            f(*args,**kwargs)


    def calibrate(self):

        # define functions
        def f(a,b,c,d=1,e=2,f=3):
            zwróć f

        args = 1,2
        kwargs = dict(c=3,d=4,e=5)

        # do calls
        dla i w range(self.rounds):
            dalej

###

klasa BuiltinFunctionCalls(Test):

    version = 2.0
    operations = 5*(2+5+5+5)
    rounds = 60000

    def test(self):

        # localize functions
        f0 = globals
        f1 = hash
        f2 = divmod
        f3 = max

        # do calls
        dla i w range(self.rounds):

            f0()
            f0()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)

            f0()
            f0()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)

            f0()
            f0()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)

            f0()
            f0()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)

            f0()
            f0()
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f1(i)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f2(1,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)
            f3(1,3,2)

    def calibrate(self):

        # localize functions
        f0 = dir
        f1 = hash
        f2 = divmod
        f3 = max

        # do calls
        dla i w range(self.rounds):
            dalej

###

klasa PythonMethodCalls(Test):

    version = 2.0
    operations = 5*(6 + 5 + 4)
    rounds = 30000

    def test(self):

        klasa c:

            x = 2
            s = 'string'

            def f(self):

                zwróć self.x

            def j(self,a,b):

                self.y = a
                self.t = b
                zwróć self.y

            def k(self,a,b,c=3):

                self.y = a
                self.s = b
                self.t = c

        o = c()

        dla i w range(self.rounds):

            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.j(i,i)
            o.j(i,i)
            o.j(i,2)
            o.j(i,2)
            o.j(2,2)
            o.k(i,i)
            o.k(i,2)
            o.k(i,2,3)
            o.k(i,i,c=4)

            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.j(i,i)
            o.j(i,i)
            o.j(i,2)
            o.j(i,2)
            o.j(2,2)
            o.k(i,i)
            o.k(i,2)
            o.k(i,2,3)
            o.k(i,i,c=4)

            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.j(i,i)
            o.j(i,i)
            o.j(i,2)
            o.j(i,2)
            o.j(2,2)
            o.k(i,i)
            o.k(i,2)
            o.k(i,2,3)
            o.k(i,i,c=4)

            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.j(i,i)
            o.j(i,i)
            o.j(i,2)
            o.j(i,2)
            o.j(2,2)
            o.k(i,i)
            o.k(i,2)
            o.k(i,2,3)
            o.k(i,i,c=4)

            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.f()
            o.j(i,i)
            o.j(i,i)
            o.j(i,2)
            o.j(i,2)
            o.j(2,2)
            o.k(i,i)
            o.k(i,2)
            o.k(i,2,3)
            o.k(i,i,c=4)

    def calibrate(self):

        klasa c:

            x = 2
            s = 'string'

            def f(self):

                zwróć self.x

            def j(self,a,b):

                self.y = a
                self.t = b

            def k(self,a,b,c=3):

                self.y = a
                self.s = b
                self.t = c

        o = c

        dla i w range(self.rounds):
            dalej

###

klasa Recursion(Test):

    version = 2.0
    operations = 5
    rounds = 100000

    def test(self):

        global f

        def f(x):

            jeżeli x > 1:
                zwróć f(x-1)
            zwróć 1

        dla i w range(self.rounds):
            f(10)
            f(10)
            f(10)
            f(10)
            f(10)

    def calibrate(self):

        global f

        def f(x):

            jeżeli x > 0:
                zwróć f(x-1)
            zwróć 1

        dla i w range(self.rounds):
            dalej


### Test to make Fredrik happy...

jeżeli __name__ == '__main__':
    zaimportuj timeit
    jeżeli 0:
        timeit.TestClass = PythonFunctionCalls
        timeit.main(['-s', 'test = TestClass(); test.rounds = 1000',
                     'test.test()'])
    inaczej:
        setup = """\
global f,f1,g,h

# define functions
def f():
    dalej

def f1(x):
    dalej

def g(a,b,c):
    zwróć a,b,c

def h(a,b,c,d=1,e=2,f=3):
    zwróć d,e,f

i = 1
"""
        test = """\
f()
f1(i)
f1(i)
f1(i)
f1(i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
h(i,i,3,i,i)
h(i,i,i,2,i,3)

f()
f1(i)
f1(i)
f1(i)
f1(i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
h(i,i,3,i,i)
h(i,i,i,2,i,3)

f()
f1(i)
f1(i)
f1(i)
f1(i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
h(i,i,3,i,i)
h(i,i,i,2,i,3)

f()
f1(i)
f1(i)
f1(i)
f1(i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
h(i,i,3,i,i)
h(i,i,i,2,i,3)

f()
f1(i)
f1(i)
f1(i)
f1(i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
g(i,i,i)
h(i,i,3,i,i)
h(i,i,i,2,i,3)
"""

        timeit.main(['-s', setup,
                     test])
