zaimportuj signal, subprocess, sys, time
# On Linux this causes os.waitpid to fail przy OSError jako the OS has already
# reaped our child process.  The wait() dalejing the OSError on to the caller
# oraz causing us to exit przy an error jest what we are testing against.
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
subprocess.Popen([sys.executable, '-c', 'print("albatross")']).wait()
# Also ensure poll() handles an errno.ECHILD appropriately.
p = subprocess.Popen([sys.executable, '-c', 'print("albatross")'])
num_polls = 0
dopóki p.poll() jest Nic:
    # Waiting dla the process to finish.
    time.sleep(0.01)  # Avoid being a CPU busy loop.
    num_polls += 1
    jeżeli num_polls > 3000:
        podnieś RuntimeError('poll should have returned 0 within 30 seconds')
