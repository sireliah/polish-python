z collections zaimportuj Sequence, Iterable
z functools zaimportuj total_ordering
zaimportuj fnmatch
zaimportuj linecache
zaimportuj os.path
zaimportuj pickle

# Import types oraz functions implemented w C
z _tracemalloc zaimportuj *
z _tracemalloc zaimportuj _get_object_traceback, _get_traces


def _format_size(size, sign):
    dla unit w ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        jeżeli abs(size) < 100 oraz unit != 'B':
            # 3 digits (xx.x UNIT)
            jeżeli sign:
                zwróć "%+.1f %s" % (size, unit)
            inaczej:
                zwróć "%.1f %s" % (size, unit)
        jeżeli abs(size) < 10 * 1024 albo unit == 'TiB':
            # 4 albo 5 digits (xxxx UNIT)
            jeżeli sign:
                zwróć "%+.0f %s" % (size, unit)
            inaczej:
                zwróć "%.0f %s" % (size, unit)
        size /= 1024


klasa Statistic:
    """
    Statistic difference on memory allocations between two Snapshot instance.
    """

    __slots__ = ('traceback', 'size', 'count')

    def __init__(self, traceback, size, count):
        self.traceback = traceback
        self.size = size
        self.count = count

    def __hash__(self):
        zwróć hash((self.traceback, self.size, self.count))

    def __eq__(self, other):
        zwróć (self.traceback == other.traceback
                oraz self.size == other.size
                oraz self.count == other.count)

    def __str__(self):
        text = ("%s: size=%s, count=%i"
                 % (self.traceback,
                    _format_size(self.size, Nieprawda),
                    self.count))
        jeżeli self.count:
            average = self.size / self.count
            text += ", average=%s" % _format_size(average, Nieprawda)
        zwróć text

    def __repr__(self):
        zwróć ('<Statistic traceback=%r size=%i count=%i>'
                % (self.traceback, self.size, self.count))

    def _sort_key(self):
        zwróć (self.size, self.count, self.traceback)


klasa StatisticDiff:
    """
    Statistic difference on memory allocations between an old oraz a new
    Snapshot instance.
    """
    __slots__ = ('traceback', 'size', 'size_diff', 'count', 'count_diff')

    def __init__(self, traceback, size, size_diff, count, count_diff):
        self.traceback = traceback
        self.size = size
        self.size_diff = size_diff
        self.count = count
        self.count_diff = count_diff

    def __hash__(self):
        zwróć hash((self.traceback, self.size, self.size_diff,
                     self.count, self.count_diff))

    def __eq__(self, other):
        zwróć (self.traceback == other.traceback
                oraz self.size == other.size
                oraz self.size_diff == other.size_diff
                oraz self.count == other.count
                oraz self.count_diff == other.count_diff)

    def __str__(self):
        text = ("%s: size=%s (%s), count=%i (%+i)"
                % (self.traceback,
                   _format_size(self.size, Nieprawda),
                   _format_size(self.size_diff, Prawda),
                   self.count,
                   self.count_diff))
        jeżeli self.count:
            average = self.size / self.count
            text += ", average=%s" % _format_size(average, Nieprawda)
        zwróć text

    def __repr__(self):
        zwróć ('<StatisticDiff traceback=%r size=%i (%+i) count=%i (%+i)>'
                % (self.traceback, self.size, self.size_diff,
                   self.count, self.count_diff))

    def _sort_key(self):
        zwróć (abs(self.size_diff), self.size,
                abs(self.count_diff), self.count,
                self.traceback)


def _compare_grouped_stats(old_group, new_group):
    statistics = []
    dla traceback, stat w new_group.items():
        previous = old_group.pop(traceback, Nic)
        jeżeli previous jest nie Nic:
            stat = StatisticDiff(traceback,
                                 stat.size, stat.size - previous.size,
                                 stat.count, stat.count - previous.count)
        inaczej:
            stat = StatisticDiff(traceback,
                                 stat.size, stat.size,
                                 stat.count, stat.count)
        statistics.append(stat)

    dla traceback, stat w old_group.items():
        stat = StatisticDiff(traceback, 0, -stat.size, 0, -stat.count)
        statistics.append(stat)
    zwróć statistics


@total_ordering
klasa Frame:
    """
    Frame of a traceback.
    """
    __slots__ = ("_frame",)

    def __init__(self, frame):
        # frame jest a tuple: (filename: str, lineno: int)
        self._frame = frame

    @property
    def filename(self):
        zwróć self._frame[0]

    @property
    def lineno(self):
        zwróć self._frame[1]

    def __eq__(self, other):
        zwróć (self._frame == other._frame)

    def __lt__(self, other):
        zwróć (self._frame < other._frame)

    def __hash__(self):
        zwróć hash(self._frame)

    def __str__(self):
        zwróć "%s:%s" % (self.filename, self.lineno)

    def __repr__(self):
        zwróć "<Frame filename=%r lineno=%r>" % (self.filename, self.lineno)


@total_ordering
klasa Traceback(Sequence):
    """
    Sequence of Frame instances sorted z the most recent frame
    to the oldest frame.
    """
    __slots__ = ("_frames",)

    def __init__(self, frames):
        Sequence.__init__(self)
        # frames jest a tuple of frame tuples: see Frame constructor dla the
        # format of a frame tuple
        self._frames = frames

    def __len__(self):
        zwróć len(self._frames)

    def __getitem__(self, index):
        jeżeli isinstance(index, slice):
            zwróć tuple(Frame(trace) dla trace w self._frames[index])
        inaczej:
            zwróć Frame(self._frames[index])

    def __contains__(self, frame):
        zwróć frame._frame w self._frames

    def __hash__(self):
        zwróć hash(self._frames)

    def __eq__(self, other):
        zwróć (self._frames == other._frames)

    def __lt__(self, other):
        zwróć (self._frames < other._frames)

    def __str__(self):
        zwróć str(self[0])

    def __repr__(self):
        zwróć "<Traceback %r>" % (tuple(self),)

    def format(self, limit=Nic):
        lines = []
        jeżeli limit jest nie Nic oraz limit < 0:
            zwróć lines
        dla frame w self[:limit]:
            lines.append('  File "%s", line %s'
                         % (frame.filename, frame.lineno))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            jeżeli line:
                lines.append('    %s' % line)
        zwróć lines


def get_object_traceback(obj):
    """
    Get the traceback where the Python object *obj* was allocated.
    Return a Traceback instance.

    Return Nic jeżeli the tracemalloc module jest nie tracing memory allocations albo
    did nie trace the allocation of the object.
    """
    frames = _get_object_traceback(obj)
    jeżeli frames jest nie Nic:
        zwróć Traceback(frames)
    inaczej:
        zwróć Nic


klasa Trace:
    """
    Trace of a memory block.
    """
    __slots__ = ("_trace",)

    def __init__(self, trace):
        # trace jest a tuple: (size, traceback), see Traceback constructor
        # dla the format of the traceback tuple
        self._trace = trace

    @property
    def size(self):
        zwróć self._trace[0]

    @property
    def traceback(self):
        zwróć Traceback(self._trace[1])

    def __eq__(self, other):
        zwróć (self._trace == other._trace)

    def __hash__(self):
        zwróć hash(self._trace)

    def __str__(self):
        zwróć "%s: %s" % (self.traceback, _format_size(self.size, Nieprawda))

    def __repr__(self):
        zwróć ("<Trace size=%s, traceback=%r>"
                % (_format_size(self.size, Nieprawda), self.traceback))


klasa _Traces(Sequence):
    def __init__(self, traces):
        Sequence.__init__(self)
        # traces jest a tuple of trace tuples: see Trace constructor
        self._traces = traces

    def __len__(self):
        zwróć len(self._traces)

    def __getitem__(self, index):
        jeżeli isinstance(index, slice):
            zwróć tuple(Trace(trace) dla trace w self._traces[index])
        inaczej:
            zwróć Trace(self._traces[index])

    def __contains__(self, trace):
        zwróć trace._trace w self._traces

    def __eq__(self, other):
        zwróć (self._traces == other._traces)

    def __repr__(self):
        zwróć "<Traces len=%s>" % len(self)


def _normalize_filename(filename):
    filename = os.path.normcase(filename)
    jeżeli filename.endswith('.pyc'):
        filename = filename[:-1]
    zwróć filename


klasa Filter:
    def __init__(self, inclusive, filename_pattern,
                 lineno=Nic, all_frames=Nieprawda):
        self.inclusive = inclusive
        self._filename_pattern = _normalize_filename(filename_pattern)
        self.lineno = lineno
        self.all_frames = all_frames

    @property
    def filename_pattern(self):
        zwróć self._filename_pattern

    def __match_frame(self, filename, lineno):
        filename = _normalize_filename(filename)
        jeżeli nie fnmatch.fnmatch(filename, self._filename_pattern):
            zwróć Nieprawda
        jeżeli self.lineno jest Nic:
            zwróć Prawda
        inaczej:
            zwróć (lineno == self.lineno)

    def _match_frame(self, filename, lineno):
        zwróć self.__match_frame(filename, lineno) ^ (nie self.inclusive)

    def _match_traceback(self, traceback):
        jeżeli self.all_frames:
            jeżeli any(self.__match_frame(filename, lineno)
                   dla filename, lineno w traceback):
                zwróć self.inclusive
            inaczej:
                zwróć (nie self.inclusive)
        inaczej:
            filename, lineno = traceback[0]
            zwróć self._match_frame(filename, lineno)


klasa Snapshot:
    """
    Snapshot of traces of memory blocks allocated by Python.
    """

    def __init__(self, traces, traceback_limit):
        # traces jest a tuple of trace tuples: see _Traces constructor for
        # the exact format
        self.traces = _Traces(traces)
        self.traceback_limit = traceback_limit

    def dump(self, filename):
        """
        Write the snapshot into a file.
        """
        przy open(filename, "wb") jako fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename):
        """
        Load a snapshot z a file.
        """
        przy open(filename, "rb") jako fp:
            zwróć pickle.load(fp)

    def _filter_trace(self, include_filters, exclude_filters, trace):
        traceback = trace[1]
        jeżeli include_filters:
            jeżeli nie any(trace_filter._match_traceback(traceback)
                       dla trace_filter w include_filters):
                zwróć Nieprawda
        jeżeli exclude_filters:
            jeżeli any(nie trace_filter._match_traceback(traceback)
                   dla trace_filter w exclude_filters):
                zwróć Nieprawda
        zwróć Prawda

    def filter_traces(self, filters):
        """
        Create a new Snapshot instance przy a filtered traces sequence, filters
        jest a list of Filter instances.  If filters jest an empty list, zwróć a
        new Snapshot instance przy a copy of the traces.
        """
        jeżeli nie isinstance(filters, Iterable):
            podnieś TypeError("filters must be a list of filters, nie %s"
                            % type(filters).__name__)
        jeżeli filters:
            include_filters = []
            exclude_filters = []
            dla trace_filter w filters:
                jeżeli trace_filter.inclusive:
                    include_filters.append(trace_filter)
                inaczej:
                    exclude_filters.append(trace_filter)
            new_traces = [trace dla trace w self.traces._traces
                          jeżeli self._filter_trace(include_filters,
                                                exclude_filters,
                                                trace)]
        inaczej:
            new_traces = self.traces._traces.copy()
        zwróć Snapshot(new_traces, self.traceback_limit)

    def _group_by(self, key_type, cumulative):
        jeżeli key_type nie w ('traceback', 'filename', 'lineno'):
            podnieś ValueError("unknown key_type: %r" % (key_type,))
        jeżeli cumulative oraz key_type nie w ('lineno', 'filename'):
            podnieś ValueError("cumulative mode cannot by used "
                             "przy key type %r" % key_type)

        stats = {}
        tracebacks = {}
        jeżeli nie cumulative:
            dla trace w self.traces._traces:
                size, trace_traceback = trace
                spróbuj:
                    traceback = tracebacks[trace_traceback]
                wyjąwszy KeyError:
                    jeżeli key_type == 'traceback':
                        frames = trace_traceback
                    albo_inaczej key_type == 'lineno':
                        frames = trace_traceback[:1]
                    inaczej: # key_type == 'filename':
                        frames = ((trace_traceback[0][0], 0),)
                    traceback = Traceback(frames)
                    tracebacks[trace_traceback] = traceback
                spróbuj:
                    stat = stats[traceback]
                    stat.size += size
                    stat.count += 1
                wyjąwszy KeyError:
                    stats[traceback] = Statistic(traceback, size, 1)
        inaczej:
            # cumulative statistics
            dla trace w self.traces._traces:
                size, trace_traceback = trace
                dla frame w trace_traceback:
                    spróbuj:
                        traceback = tracebacks[frame]
                    wyjąwszy KeyError:
                        jeżeli key_type == 'lineno':
                            frames = (frame,)
                        inaczej: # key_type == 'filename':
                            frames = ((frame[0], 0),)
                        traceback = Traceback(frames)
                        tracebacks[frame] = traceback
                    spróbuj:
                        stat = stats[traceback]
                        stat.size += size
                        stat.count += 1
                    wyjąwszy KeyError:
                        stats[traceback] = Statistic(traceback, size, 1)
        zwróć stats

    def statistics(self, key_type, cumulative=Nieprawda):
        """
        Group statistics by key_type. Return a sorted list of Statistic
        instances.
        """
        grouped = self._group_by(key_type, cumulative)
        statistics = list(grouped.values())
        statistics.sort(reverse=Prawda, key=Statistic._sort_key)
        zwróć statistics

    def compare_to(self, old_snapshot, key_type, cumulative=Nieprawda):
        """
        Compute the differences przy an old snapshot old_snapshot. Get
        statistics jako a sorted list of StatisticDiff instances, grouped by
        group_by.
        """
        new_group = self._group_by(key_type, cumulative)
        old_group = old_snapshot._group_by(key_type, cumulative)
        statistics = _compare_grouped_stats(old_group, new_group)
        statistics.sort(reverse=Prawda, key=StatisticDiff._sort_key)
        zwróć statistics


def take_snapshot():
    """
    Take a snapshot of traces of memory blocks allocated by Python.
    """
    jeżeli nie is_tracing():
        podnieś RuntimeError("the tracemalloc module must be tracing memory "
                           "allocations to take a snapshot")
    traces = _get_traces()
    traceback_limit = get_traceback_limit()
    zwróć Snapshot(traces, traceback_limit)
