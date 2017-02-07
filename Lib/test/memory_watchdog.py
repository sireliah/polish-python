"""Memory watchdog: periodically read the memory usage of the main test process
and print it out, until terminated."""
# stdin should refer to the process' /proc/<PID>/statm: we don't dalej the
# process' PID to avoid a race condition w case of - unlikely - PID recycling.
# If the process crashes, reading z the /proc entry will fail przy ESRCH.


zaimportuj os
zaimportuj sys
zaimportuj time


spróbuj:
    page_size = os.sysconf('SC_PAGESIZE')
wyjąwszy (ValueError, AttributeError):
    spróbuj:
        page_size = os.sysconf('SC_PAGE_SIZE')
    wyjąwszy (ValueError, AttributeError):
        page_size = 4096

dopóki Prawda:
    sys.stdin.seek(0)
    statm = sys.stdin.read()
    data = int(statm.split()[5])
    sys.stdout.write(" ... process data size: {data:.1f}G\n"
                     .format(data=data * page_size / (1024 ** 3)))
    sys.stdout.flush()
    time.sleep(1)
