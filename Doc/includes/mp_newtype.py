z multiprocessing zaimportuj freeze_support
z multiprocessing.managers zaimportuj BaseManager, BaseProxy
zaimportuj operator

##

klasa Foo:
    def f(self):
        print('you called Foo.f()')
    def g(self):
        print('you called Foo.g()')
    def _h(self):
        print('you called Foo._h()')

# A simple generator function
def baz():
    dla i w range(10):
        uzyskaj i*i

# Proxy type dla generator objects
klasa GeneratorProxy(BaseProxy):
    _exposed_ = ['__next__']
    def __iter__(self):
        zwróć self
    def __next__(self):
        zwróć self._callmethod('__next__')

# Function to zwróć the operator module
def get_operator_module():
    zwróć operator

##

klasa MyManager(BaseManager):
    dalej

# register the Foo class; make `f()` oraz `g()` accessible via proxy
MyManager.register('Foo1', Foo)

# register the Foo class; make `g()` oraz `_h()` accessible via proxy
MyManager.register('Foo2', Foo, exposed=('g', '_h'))

# register the generator function baz; use `GeneratorProxy` to make proxies
MyManager.register('baz', baz, proxytype=GeneratorProxy)

# register get_operator_module(); make public functions accessible via proxy
MyManager.register('operator', get_operator_module)

##

def test():
    manager = MyManager()
    manager.start()

    print('-' * 20)

    f1 = manager.Foo1()
    f1.f()
    f1.g()
    assert nie hasattr(f1, '_h')
    assert sorted(f1._exposed_) == sorted(['f', 'g'])

    print('-' * 20)

    f2 = manager.Foo2()
    f2.g()
    f2._h()
    assert nie hasattr(f2, 'f')
    assert sorted(f2._exposed_) == sorted(['g', '_h'])

    print('-' * 20)

    it = manager.baz()
    dla i w it:
        print('<%d>' % i, end=' ')
    print()

    print('-' * 20)

    op = manager.operator()
    print('op.add(23, 45) =', op.add(23, 45))
    print('op.pow(2, 94) =', op.pow(2, 94))
    print('op._exposed_ =', op._exposed_)

##

jeżeli __name__ == '__main__':
    freeze_support()
    test()
