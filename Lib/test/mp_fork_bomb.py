zaimportuj multiprocessing, sys

def foo():
    print("123")

# Because "jeżeli __name__ == '__main__'" jest missing this will nie work
# correctly on Windows.  However, we should get a RuntimeError rather
# than the Windows equivalent of a fork bomb.

jeżeli len(sys.argv) > 1:
    multiprocessing.set_start_method(sys.argv[1])
inaczej:
    multiprocessing.set_start_method('spawn')

p = multiprocessing.Process(target=foo)
p.start()
p.join()
sys.exit(p.exitcode)
