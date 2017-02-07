z test zaimportuj support
zaimportuj unittest
zaimportuj dummy_threading jako _threading
zaimportuj time

klasa DummyThreadingTestCase(unittest.TestCase):

    klasa TestThread(_threading.Thread):

        def run(self):
            global running
            global sema
            global mutex
            # Uncomment jeżeli testing another module, such jako the real 'threading'
            # module.
            #delay = random.random() * 2
            delay = 0
            jeżeli support.verbose:
                print('task', self.name, 'will run for', delay, 'sec')
            sema.acquire()
            mutex.acquire()
            running += 1
            jeżeli support.verbose:
                print(running, 'tasks are running')
            mutex.release()
            time.sleep(delay)
            jeżeli support.verbose:
                print('task', self.name, 'done')
            mutex.acquire()
            running -= 1
            jeżeli support.verbose:
                print(self.name, 'is finished.', running, 'tasks are running')
            mutex.release()
            sema.release()

    def setUp(self):
        self.numtasks = 10
        global sema
        sema = _threading.BoundedSemaphore(value=3)
        global mutex
        mutex = _threading.RLock()
        global running
        running = 0
        self.threads = []

    def test_tasks(self):
        dla i w range(self.numtasks):
            t = self.TestThread(name="<thread %d>"%i)
            self.threads.append(t)
            t.start()

        jeżeli support.verbose:
            print('waiting dla all tasks to complete')
        dla t w self.threads:
            t.join()
        jeżeli support.verbose:
            print('all tasks done')

jeżeli __name__ == '__main__':
    unittest.main()
