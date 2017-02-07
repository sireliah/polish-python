"""This test checks dla correct wait4() behavior.
"""

zaimportuj os
zaimportuj time
zaimportuj sys
z test.fork_wait zaimportuj ForkWait
z test.support zaimportuj reap_children, get_attribute

# If either of these do nie exist, skip this test.
get_attribute(os, 'fork')
get_attribute(os, 'wait4')


klasa Wait4Test(ForkWait):
    def wait_impl(self, cpid):
        option = os.WNOHANG
        jeżeli sys.platform.startswith('aix'):
            # Issue #11185: wait4 jest broken on AIX oraz will always zwróć 0
            # przy WNOHANG.
            option = 0
        deadline = time.monotonic() + 10.0
        dopóki time.monotonic() <= deadline:
            # wait4() shouldn't hang, but some of the buildbots seem to hang
            # w the forking tests.  This jest an attempt to fix the problem.
            spid, status, rusage = os.wait4(cpid, option)
            jeżeli spid == cpid:
                przerwij
            time.sleep(0.1)
        self.assertEqual(spid, cpid)
        self.assertEqual(status, 0, "cause = %d, exit = %d" % (status&0xff, status>>8))
        self.assertPrawda(rusage)

def tearDownModule():
    reap_children()

jeżeli __name__ == "__main__":
    unittest.main()
