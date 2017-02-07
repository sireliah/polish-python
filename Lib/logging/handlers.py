# Copyright 2001-2015 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, oraz distribute this software oraz its
# documentation dla any purpose oraz without fee jest hereby granted,
# provided that the above copyright notice appear w all copies oraz that
# both that copyright notice oraz this permission notice appear w
# supporting documentation, oraz that the name of Vinay Sajip
# nie be used w advertising albo publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Additional handlers dla the logging package dla Python. The core package jest
based on PEP 282 oraz comments thereto w comp.lang.python.

Copyright (C) 2001-2015 Vinay Sajip. All Rights Reserved.

To use, simply 'zaimportuj logging.handlers' oraz log away!
"""

zaimportuj logging, socket, os, pickle, struct, time, re
z stat zaimportuj ST_DEV, ST_INO, ST_MTIME
zaimportuj queue
spróbuj:
    zaimportuj threading
wyjąwszy ImportError: #pragma: no cover
    threading = Nic

#
# Some constants...
#

DEFAULT_TCP_LOGGING_PORT    = 9020
DEFAULT_UDP_LOGGING_PORT    = 9021
DEFAULT_HTTP_LOGGING_PORT   = 9022
DEFAULT_SOAP_LOGGING_PORT   = 9023
SYSLOG_UDP_PORT             = 514
SYSLOG_TCP_PORT             = 514

_MIDNIGHT = 24 * 60 * 60  # number of seconds w a day

klasa BaseRotatingHandler(logging.FileHandler):
    """
    Base klasa dla handlers that rotate log files at a certain point.
    Not meant to be instantiated directly.  Instead, use RotatingFileHandler
    albo TimedRotatingFileHandler.
    """
    def __init__(self, filename, mode, encoding=Nic, delay=Nieprawda):
        """
        Use the specified filename dla streamed logging
        """
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.mode = mode
        self.encoding = encoding
        self.namer = Nic
        self.rotator = Nic

    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering dla rollover jako described
        w doRollover().
        """
        spróbuj:
            jeżeli self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        wyjąwszy Exception:
            self.handleError(record)

    def rotation_filename(self, default_name):
        """
        Modify the filename of a log file when rotating.

        This jest provided so that a custom filename can be provided.

        The default implementation calls the 'namer' attribute of the
        handler, jeżeli it's callable, dalejing the default name to
        it. If the attribute isn't callable (the default jest Nic), the name
        jest returned unchanged.

        :param default_name: The default name dla the log file.
        """
        jeżeli nie callable(self.namer):
            result = default_name
        inaczej:
            result = self.namer(default_name)
        zwróć result

    def rotate(self, source, dest):
        """
        When rotating, rotate the current log.

        The default implementation calls the 'rotator' attribute of the
        handler, jeżeli it's callable, dalejing the source oraz dest arguments to
        it. If the attribute isn't callable (the default jest Nic), the source
        jest simply renamed to the destination.

        :param source: The source filename. This jest normally the base
                       filename, e.g. 'test.log'
        :param dest:   The destination filename. This jest normally
                       what the source jest rotated to, e.g. 'test.log.1'.
        """
        jeżeli nie callable(self.rotator):
            # Issue 18940: A file may nie have been created jeżeli delay jest Prawda.
            jeżeli os.path.exists(source):
                os.rename(source, dest)
        inaczej:
            self.rotator(source, dest)

klasa RotatingFileHandler(BaseRotatingHandler):
    """
    Handler dla logging to a set of files, which switches z one file
    to the next when the current file reaches a certain size.
    """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=Nic, delay=Nieprawda):
        """
        Open the specified file oraz use it jako the stream dla logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes oraz backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file jest nearly maxBytes w
        length. If backupCount jest >= 1, the system will successively create
        new files przy the same pathname jako the base file, but przy extensions
        ".1", ".2" etc. appended to it. For example, przy a backupCount of 5
        oraz a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to jest always "app.log" - when it gets filled up, it jest closed
        oraz renamed to "app.log.1", oraz jeżeli files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes jest zero, rollover never occurs.
        """
        # If rotation/rollover jest wanted, it doesn't make sense to use another
        # mode. If dla example 'w' were specified, then jeżeli there were multiple
        # runs of the calling application, the logs z previous runs would be
        # lost jeżeli the 'w' jest respected, because the log file would be truncated
        # on each run.
        jeżeli maxBytes > 0:
            mode = 'a'
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def doRollover(self):
        """
        Do a rollover, jako described w __init__().
        """
        jeżeli self.stream:
            self.stream.close()
            self.stream = Nic
        jeżeli self.backupCount > 0:
            dla i w range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename,
                                                        i + 1))
                jeżeli os.path.exists(sfn):
                    jeżeli os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            jeżeli os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        jeżeli nie self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):
        """
        Determine jeżeli rollover should occur.

        Basically, see jeżeli the supplied record would cause the file to exceed
        the size limit we have.
        """
        jeżeli self.stream jest Nic:                 # delay was set...
            self.stream = self._open()
        jeżeli self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            jeżeli self.stream.tell() + len(msg) >= self.maxBytes:
                zwróć 1
        zwróć 0

klasa TimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler dla logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount jest > 0, when rollover jest done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=Nic, delay=Nieprawda, utc=Nieprawda, atTime=Nic):
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.when = when.upper()
        self.backupCount = backupCount
        self.utc = utc
        self.atTime = atTime
        # Calculate the real rollover interval, which jest just the number of
        # seconds between rollovers.  Also set the filename suffix used when
        # a rollover occurs.  Current 'when' events supported:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        # W{0-6} - roll over on a certain day; 0 - Monday
        #
        # Case of the 'when' specifier jest nie important; lower albo upper case
        # will work.
        jeżeli self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        albo_inaczej self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(\.\w+)?$"
        albo_inaczej self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}(\.\w+)?$"
        albo_inaczej self.when == 'D' albo self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        albo_inaczej self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            jeżeli len(self.when) != 2:
                podnieś ValueError("You must specify a day dla weekly rollover z 0 to 6 (0 jest Monday): %s" % self.when)
            jeżeli self.when[1] < '0' albo self.when[1] > '6':
                podnieś ValueError("Invalid day specified dla weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        inaczej:
            podnieś ValueError("Invalid rollover interval specified: %s" % self.when)

        self.extMatch = re.compile(self.extMatch, re.ASCII)
        self.interval = self.interval * interval # multiply by units requested
        jeżeli os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        inaczej:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    def computeRollover(self, currentTime):
        """
        Work out the rollover time based on the specified time.
        """
        result = currentTime + self.interval
        # If we are rolling over at midnight albo weekly, then the interval jest already known.
        # What we need to figure out jest WHEN the next interval is.  In other words,
        # jeżeli you are rolling over at midnight, then your base interval jest 1 day,
        # but you want to start that one day clock at midnight, nie now.  So, we
        # have to fudge the rolloverAt value w order to trigger the first rollover
        # at the right time.  After that, the regular interval will take care of
        # the rest.  Note that this code doesn't care about leap seconds. :)
        jeżeli self.when == 'MIDNIGHT' albo self.when.startswith('W'):
            # This could be done przy less code, but I wanted it to be clear
            jeżeli self.utc:
                t = time.gmtime(currentTime)
            inaczej:
                t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            currentDay = t[6]
            # r jest the number of seconds left between now oraz the next rotation
            jeżeli self.atTime jest Nic:
                rotate_ts = _MIDNIGHT
            inaczej:
                rotate_ts = ((self.atTime.hour * 60 + self.atTime.minute)*60 +
                    self.atTime.second)

            r = rotate_ts - ((currentHour * 60 + currentMinute) * 60 +
                currentSecond)
            jeżeli r < 0:
                # Rotate time jest before the current time (dla example when
                # self.rotateAt jest 13:45 oraz it now 14:15), rotation jest
                # tomorrow.
                r += _MIDNIGHT
                currentDay = (currentDay + 1) % 7
            result = currentTime + r
            # If we are rolling over on a certain day, add w the number of days until
            # the next rollover, but offset by 1 since we just calculated the time
            # until the next day starts.  There are three cases:
            # Case 1) The day to rollover jest today; w this case, do nothing
            # Case 2) The day to rollover jest further w the interval (i.e., today jest
            #         day 2 (Wednesday) oraz rollover jest on day 6 (Sunday).  Days to
            #         next rollover jest simply 6 - 2 - 1, albo 3.
            # Case 3) The day to rollover jest behind us w the interval (i.e., today
            #         jest day 5 (Saturday) oraz rollover jest on day 3 (Thursday).
            #         Days to rollover jest 6 - 5 + 3, albo 4.  In this case, it's the
            #         number of days left w the current week (1) plus the number
            #         of days w the next week until the rollover day (3).
            # The calculations described w 2) oraz 3) above need to have a day added.
            # This jest because the above time calculation takes us to midnight on this
            # day, i.e. the start of the next day.
            jeżeli self.when.startswith('W'):
                day = currentDay # 0 jest Monday
                jeżeli day != self.dayOfWeek:
                    jeżeli day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    inaczej:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    newRolloverAt = result + (daysToWait * (60 * 60 * 24))
                    jeżeli nie self.utc:
                        dstNow = t[-1]
                        dstAtRollover = time.localtime(newRolloverAt)[-1]
                        jeżeli dstNow != dstAtRollover:
                            jeżeli nie dstNow:  # DST kicks w before next rollover, so we need to deduct an hour
                                addend = -3600
                            inaczej:           # DST bows out before next rollover, so we need to add an hour
                                addend = 3600
                            newRolloverAt += addend
                    result = newRolloverAt
        zwróć result

    def shouldRollover(self, record):
        """
        Determine jeżeli rollover should occur.

        record jest nie used, jako we are just comparing times, but it jest needed so
        the method signatures are the same
        """
        t = int(time.time())
        jeżeli t >= self.rolloverAt:
            zwróć 1
        zwróć 0

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        dla fileName w fileNames:
            jeżeli fileName[:plen] == prefix:
                suffix = fileName[plen:]
                jeżeli self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        result.sort()
        jeżeli len(result) < self.backupCount:
            result = []
        inaczej:
            result = result[:len(result) - self.backupCount]
        zwróć result

    def doRollover(self):
        """
        do a rollover; w this case, a date/time stamp jest appended to the filename
        when the rollover happens.  However, you want the file to be named dla the
        start of the interval, nie the current time.  If there jest a backup count,
        then we have to get a list of matching filenames, sort them oraz remove
        the one przy the oldest suffix.
        """
        jeżeli self.stream:
            self.stream.close()
            self.stream = Nic
        # get the time that this sequence started at oraz make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        jeżeli self.utc:
            timeTuple = time.gmtime(t)
        inaczej:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            jeżeli dstNow != dstThen:
                jeżeli dstNow:
                    addend = 3600
                inaczej:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        jeżeli os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        jeżeli self.backupCount > 0:
            dla s w self.getFilesToDelete():
                os.remove(s)
        jeżeli nie self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        dopóki newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes oraz midnight albo weekly rollover, adjust dla this.
        jeżeli (self.when == 'MIDNIGHT' albo self.when.startswith('W')) oraz nie self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            jeżeli dstNow != dstAtRollover:
                jeżeli nie dstNow:  # DST kicks w before next rollover, so we need to deduct an hour
                    addend = -3600
                inaczej:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

klasa WatchedFileHandler(logging.FileHandler):
    """
    A handler dla logging to a file, which watches the file
    to see jeżeli it has changed dopóki w use. This can happen because of
    usage of programs such jako newsyslog oraz logrotate which perform
    log file rotation. This handler, intended dla use under Unix,
    watches the file to see jeżeli it has changed since the last emit.
    (A file has changed jeżeli its device albo inode have changed.)
    If it has changed, the old file stream jest closed, oraz the file
    opened to get a new stream.

    This handler jest nie appropriate dla use under Windows, because
    under Windows open files cannot be moved albo renamed - logging
    opens the files przy exclusive locks - oraz so there jest no need
    dla such a handler. Furthermore, ST_INO jest nie supported under
    Windows; stat always returns zero dla this value.

    This handler jest based on a suggestion oraz patch by Chad J.
    Schroeder.
    """
    def __init__(self, filename, mode='a', encoding=Nic, delay=Nieprawda):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.dev, self.ino = -1, -1
        self._statstream()

    def _statstream(self):
        jeżeli self.stream:
            sres = os.fstat(self.stream.fileno())
            self.dev, self.ino = sres[ST_DEV], sres[ST_INO]

    def emit(self, record):
        """
        Emit a record.

        First check jeżeli the underlying file has changed, oraz jeżeli it
        has, close the old stream oraz reopen the file to get the
        current stream.
        """
        # Reduce the chance of race conditions by stat'ing by path only
        # once oraz then fstat'ing our new fd jeżeli we opened a new log stream.
        # See issue #14632: Thanks to John Mulligan dla the problem report
        # oraz patch.
        spróbuj:
            # stat the file by path, checking dla existence
            sres = os.stat(self.baseFilename)
        wyjąwszy FileNotFoundError:
            sres = Nic
        # compare file system stat przy that of our stream file handle
        jeżeli nie sres albo sres[ST_DEV] != self.dev albo sres[ST_INO] != self.ino:
            jeżeli self.stream jest nie Nic:
                # we have an open file handle, clean it up
                self.stream.flush()
                self.stream.close()
                self.stream = Nic  # See Issue #21742: _open () might fail.
                # open a new file handle oraz get new stat info z that fd
                self.stream = self._open()
                self._statstream()
        logging.FileHandler.emit(self, record)


klasa SocketHandler(logging.Handler):
    """
    A handler klasa which writes logging records, w pickle format, to
    a streaming socket. The socket jest kept open across logging calls.
    If the peer resets it, an attempt jest made to reconnect on the next call.
    The pickle which jest sent jest that of the LogRecord's attribute dictionary
    (__dict__), so that the receiver does nie need to have the logging module
    installed w order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.
    """

    def __init__(self, host, port):
        """
        Initializes the handler przy a specific host address oraz port.

        When the attribute *closeOnError* jest set to Prawda - jeżeli a socket error
        occurs, the socket jest silently closed oraz then reopened on the next
        logging call.
        """
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        jeżeli port jest Nic:
            self.address = host
        inaczej:
            self.address = (host, port)
        self.sock = Nic
        self.closeOnError = Nieprawda
        self.retryTime = Nic
        #
        # Exponential backoff parameters.
        #
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    def makeSocket(self, timeout=1):
        """
        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        jeżeli self.port jest nie Nic:
            result = socket.create_connection(self.address, timeout=timeout)
        inaczej:
            result = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            result.settimeout(timeout)
            spróbuj:
                result.connect(self.address)
            wyjąwszy OSError:
                result.close()  # Issue 19182
                podnieś
        zwróć result

    def createSocket(self):
        """
        Try to create a socket, using an exponential backoff with
        a max retry time. Thanks to Robert Olson dla the original patch
        (SF #815911) which has been slightly refactored.
        """
        now = time.time()
        # Either retryTime jest Nic, w which case this
        # jest the first time back after a disconnect, albo
        # we've waited long enough.
        jeżeli self.retryTime jest Nic:
            attempt = Prawda
        inaczej:
            attempt = (now >= self.retryTime)
        jeżeli attempt:
            spróbuj:
                self.sock = self.makeSocket()
                self.retryTime = Nic # next time, no delay before trying
            wyjąwszy OSError:
                #Creation failed, so set the retry time oraz return.
                jeżeli self.retryTime jest Nic:
                    self.retryPeriod = self.retryStart
                inaczej:
                    self.retryPeriod = self.retryPeriod * self.retryFactor
                    jeżeli self.retryPeriod > self.retryMax:
                        self.retryPeriod = self.retryMax
                self.retryTime = now + self.retryPeriod

    def send(self, s):
        """
        Send a pickled string to the socket.

        This function allows dla partial sends which can happen when the
        network jest busy.
        """
        jeżeli self.sock jest Nic:
            self.createSocket()
        #self.sock can be Nic either because we haven't reached the retry
        #time yet, albo because we have reached the retry time oraz retried,
        #but are still unable to connect.
        jeżeli self.sock:
            spróbuj:
                self.sock.sendall(s)
            wyjąwszy OSError: #pragma: no cover
                self.sock.close()
                self.sock = Nic  # so we can call createSocket next time

    def makePickle(self, record):
        """
        Pickles the record w binary format przy a length prefix, oraz
        returns it ready dla transmission across the socket.
        """
        ei = record.exc_info
        jeżeli ei:
            # just to get traceback text into record.exc_text ...
            dummy = self.format(record)
        # See issue #14436: If msg albo args are objects, they may nie be
        # available on the receiving end. So we convert the msg % args
        # to a string, save it jako msg oraz zap the args.
        d = dict(record.__dict__)
        d['msg'] = record.getMessage()
        d['args'] = Nic
        d['exc_info'] = Nic
        s = pickle.dumps(d, 1)
        slen = struct.pack(">L", len(s))
        zwróć slen + s

    def handleError(self, record):
        """
        Handle an error during logging.

        An error has occurred during logging. Most likely cause -
        connection lost. Close the socket so that we can retry on the
        next event.
        """
        jeżeli self.closeOnError oraz self.sock:
            self.sock.close()
            self.sock = Nic        #try to reconnect next time
        inaczej:
            logging.Handler.handleError(self, record)

    def emit(self, record):
        """
        Emit a record.

        Pickles the record oraz writes it to the socket w binary format.
        If there jest an error przy the socket, silently drop the packet.
        If there was a problem przy the socket, re-establishes the
        socket.
        """
        spróbuj:
            s = self.makePickle(record)
            self.send(s)
        wyjąwszy Exception:
            self.handleError(record)

    def close(self):
        """
        Closes the socket.
        """
        self.acquire()
        spróbuj:
            sock = self.sock
            jeżeli sock:
                self.sock = Nic
                sock.close()
            logging.Handler.close(self)
        w_końcu:
            self.release()

klasa DatagramHandler(SocketHandler):
    """
    A handler klasa which writes logging records, w pickle format, to
    a datagram socket.  The pickle which jest sent jest that of the LogRecord's
    attribute dictionary (__dict__), so that the receiver does nie need to
    have the logging module installed w order to process the logging event.

    To unpickle the record at the receiving end into a LogRecord, use the
    makeLogRecord function.

    """
    def __init__(self, host, port):
        """
        Initializes the handler przy a specific host address oraz port.
        """
        SocketHandler.__init__(self, host, port)
        self.closeOnError = Nieprawda

    def makeSocket(self):
        """
        The factory method of SocketHandler jest here overridden to create
        a UDP socket (SOCK_DGRAM).
        """
        jeżeli self.port jest Nic:
            family = socket.AF_UNIX
        inaczej:
            family = socket.AF_INET
        s = socket.socket(family, socket.SOCK_DGRAM)
        zwróć s

    def send(self, s):
        """
        Send a pickled string to a socket.

        This function no longer allows dla partial sends which can happen
        when the network jest busy - UDP does nie guarantee delivery oraz
        can deliver packets out of sequence.
        """
        jeżeli self.sock jest Nic:
            self.createSocket()
        self.sock.sendto(s, self.address)

klasa SysLogHandler(logging.Handler):
    """
    A handler klasa which sends formatted logging records to a syslog
    server. Based on Sam Rushing's syslog module:
    http://www.nightmare.com/squirl/python-ext/misc/syslog.py
    Contributed by Nicolas Untz (after which minor refactoring changes
    have been made).
    """

    # z <linux/sys/syslog.h>:
    # ======================================================================
    # priorities/facilities are encoded into a single 32-bit quantity, where
    # the bottom 3 bits are the priority (0-7) oraz the top 28 bits are the
    # facility (0-big number). Both the priorities oraz the facilities map
    # roughly one-to-one to strings w the syslogd(8) source code.  This
    # mapping jest included w this file.
    #
    # priorities (these are ordered)

    LOG_EMERG     = 0       #  system jest unusable
    LOG_ALERT     = 1       #  action must be taken immediately
    LOG_CRIT      = 2       #  critical conditions
    LOG_ERR       = 3       #  error conditions
    LOG_WARNING   = 4       #  warning conditions
    LOG_NOTICE    = 5       #  normal but significant condition
    LOG_INFO      = 6       #  informational
    LOG_DEBUG     = 7       #  debug-level messages

    #  facility codes
    LOG_KERN      = 0       #  kernel messages
    LOG_USER      = 1       #  random user-level messages
    LOG_MAIL      = 2       #  mail system
    LOG_DAEMON    = 3       #  system daemons
    LOG_AUTH      = 4       #  security/authorization messages
    LOG_SYSLOG    = 5       #  messages generated internally by syslogd
    LOG_LPR       = 6       #  line printer subsystem
    LOG_NEWS      = 7       #  network news subsystem
    LOG_UUCP      = 8       #  UUCP subsystem
    LOG_CRON      = 9       #  clock daemon
    LOG_AUTHPRIV  = 10      #  security/authorization messages (private)
    LOG_FTP       = 11      #  FTP daemon

    #  other codes through 15 reserved dla system use
    LOG_LOCAL0    = 16      #  reserved dla local use
    LOG_LOCAL1    = 17      #  reserved dla local use
    LOG_LOCAL2    = 18      #  reserved dla local use
    LOG_LOCAL3    = 19      #  reserved dla local use
    LOG_LOCAL4    = 20      #  reserved dla local use
    LOG_LOCAL5    = 21      #  reserved dla local use
    LOG_LOCAL6    = 22      #  reserved dla local use
    LOG_LOCAL7    = 23      #  reserved dla local use

    priority_names = {
        "alert":    LOG_ALERT,
        "crit":     LOG_CRIT,
        "critical": LOG_CRIT,
        "debug":    LOG_DEBUG,
        "emerg":    LOG_EMERG,
        "err":      LOG_ERR,
        "error":    LOG_ERR,        #  DEPRECATED
        "info":     LOG_INFO,
        "notice":   LOG_NOTICE,
        "panic":    LOG_EMERG,      #  DEPRECATED
        "warn":     LOG_WARNING,    #  DEPRECATED
        "warning":  LOG_WARNING,
        }

    facility_names = {
        "auth":     LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron":     LOG_CRON,
        "daemon":   LOG_DAEMON,
        "ftp":      LOG_FTP,
        "kern":     LOG_KERN,
        "lpr":      LOG_LPR,
        "mail":     LOG_MAIL,
        "news":     LOG_NEWS,
        "security": LOG_AUTH,       #  DEPRECATED
        "syslog":   LOG_SYSLOG,
        "user":     LOG_USER,
        "uucp":     LOG_UUCP,
        "local0":   LOG_LOCAL0,
        "local1":   LOG_LOCAL1,
        "local2":   LOG_LOCAL2,
        "local3":   LOG_LOCAL3,
        "local4":   LOG_LOCAL4,
        "local5":   LOG_LOCAL5,
        "local6":   LOG_LOCAL6,
        "local7":   LOG_LOCAL7,
        }

    #The map below appears to be trivially lowercasing the key. However,
    #there's more to it than meets the eye - w some locales, lowercasing
    #gives unexpected results. See SF #1524081: w the Turkish locale,
    #"INFO".lower() != "info"
    priority_map = {
        "DEBUG" : "debug",
        "INFO" : "info",
        "WARNING" : "warning",
        "ERROR" : "error",
        "CRITICAL" : "critical"
    }

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 facility=LOG_USER, socktype=Nic):
        """
        Initialize a handler.

        If address jest specified jako a string, a UNIX socket jest used. To log to a
        local syslogd, "SysLogHandler(address="/dev/log")" can be used.
        If facility jest nie specified, LOG_USER jest used. If socktype jest
        specified jako socket.SOCK_DGRAM albo socket.SOCK_STREAM, that specific
        socket type will be used. For Unix sockets, you can also specify a
        socktype of Nic, w which case socket.SOCK_DGRAM will be used, falling
        back to socket.SOCK_STREAM.
        """
        logging.Handler.__init__(self)

        self.address = address
        self.facility = facility
        self.socktype = socktype

        jeżeli isinstance(address, str):
            self.unixsocket = Prawda
            self._connect_unixsocket(address)
        inaczej:
            self.unixsocket = Nieprawda
            jeżeli socktype jest Nic:
                socktype = socket.SOCK_DGRAM
            self.socket = socket.socket(socket.AF_INET, socktype)
            jeżeli socktype == socket.SOCK_STREAM:
                self.socket.connect(address)
            self.socktype = socktype
        self.formatter = Nic

    def _connect_unixsocket(self, address):
        use_socktype = self.socktype
        jeżeli use_socktype jest Nic:
            use_socktype = socket.SOCK_DGRAM
        self.socket = socket.socket(socket.AF_UNIX, use_socktype)
        spróbuj:
            self.socket.connect(address)
            # it worked, so set self.socktype to the used type
            self.socktype = use_socktype
        wyjąwszy OSError:
            self.socket.close()
            jeżeli self.socktype jest nie Nic:
                # user didn't specify falling back, so fail
                podnieś
            use_socktype = socket.SOCK_STREAM
            self.socket = socket.socket(socket.AF_UNIX, use_socktype)
            spróbuj:
                self.socket.connect(address)
                # it worked, so set self.socktype to the used type
                self.socktype = use_socktype
            wyjąwszy OSError:
                self.socket.close()
                podnieś

    def encodePriority(self, facility, priority):
        """
        Encode the facility oraz priority. You can dalej w strings albo
        integers - jeżeli strings are dalejed, the facility_names oraz
        priority_names mapping dictionaries are used to convert them to
        integers.
        """
        jeżeli isinstance(facility, str):
            facility = self.facility_names[facility]
        jeżeli isinstance(priority, str):
            priority = self.priority_names[priority]
        zwróć (facility << 3) | priority

    def close (self):
        """
        Closes the socket.
        """
        self.acquire()
        spróbuj:
            self.socket.close()
            logging.Handler.close(self)
        w_końcu:
            self.release()

    def mapPriority(self, levelName):
        """
        Map a logging level name to a key w the priority_names map.
        This jest useful w two scenarios: when custom levels are being
        used, oraz w the case where you can't do a straightforward
        mapping by lowercasing the logging level name because of locale-
        specific issues (see SF #1524081).
        """
        zwróć self.priority_map.get(levelName, "warning")

    ident = ''          # prepended to all messages
    append_nul = Prawda   # some old syslog daemons expect a NUL terminator

    def emit(self, record):
        """
        Emit a record.

        The record jest formatted, oraz then sent to the syslog server. If
        exception information jest present, it jest NOT sent to the server.
        """
        spróbuj:
            msg = self.format(record)
            jeżeli self.ident:
                msg = self.ident + msg
            jeżeli self.append_nul:
                msg += '\000'

            # We need to convert record level to lowercase, maybe this will
            # change w the future.
            prio = '<%d>' % self.encodePriority(self.facility,
                                                self.mapPriority(record.levelname))
            prio = prio.encode('utf-8')
            # Message jest a string. Convert to bytes jako required by RFC 5424
            msg = msg.encode('utf-8')
            msg = prio + msg
            jeżeli self.unixsocket:
                spróbuj:
                    self.socket.send(msg)
                wyjąwszy OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            albo_inaczej self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            inaczej:
                self.socket.sendall(msg)
        wyjąwszy Exception:
            self.handleError(record)

klasa SMTPHandler(logging.Handler):
    """
    A handler klasa which sends an SMTP email dla each logging event.
    """
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=Nic, secure=Nic, timeout=5.0):
        """
        Initialize the handler.

        Initialize the instance przy the z oraz to addresses oraz subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format dla the mailhost argument. To specify
        authentication credentials, supply a (username, dalejword) tuple
        dla the credentials argument. To specify the use of a secure
        protocol (TLS), dalej w a tuple dla the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, albo a single-value tuple przy the name
        of a keyfile, albo a 2-value tuple przy the names of the keyfile oraz
        certificate file. (This tuple jest dalejed to the `starttls` method).
        A timeout w seconds can be specified dla the SMTP connection (the
        default jest one second).
        """
        logging.Handler.__init__(self)
        jeżeli isinstance(mailhost, (list, tuple)):
            self.mailhost, self.mailport = mailhost
        inaczej:
            self.mailhost, self.mailport = mailhost, Nic
        jeżeli isinstance(credentials, (list, tuple)):
            self.username, self.password = credentials
        inaczej:
            self.username = Nic
        self.fromaddr = fromaddr
        jeżeli isinstance(toaddrs, str):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self.timeout = timeout

    def getSubject(self, record):
        """
        Determine the subject dla the email.

        If you want to specify a subject line which jest record-dependent,
        override this method.
        """
        zwróć self.subject

    def emit(self, record):
        """
        Emit a record.

        Format the record oraz send it to the specified addressees.
        """
        spróbuj:
            zaimportuj smtplib
            z email.utils zaimportuj formatdate
            port = self.mailport
            jeżeli nie port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port, timeout=self.timeout)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            jeżeli self.username:
                jeżeli self.secure jest nie Nic:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        wyjąwszy Exception:
            self.handleError(record)

klasa NTEventLogHandler(logging.Handler):
    """
    A handler klasa which sends events to the NT Event Log. Adds a
    registry entry dla the specified application name. If no dllname jest
    provided, win32service.pyd (which contains some basic message
    placeholders) jest used. Note that use of these placeholders will make
    your event logs big, jako the entire message source jest held w the log.
    If you want slimmer logs, you have to dalej w the name of your own DLL
    which contains the message definitions you want to use w the event log.
    """
    def __init__(self, appname, dllname=Nic, logtype="Application"):
        logging.Handler.__init__(self)
        spróbuj:
            zaimportuj win32evtlogutil, win32evtlog
            self.appname = appname
            self._welu = win32evtlogutil
            jeżeli nie dllname:
                dllname = os.path.split(self._welu.__file__)
                dllname = os.path.split(dllname[0])
                dllname = os.path.join(dllname[0], r'win32service.pyd')
            self.dllname = dllname
            self.logtype = logtype
            self._welu.AddSourceToRegistry(appname, dllname, logtype)
            self.deftype = win32evtlog.EVENTLOG_ERROR_TYPE
            self.typemap = {
                logging.DEBUG   : win32evtlog.EVENTLOG_INFORMATION_TYPE,
                logging.INFO    : win32evtlog.EVENTLOG_INFORMATION_TYPE,
                logging.WARNING : win32evtlog.EVENTLOG_WARNING_TYPE,
                logging.ERROR   : win32evtlog.EVENTLOG_ERROR_TYPE,
                logging.CRITICAL: win32evtlog.EVENTLOG_ERROR_TYPE,
         }
        wyjąwszy ImportError:
            print("The Python Win32 extensions dla NT (service, event "\
                        "logging) appear nie to be available.")
            self._welu = Nic

    def getMessageID(self, record):
        """
        Return the message ID dla the event record. If you are using your
        own messages, you could do this by having the msg dalejed to the
        logger being an ID rather than a formatting string. Then, w here,
        you could use a dictionary lookup to get the message ID. This
        version returns 1, which jest the base message ID w win32service.pyd.
        """
        zwróć 1

    def getEventCategory(self, record):
        """
        Return the event category dla the record.

        Override this jeżeli you want to specify your own categories. This version
        returns 0.
        """
        zwróć 0

    def getEventType(self, record):
        """
        Return the event type dla the record.

        Override this jeżeli you want to specify your own types. This version does
        a mapping using the handler's typemap attribute, which jest set up w
        __init__() to a dictionary which contains mappings dla DEBUG, INFO,
        WARNING, ERROR oraz CRITICAL. If you are using your own levels you will
        either need to override this method albo place a suitable dictionary w
        the handler's typemap attribute.
        """
        zwróć self.typemap.get(record.levelno, self.deftype)

    def emit(self, record):
        """
        Emit a record.

        Determine the message ID, event category oraz event type. Then
        log the message w the NT event log.
        """
        jeżeli self._welu:
            spróbuj:
                id = self.getMessageID(record)
                cat = self.getEventCategory(record)
                type = self.getEventType(record)
                msg = self.format(record)
                self._welu.ReportEvent(self.appname, id, cat, type, [msg])
            wyjąwszy Exception:
                self.handleError(record)

    def close(self):
        """
        Clean up this handler.

        You can remove the application name z the registry jako a
        source of event log entries. However, jeżeli you do this, you will
        nie be able to see the events jako you intended w the Event Log
        Viewer - it needs to be able to access the registry to get the
        DLL name.
        """
        #self._welu.RemoveSourceFromRegistry(self.appname, self.logtype)
        logging.Handler.close(self)

klasa HTTPHandler(logging.Handler):
    """
    A klasa which sends records to a Web server, using either GET albo
    POST semantics.
    """
    def __init__(self, host, url, method="GET", secure=Nieprawda, credentials=Nic,
                 context=Nic):
        """
        Initialize the instance przy the host, the request URL, oraz the method
        ("GET" albo "POST")
        """
        logging.Handler.__init__(self)
        method = method.upper()
        jeżeli method nie w ["GET", "POST"]:
            podnieś ValueError("method must be GET albo POST")
        jeżeli nie secure oraz context jest nie Nic:
            podnieś ValueError("context parameter only makes sense "
                             "przy secure=Prawda")
        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.context = context

    def mapLogRecord(self, record):
        """
        Default implementation of mapping the log record into a dict
        that jest sent jako the CGI data. Overwrite w your class.
        Contributed by Franz Glasner.
        """
        zwróć record.__dict__

    def emit(self, record):
        """
        Emit a record.

        Send the record to the Web server jako a percent-encoded dictionary
        """
        spróbuj:
            zaimportuj http.client, urllib.parse
            host = self.host
            jeżeli self.secure:
                h = http.client.HTTPSConnection(host, context=self.context)
            inaczej:
                h = http.client.HTTPConnection(host)
            url = self.url
            data = urllib.parse.urlencode(self.mapLogRecord(record))
            jeżeli self.method == "GET":
                jeżeli (url.find('?') >= 0):
                    sep = '&'
                inaczej:
                    sep = '?'
                url = url + "%c%s" % (sep, data)
            h.putrequest(self.method, url)
            # support multiple hosts on one IP address...
            # need to strip optional :port z host, jeżeli present
            i = host.find(":")
            jeżeli i >= 0:
                host = host[:i]
            h.putheader("Host", host)
            jeżeli self.method == "POST":
                h.putheader("Content-type",
                            "application/x-www-form-urlencoded")
                h.putheader("Content-length", str(len(data)))
            jeżeli self.credentials:
                zaimportuj base64
                s = ('u%s:%s' % self.credentials).encode('utf-8')
                s = 'Basic ' + base64.b64encode(s).strip()
                h.putheader('Authorization', s)
            h.endheaders()
            jeżeli self.method == "POST":
                h.send(data.encode('utf-8'))
            h.getresponse()    #can't do anything przy the result
        wyjąwszy Exception:
            self.handleError(record)

klasa BufferingHandler(logging.Handler):
    """
  A handler klasa which buffers logging records w memory. Whenever each
  record jest added to the buffer, a check jest made to see jeżeli the buffer should
  be flushed. If it should, then flush() jest expected to do what's needed.
    """
    def __init__(self, capacity):
        """
        Initialize the handler przy the buffer size.
        """
        logging.Handler.__init__(self)
        self.capacity = capacity
        self.buffer = []

    def shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true jeżeli the buffer jest up to capacity. This method can be
        overridden to implement custom flushing strategies.
        """
        zwróć (len(self.buffer) >= self.capacity)

    def emit(self, record):
        """
        Emit a record.

        Append the record. If shouldFlush() tells us to, call flush() to process
        the buffer.
        """
        self.buffer.append(record)
        jeżeli self.shouldFlush(record):
            self.flush()

    def flush(self):
        """
        Override to implement custom flushing behaviour.

        This version just zaps the buffer to empty.
        """
        self.acquire()
        spróbuj:
            self.buffer = []
        w_końcu:
            self.release()

    def close(self):
        """
        Close the handler.

        This version just flushes oraz chains to the parent class' close().
        """
        spróbuj:
            self.flush()
        w_końcu:
            logging.Handler.close(self)

klasa MemoryHandler(BufferingHandler):
    """
    A handler klasa which buffers logging records w memory, periodically
    flushing them to a target handler. Flushing occurs whenever the buffer
    jest full, albo when an event of a certain severity albo greater jest seen.
    """
    def __init__(self, capacity, flushLevel=logging.ERROR, target=Nic):
        """
        Initialize the handler przy the buffer size, the level at which
        flushing should occur oraz an optional target.

        Note that without a target being set either here albo via setTarget(),
        a MemoryHandler jest no use to anyone!
        """
        BufferingHandler.__init__(self, capacity)
        self.flushLevel = flushLevel
        self.target = target

    def shouldFlush(self, record):
        """
        Check dla buffer full albo a record at the flushLevel albo higher.
        """
        zwróć (len(self.buffer) >= self.capacity) albo \
                (record.levelno >= self.flushLevel)

    def setTarget(self, target):
        """
        Set the target handler dla this handler.
        """
        self.target = target

    def flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target, jeżeli there jest one. Override jeżeli you want
        different behaviour.

        The record buffer jest also cleared by this operation.
        """
        self.acquire()
        spróbuj:
            jeżeli self.target:
                dla record w self.buffer:
                    self.target.handle(record)
                self.buffer = []
        w_końcu:
            self.release()

    def close(self):
        """
        Flush, set the target to Nic oraz lose the buffer.
        """
        spróbuj:
            self.flush()
        w_końcu:
            self.acquire()
            spróbuj:
                self.target = Nic
                BufferingHandler.close(self)
            w_końcu:
                self.release()


klasa QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    przy a multiprocessing Queue to centralise logging to file w one process
    (in a multi-process application), so jako to avoid file write contention
    between processes.

    This code jest new w Python 3.2, but this klasa can be copy pasted into
    user code dla use przy earlier Python versions.
    """

    def __init__(self, queue):
        """
        Initialise an instance, using the dalejed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method jeżeli you want to use blocking, timeouts albo custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    def prepare(self, record):
        """
        Prepares a record dla queuing. The object returned by this method jest
        enqueued.

        The base implementation formats the record to merge the message
        oraz arguments, oraz removes unpickleable items z the record
        in-place.

        You might want to override this method jeżeli you want to convert
        the record to a dict albo JSON string, albo send a modified copy
        of the record dopóki leaving the original intact.
        """
        # The format operation gets traceback text into record.exc_text
        # (jeżeli there's exception data), oraz also puts the message into
        # record.message. We can then use this to replace the original
        # msg + args, jako these might be unpickleable. We also zap the
        # exc_info attribute, jako it's no longer needed and, jeżeli nie Nic,
        # will typically nie be pickleable.
        self.format(record)
        record.msg = record.message
        record.args = Nic
        record.exc_info = Nic
        zwróć record

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it dla pickling first.
        """
        spróbuj:
            self.enqueue(self.prepare(record))
        wyjąwszy Exception:
            self.handleError(record)

jeżeli threading:
    klasa QueueListener(object):
        """
        This klasa implements an internal threaded listener which watches for
        LogRecords being added to a queue, removes them oraz dalejes them to a
        list of handlers dla processing.
        """
        _sentinel = Nic

        def __init__(self, queue, *handlers, respect_handler_level=Nieprawda):
            """
            Initialise an instance przy the specified queue oraz
            handlers.
            """
            self.queue = queue
            self.handlers = handlers
            self._stop = threading.Event()
            self._thread = Nic
            self.respect_handler_level = respect_handler_level

        def dequeue(self, block):
            """
            Dequeue a record oraz zwróć it, optionally blocking.

            The base implementation uses get. You may want to override this method
            jeżeli you want to use timeouts albo work przy custom queue implementations.
            """
            zwróć self.queue.get(block)

        def start(self):
            """
            Start the listener.

            This starts up a background thread to monitor the queue for
            LogRecords to process.
            """
            self._thread = t = threading.Thread(target=self._monitor)
            t.setDaemon(Prawda)
            t.start()

        def prepare(self , record):
            """
            Prepare a record dla handling.

            This method just returns the dalejed-in record. You may want to
            override this method jeżeli you need to do any custom marshalling albo
            manipulation of the record before dalejing it to the handlers.
            """
            zwróć record

        def handle(self, record):
            """
            Handle a record.

            This just loops through the handlers offering them the record
            to handle.
            """
            record = self.prepare(record)
            dla handler w self.handlers:
                jeżeli nie self.respect_handler_level:
                    process = Prawda
                inaczej:
                    process = record.levelno >= handler.level
                jeżeli process:
                    handler.handle(record)

        def _monitor(self):
            """
            Monitor the queue dla records, oraz ask the handler
            to deal przy them.

            This method runs on a separate, internal thread.
            The thread will terminate jeżeli it sees a sentinel object w the queue.
            """
            q = self.queue
            has_task_done = hasattr(q, 'task_done')
            dopóki nie self._stop.isSet():
                spróbuj:
                    record = self.dequeue(Prawda)
                    jeżeli record jest self._sentinel:
                        przerwij
                    self.handle(record)
                    jeżeli has_task_done:
                        q.task_done()
                wyjąwszy queue.Empty:
                    dalej
            # There might still be records w the queue.
            dopóki Prawda:
                spróbuj:
                    record = self.dequeue(Nieprawda)
                    jeżeli record jest self._sentinel:
                        przerwij
                    self.handle(record)
                    jeżeli has_task_done:
                        q.task_done()
                wyjąwszy queue.Empty:
                    przerwij

        def enqueue_sentinel(self):
            """
            This jest used to enqueue the sentinel record.

            The base implementation uses put_nowait. You may want to override this
            method jeżeli you want to use timeouts albo work przy custom queue
            implementations.
            """
            self.queue.put_nowait(self._sentinel)

        def stop(self):
            """
            Stop the listener.

            This asks the thread to terminate, oraz then waits dla it to do so.
            Note that jeżeli you don't call this before your application exits, there
            may be some records still left on the queue, which won't be processed.
            """
            self._stop.set()
            self.enqueue_sentinel()
            self._thread.join()
            self._thread = Nic
