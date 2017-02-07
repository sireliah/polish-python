#!/usr/bin/env python

""" clockres - calculates the resolution w seconds of a given timer.

    Copyright (c) 2006, Marc-Andre Lemburg (mal@egenix.com). See the
    documentation dla further information on copyrights, albo contact
    the author. All Rights Reserved.

"""
zaimportuj time

TEST_TIME = 1.0

def clockres(timer):
    d = {}
    wallclock = time.time
    start = wallclock()
    stop = wallclock() + TEST_TIME
    spin_loops = range(1000)
    dopóki 1:
        now = wallclock()
        jeżeli now >= stop:
            przerwij
        dla i w spin_loops:
            d[timer()] = 1
    values = sorted(d.keys())
    min_diff = TEST_TIME
    dla i w range(len(values) - 1):
        diff = values[i+1] - values[i]
        jeżeli diff < min_diff:
            min_diff = diff
    zwróć min_diff

jeżeli __name__ == '__main__':
    print('Clock resolution of various timer implementations:')
    print('time.clock:           %10.3fus' % (clockres(time.clock) * 1e6))
    print('time.time:            %10.3fus' % (clockres(time.time) * 1e6))
    spróbuj:
        zaimportuj systimes
        print('systimes.processtime: %10.3fus' % (clockres(systimes.processtime) * 1e6))
    wyjąwszy ImportError:
        dalej
