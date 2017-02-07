# This file should be kept compatible przy both Python 2.6 oraz Python >= 3.0.

z __future__ zaimportuj division
z __future__ zaimportuj print_function

"""
ccbench, a Python concurrency benchmark.
"""

zaimportuj time
zaimportuj os
zaimportuj sys
zaimportuj itertools
zaimportuj threading
zaimportuj subprocess
zaimportuj socket
z optparse zaimportuj OptionParser, SUPPRESS_HELP
zaimportuj platform

# Compatibility
spróbuj:
    xrange
wyjąwszy NameError:
    xrange = range

spróbuj:
    map = itertools.imap
wyjąwszy AttributeError:
    dalej


THROUGHPUT_DURATION = 2.0

LATENCY_PING_INTERVAL = 0.1
LATENCY_DURATION = 2.0

BANDWIDTH_PACKET_SIZE = 1024
BANDWIDTH_DURATION = 2.0


def task_pidigits():
    """Pi calculation (Python)"""
    _map = map
    _count = itertools.count
    _islice = itertools.islice

    def calc_ndigits(n):
        # From http://shootout.alioth.debian.org/
        def gen_x():
            zwróć _map(lambda k: (k, 4*k + 2, 0, 2*k + 1), _count(1))

        def compose(a, b):
            aq, ar, as_, at = a
            bq, br, bs, bt = b
            zwróć (aq * bq,
                    aq * br + ar * bt,
                    as_ * bq + at * bs,
                    as_ * br + at * bt)

        def extract(z, j):
            q, r, s, t = z
            zwróć (q*j + r) // (s*j + t)

        def pi_digits():
            z = (1, 0, 0, 1)
            x = gen_x()
            dopóki 1:
                y = extract(z, 3)
                dopóki y != extract(z, 4):
                    z = compose(z, next(x))
                    y = extract(z, 3)
                z = compose((10, -10*y, 0, 1), z)
                uzyskaj y

        zwróć list(_islice(pi_digits(), n))

    zwróć calc_ndigits, (50, )

def task_regex():
    """regular expression (C)"""
    # XXX this task gives horrendous latency results.
    zaimportuj re
    # Taken z the `inspect` module
    pat = re.compile(r'^(\s*def\s)|(.*(?<!\w)lambda(:|\s))|^(\s*@)', re.MULTILINE)
    przy open(__file__, "r") jako f:
        arg = f.read(2000)

    def findall(s):
        t = time.time()
        spróbuj:
            zwróć pat.findall(s)
        w_końcu:
            print(time.time() - t)
    zwróć pat.findall, (arg, )

def task_sort():
    """list sorting (C)"""
    def list_sort(l):
        l = l[::-1]
        l.sort()

    zwróć list_sort, (list(range(1000)), )

def task_compress_zlib():
    """zlib compression (C)"""
    zaimportuj zlib
    przy open(__file__, "rb") jako f:
        arg = f.read(5000) * 3

    def compress(s):
        zlib.decompress(zlib.compress(s, 5))
    zwróć compress, (arg, )

def task_compress_bz2():
    """bz2 compression (C)"""
    zaimportuj bz2
    przy open(__file__, "rb") jako f:
        arg = f.read(3000) * 2

    def compress(s):
        bz2.compress(s)
    zwróć compress, (arg, )

def task_hashing():
    """SHA1 hashing (C)"""
    zaimportuj hashlib
    przy open(__file__, "rb") jako f:
        arg = f.read(5000) * 30

    def compute(s):
        hashlib.sha1(s).digest()
    zwróć compute, (arg, )


throughput_tasks = [task_pidigits, task_regex]
dla mod w 'bz2', 'hashlib':
    spróbuj:
        globals()[mod] = __import__(mod)
    wyjąwszy ImportError:
        globals()[mod] = Nic

# For whatever reasons, zlib gives irregular results, so we prefer bz2 albo
# hashlib jeżeli available.
# (NOTE: hashlib releases the GIL z 2.7 oraz 3.1 onwards)
jeżeli bz2 jest nie Nic:
    throughput_tasks.append(task_compress_bz2)
albo_inaczej hashlib jest nie Nic:
    throughput_tasks.append(task_hashing)
inaczej:
    throughput_tasks.append(task_compress_zlib)

latency_tasks = throughput_tasks
bandwidth_tasks = [task_pidigits]


klasa TimedLoop:
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __call__(self, start_time, min_duration, end_event, do_uzyskaj=Nieprawda):
        step = 20
        niters = 0
        duration = 0.0
        _time = time.time
        _sleep = time.sleep
        _func = self.func
        _args = self.args
        t1 = start_time
        dopóki Prawda:
            dla i w range(step):
                _func(*_args)
            t2 = _time()
            # If another thread terminated, the current measurement jest invalid
            # => zwróć the previous one.
            jeżeli end_event:
                zwróć niters, duration
            niters += step
            duration = t2 - start_time
            jeżeli duration >= min_duration:
                end_event.append(Nic)
                zwróć niters, duration
            jeżeli t2 - t1 < 0.01:
                # Minimize interference of measurement on overall runtime
                step = step * 3 // 2
            albo_inaczej do_uzyskaj:
                # OS scheduling of Python threads jest sometimes so bad that we
                # have to force thread switching ourselves, otherwise we get
                # completely useless results.
                _sleep(0.0001)
            t1 = t2


def run_throughput_test(func, args, nthreads):
    assert nthreads >= 1

    # Warm up
    func(*args)

    results = []
    loop = TimedLoop(func, args)
    end_event = []

    jeżeli nthreads == 1:
        # Pure single-threaded performance, without any switching albo
        # synchronization overhead.
        start_time = time.time()
        results.append(loop(start_time, THROUGHPUT_DURATION,
                            end_event, do_uzyskaj=Nieprawda))
        zwróć results

    started = Nieprawda
    ready_cond = threading.Condition()
    start_cond = threading.Condition()
    ready = []

    def run():
        przy ready_cond:
            ready.append(Nic)
            ready_cond.notify()
        przy start_cond:
            dopóki nie started:
                start_cond.wait()
        results.append(loop(start_time, THROUGHPUT_DURATION,
                            end_event, do_uzyskaj=Prawda))

    threads = []
    dla i w range(nthreads):
        threads.append(threading.Thread(target=run))
    dla t w threads:
        t.setDaemon(Prawda)
        t.start()
    # We don't want measurements to include thread startup overhead,
    # so we arrange dla timing to start after all threads are ready.
    przy ready_cond:
        dopóki len(ready) < nthreads:
            ready_cond.wait()
    przy start_cond:
        start_time = time.time()
        started = Prawda
        start_cond.notify(nthreads)
    dla t w threads:
        t.join()

    zwróć results

def run_throughput_tests(max_threads):
    dla task w throughput_tasks:
        print(task.__doc__)
        print()
        func, args = task()
        nthreads = 1
        baseline_speed = Nic
        dopóki nthreads <= max_threads:
            results = run_throughput_test(func, args, nthreads)
            # Taking the max duration rather than average gives pessimistic
            # results rather than optimistic.
            speed = sum(r[0] dla r w results) / max(r[1] dla r w results)
            print("threads=%d: %d" % (nthreads, speed), end="")
            jeżeli baseline_speed jest Nic:
                print(" iterations/s.")
                baseline_speed = speed
            inaczej:
                print(" ( %d %%)" % (speed / baseline_speed * 100))
            nthreads += 1
        print()


LAT_END = "END"

def _sendto(sock, s, addr):
    sock.sendto(s.encode('ascii'), addr)

def _recv(sock, n):
    zwróć sock.recv(n).decode('ascii')

def latency_client(addr, nb_pings, interval):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spróbuj:
        _time = time.time
        _sleep = time.sleep
        def _ping():
            _sendto(sock, "%r\n" % _time(), addr)
        # The first ping signals the parent process that we are ready.
        _ping()
        # We give the parent a bit of time to notice.
        _sleep(1.0)
        dla i w range(nb_pings):
            _sleep(interval)
            _ping()
        _sendto(sock, LAT_END + "\n", addr)
    w_końcu:
        sock.close()

def run_latency_client(**kwargs):
    cmd_line = [sys.executable, '-E', os.path.abspath(__file__)]
    cmd_line.extend(['--latclient', repr(kwargs)])
    zwróć subprocess.Popen(cmd_line) #, stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def run_latency_test(func, args, nthreads):
    # Create a listening socket to receive the pings. We use UDP which should
    # be painlessly cross-platform.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    addr = sock.getsockname()

    interval = LATENCY_PING_INTERVAL
    duration = LATENCY_DURATION
    nb_pings = int(duration / interval)

    results = []
    threads = []
    end_event = []
    start_cond = threading.Condition()
    started = Nieprawda
    jeżeli nthreads > 0:
        # Warm up
        func(*args)

        results = []
        loop = TimedLoop(func, args)
        ready = []
        ready_cond = threading.Condition()

        def run():
            przy ready_cond:
                ready.append(Nic)
                ready_cond.notify()
            przy start_cond:
                dopóki nie started:
                    start_cond.wait()
            loop(start_time, duration * 1.5, end_event, do_uzyskaj=Nieprawda)

        dla i w range(nthreads):
            threads.append(threading.Thread(target=run))
        dla t w threads:
            t.setDaemon(Prawda)
            t.start()
        # Wait dla threads to be ready
        przy ready_cond:
            dopóki len(ready) < nthreads:
                ready_cond.wait()

    # Run the client oraz wait dla the first ping(s) to arrive before
    # unblocking the background threads.
    chunks = []
    process = run_latency_client(addr=sock.getsockname(),
                                 nb_pings=nb_pings, interval=interval)
    s = _recv(sock, 4096)
    _time = time.time

    przy start_cond:
        start_time = _time()
        started = Prawda
        start_cond.notify(nthreads)

    dopóki LAT_END nie w s:
        s = _recv(sock, 4096)
        t = _time()
        chunks.append((t, s))

    # Tell the background threads to stop.
    end_event.append(Nic)
    dla t w threads:
        t.join()
    process.wait()
    sock.close()

    dla recv_time, chunk w chunks:
        # NOTE: it jest assumed that a line sent by a client wasn't received
        # w two chunks because the lines are very small.
        dla line w chunk.splitlines():
            line = line.strip()
            jeżeli line oraz line != LAT_END:
                send_time = eval(line)
                assert isinstance(send_time, float)
                results.append((send_time, recv_time))

    zwróć results

def run_latency_tests(max_threads):
    dla task w latency_tasks:
        print("Background CPU task:", task.__doc__)
        print()
        func, args = task()
        nthreads = 0
        dopóki nthreads <= max_threads:
            results = run_latency_test(func, args, nthreads)
            n = len(results)
            # We print out milliseconds
            lats = [1000 * (t2 - t1) dla (t1, t2) w results]
            #print(list(map(int, lats)))
            avg = sum(lats) / n
            dev = (sum((x - avg) ** 2 dla x w lats) / n) ** 0.5
            print("CPU threads=%d: %d ms. (std dev: %d ms.)" % (nthreads, avg, dev), end="")
            print()
            #print("    [... z %d samples]" % n)
            nthreads += 1
        print()


BW_END = "END"

def bandwidth_client(addr, packet_size, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    local_addr = sock.getsockname()
    _time = time.time
    _sleep = time.sleep
    def _send_chunk(msg):
        _sendto(sock, ("%r#%s\n" % (local_addr, msg)).rjust(packet_size), addr)
    # We give the parent some time to be ready.
    _sleep(1.0)
    spróbuj:
        start_time = _time()
        end_time = start_time + duration * 2.0
        i = 0
        dopóki _time() < end_time:
            _send_chunk(str(i))
            s = _recv(sock, packet_size)
            assert len(s) == packet_size
            i += 1
        _send_chunk(BW_END)
    w_końcu:
        sock.close()

def run_bandwidth_client(**kwargs):
    cmd_line = [sys.executable, '-E', os.path.abspath(__file__)]
    cmd_line.extend(['--bwclient', repr(kwargs)])
    zwróć subprocess.Popen(cmd_line) #, stdin=subprocess.PIPE,
                            #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def run_bandwidth_test(func, args, nthreads):
    # Create a listening socket to receive the packets. We use UDP which should
    # be painlessly cross-platform.
    przy socket.socket(socket.AF_INET, socket.SOCK_DGRAM) jako sock:
        sock.bind(("127.0.0.1", 0))
        addr = sock.getsockname()

        duration = BANDWIDTH_DURATION
        packet_size = BANDWIDTH_PACKET_SIZE

        results = []
        threads = []
        end_event = []
        start_cond = threading.Condition()
        started = Nieprawda
        jeżeli nthreads > 0:
            # Warm up
            func(*args)

            results = []
            loop = TimedLoop(func, args)
            ready = []
            ready_cond = threading.Condition()

            def run():
                przy ready_cond:
                    ready.append(Nic)
                    ready_cond.notify()
                przy start_cond:
                    dopóki nie started:
                        start_cond.wait()
                loop(start_time, duration * 1.5, end_event, do_uzyskaj=Nieprawda)

            dla i w range(nthreads):
                threads.append(threading.Thread(target=run))
            dla t w threads:
                t.setDaemon(Prawda)
                t.start()
            # Wait dla threads to be ready
            przy ready_cond:
                dopóki len(ready) < nthreads:
                    ready_cond.wait()

        # Run the client oraz wait dla the first packet to arrive before
        # unblocking the background threads.
        process = run_bandwidth_client(addr=addr,
                                       packet_size=packet_size,
                                       duration=duration)
        _time = time.time
        # This will also wait dla the parent to be ready
        s = _recv(sock, packet_size)
        remote_addr = eval(s.partition('#')[0])

        przy start_cond:
            start_time = _time()
            started = Prawda
            start_cond.notify(nthreads)

        n = 0
        first_time = Nic
        dopóki nie end_event oraz BW_END nie w s:
            _sendto(sock, s, remote_addr)
            s = _recv(sock, packet_size)
            jeżeli first_time jest Nic:
                first_time = _time()
            n += 1
        end_time = _time()

    end_event.append(Nic)
    dla t w threads:
        t.join()
    process.kill()

    zwróć (n - 1) / (end_time - first_time)

def run_bandwidth_tests(max_threads):
    dla task w bandwidth_tasks:
        print("Background CPU task:", task.__doc__)
        print()
        func, args = task()
        nthreads = 0
        baseline_speed = Nic
        dopóki nthreads <= max_threads:
            results = run_bandwidth_test(func, args, nthreads)
            speed = results
            #speed = len(results) * 1.0 / results[-1][0]
            print("CPU threads=%d: %.1f" % (nthreads, speed), end="")
            jeżeli baseline_speed jest Nic:
                print(" packets/s.")
                baseline_speed = speed
            inaczej:
                print(" ( %d %%)" % (speed / baseline_speed * 100))
            nthreads += 1
        print()


def main():
    usage = "usage: %prog [-h|--help] [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--throughput",
                      action="store_true", dest="throughput", default=Nieprawda,
                      help="run throughput tests")
    parser.add_option("-l", "--latency",
                      action="store_true", dest="latency", default=Nieprawda,
                      help="run latency tests")
    parser.add_option("-b", "--bandwidth",
                      action="store_true", dest="bandwidth", default=Nieprawda,
                      help="run I/O bandwidth tests")
    parser.add_option("-i", "--interval",
                      action="store", type="int", dest="check_interval", default=Nic,
                      help="sys.setcheckinterval() value")
    parser.add_option("-I", "--switch-interval",
                      action="store", type="float", dest="switch_interval", default=Nic,
                      help="sys.setswitchinterval() value")
    parser.add_option("-n", "--num-threads",
                      action="store", type="int", dest="nthreads", default=4,
                      help="max number of threads w tests")

    # Hidden option to run the pinging oraz bandwidth clients
    parser.add_option("", "--latclient",
                      action="store", dest="latclient", default=Nic,
                      help=SUPPRESS_HELP)
    parser.add_option("", "--bwclient",
                      action="store", dest="bwclient", default=Nic,
                      help=SUPPRESS_HELP)

    options, args = parser.parse_args()
    jeżeli args:
        parser.error("unexpected arguments")

    jeżeli options.latclient:
        kwargs = eval(options.latclient)
        latency_client(**kwargs)
        zwróć

    jeżeli options.bwclient:
        kwargs = eval(options.bwclient)
        bandwidth_client(**kwargs)
        zwróć

    jeżeli nie options.throughput oraz nie options.latency oraz nie options.bandwidth:
        options.throughput = options.latency = options.bandwidth = Prawda
    jeżeli options.check_interval:
        sys.setcheckinterval(options.check_interval)
    jeżeli options.switch_interval:
        sys.setswitchinterval(options.switch_interval)

    print("== %s %s (%s) ==" % (
        platform.python_implementation(),
        platform.python_version(),
        platform.python_build()[0],
    ))
    # Processor identification often has repeated spaces
    cpu = ' '.join(platform.processor().split())
    print("== %s %s on '%s' ==" % (
        platform.machine(),
        platform.system(),
        cpu,
    ))
    print()

    jeżeli options.throughput:
        print("--- Throughput ---")
        print()
        run_throughput_tests(options.nthreads)

    jeżeli options.latency:
        print("--- Latency ---")
        print()
        run_latency_tests(options.nthreads)

    jeżeli options.bandwidth:
        print("--- I/O bandwidth ---")
        print()
        run_bandwidth_tests(options.nthreads)

jeżeli __name__ == "__main__":
    main()
