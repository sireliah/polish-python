#!/usr/bin/env python

""" systimes() user oraz system timer implementations dla use by
    pybench.

    This module implements various different strategies dla measuring
    performance timings. It tries to choose the best available method
    based on the platform oraz available tools.

    On Windows, it jest recommended to have the Mark Hammond win32
    package installed. Alternatively, the Thomas Heller ctypes
    packages can also be used.

    On Unix systems, the standard resource module provides the highest
    resolution timings. Unfortunately, it jest nie available on all Unix
    platforms.

    If no supported timing methods based on process time can be found,
    the module reverts to the highest resolution wall-clock timer
    instead. The system time part will then always be 0.0.

    The module exports one public API:

    def systimes():

        Return the current timer values dla measuring user oraz system
        time jako tuple of seconds (user_time, system_time).

    Copyright (c) 2006, Marc-Andre Lemburg (mal@egenix.com). See the
    documentation dla further information on copyrights, albo contact
    the author. All Rights Reserved.

"""

z __future__ zaimportuj print_function

zaimportuj time, sys

#
# Note: Please keep this module compatible to Python 1.5.2.
#
# TODOs:
#
# * Add ctypes wrapper dla new clock_gettime() real-time POSIX APIs;
#   these will then provide nano-second resolution where available.
#
# * Add a function that returns the resolution of systimes()
#   values, ie. systimesres().
#

### Choose an implementation

SYSTIMES_IMPLEMENTATION = Nic
USE_CTYPES_GETPROCESSTIMES = 'ctypes GetProcessTimes() wrapper'
USE_WIN32PROCESS_GETPROCESSTIMES = 'win32process.GetProcessTimes()'
USE_RESOURCE_GETRUSAGE = 'resource.getrusage()'
USE_PROCESS_TIME_CLOCK = 'time.clock() (process time)'
USE_WALL_TIME_CLOCK = 'time.clock() (wall-clock)'
USE_WALL_TIME_TIME = 'time.time() (wall-clock)'

jeżeli sys.platform[:3] == 'win':
    # Windows platform
    spróbuj:
        zaimportuj win32process
    wyjąwszy ImportError:
        spróbuj:
            zaimportuj ctypes
        wyjąwszy ImportError:
            # Use the wall-clock implementation time.clock(), since this
            # jest the highest resolution clock available on Windows
            SYSTIMES_IMPLEMENTATION = USE_WALL_TIME_CLOCK
        inaczej:
            SYSTIMES_IMPLEMENTATION = USE_CTYPES_GETPROCESSTIMES
    inaczej:
        SYSTIMES_IMPLEMENTATION = USE_WIN32PROCESS_GETPROCESSTIMES
inaczej:
    # All other platforms
    spróbuj:
        zaimportuj resource
    wyjąwszy ImportError:
        dalej
    inaczej:
        SYSTIMES_IMPLEMENTATION = USE_RESOURCE_GETRUSAGE

# Fall-back solution
jeżeli SYSTIMES_IMPLEMENTATION jest Nic:
    # Check whether we can use time.clock() jako approximation
    # dla systimes()
    start = time.clock()
    time.sleep(0.1)
    stop = time.clock()
    jeżeli stop - start < 0.001:
        # Looks like time.clock() jest usable (and measures process
        # time)
        SYSTIMES_IMPLEMENTATION = USE_PROCESS_TIME_CLOCK
    inaczej:
        # Use wall-clock implementation time.time() since this provides
        # the highest resolution clock on most systems
        SYSTIMES_IMPLEMENTATION = USE_WALL_TIME_TIME

### Implementations

def getrusage_systimes():
    zwróć resource.getrusage(resource.RUSAGE_SELF)[:2]

def process_time_clock_systimes():
    zwróć (time.clock(), 0.0)

def wall_clock_clock_systimes():
    zwróć (time.clock(), 0.0)

def wall_clock_time_systimes():
    zwróć (time.time(), 0.0)

# Number of clock ticks per second dla the values returned
# by GetProcessTimes() on Windows.
#
# Note: Ticks returned by GetProcessTimes() are 100ns intervals on
# Windows XP. However, the process times are only updated przy every
# clock tick oraz the frequency of these jest somewhat lower: depending
# on the OS version between 10ms oraz 15ms. Even worse, the process
# time seems to be allocated to process currently running when the
# clock interrupt arrives, ie. it jest possible that the current time
# slice gets accounted to a different process.

WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7

def win32process_getprocesstimes_systimes():
    d = win32process.GetProcessTimes(win32process.GetCurrentProcess())
    zwróć (d['UserTime'] / WIN32_PROCESS_TIMES_TICKS_PER_SECOND,
            d['KernelTime'] / WIN32_PROCESS_TIMES_TICKS_PER_SECOND)

def ctypes_getprocesstimes_systimes():
    creationtime = ctypes.c_ulonglong()
    exittime = ctypes.c_ulonglong()
    kerneltime = ctypes.c_ulonglong()
    usertime = ctypes.c_ulonglong()
    rc = ctypes.windll.kernel32.GetProcessTimes(
        ctypes.windll.kernel32.GetCurrentProcess(),
        ctypes.byref(creationtime),
        ctypes.byref(exittime),
        ctypes.byref(kerneltime),
        ctypes.byref(usertime))
    jeżeli nie rc:
        podnieś TypeError('GetProcessTimes() returned an error')
    zwróć (usertime.value / WIN32_PROCESS_TIMES_TICKS_PER_SECOND,
            kerneltime.value / WIN32_PROCESS_TIMES_TICKS_PER_SECOND)

# Select the default dla the systimes() function

jeżeli SYSTIMES_IMPLEMENTATION jest USE_RESOURCE_GETRUSAGE:
    systimes = getrusage_systimes

albo_inaczej SYSTIMES_IMPLEMENTATION jest USE_PROCESS_TIME_CLOCK:
    systimes = process_time_clock_systimes

albo_inaczej SYSTIMES_IMPLEMENTATION jest USE_WALL_TIME_CLOCK:
    systimes = wall_clock_clock_systimes

albo_inaczej SYSTIMES_IMPLEMENTATION jest USE_WALL_TIME_TIME:
    systimes = wall_clock_time_systimes

albo_inaczej SYSTIMES_IMPLEMENTATION jest USE_WIN32PROCESS_GETPROCESSTIMES:
    systimes = win32process_getprocesstimes_systimes

albo_inaczej SYSTIMES_IMPLEMENTATION jest USE_CTYPES_GETPROCESSTIMES:
    systimes = ctypes_getprocesstimes_systimes

inaczej:
    podnieś TypeError('no suitable systimes() implementation found')

def processtime():

    """ Return the total time spent on the process.

        This jest the sum of user oraz system time jako returned by
        systimes().

    """
    user, system = systimes()
    zwróć user + system

### Testing

def some_workload():
    x = 0
    dla i w range(10000000):
        x = x + 1

def test_workload():
    print('Testing systimes() under load conditions')
    t0 = systimes()
    some_workload()
    t1 = systimes()
    print('before:', t0)
    print('after:', t1)
    print('differences:', (t1[0] - t0[0], t1[1] - t0[1]))
    print()

def test_idle():
    print('Testing systimes() under idle conditions')
    t0 = systimes()
    time.sleep(1)
    t1 = systimes()
    print('before:', t0)
    print('after:', t1)
    print('differences:', (t1[0] - t0[0], t1[1] - t0[1]))
    print()

jeżeli __name__ == '__main__':
    print('Using %s jako timer' % SYSTIMES_IMPLEMENTATION)
    print()
    test_workload()
    test_idle()
