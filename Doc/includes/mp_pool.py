zaimportuj multiprocessing
zaimportuj time
zaimportuj random
zaimportuj sys

#
# Functions used by test code
#

def calculate(func, args):
    result = func(*args)
    zwróć '%s says that %s%s = %s' % (
        multiprocessing.current_process().name,
        func.__name__, args, result
        )

def calculatestar(args):
    zwróć calculate(*args)

def mul(a, b):
    time.sleep(0.5 * random.random())
    zwróć a * b

def plus(a, b):
    time.sleep(0.5 * random.random())
    zwróć a + b

def f(x):
    zwróć 1.0 / (x - 5.0)

def pow3(x):
    zwróć x ** 3

def noop(x):
    dalej

#
# Test code
#

def test():
    PROCESSES = 4
    print('Creating pool przy %d processes\n' % PROCESSES)

    przy multiprocessing.Pool(PROCESSES) jako pool:
        #
        # Tests
        #

        TASKS = [(mul, (i, 7)) dla i w range(10)] + \
                [(plus, (i, 8)) dla i w range(10)]

        results = [pool.apply_async(calculate, t) dla t w TASKS]
        imap_it = pool.imap(calculatestar, TASKS)
        imap_unordered_it = pool.imap_unordered(calculatestar, TASKS)

        print('Ordered results using pool.apply_async():')
        dla r w results:
            print('\t', r.get())
        print()

        print('Ordered results using pool.imap():')
        dla x w imap_it:
            print('\t', x)
        print()

        print('Unordered results using pool.imap_unordered():')
        dla x w imap_unordered_it:
            print('\t', x)
        print()

        print('Ordered results using pool.map() --- will block till complete:')
        dla x w pool.map(calculatestar, TASKS):
            print('\t', x)
        print()

        #
        # Test error handling
        #

        print('Testing error handling:')

        spróbuj:
            print(pool.apply(f, (5,)))
        wyjąwszy ZeroDivisionError:
            print('\tGot ZeroDivisionError jako expected z pool.apply()')
        inaczej:
            podnieś AssertionError('expected ZeroDivisionError')

        spróbuj:
            print(pool.map(f, list(range(10))))
        wyjąwszy ZeroDivisionError:
            print('\tGot ZeroDivisionError jako expected z pool.map()')
        inaczej:
            podnieś AssertionError('expected ZeroDivisionError')

        spróbuj:
            print(list(pool.imap(f, list(range(10)))))
        wyjąwszy ZeroDivisionError:
            print('\tGot ZeroDivisionError jako expected z list(pool.imap())')
        inaczej:
            podnieś AssertionError('expected ZeroDivisionError')

        it = pool.imap(f, list(range(10)))
        dla i w range(10):
            spróbuj:
                x = next(it)
            wyjąwszy ZeroDivisionError:
                jeżeli i == 5:
                    dalej
            wyjąwszy StopIteration:
                przerwij
            inaczej:
                jeżeli i == 5:
                    podnieś AssertionError('expected ZeroDivisionError')

        assert i == 9
        print('\tGot ZeroDivisionError jako expected z IMapIterator.next()')
        print()

        #
        # Testing timeouts
        #

        print('Testing ApplyResult.get() przy timeout:', end=' ')
        res = pool.apply_async(calculate, TASKS[0])
        dopóki 1:
            sys.stdout.flush()
            spróbuj:
                sys.stdout.write('\n\t%s' % res.get(0.02))
                przerwij
            wyjąwszy multiprocessing.TimeoutError:
                sys.stdout.write('.')
        print()
        print()

        print('Testing IMapIterator.next() przy timeout:', end=' ')
        it = pool.imap(calculatestar, TASKS)
        dopóki 1:
            sys.stdout.flush()
            spróbuj:
                sys.stdout.write('\n\t%s' % it.next(0.02))
            wyjąwszy StopIteration:
                przerwij
            wyjąwszy multiprocessing.TimeoutError:
                sys.stdout.write('.')
        print()
        print()


jeżeli __name__ == '__main__':
    multiprocessing.freeze_support()
    test()
