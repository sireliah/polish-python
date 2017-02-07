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
Logging package dla Python. Based on PEP 282 oraz comments thereto w
comp.lang.python.

Copyright (C) 2001-2015 Vinay Sajip. All Rights Reserved.

To use, simply 'zaimportuj logging' oraz log away!
"""

zaimportuj sys, os, time, io, traceback, warnings, weakref, collections

z string zaimportuj Template

__all__ = ['BASIC_FORMAT', 'BufferingFormatter', 'CRITICAL', 'DEBUG', 'ERROR',
           'FATAL', 'FileHandler', 'Filter', 'Formatter', 'Handler', 'INFO',
           'LogRecord', 'Logger', 'LoggerAdapter', 'NOTSET', 'NullHandler',
           'StreamHandler', 'WARN', 'WARNING', 'addLevelName', 'basicConfig',
           'captureWarnings', 'critical', 'debug', 'disable', 'error',
           'exception', 'fatal', 'getLevelName', 'getLogger', 'getLoggerClass',
           'info', 'log', 'makeLogRecord', 'setLoggerClass', 'warn', 'warning',
           'getLogRecordFactory', 'setLogRecordFactory', 'lastResort']

spróbuj:
    zaimportuj threading
wyjąwszy ImportError: #pragma: no cover
    threading = Nic

__author__  = "Vinay Sajip <vinay_sajip@red-dove.com>"
__status__  = "production"
# The following module attributes are no longer updated.
__version__ = "0.5.1.2"
__date__    = "07 February 2010"

#---------------------------------------------------------------------------
#   Miscellaneous module data
#---------------------------------------------------------------------------

#
#_startTime jest used jako the base when calculating the relative time of events
#
_startTime = time.time()

#
#raiseExceptions jest used to see jeżeli exceptions during handling should be
#propagated
#
raiseExceptions = Prawda

#
# If you don't want threading information w the log, set this to zero
#
logThreads = Prawda

#
# If you don't want multiprocessing information w the log, set this to zero
#
logMultiprocessing = Prawda

#
# If you don't want process information w the log, set this to zero
#
logProcesses = Prawda

#---------------------------------------------------------------------------
#   Level related stuff
#---------------------------------------------------------------------------
#
# Default levels oraz level names, these can be replaced przy any positive set
# of values having corresponding names. There jest a pseudo-level, NOTSET, which
# jest only really there jako a lower limit dla user-defined levels. Handlers oraz
# loggers are initialized przy NOTSET so that they will log all messages, even
# at user-defined levels.
#

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}
_nameToLevel = {
    'CRITICAL': CRITICAL,
    'ERROR': ERROR,
    'WARN': WARNING,
    'WARNING': WARNING,
    'INFO': INFO,
    'DEBUG': DEBUG,
    'NOTSET': NOTSET,
}

def getLevelName(level):
    """
    Return the textual representation of logging level 'level'.

    If the level jest one of the predefined levels (CRITICAL, ERROR, WARNING,
    INFO, DEBUG) then you get the corresponding string. If you have
    associated levels przy names using addLevelName then the name you have
    associated przy 'level' jest returned.

    If a numeric value corresponding to one of the defined levels jest dalejed
    in, the corresponding string representation jest returned.

    Otherwise, the string "Level %s" % level jest returned.
    """
    # See Issue #22386 dla the reason dla this convoluted expression
    zwróć _levelToName.get(level, _nameToLevel.get(level, ("Level %s" % level)))

def addLevelName(level, levelName):
    """
    Associate 'levelName' przy 'level'.

    This jest used when converting levels to text during message formatting.
    """
    _acquireLock()
    spróbuj:    #unlikely to cause an exception, but you never know...
        _levelToName[level] = levelName
        _nameToLevel[levelName] = level
    w_końcu:
        _releaseLock()

jeżeli hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
inaczej: #pragma: no cover
    def currentframe():
        """Return the frame object dla the caller's stack frame."""
        spróbuj:
            podnieś Exception
        wyjąwszy Exception:
            zwróć sys.exc_info()[2].tb_frame.f_back

#
# _srcfile jest used when walking the stack to check when we've got the first
# caller stack frame, by skipping frames whose filename jest that of this
# module's source. It therefore should contain the filename of this module's
# source file.
#
# Ordinarily we would use __file__ dla this, but frozen modules don't always
# have __file__ set, dla some reason (see Issue #21736). Thus, we get the
# filename z a handy code object z a function defined w this module.
# (There's no particular reason dla picking addLevelName.)
#

_srcfile = os.path.normcase(addLevelName.__code__.co_filename)

# _srcfile jest only used w conjunction przy sys._getframe().
# To provide compatibility przy older versions of Python, set _srcfile
# to Nic jeżeli _getframe() jest nie available; this value will prevent
# findCaller() z being called. You can also do this jeżeli you want to avoid
# the overhead of fetching caller information, even when _getframe() jest
# available.
#jeżeli nie hasattr(sys, '_getframe'):
#    _srcfile = Nic


def _checkLevel(level):
    jeżeli isinstance(level, int):
        rv = level
    albo_inaczej str(level) == level:
        jeżeli level nie w _nameToLevel:
            podnieś ValueError("Unknown level: %r" % level)
        rv = _nameToLevel[level]
    inaczej:
        podnieś TypeError("Level nie an integer albo a valid string: %r" % level)
    zwróć rv

#---------------------------------------------------------------------------
#   Thread-related stuff
#---------------------------------------------------------------------------

#
#_lock jest used to serialize access to shared data structures w this module.
#This needs to be an RLock because fileConfig() creates oraz configures
#Handlers, oraz so might arbitrary user threads. Since Handler code updates the
#shared dictionary _handlers, it needs to acquire the lock. But jeżeli configuring,
#the lock would already have been acquired - so we need an RLock.
#The same argument applies to Loggers oraz Manager.loggerDict.
#
jeżeli threading:
    _lock = threading.RLock()
inaczej: #pragma: no cover
    _lock = Nic


def _acquireLock():
    """
    Acquire the module-level lock dla serializing access to shared data.

    This should be released przy _releaseLock().
    """
    jeżeli _lock:
        _lock.acquire()

def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    jeżeli _lock:
        _lock.release()

#---------------------------------------------------------------------------
#   The logging record
#---------------------------------------------------------------------------

klasa LogRecord(object):
    """
    A LogRecord instance represents an event being logged.

    LogRecord instances are created every time something jest logged. They
    contain all the information pertinent to the event being logged. The
    main information dalejed w jest w msg oraz args, which are combined
    using str(msg) % args to create the message field of the record. The
    record also includes information such jako when the record was created,
    the source line where the logging call was made, oraz any exception
    information to be logged.
    """
    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=Nic, sinfo=Nic, **kwargs):
        """
        Initialize a logging record przy interesting information.
        """
        ct = time.time()
        self.name = name
        self.msg = msg
        #
        # The following statement allows dalejing of a dictionary jako a sole
        # argument, so that you can do something like
        #  logging.debug("a %(a)d b %(b)s", {'a':1, 'b':2})
        # Suggested by Stefan Behnel.
        # Note that without the test dla args[0], we get a problem because
        # during formatting, we test to see jeżeli the arg jest present using
        # 'jeżeli self.args:'. If the event being logged jest e.g. 'Value jest %d'
        # oraz jeżeli the dalejed arg fails 'jeżeli self.args:' then no formatting
        # jest done. For example, logger.warning('Value jest %d', 0) would log
        # 'Value jest %d' instead of 'Value jest 0'.
        # For the use case of dalejing a dictionary, this should nie be a
        # problem.
        # Issue #21172: a request was made to relax the isinstance check
        # to hasattr(args[0], '__getitem__'). However, the docs on string
        # formatting still seem to suggest a mapping object jest required.
        # Thus, dopóki nie removing the isinstance check, it does now look
        # dla collections.Mapping rather than, jako before, dict.
        jeżeli (args oraz len(args) == 1 oraz isinstance(args[0], collections.Mapping)
            oraz args[0]):
            args = args[0]
        self.args = args
        self.levelname = getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        spróbuj:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        wyjąwszy (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = "Unknown module"
        self.exc_info = exc_info
        self.exc_text = Nic      # used to cache the traceback text
        self.stack_info = sinfo
        self.lineno = lineno
        self.funcName = func
        self.created = ct
        self.msecs = (ct - int(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000
        jeżeli logThreads oraz threading:
            self.thread = threading.get_ident()
            self.threadName = threading.current_thread().name
        inaczej: # pragma: no cover
            self.thread = Nic
            self.threadName = Nic
        jeżeli nie logMultiprocessing: # pragma: no cover
            self.processName = Nic
        inaczej:
            self.processName = 'MainProcess'
            mp = sys.modules.get('multiprocessing')
            jeżeli mp jest nie Nic:
                # Errors may occur jeżeli multiprocessing has nie finished loading
                # yet - e.g. jeżeli a custom zaimportuj hook causes third-party code
                # to run when multiprocessing calls import. See issue 8200
                # dla an example
                spróbuj:
                    self.processName = mp.current_process().name
                wyjąwszy Exception: #pragma: no cover
                    dalej
        jeżeli logProcesses oraz hasattr(os, 'getpid'):
            self.process = os.getpid()
        inaczej:
            self.process = Nic

    def __str__(self):
        zwróć '<LogRecord: %s, %s, %s, %s, "%s">'%(self.name, self.levelno,
            self.pathname, self.lineno, self.msg)

    __repr__ = __str__

    def getMessage(self):
        """
        Return the message dla this LogRecord.

        Return the message dla this LogRecord after merging any user-supplied
        arguments przy the message.
        """
        msg = str(self.msg)
        jeżeli self.args:
            msg = msg % self.args
        zwróć msg

#
#   Determine which klasa to use when instantiating log records.
#
_logRecordFactory = LogRecord

def setLogRecordFactory(factory):
    """
    Set the factory to be used when instantiating a log record.

    :param factory: A callable which will be called to instantiate
    a log record.
    """
    global _logRecordFactory
    _logRecordFactory = factory

def getLogRecordFactory():
    """
    Return the factory to be used when instantiating a log record.
    """

    zwróć _logRecordFactory

def makeLogRecord(dict):
    """
    Make a LogRecord whose attributes are defined by the specified dictionary,
    This function jest useful dla converting a logging event received over
    a socket connection (which jest sent jako a dictionary) into a LogRecord
    instance.
    """
    rv = _logRecordFactory(Nic, Nic, "", 0, "", (), Nic, Nic)
    rv.__dict__.update(dict)
    zwróć rv

#---------------------------------------------------------------------------
#   Formatter classes oraz functions
#---------------------------------------------------------------------------

klasa PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'

    def __init__(self, fmt):
        self._fmt = fmt albo self.default_format

    def usesTime(self):
        zwróć self._fmt.find(self.asctime_search) >= 0

    def format(self, record):
        zwróć self._fmt % record.__dict__

klasa StrFormatStyle(PercentStyle):
    default_format = '{message}'
    asctime_format = '{asctime}'
    asctime_search = '{asctime'

    def format(self, record):
        zwróć self._fmt.format(**record.__dict__)


klasa StringTemplateStyle(PercentStyle):
    default_format = '${message}'
    asctime_format = '${asctime}'
    asctime_search = '${asctime}'

    def __init__(self, fmt):
        self._fmt = fmt albo self.default_format
        self._tpl = Template(self._fmt)

    def usesTime(self):
        fmt = self._fmt
        zwróć fmt.find('$asctime') >= 0 albo fmt.find(self.asctime_format) >= 0

    def format(self, record):
        zwróć self._tpl.substitute(**record.__dict__)

BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"

_STYLES = {
    '%': (PercentStyle, BASIC_FORMAT),
    '{': (StrFormatStyle, '{levelname}:{name}:{message}'),
    '$': (StringTemplateStyle, '${levelname}:${name}:${message}'),
}

klasa Formatter(object):
    """
    Formatter instances are used to convert a LogRecord to text.

    Formatters need to know how a LogRecord jest constructed. They are
    responsible dla converting a LogRecord to (usually) a string which can
    be interpreted by either a human albo an external system. The base Formatter
    allows a formatting string to be specified. If none jest supplied, the
    default value of "%s(message)" jest used.

    The Formatter can be initialized przy a format string which makes use of
    knowledge of the LogRecord attributes - e.g. the default value mentioned
    above makes use of the fact that the user's message oraz arguments are pre-
    formatted into a LogRecord's message attribute. Currently, the useful
    attributes w a LogRecord are described by:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level dla the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level dla the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (jeżeli available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (jeżeli available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        zwróć value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time w milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (jeżeli available)
    %(threadName)s      Thread name (jeżeli available)
    %(process)d         Process ID (jeżeli available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record jest emitted
    """

    converter = time.localtime

    def __init__(self, fmt=Nic, datefmt=Nic, style='%'):
        """
        Initialize the formatter przy specified format strings.

        Initialize the formatter either przy the specified format string, albo a
        default jako described above. Allow dla specialized date formatting with
        the optional datefmt argument (jeżeli omitted, you get the ISO8601 format).

        Use a style parameter of '%', '{' albo '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting albo
        :class:`string.Template` formatting w your format string.

        .. versionchanged: 3.2
           Added the ``style`` parameter.
        """
        jeżeli style nie w _STYLES:
            podnieś ValueError('Style must be one of: %s' % ','.join(
                             _STYLES.keys()))
        self._style = _STYLES[style][0](fmt)
        self._fmt = self._style._fmt
        self.datefmt = datefmt

    default_time_format = '%Y-%m-%d %H:%M:%S'
    default_msec_format = '%s,%03d'

    def formatTime(self, record, datefmt=Nic):
        """
        Return the creation time of the specified LogRecord jako formatted text.

        This method should be called z format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        w formatters to provide dla any specific requirement, but the
        basic behaviour jest jako follows: jeżeli datefmt (a string) jest specified,
        it jest used przy time.strftime() to format the creation time of the
        record. Otherwise, the ISO8601 format jest used. The resulting
        string jest returned. This function uses a user-configurable function
        to convert the creation time to a tuple. By default, time.localtime()
        jest used; to change this dla a particular formatter instance, set the
        'converter' attribute to a function przy the same signature as
        time.localtime() albo time.gmtime(). To change it dla all formatters,
        dla example jeżeli you want all logging times to be shown w GMT,
        set the 'converter' attribute w the Formatter class.
        """
        ct = self.converter(record.created)
        jeżeli datefmt:
            s = time.strftime(datefmt, ct)
        inaczej:
            t = time.strftime(self.default_time_format, ct)
            s = self.default_msec_format % (t, record.msecs)
        zwróć s

    def formatException(self, ei):
        """
        Format oraz zwróć the specified exception information jako a string.

        This default implementation just uses
        traceback.print_exception()
        """
        sio = io.StringIO()
        tb = ei[2]
        # See issues #9427, #1553375. Commented out dla now.
        #jeżeli getattr(self, 'fullstack', Nieprawda):
        #    traceback.print_stack(tb.tb_frame.f_back, file=sio)
        traceback.print_exception(ei[0], ei[1], tb, Nic, sio)
        s = sio.getvalue()
        sio.close()
        jeżeli s[-1:] == "\n":
            s = s[:-1]
        zwróć s

    def usesTime(self):
        """
        Check jeżeli the format uses the creation time of the record.
        """
        zwróć self._style.usesTime()

    def formatMessage(self, record):
        zwróć self._style.format(record)

    def formatStack(self, stack_info):
        """
        This method jest provided jako an extension point dla specialized
        formatting of stack information.

        The input data jest a string jako returned z a call to
        :func:`traceback.print_stack`, but przy the last trailing newline
        removed.

        The base implementation just returns the value dalejed in.
        """
        zwróć stack_info

    def format(self, record):
        """
        Format the specified record jako text.

        The record's attribute dictionary jest used jako the operand to a
        string formatting operation which uzyskajs the returned string.
        Before formatting the dictionary, a couple of preparatory steps
        are carried out. The message attribute of the record jest computed
        using LogRecord.getMessage(). If the formatting string uses the
        time (as determined by a call to usesTime(), formatTime() jest
        called to format the event time. If there jest exception information,
        it jest formatted using formatException() oraz appended to the message.
        """
        record.message = record.getMessage()
        jeżeli self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        jeżeli record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            jeżeli nie record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        jeżeli record.exc_text:
            jeżeli s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        jeżeli record.stack_info:
            jeżeli s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        zwróć s

#
#   The default formatter to use when no other jest specified
#
_defaultFormatter = Formatter()

klasa BufferingFormatter(object):
    """
    A formatter suitable dla formatting a number of records.
    """
    def __init__(self, linefmt=Nic):
        """
        Optionally specify a formatter which will be used to format each
        individual record.
        """
        jeżeli linefmt:
            self.linefmt = linefmt
        inaczej:
            self.linefmt = _defaultFormatter

    def formatHeader(self, records):
        """
        Return the header string dla the specified records.
        """
        zwróć ""

    def formatFooter(self, records):
        """
        Return the footer string dla the specified records.
        """
        zwróć ""

    def format(self, records):
        """
        Format the specified records oraz zwróć the result jako a string.
        """
        rv = ""
        jeżeli len(records) > 0:
            rv = rv + self.formatHeader(records)
            dla record w records:
                rv = rv + self.linefmt.format(record)
            rv = rv + self.formatFooter(records)
        zwróć rv

#---------------------------------------------------------------------------
#   Filter classes oraz functions
#---------------------------------------------------------------------------

klasa Filter(object):
    """
    Filter instances are used to perform arbitrary filtering of LogRecords.

    Loggers oraz Handlers can optionally use Filter instances to filter
    records jako desired. The base filter klasa only allows events which are
    below a certain point w the logger hierarchy. For example, a filter
    initialized przy "A.B" will allow events logged by loggers "A.B",
    "A.B.C", "A.B.C.D", "A.B.D" etc. but nie "A.BB", "B.A.B" etc. If
    initialized przy the empty string, all events are dalejed.
    """
    def __init__(self, name=''):
        """
        Initialize a filter.

        Initialize przy the name of the logger which, together przy its
        children, will have its events allowed through the filter. If no
        name jest specified, allow every event.
        """
        self.name = name
        self.nlen = len(name)

    def filter(self, record):
        """
        Determine jeżeli the specified record jest to be logged.

        Is the specified record to be logged? Returns 0 dla no, nonzero for
        yes. If deemed appropriate, the record may be modified in-place.
        """
        jeżeli self.nlen == 0:
            zwróć Prawda
        albo_inaczej self.name == record.name:
            zwróć Prawda
        albo_inaczej record.name.find(self.name, 0, self.nlen) != 0:
            zwróć Nieprawda
        zwróć (record.name[self.nlen] == ".")

klasa Filterer(object):
    """
    A base klasa dla loggers oraz handlers which allows them to share
    common code.
    """
    def __init__(self):
        """
        Initialize the list of filters to be an empty list.
        """
        self.filters = []

    def addFilter(self, filter):
        """
        Add the specified filter to this handler.
        """
        jeżeli nie (filter w self.filters):
            self.filters.append(filter)

    def removeFilter(self, filter):
        """
        Remove the specified filter z this handler.
        """
        jeżeli filter w self.filters:
            self.filters.remove(filter)

    def filter(self, record):
        """
        Determine jeżeli a record jest loggable by consulting all the filters.

        The default jest to allow the record to be logged; any filter can veto
        this oraz the record jest then dropped. Returns a zero value jeżeli a record
        jest to be dropped, inaczej non-zero.

        .. versionchanged: 3.2

           Allow filters to be just callables.
        """
        rv = Prawda
        dla f w self.filters:
            jeżeli hasattr(f, 'filter'):
                result = f.filter(record)
            inaczej:
                result = f(record) # assume callable - will podnieś jeżeli nie
            jeżeli nie result:
                rv = Nieprawda
                przerwij
        zwróć rv

#---------------------------------------------------------------------------
#   Handler classes oraz functions
#---------------------------------------------------------------------------

_handlers = weakref.WeakValueDictionary()  #map of handler names to handlers
_handlerList = [] # added to allow handlers to be removed w reverse of order initialized

def _removeHandlerRef(wr):
    """
    Remove a handler reference z the internal cleanup list.
    """
    # This function can be called during module teardown, when globals are
    # set to Nic. It can also be called z another thread. So we need to
    # pre-emptively grab the necessary globals oraz check jeżeli they're Nic,
    # to prevent race conditions oraz failures during interpreter shutdown.
    acquire, release, handlers = _acquireLock, _releaseLock, _handlerList
    jeżeli acquire oraz release oraz handlers:
        acquire()
        spróbuj:
            jeżeli wr w handlers:
                handlers.remove(wr)
        w_końcu:
            release()

def _addHandlerRef(handler):
    """
    Add a handler to the internal cleanup list using a weak reference.
    """
    _acquireLock()
    spróbuj:
        _handlerList.append(weakref.ref(handler, _removeHandlerRef))
    w_końcu:
        _releaseLock()

klasa Handler(Filterer):
    """
    Handler instances dispatch logging events to specific destinations.

    The base handler class. Acts jako a placeholder which defines the Handler
    interface. Handlers can optionally use Formatter instances to format
    records jako desired. By default, no formatter jest specified; w this case,
    the 'raw' message jako determined by record.message jest logged.
    """
    def __init__(self, level=NOTSET):
        """
        Initializes the instance - basically setting the formatter to Nic
        oraz the filter list to empty.
        """
        Filterer.__init__(self)
        self._name = Nic
        self.level = _checkLevel(level)
        self.formatter = Nic
        # Add the handler to the global _handlerList (dla cleanup on shutdown)
        _addHandlerRef(self)
        self.createLock()

    def get_name(self):
        zwróć self._name

    def set_name(self, name):
        _acquireLock()
        spróbuj:
            jeżeli self._name w _handlers:
                usuń _handlers[self._name]
            self._name = name
            jeżeli name:
                _handlers[name] = self
        w_końcu:
            _releaseLock()

    name = property(get_name, set_name)

    def createLock(self):
        """
        Acquire a thread lock dla serializing access to the underlying I/O.
        """
        jeżeli threading:
            self.lock = threading.RLock()
        inaczej: #pragma: no cover
            self.lock = Nic

    def acquire(self):
        """
        Acquire the I/O thread lock.
        """
        jeżeli self.lock:
            self.lock.acquire()

    def release(self):
        """
        Release the I/O thread lock.
        """
        jeżeli self.lock:
            self.lock.release()

    def setLevel(self, level):
        """
        Set the logging level of this handler.  level must be an int albo a str.
        """
        self.level = _checkLevel(level)

    def format(self, record):
        """
        Format the specified record.

        If a formatter jest set, use it. Otherwise, use the default formatter
        dla the module.
        """
        jeżeli self.formatter:
            fmt = self.formatter
        inaczej:
            fmt = _defaultFormatter
        zwróć fmt.format(record)

    def emit(self, record):
        """
        Do whatever it takes to actually log the specified logging record.

        This version jest intended to be implemented by subclasses oraz so
        podnieśs a NotImplementedError.
        """
        podnieś NotImplementedError('emit must be implemented '
                                  'by Handler subclasses')

    def handle(self, record):
        """
        Conditionally emit the specified logging record.

        Emission depends on filters which may have been added to the handler.
        Wrap the actual emission of the record przy acquisition/release of
        the I/O thread lock. Returns whether the filter dalejed the record for
        emission.
        """
        rv = self.filter(record)
        jeżeli rv:
            self.acquire()
            spróbuj:
                self.emit(record)
            w_końcu:
                self.release()
        zwróć rv

    def setFormatter(self, fmt):
        """
        Set the formatter dla this handler.
        """
        self.formatter = fmt

    def flush(self):
        """
        Ensure all logging output has been flushed.

        This version does nothing oraz jest intended to be implemented by
        subclasses.
        """
        dalej

    def close(self):
        """
        Tidy up any resources used by the handler.

        This version removes the handler z an internal map of handlers,
        _handlers, which jest used dla handler lookup by name. Subclasses
        should ensure that this gets called z overridden close()
        methods.
        """
        #get the module data lock, jako we're updating a shared structure.
        _acquireLock()
        spróbuj:    #unlikely to podnieś an exception, but you never know...
            jeżeli self._name oraz self._name w _handlers:
                usuń _handlers[self._name]
        w_końcu:
            _releaseLock()

    def handleError(self, record):
        """
        Handle errors which occur during an emit() call.

        This method should be called z handlers when an exception jest
        encountered during an emit() call. If podnieśExceptions jest false,
        exceptions get silently ignored. This jest what jest mostly wanted
        dla a logging system - most users will nie care about errors w
        the logging system, they are more interested w application errors.
        You could, however, replace this przy a custom handler jeżeli you wish.
        The record which was being processed jest dalejed w to this method.
        """
        jeżeli podnieśExceptions oraz sys.stderr:  # see issue 13807
            t, v, tb = sys.exc_info()
            spróbuj:
                sys.stderr.write('--- Logging error ---\n')
                traceback.print_exception(t, v, tb, Nic, sys.stderr)
                sys.stderr.write('Call stack:\n')
                # Walk the stack frame up until we're out of logging,
                # so jako to print the calling context.
                frame = tb.tb_frame
                dopóki (frame oraz os.path.dirname(frame.f_code.co_filename) ==
                       __path__[0]):
                    frame = frame.f_back
                jeżeli frame:
                    traceback.print_stack(frame, file=sys.stderr)
                inaczej:
                    # couldn't find the right stack frame, dla some reason
                    sys.stderr.write('Logged z file %s, line %s\n' % (
                                     record.filename, record.lineno))
                # Issue 18671: output logging message oraz arguments
                spróbuj:
                    sys.stderr.write('Message: %r\n'
                                     'Arguments: %s\n' % (record.msg,
                                                          record.args))
                wyjąwszy Exception:
                    sys.stderr.write('Unable to print the message oraz arguments'
                                     ' - possible formatting error.\nUse the'
                                     ' traceback above to help find the error.\n'
                                    )
            wyjąwszy OSError: #pragma: no cover
                dalej    # see issue 5971
            w_końcu:
                usuń t, v, tb

klasa StreamHandler(Handler):
    """
    A handler klasa which writes logging records, appropriately formatted,
    to a stream. Note that this klasa does nie close the stream, as
    sys.stdout albo sys.stderr may be used.
    """

    terminator = '\n'

    def __init__(self, stream=Nic):
        """
        Initialize the handler.

        If stream jest nie specified, sys.stderr jest used.
        """
        Handler.__init__(self)
        jeżeli stream jest Nic:
            stream = sys.stderr
        self.stream = stream

    def flush(self):
        """
        Flushes the stream.
        """
        self.acquire()
        spróbuj:
            jeżeli self.stream oraz hasattr(self.stream, "flush"):
                self.stream.flush()
        w_końcu:
            self.release()

    def emit(self, record):
        """
        Emit a record.

        If a formatter jest specified, it jest used to format the record.
        The record jest then written to the stream przy a trailing newline.  If
        exception information jest present, it jest formatted using
        traceback.print_exception oraz appended to the stream.  If the stream
        has an 'encoding' attribute, it jest used to determine how to do the
        output to the stream.
        """
        spróbuj:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        wyjąwszy Exception:
            self.handleError(record)

klasa FileHandler(StreamHandler):
    """
    A handler klasa which writes formatted logging records to disk files.
    """
    def __init__(self, filename, mode='a', encoding=Nic, delay=Nieprawda):
        """
        Open the specified file oraz use it jako the stream dla logging.
        """
        #keep the absolute path, otherwise derived classes which use this
        #may come a cropper when the current directory changes
        self.baseFilename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        jeżeli delay:
            #We don't open the stream, but we still need to call the
            #Handler constructor to set level, formatter, lock etc.
            Handler.__init__(self)
            self.stream = Nic
        inaczej:
            StreamHandler.__init__(self, self._open())

    def close(self):
        """
        Closes the stream.
        """
        self.acquire()
        spróbuj:
            spróbuj:
                jeżeli self.stream:
                    spróbuj:
                        self.flush()
                    w_końcu:
                        stream = self.stream
                        self.stream = Nic
                        jeżeli hasattr(stream, "close"):
                            stream.close()
            w_końcu:
                # Issue #19523: call unconditionally to
                # prevent a handler leak when delay jest set
                StreamHandler.close(self)
        w_końcu:
            self.release()

    def _open(self):
        """
        Open the current base file przy the (original) mode oraz encoding.
        Return the resulting stream.
        """
        zwróć open(self.baseFilename, self.mode, encoding=self.encoding)

    def emit(self, record):
        """
        Emit a record.

        If the stream was nie opened because 'delay' was specified w the
        constructor, open it before calling the superclass's emit.
        """
        jeżeli self.stream jest Nic:
            self.stream = self._open()
        StreamHandler.emit(self, record)

klasa _StderrHandler(StreamHandler):
    """
    This klasa jest like a StreamHandler using sys.stderr, but always uses
    whatever sys.stderr jest currently set to rather than the value of
    sys.stderr at handler construction time.
    """
    def __init__(self, level=NOTSET):
        """
        Initialize the handler.
        """
        Handler.__init__(self, level)

    @property
    def stream(self):
        zwróć sys.stderr


_defaultLastResort = _StderrHandler(WARNING)
lastResort = _defaultLastResort

#---------------------------------------------------------------------------
#   Manager classes oraz functions
#---------------------------------------------------------------------------

klasa PlaceHolder(object):
    """
    PlaceHolder instances are used w the Manager logger hierarchy to take
    the place of nodes dla which no loggers have been defined. This klasa jest
    intended dla internal use only oraz nie jako part of the public API.
    """
    def __init__(self, alogger):
        """
        Initialize przy the specified logger being a child of this placeholder.
        """
        self.loggerMap = { alogger : Nic }

    def append(self, alogger):
        """
        Add the specified logger jako a child of this placeholder.
        """
        jeżeli alogger nie w self.loggerMap:
            self.loggerMap[alogger] = Nic

#
#   Determine which klasa to use when instantiating loggers.
#

def setLoggerClass(klass):
    """
    Set the klasa to be used when instantiating a logger. The klasa should
    define __init__() such that only a name argument jest required, oraz the
    __init__() should call Logger.__init__()
    """
    jeżeli klass != Logger:
        jeżeli nie issubclass(klass, Logger):
            podnieś TypeError("logger nie derived z logging.Logger: "
                            + klass.__name__)
    global _loggerClass
    _loggerClass = klass

def getLoggerClass():
    """
    Return the klasa to be used when instantiating a logger.
    """
    zwróć _loggerClass

klasa Manager(object):
    """
    There jest [under normal circumstances] just one Manager instance, which
    holds the hierarchy of loggers.
    """
    def __init__(self, rootnode):
        """
        Initialize the manager przy the root node of the logger hierarchy.
        """
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = Nieprawda
        self.loggerDict = {}
        self.loggerClass = Nic
        self.logRecordFactory = Nic

    def getLogger(self, name):
        """
        Get a logger przy the specified name (channel name), creating it
        jeżeli it doesn't yet exist. This name jest a dot-separated hierarchical
        name, such jako "a", "a.b", "a.b.c" albo similar.

        If a PlaceHolder existed dla the specified name [i.e. the logger
        didn't exist but a child of it did], replace it przy the created
        logger oraz fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = Nic
        jeżeli nie isinstance(name, str):
            podnieś TypeError('A logger name must be a string')
        _acquireLock()
        spróbuj:
            jeżeli name w self.loggerDict:
                rv = self.loggerDict[name]
                jeżeli isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass albo _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            inaczej:
                rv = (self.loggerClass albo _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        w_końcu:
            _releaseLock()
        zwróć rv

    def setLoggerClass(self, klass):
        """
        Set the klasa to be used when instantiating a logger przy this Manager.
        """
        jeżeli klass != Logger:
            jeżeli nie issubclass(klass, Logger):
                podnieś TypeError("logger nie derived z logging.Logger: "
                                + klass.__name__)
        self.loggerClass = klass

    def setLogRecordFactory(self, factory):
        """
        Set the factory to be used when instantiating a log record przy this
        Manager.
        """
        self.logRecordFactory = factory

    def _fixupParents(self, alogger):
        """
        Ensure that there are either loggers albo placeholders all the way
        z the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = Nic
        dopóki (i > 0) oraz nie rv:
            substr = name[:i]
            jeżeli substr nie w self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            inaczej:
                obj = self.loggerDict[substr]
                jeżeli isinstance(obj, Logger):
                    rv = obj
                inaczej:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        jeżeli nie rv:
            rv = self.root
        alogger.parent = rv

    def _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        dla c w ph.loggerMap.keys():
            #The jeżeli means ... jeżeli nie c.parent.name.startswith(nm)
            jeżeli c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger

#---------------------------------------------------------------------------
#   Logger classes oraz functions
#---------------------------------------------------------------------------

klasa Logger(Filterer):
    """
    Instances of the Logger klasa represent a single logging channel. A
    "logging channel" indicates an area of an application. Exactly how an
    "area" jest defined jest up to the application developer. Since an
    application can have any number of areas, logging channels are identified
    by a unique string. Application areas can be nested (e.g. an area
    of "input processing" might include sub-areas "read CSV files", "read
    XLS files" oraz "read Gnumeric files"). To cater dla this natural nesting,
    channel names are organized into a namespace hierarchy where levels are
    separated by periods, much like the Java albo Python package namespace. So
    w the instance given above, channel names might be "input" dla the upper
    level, oraz "input.csv", "input.xls" oraz "input.gnu" dla the sub-levels.
    There jest no arbitrary limit to the depth of nesting.
    """
    def __init__(self, name, level=NOTSET):
        """
        Initialize the logger przy a name oraz an optional level.
        """
        Filterer.__init__(self)
        self.name = name
        self.level = _checkLevel(level)
        self.parent = Nic
        self.propagate = Prawda
        self.handlers = []
        self.disabled = Nieprawda

    def setLevel(self, level):
        """
        Set the logging level of this logger.  level must be an int albo a str.
        """
        self.level = _checkLevel(level)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' przy severity 'DEBUG'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        jeżeli self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' przy severity 'INFO'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        jeżeli self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' przy severity 'WARNING'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        jeżeli self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method jest deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' przy severity 'ERROR'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        jeżeli self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=Prawda, **kwargs):
        """
        Convenience method dla logging an ERROR przy exception information.
        """
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' przy severity 'CRITICAL'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        jeżeli self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    def log(self, level, msg, *args, **kwargs):
        """
        Log 'msg % args' przy the integer severity 'level'.

        To dalej exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        jeżeli nie isinstance(level, int):
            jeżeli podnieśExceptions:
                podnieś TypeError("level must be an integer")
            inaczej:
                zwróć
        jeżeli self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    def findCaller(self, stack_info=Nieprawda):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number oraz function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns Nic if
        #IronPython isn't run przy -X:Frames.
        jeżeli f jest nie Nic:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", Nic
        dopóki hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            jeżeli filename == _srcfile:
                f = f.f_back
                kontynuuj
            sinfo = Nic
            jeżeli stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                jeżeli sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            przerwij
        zwróć rv

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=Nic, extra=Nic, sinfo=Nic):
        """
        A factory method which can be overridden w subclasses to create
        specialized LogRecords.
        """
        rv = _logRecordFactory(name, level, fn, lno, msg, args, exc_info, func,
                             sinfo)
        jeżeli extra jest nie Nic:
            dla key w extra:
                jeżeli (key w ["message", "asctime"]) albo (key w rv.__dict__):
                    podnieś KeyError("Attempt to overwrite %r w LogRecord" % key)
                rv.__dict__[key] = extra[key]
        zwróć rv

    def _log(self, level, msg, args, exc_info=Nic, extra=Nic, stack_info=Nieprawda):
        """
        Low-level logging routine which creates a LogRecord oraz then calls
        all the handlers of this logger to handle the record.
        """
        sinfo = Nic
        jeżeli _srcfile:
            #IronPython doesn't track Python frames, so findCaller podnieśs an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            spróbuj:
                fn, lno, func, sinfo = self.findCaller(stack_info)
            wyjąwszy ValueError: # pragma: no cover
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        inaczej: # pragma: no cover
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        jeżeli exc_info:
            jeżeli isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            albo_inaczej nie isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args,
                                 exc_info, func, extra, sinfo)
        self.handle(record)

    def handle(self, record):
        """
        Call the handlers dla the specified record.

        This method jest used dla unpickled records received z a socket, as
        well jako those created locally. Logger-level filtering jest applied.
        """
        jeżeli (nie self.disabled) oraz self.filter(record):
            self.callHandlers(record)

    def addHandler(self, hdlr):
        """
        Add the specified handler to this logger.
        """
        _acquireLock()
        spróbuj:
            jeżeli nie (hdlr w self.handlers):
                self.handlers.append(hdlr)
        w_końcu:
            _releaseLock()

    def removeHandler(self, hdlr):
        """
        Remove the specified handler z this logger.
        """
        _acquireLock()
        spróbuj:
            jeżeli hdlr w self.handlers:
                self.handlers.remove(hdlr)
        w_końcu:
            _releaseLock()

    def hasHandlers(self):
        """
        See jeżeli this logger has any handlers configured.

        Loop through all handlers dla this logger oraz its parents w the
        logger hierarchy. Return Prawda jeżeli a handler was found, inaczej Nieprawda.
        Stop searching up the hierarchy whenever a logger przy the "propagate"
        attribute set to zero jest found - that will be the last logger which
        jest checked dla the existence of handlers.
        """
        c = self
        rv = Nieprawda
        dopóki c:
            jeżeli c.handlers:
                rv = Prawda
                przerwij
            jeżeli nie c.propagate:
                przerwij
            inaczej:
                c = c.parent
        zwróć rv

    def callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers dla this logger oraz its parents w the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger przy the "propagate" attribute set to zero jest found - that
        will be the last logger whose handlers are called.
        """
        c = self
        found = 0
        dopóki c:
            dla hdlr w c.handlers:
                found = found + 1
                jeżeli record.levelno >= hdlr.level:
                    hdlr.handle(record)
            jeżeli nie c.propagate:
                c = Nic    #break out
            inaczej:
                c = c.parent
        jeżeli (found == 0):
            jeżeli lastResort:
                jeżeli record.levelno >= lastResort.level:
                    lastResort.handle(record)
            albo_inaczej podnieśExceptions oraz nie self.manager.emittedNoHandlerWarning:
                sys.stderr.write("No handlers could be found dla logger"
                                 " \"%s\"\n" % self.name)
                self.manager.emittedNoHandlerWarning = Prawda

    def getEffectiveLevel(self):
        """
        Get the effective level dla this logger.

        Loop through this logger oraz its parents w the logger hierarchy,
        looking dla a non-zero logging level. Return the first one found.
        """
        logger = self
        dopóki logger:
            jeżeli logger.level:
                zwróć logger.level
            logger = logger.parent
        zwróć NOTSET

    def isEnabledFor(self, level):
        """
        Is this logger enabled dla level 'level'?
        """
        jeżeli self.manager.disable >= level:
            zwróć Nieprawda
        zwróć level >= self.getEffectiveLevel()

    def getChild(self, suffix):
        """
        Get a logger which jest a descendant to this one.

        This jest a convenience method, such that

        logging.getLogger('abc').getChild('def.ghi')

        jest the same as

        logging.getLogger('abc.def.ghi')

        It's useful, dla example, when the parent logger jest named using
        __name__ rather than a literal string.
        """
        jeżeli self.root jest nie self:
            suffix = '.'.join((self.name, suffix))
        zwróć self.manager.getLogger(suffix)

klasa RootLogger(Logger):
    """
    A root logger jest nie that different to any other logger, wyjąwszy that
    it must have a logging level oraz there jest only one instance of it w
    the hierarchy.
    """
    def __init__(self, level):
        """
        Initialize the logger przy the name "root".
        """
        Logger.__init__(self, "root", level)

_loggerClass = Logger

klasa LoggerAdapter(object):
    """
    An adapter dla loggers which makes it easier to specify contextual
    information w logging output.
    """

    def __init__(self, logger, extra):
        """
        Initialize the adapter przy a logger oraz a dict-like object which
        provides contextual information. This constructor signature allows
        easy stacking of LoggerAdapters, jeżeli so desired.

        You can effectively dalej keyword arguments jako shown w the
        following example:

        adapter = LoggerAdapter(someLogger, dict(p1=v1, p2="v2"))
        """
        self.logger = logger
        self.extra = extra

    def process(self, msg, kwargs):
        """
        Process the logging message oraz keyword arguments dalejed w to
        a logging call to insert contextual information. You can either
        manipulate the message itself, the keyword args albo both. Return
        the message oraz kwargs modified (or not) to suit your needs.

        Normally, you'll only need to override this one method w a
        LoggerAdapter subclass dla your specific needs.
        """
        kwargs["extra"] = self.extra
        zwróć msg, kwargs

    #
    # Boilerplate convenience methods
    #
    def debug(self, msg, *args, **kwargs):
        """
        Delegate a debug call to the underlying logger.
        """
        self.log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Delegate an info call to the underlying logger.
        """
        self.log(INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Delegate a warning call to the underlying logger.
        """
        self.log(WARNING, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method jest deprecated, "
            "use 'warning' instead", DeprecationWarning, 2)
        self.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Delegate an error call to the underlying logger.
        """
        self.log(ERROR, msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=Prawda, **kwargs):
        """
        Delegate an exception call to the underlying logger.
        """
        self.log(ERROR, msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Delegate a critical call to the underlying logger.
        """
        self.log(CRITICAL, msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        """
        Delegate a log call to the underlying logger, after adding
        contextual information z this adapter instance.
        """
        jeżeli self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, msg, args, **kwargs)

    def isEnabledFor(self, level):
        """
        Is this logger enabled dla level 'level'?
        """
        jeżeli self.logger.manager.disable >= level:
            zwróć Nieprawda
        zwróć level >= self.getEffectiveLevel()

    def setLevel(self, level):
        """
        Set the specified level on the underlying logger.
        """
        self.logger.setLevel(level)

    def getEffectiveLevel(self):
        """
        Get the effective level dla the underlying logger.
        """
        zwróć self.logger.getEffectiveLevel()

    def hasHandlers(self):
        """
        See jeżeli the underlying logger has any handlers.
        """
        zwróć self.logger.hasHandlers()

root = RootLogger(WARNING)
Logger.root = root
Logger.manager = Manager(Logger.root)

#---------------------------------------------------------------------------
# Configuration classes oraz functions
#---------------------------------------------------------------------------

def basicConfig(**kwargs):
    """
    Do basic configuration dla the logging system.

    This function does nothing jeżeli the root logger already has handlers
    configured. It jest a convenience method intended dla use by simple scripts
    to do one-shot configuration of the logging package.

    The default behaviour jest to create a StreamHandler which writes to
    sys.stderr, set a formatter using the BASIC_FORMAT format string, oraz
    add the handler to the root logger.

    A number of optional keyword arguments may be specified, which can alter
    the default behaviour.

    filename  Specifies that a FileHandler be created, using the specified
              filename, rather than a StreamHandler.
    filemode  Specifies the mode to open the file, jeżeli filename jest specified
              (jeżeli filemode jest unspecified, it defaults to 'a').
    format    Use the specified format string dla the handler.
    datefmt   Use the specified date/time format.
    style     If a format string jest specified, use this to specify the
              type of format string (possible values '%', '{', '$', for
              %-formatting, :meth:`str.format` oraz :class:`string.Template`
              - defaults to '%').
    level     Set the root logger level to the specified level.
    stream    Use the specified stream to initialize the StreamHandler. Note
              that this argument jest incompatible przy 'filename' - jeżeli both
              are present, 'stream' jest ignored.
    handlers  If specified, this should be an iterable of already created
              handlers, which will be added to the root handler. Any handler
              w the list which does nie have a formatter assigned will be
              assigned the formatter created w this function.

    Note that you could specify a stream created using open(filename, mode)
    rather than dalejing the filename oraz mode in. However, it should be
    remembered that StreamHandler does nie close its stream (since it may be
    using sys.stdout albo sys.stderr), whereas FileHandler closes its stream
    when the handler jest closed.

    .. versionchanged:: 3.2
       Added the ``style`` parameter.

    .. versionchanged:: 3.3
       Added the ``handlers`` parameter. A ``ValueError`` jest now thrown for
       incompatible arguments (e.g. ``handlers`` specified together with
       ``filename``/``filemode``, albo ``filename``/``filemode`` specified
       together przy ``stream``, albo ``handlers`` specified together with
       ``stream``.
    """
    # Add thread safety w case someone mistakenly calls
    # basicConfig() z multiple threads
    _acquireLock()
    spróbuj:
        jeżeli len(root.handlers) == 0:
            handlers = kwargs.pop("handlers", Nic)
            jeżeli handlers jest Nic:
                jeżeli "stream" w kwargs oraz "filename" w kwargs:
                    podnieś ValueError("'stream' oraz 'filename' should nie be "
                                     "specified together")
            inaczej:
                jeżeli "stream" w kwargs albo "filename" w kwargs:
                    podnieś ValueError("'stream' albo 'filename' should nie be "
                                     "specified together przy 'handlers'")
            jeżeli handlers jest Nic:
                filename = kwargs.pop("filename", Nic)
                mode = kwargs.pop("filemode", 'a')
                jeżeli filename:
                    h = FileHandler(filename, mode)
                inaczej:
                    stream = kwargs.pop("stream", Nic)
                    h = StreamHandler(stream)
                handlers = [h]
            dfs = kwargs.pop("datefmt", Nic)
            style = kwargs.pop("style", '%')
            jeżeli style nie w _STYLES:
                podnieś ValueError('Style must be one of: %s' % ','.join(
                                 _STYLES.keys()))
            fs = kwargs.pop("format", _STYLES[style][1])
            fmt = Formatter(fs, dfs, style)
            dla h w handlers:
                jeżeli h.formatter jest Nic:
                    h.setFormatter(fmt)
                root.addHandler(h)
            level = kwargs.pop("level", Nic)
            jeżeli level jest nie Nic:
                root.setLevel(level)
            jeżeli kwargs:
                keys = ', '.join(kwargs.keys())
                podnieś ValueError('Unrecognised argument(s): %s' % keys)
    w_końcu:
        _releaseLock()

#---------------------------------------------------------------------------
# Utility functions at module level.
# Basically delegate everything to the root logger.
#---------------------------------------------------------------------------

def getLogger(name=Nic):
    """
    Return a logger przy the specified name, creating it jeżeli necessary.

    If no name jest specified, zwróć the root logger.
    """
    jeżeli name:
        zwróć Logger.manager.getLogger(name)
    inaczej:
        zwróć root

def critical(msg, *args, **kwargs):
    """
    Log a message przy severity 'CRITICAL' on the root logger. If the logger
    has no handlers, call basicConfig() to add a console handler przy a
    pre-defined format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.critical(msg, *args, **kwargs)

fatal = critical

def error(msg, *args, **kwargs):
    """
    Log a message przy severity 'ERROR' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler przy a pre-defined
    format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.error(msg, *args, **kwargs)

def exception(msg, *args, exc_info=Prawda, **kwargs):
    """
    Log a message przy severity 'ERROR' on the root logger, przy exception
    information. If the logger has no handlers, basicConfig() jest called to add
    a console handler przy a pre-defined format.
    """
    error(msg, *args, exc_info=exc_info, **kwargs)

def warning(msg, *args, **kwargs):
    """
    Log a message przy severity 'WARNING' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler przy a pre-defined
    format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.warning(msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    warnings.warn("The 'warn' function jest deprecated, "
        "use 'warning' instead", DeprecationWarning, 2)
    warning(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    """
    Log a message przy severity 'INFO' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler przy a pre-defined
    format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    """
    Log a message przy severity 'DEBUG' on the root logger. If the logger has
    no handlers, call basicConfig() to add a console handler przy a pre-defined
    format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.debug(msg, *args, **kwargs)

def log(level, msg, *args, **kwargs):
    """
    Log 'msg % args' przy the integer severity 'level' on the root logger. If
    the logger has no handlers, call basicConfig() to add a console handler
    przy a pre-defined format.
    """
    jeżeli len(root.handlers) == 0:
        basicConfig()
    root.log(level, msg, *args, **kwargs)

def disable(level):
    """
    Disable all logging calls of severity 'level' oraz below.
    """
    root.manager.disable = level

def shutdown(handlerList=_handlerList):
    """
    Perform any cleanup actions w the logging system (e.g. flushing
    buffers).

    Should be called at application exit.
    """
    dla wr w reversed(handlerList[:]):
        #errors might occur, dla example, jeżeli files are locked
        #we just ignore them jeżeli podnieśExceptions jest nie set
        spróbuj:
            h = wr()
            jeżeli h:
                spróbuj:
                    h.acquire()
                    h.flush()
                    h.close()
                wyjąwszy (OSError, ValueError):
                    # Ignore errors which might be caused
                    # because handlers have been closed but
                    # references to them are still around at
                    # application exit.
                    dalej
                w_końcu:
                    h.release()
        wyjąwszy: # ignore everything, jako we're shutting down
            jeżeli podnieśExceptions:
                podnieś
            #inaczej, swallow

#Let's try oraz shutdown automatically on application exit...
zaimportuj atexit
atexit.register(shutdown)

# Null handler

klasa NullHandler(Handler):
    """
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found dla logger XXX" one-off warning. This jest
    important dla library code, which may contain code to log events. If a user
    of the library does nie configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler oraz add it to the top-level logger of the library module albo
    package.
    """
    def handle(self, record):
        """Stub."""

    def emit(self, record):
        """Stub."""

    def createLock(self):
        self.lock = Nic

# Warnings integration

_warnings_showwarning = Nic

def _showwarning(message, category, filename, lineno, file=Nic, line=Nic):
    """
    Implementation of showwarnings which redirects to logging, which will first
    check to see jeżeli the file parameter jest Nic. If a file jest specified, it will
    delegate to the original warnings implementation of showwarning. Otherwise,
    it will call warnings.formatwarning oraz will log the resulting string to a
    warnings logger named "py.warnings" przy level logging.WARNING.
    """
    jeżeli file jest nie Nic:
        jeżeli _warnings_showwarning jest nie Nic:
            _warnings_showwarning(message, category, filename, lineno, file, line)
    inaczej:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = getLogger("py.warnings")
        jeżeli nie logger.handlers:
            logger.addHandler(NullHandler())
        logger.warning("%s", s)

def captureWarnings(capture):
    """
    If capture jest true, redirect all warnings to the logging package.
    If capture jest Nieprawda, ensure that warnings are nie redirected to logging
    but to their original destinations.
    """
    global _warnings_showwarning
    jeżeli capture:
        jeżeli _warnings_showwarning jest Nic:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = _showwarning
    inaczej:
        jeżeli _warnings_showwarning jest nie Nic:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = Nic
