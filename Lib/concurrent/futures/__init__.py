# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Execute computations asynchronously using threads albo processes."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

z concurrent.futures._base zaimportuj (FIRST_COMPLETED,
                                      FIRST_EXCEPTION,
                                      ALL_COMPLETED,
                                      CancelledError,
                                      TimeoutError,
                                      Future,
                                      Executor,
                                      wait,
                                      as_completed)
z concurrent.futures.process zaimportuj ProcessPoolExecutor
z concurrent.futures.thread zaimportuj ThreadPoolExecutor
