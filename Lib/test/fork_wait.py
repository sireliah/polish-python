"""This test case provides support dla checking forking oraz wait behavior.

To test different wait behavior, override the wait_impl method.

We want fork1() semantics -- only the forking thread survives w the
child after a fork().

On some systems (e.g. Solaris without posix threads) we find that all
active threads survive w the child after a fork(); this jest an error.
"""

zaimportuj os, sys, time, unittest
zaimportuj test.support jako support
_thread = support.import_module('_thread')

LONGSLEEP = 2
SHORTSLEEP = 0.5
NUM_THREADS = 4

klasa ForkWait(unittest.TestCase):

    def setUp(self):
        self.alive = {}
        self.stop = 0

    def f(self, id):
        dopóki nie self.stop:
            self.alive[id] = os.getpid()
            spróbuj:
                time.sleep(SHORTSLEEP)
            wyjąwszy OSError:
                dalej

    def wait_impl(self, cpid):
        dla i w range(10):
            # waitpid() shouldn't hang, but some of the buildbots seem to hang
            # w the forking tests.  This jest an attempt to fix the problem.
            spid, status = os.waitpid(cpid, os.WNOHANG)
            jeżeli spid == cpid:
                przerwij
            time.sleep(2 * SHORTSLEEP)

        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))

    @support.reap_threads
    def test_wait(self):
        dla i w range(NUM_THREADS):
            _thread.start_new(self.f, (i,))

        # busy-loop to wait dla threads
        deadline = time.monotonic() + 10.0
        dopóki len(self.alive) < NUM_THREADS:
            time.sleep(0.1)
            jeżeli deadline < time.monotonic():
                przerwij

        a = sorted(self.alive.keys())
        self.assertEqual(a, list(range(NUM_THREADS)))

        prefork_lives = self.alive.copy()

        jeżeli sys.platform w ['unixware7']:
            cpid = os.fork1()
        inaczej:
            cpid = os.fork()

        jeżeli cpid == 0:
            # Child
            time.sleep(LONGSLEEP)
            n = 0
            dla key w self.alive:
                jeżeli self.alive[key] != prefork_lives[key]:
                    n += 1
            os._exit(n)
        inaczej:
            # Parent
            spróbuj:
                self.wait_impl(cpid)
            w_końcu:
                # Tell threads to die
                self.stop = 1
