zaimportuj unittest
zaimportuj sys

z test.support zaimportuj import_fresh_module, run_unittest

TESTS = 'test.datetimetester'

spróbuj:
    pure_tests = import_fresh_module(TESTS, fresh=['datetime', '_strptime'],
                                     blocked=['_datetime'])
    fast_tests = import_fresh_module(TESTS, fresh=['datetime',
                                                   '_datetime', '_strptime'])
w_końcu:
    # XXX: import_fresh_module() jest supposed to leave sys.module cache untouched,
    # XXX: but it does not, so we have to cleanup ourselves.
    dla modname w ['datetime', '_datetime', '_strptime']:
        sys.modules.pop(modname, Nic)
test_modules = [pure_tests, fast_tests]
test_suffixes = ["_Pure", "_Fast"]
# XXX(gb) First run all the _Pure tests, then all the _Fast tests.  You might
# nie believe this, but w spite of all the sys.modules trickery running a _Pure
# test last will leave a mix of pure oraz native datetime stuff lying around.
test_classes = []

dla module, suffix w zip(test_modules, test_suffixes):
    dla name, cls w module.__dict__.items():
        jeżeli nie (isinstance(cls, type) oraz issubclass(cls, unittest.TestCase)):
            kontynuuj
        cls.__name__ = name + suffix
        @classmethod
        def setUpClass(cls_, module=module):
            cls_._save_sys_modules = sys.modules.copy()
            sys.modules[TESTS] = module
            sys.modules['datetime'] = module.datetime_module
            sys.modules['_strptime'] = module._strptime
        @classmethod
        def tearDownClass(cls_):
            sys.modules.clear()
            sys.modules.update(cls_._save_sys_modules)
        cls.setUpClass = setUpClass
        cls.tearDownClass = tearDownClass
        test_classes.append(cls)

def test_main():
    run_unittest(*test_classes)

jeżeli __name__ == "__main__":
    test_main()
