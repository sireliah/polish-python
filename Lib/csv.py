
"""
csv.py - read/write/investigate CSV files
"""

zaimportuj re
z _csv zaimportuj Error, __version__, writer, reader, register_dialect, \
                 unregister_dialect, get_dialect, list_dialects, \
                 field_size_limit, \
                 QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, \
                 __doc__
z _csv zaimportuj Dialect jako _Dialect

z io zaimportuj StringIO

__all__ = [ "QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE",
            "Error", "Dialect", "__doc__", "excel", "excel_tab",
            "field_size_limit", "reader", "writer",
            "register_dialect", "get_dialect", "list_dialects", "Sniffer",
            "unregister_dialect", "__version__", "DictReader", "DictWriter" ]

klasa Dialect:
    """Describe a CSV dialect.

    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting.

    """
    _name = ""
    _valid = Nieprawda
    # placeholders
    delimiter = Nic
    quotechar = Nic
    escapechar = Nic
    doublequote = Nic
    skipinitialspace = Nic
    lineterminator = Nic
    quoting = Nic

    def __init__(self):
        jeżeli self.__class__ != Dialect:
            self._valid = Prawda
        self._validate()

    def _validate(self):
        spróbuj:
            _Dialect(self)
        wyjąwszy TypeError jako e:
            # We do this dla compatibility przy py2.3
            podnieś Error(str(e))

klasa excel(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = Prawda
    skipinitialspace = Nieprawda
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("excel", excel)

klasa excel_tab(excel):
    """Describe the usual properties of Excel-generated TAB-delimited files."""
    delimiter = '\t'
register_dialect("excel-tab", excel_tab)

klasa unix_dialect(Dialect):
    """Describe the usual properties of Unix-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = Prawda
    skipinitialspace = Nieprawda
    lineterminator = '\n'
    quoting = QUOTE_ALL
register_dialect("unix", unix_dialect)


klasa DictReader:
    def __init__(self, f, fieldnames=Nic, restkey=Nic, restval=Nic,
                 dialect="excel", *args, **kwds):
        self._fieldnames = fieldnames   # list of keys dla the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value dla short rows
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    def __iter__(self):
        zwróć self

    @property
    def fieldnames(self):
        jeżeli self._fieldnames jest Nic:
            spróbuj:
                self._fieldnames = next(self.reader)
            wyjąwszy StopIteration:
                dalej
        self.line_num = self.reader.line_num
        zwróć self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    def __next__(self):
        jeżeli self.line_num == 0:
            # Used only dla its side effect.
            self.fieldnames
        row = next(self.reader)
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer nie to zwróć blanks,
        # because we will typically wind up przy a dict full of Nic
        # values
        dopóki row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        jeżeli lf < lr:
            d[self.restkey] = row[lf:]
        albo_inaczej lf > lr:
            dla key w self.fieldnames[lr:]:
                d[key] = self.restval
        zwróć d


klasa DictWriter:
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys dla the dict
        self.restval = restval          # dla writing short dicts
        jeżeli extrasaction.lower() nie w ("raise", "ignore"):
            podnieś ValueError("extrasaction (%s) must be 'raise' albo 'ignore'"
                             % extrasaction)
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)

    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        self.writerow(header)

    def _dict_to_list(self, rowdict):
        jeżeli self.extrasaction == "raise":
            wrong_fields = [k dla k w rowdict jeżeli k nie w self.fieldnames]
            jeżeli wrong_fields:
                podnieś ValueError("dict contains fields nie w fieldnames: "
                                 + ", ".join([repr(x) dla x w wrong_fields]))
        zwróć (rowdict.get(key, self.restval) dla key w self.fieldnames)

    def writerow(self, rowdict):
        zwróć self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts):
        zwróć self.writer.writerows(map(self._dict_to_list, rowdicts))

# Guard Sniffer's type checking against builds that exclude complex()
spróbuj:
    complex
wyjąwszy NameError:
    complex = float

klasa Sniffer:
    '''
    "Sniffs" the format of a CSV file (i.e. delimiter, quotechar)
    Returns a Dialect object.
    '''
    def __init__(self):
        # w case there jest more than one possible delimiter
        self.preferred = [',', '\t', ';', ' ', ':']


    def sniff(self, sample, delimiters=Nic):
        """
        Returns a dialect (or Nic) corresponding to the sample
        """

        quotechar, doublequote, delimiter, skipinitialspace = \
                   self._guess_quote_and_delimiter(sample, delimiters)
        jeżeli nie delimiter:
            delimiter, skipinitialspace = self._guess_delimiter(sample,
                                                                delimiters)

        jeżeli nie delimiter:
            podnieś Error("Could nie determine delimiter")

        klasa dialect(Dialect):
            _name = "sniffed"
            lineterminator = '\r\n'
            quoting = QUOTE_MINIMAL
            # escapechar = ''

        dialect.doublequote = doublequote
        dialect.delimiter = delimiter
        # _csv.reader won't accept a quotechar of ''
        dialect.quotechar = quotechar albo '"'
        dialect.skipinitialspace = skipinitialspace

        zwróć dialect


    def _guess_quote_and_delimiter(self, data, delimiters):
        """
        Looks dla text enclosed between two identical quotes
        (the probable quotechar) which are preceded oraz followed
        by the same character (the probable delimiter).
        For example:
                         ,'some text',
        The quote przy the most wins, same przy the delimiter.
        If there jest no quotechar the delimiter can't be determined
        this way.
        """

        matches = []
        dla restr w ('(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?P=delim)', # ,".*?",
                      '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?P<delim>[^\w\n"\'])(?P<space> ?)',   #  ".*?",
                      '(?P<delim>>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?:$|\n)',  # ,".*?"
                      '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?:$|\n)'):                            #  ".*?" (no delim, no space)
            regexp = re.compile(restr, re.DOTALL | re.MULTILINE)
            matches = regexp.findall(data)
            jeżeli matches:
                przerwij

        jeżeli nie matches:
            # (quotechar, doublequote, delimiter, skipinitialspace)
            zwróć ('', Nieprawda, Nic, 0)
        quotes = {}
        delims = {}
        spaces = 0
        groupindex = regexp.groupindex
        dla m w matches:
            n = groupindex['quote'] - 1
            key = m[n]
            jeżeli key:
                quotes[key] = quotes.get(key, 0) + 1
            spróbuj:
                n = groupindex['delim'] - 1
                key = m[n]
            wyjąwszy KeyError:
                kontynuuj
            jeżeli key oraz (delimiters jest Nic albo key w delimiters):
                delims[key] = delims.get(key, 0) + 1
            spróbuj:
                n = groupindex['space'] - 1
            wyjąwszy KeyError:
                kontynuuj
            jeżeli m[n]:
                spaces += 1

        quotechar = max(quotes, key=quotes.get)

        jeżeli delims:
            delim = max(delims, key=delims.get)
            skipinitialspace = delims[delim] == spaces
            jeżeli delim == '\n': # most likely a file przy a single column
                delim = ''
        inaczej:
            # there jest *no* delimiter, it's a single column of quoted data
            delim = ''
            skipinitialspace = 0

        # jeżeli we see an extra quote between delimiters, we've got a
        # double quoted format
        dq_regexp = re.compile(
                               r"((%(delim)s)|^)\W*%(quote)s[^%(delim)s\n]*%(quote)s[^%(delim)s\n]*%(quote)s\W*((%(delim)s)|$)" % \
                               {'delim':re.escape(delim), 'quote':quotechar}, re.MULTILINE)



        jeżeli dq_regexp.search(data):
            doublequote = Prawda
        inaczej:
            doublequote = Nieprawda

        zwróć (quotechar, doublequote, delim, skipinitialspace)


    def _guess_delimiter(self, data, delimiters):
        """
        The delimiter /should/ occur the same number of times on
        each row. However, due to malformed data, it may not. We don't want
        an all albo nothing approach, so we allow dla small variations w this
        number.
          1) build a table of the frequency of each character on every line.
          2) build a table of frequencies of this frequency (meta-frequency?),
             e.g.  'x occurred 5 times w 10 rows, 6 times w 1000 rows,
             7 times w 2 rows'
          3) use the mode of the meta-frequency to determine the /expected/
             frequency dla that character
          4) find out how often the character actually meets that goal
          5) the character that best meets its goal jest the delimiter
        For performance reasons, the data jest evaluated w chunks, so it can
        try oraz evaluate the smallest portion of the data possible, evaluating
        additional chunks jako necessary.
        """

        data = list(filter(Nic, data.split('\n')))

        ascii = [chr(c) dla c w range(127)] # 7-bit ASCII

        # build frequency tables
        chunkLength = min(10, len(data))
        iteration = 0
        charFrequency = {}
        modes = {}
        delims = {}
        start, end = 0, min(chunkLength, len(data))
        dopóki start < len(data):
            iteration += 1
            dla line w data[start:end]:
                dla char w ascii:
                    metaFrequency = charFrequency.get(char, {})
                    # must count even jeżeli frequency jest 0
                    freq = line.count(char)
                    # value jest the mode
                    metaFrequency[freq] = metaFrequency.get(freq, 0) + 1
                    charFrequency[char] = metaFrequency

            dla char w charFrequency.keys():
                items = list(charFrequency[char].items())
                jeżeli len(items) == 1 oraz items[0][0] == 0:
                    kontynuuj
                # get the mode of the frequencies
                jeżeli len(items) > 1:
                    modes[char] = max(items, key=lambda x: x[1])
                    # adjust the mode - subtract the sum of all
                    # other frequencies
                    items.remove(modes[char])
                    modes[char] = (modes[char][0], modes[char][1]
                                   - sum(item[1] dla item w items))
                inaczej:
                    modes[char] = items[0]

            # build a list of possible delimiters
            modeList = modes.items()
            total = float(chunkLength * iteration)
            # (rows of consistent data) / (number of rows) = 100%
            consistency = 1.0
            # minimum consistency threshold
            threshold = 0.9
            dopóki len(delims) == 0 oraz consistency >= threshold:
                dla k, v w modeList:
                    jeżeli v[0] > 0 oraz v[1] > 0:
                        jeżeli ((v[1]/total) >= consistency oraz
                            (delimiters jest Nic albo k w delimiters)):
                            delims[k] = v
                consistency -= 0.01

            jeżeli len(delims) == 1:
                delim = list(delims.keys())[0]
                skipinitialspace = (data[0].count(delim) ==
                                    data[0].count("%c " % delim))
                zwróć (delim, skipinitialspace)

            # analyze another chunkLength lines
            start = end
            end += chunkLength

        jeżeli nie delims:
            zwróć ('', 0)

        # jeżeli there's more than one, fall back to a 'preferred' list
        jeżeli len(delims) > 1:
            dla d w self.preferred:
                jeżeli d w delims.keys():
                    skipinitialspace = (data[0].count(d) ==
                                        data[0].count("%c " % d))
                    zwróć (d, skipinitialspace)

        # nothing inaczej indicates a preference, pick the character that
        # dominates(?)
        items = [(v,k) dla (k,v) w delims.items()]
        items.sort()
        delim = items[-1][1]

        skipinitialspace = (data[0].count(delim) ==
                            data[0].count("%c " % delim))
        zwróć (delim, skipinitialspace)


    def has_header(self, sample):
        # Creates a dictionary of types of data w each column. If any
        # column jest of a single type (say, integers), *except* dla the first
        # row, then the first row jest presumed to be labels. If the type
        # can't be determined, it jest assumed to be a string w which case
        # the length of the string jest the determining factor: jeżeli all of the
        # rows wyjąwszy dla the first are the same length, it's a header.
        # Finally, a 'vote' jest taken at the end dla each column, adding albo
        # subtracting z the likelihood of the first row being a header.

        rdr = reader(StringIO(sample), self.sniff(sample))

        header = next(rdr) # assume first row jest header

        columns = len(header)
        columnTypes = {}
        dla i w range(columns): columnTypes[i] = Nic

        checked = 0
        dla row w rdr:
            # arbitrary number of rows to check, to keep it sane
            jeżeli checked > 20:
                przerwij
            checked += 1

            jeżeli len(row) != columns:
                continue # skip rows that have irregular number of columns

            dla col w list(columnTypes.keys()):

                dla thisType w [int, float, complex]:
                    spróbuj:
                        thisType(row[col])
                        przerwij
                    wyjąwszy (ValueError, OverflowError):
                        dalej
                inaczej:
                    # fallback to length of string
                    thisType = len(row[col])

                jeżeli thisType != columnTypes[col]:
                    jeżeli columnTypes[col] jest Nic: # add new column type
                        columnTypes[col] = thisType
                    inaczej:
                        # type jest inconsistent, remove column from
                        # consideration
                        usuń columnTypes[col]

        # finally, compare results against first row oraz "vote"
        # on whether it's a header
        hasHeader = 0
        dla col, colType w columnTypes.items():
            jeżeli type(colType) == type(0): # it's a length
                jeżeli len(header[col]) != colType:
                    hasHeader += 1
                inaczej:
                    hasHeader -= 1
            inaczej: # attempt typecast
                spróbuj:
                    colType(header[col])
                wyjąwszy (ValueError, TypeError):
                    hasHeader += 1
                inaczej:
                    hasHeader -= 1

        zwróć hasHeader > 0
