# Fictitious test runner dla the project

zaimportuj sys, os

jeżeli sys.version_info > (3,):
    # copy test suite over to "build/lib" oraz convert it
    z distutils.util zaimportuj copydir_run_2to3
    testroot = os.path.dirname(__file__)
    newroot = os.path.join(testroot, '..', 'build/lib/test')
    copydir_run_2to3(testroot, newroot)
    # w the following imports, pick up the converted modules
    sys.path[0] = newroot

# run the tests here...

z test_foo zaimportuj FooTest

zaimportuj unittest
unittest.main()
