# Copyright 2001-2014 by Vinay Sajip. All Rights Reserved.
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
Configuration functions dla the logging package dla Python. The core package
is based on PEP 282 oraz comments thereto w comp.lang.python, oraz influenced
by Apache's log4j system.

Copyright (C) 2001-2014 Vinay Sajip. All Rights Reserved.

To use, simply 'zaimportuj logging' oraz log away!
"""

zaimportuj errno
zaimportuj io
zaimportuj logging
zaimportuj logging.handlers
zaimportuj re
zaimportuj struct
zaimportuj sys
zaimportuj traceback

spróbuj:
    zaimportuj _thread jako thread
    zaimportuj threading
wyjąwszy ImportError: #pragma: no cover
    thread = Nic

z socketserver zaimportuj ThreadingTCPServer, StreamRequestHandler


DEFAULT_LOGGING_CONFIG_PORT = 9030

RESET_ERROR = errno.ECONNRESET

#
#   The following code implements a socket listener dla on-the-fly
#   reconfiguration of logging.
#
#   _listener holds the server object doing the listening
_listener = Nic

def fileConfig(fname, defaults=Nic, disable_existing_loggers=Prawda):
    """
    Read the logging configuration z a ConfigParser-format file.

    This can be called several times z an application, allowing an end user
    the ability to select z various pre-canned configurations (jeżeli the
    developer provides a mechanism to present the choices oraz load the chosen
    configuration).
    """
    zaimportuj configparser

    jeżeli isinstance(fname, configparser.RawConfigParser):
        cp = fname
    inaczej:
        cp = configparser.ConfigParser(defaults)
        jeżeli hasattr(fname, 'readline'):
            cp.read_file(fname)
        inaczej:
            cp.read(fname)

    formatters = _create_formatters(cp)

    # critical section
    logging._acquireLock()
    spróbuj:
        logging._handlers.clear()
        usuń logging._handlerList[:]
        # Handlers add themselves to logging._handlers
        handlers = _install_handlers(cp, formatters)
        _install_loggers(cp, handlers, disable_existing_loggers)
    w_końcu:
        logging._releaseLock()


def _resolve(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    dla n w name:
        used = used + '.' + n
        spróbuj:
            found = getattr(found, n)
        wyjąwszy AttributeError:
            __import__(used)
            found = getattr(found, n)
    zwróć found

def _strip_spaces(alist):
    zwróć map(lambda x: x.strip(), alist)

def _create_formatters(cp):
    """Create oraz zwróć formatters"""
    flist = cp["formatters"]["keys"]
    jeżeli nie len(flist):
        zwróć {}
    flist = flist.split(",")
    flist = _strip_spaces(flist)
    formatters = {}
    dla form w flist:
        sectname = "formatter_%s" % form
        fs = cp.get(sectname, "format", raw=Prawda, fallback=Nic)
        dfs = cp.get(sectname, "datefmt", raw=Prawda, fallback=Nic)
        stl = cp.get(sectname, "style", raw=Prawda, fallback='%')
        c = logging.Formatter
        class_name = cp[sectname].get("class")
        jeżeli class_name:
            c = _resolve(class_name)
        f = c(fs, dfs, stl)
        formatters[form] = f
    zwróć formatters


def _install_handlers(cp, formatters):
    """Install oraz zwróć handlers"""
    hlist = cp["handlers"]["keys"]
    jeżeli nie len(hlist):
        zwróć {}
    hlist = hlist.split(",")
    hlist = _strip_spaces(hlist)
    handlers = {}
    fixups = [] #dla inter-handler references
    dla hand w hlist:
        section = cp["handler_%s" % hand]
        klass = section["class"]
        fmt = section.get("formatter", "")
        spróbuj:
            klass = eval(klass, vars(logging))
        wyjąwszy (AttributeError, NameError):
            klass = _resolve(klass)
        args = section["args"]
        args = eval(args, vars(logging))
        h = klass(*args)
        jeżeli "level" w section:
            level = section["level"]
            h.setLevel(level)
        jeżeli len(fmt):
            h.setFormatter(formatters[fmt])
        jeżeli issubclass(klass, logging.handlers.MemoryHandler):
            target = section.get("target", "")
            jeżeli len(target): #the target handler may nie be loaded yet, so keep dla later...
                fixups.append((h, target))
        handlers[hand] = h
    #now all handlers are loaded, fixup inter-handler references...
    dla h, t w fixups:
        h.setTarget(handlers[t])
    zwróć handlers

def _handle_existing_loggers(existing, child_loggers, disable_existing):
    """
    When (re)configuring logging, handle loggers which were w the previous
    configuration but are nie w the new configuration. There's no point
    deleting them jako other threads may continue to hold references to them;
    oraz by disabling them, you stop them doing any logging.

    However, don't disable children of named loggers, jako that's probably nie
    what was intended by the user. Also, allow existing loggers to NOT be
    disabled jeżeli disable_existing jest false.
    """
    root = logging.root
    dla log w existing:
        logger = root.manager.loggerDict[log]
        jeżeli log w child_loggers:
            logger.level = logging.NOTSET
            logger.handlers = []
            logger.propagate = Prawda
        inaczej:
            logger.disabled = disable_existing

def _install_loggers(cp, handlers, disable_existing):
    """Create oraz install loggers"""

    # configure the root first
    llist = cp["loggers"]["keys"]
    llist = llist.split(",")
    llist = list(map(lambda x: x.strip(), llist))
    llist.remove("root")
    section = cp["logger_root"]
    root = logging.root
    log = root
    jeżeli "level" w section:
        level = section["level"]
        log.setLevel(level)
    dla h w root.handlers[:]:
        root.removeHandler(h)
    hlist = section["handlers"]
    jeżeli len(hlist):
        hlist = hlist.split(",")
        hlist = _strip_spaces(hlist)
        dla hand w hlist:
            log.addHandler(handlers[hand])

    #and now the others...
    #we don't want to lose the existing loggers,
    #since other threads may have pointers to them.
    #existing jest set to contain all existing loggers,
    #and jako we go through the new configuration we
    #remove any which are configured. At the end,
    #what's left w existing jest the set of loggers
    #which were w the previous configuration but
    #which are nie w the new configuration.
    existing = list(root.manager.loggerDict.keys())
    #The list needs to be sorted so that we can
    #avoid disabling child loggers of explicitly
    #named loggers. With a sorted list it jest easier
    #to find the child loggers.
    existing.sort()
    #We'll keep the list of existing loggers
    #which are children of named loggers here...
    child_loggers = []
    #now set up the new ones...
    dla log w llist:
        section = cp["logger_%s" % log]
        qn = section["qualname"]
        propagate = section.getint("propagate", fallback=1)
        logger = logging.getLogger(qn)
        jeżeli qn w existing:
            i = existing.index(qn) + 1 # start przy the entry after qn
            prefixed = qn + "."
            pflen = len(prefixed)
            num_existing = len(existing)
            dopóki i < num_existing:
                jeżeli existing[i][:pflen] == prefixed:
                    child_loggers.append(existing[i])
                i += 1
            existing.remove(qn)
        jeżeli "level" w section:
            level = section["level"]
            logger.setLevel(level)
        dla h w logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = propagate
        logger.disabled = 0
        hlist = section["handlers"]
        jeżeli len(hlist):
            hlist = hlist.split(",")
            hlist = _strip_spaces(hlist)
            dla hand w hlist:
                logger.addHandler(handlers[hand])

    #Disable any old loggers. There's no point deleting
    #them jako other threads may continue to hold references
    #and by disabling them, you stop them doing any logging.
    #However, don't disable children of named loggers, jako that's
    #probably nie what was intended by the user.
    #dla log w existing:
    #    logger = root.manager.loggerDict[log]
    #    jeżeli log w child_loggers:
    #        logger.level = logging.NOTSET
    #        logger.handlers = []
    #        logger.propagate = 1
    #    albo_inaczej disable_existing_loggers:
    #        logger.disabled = 1
    _handle_existing_loggers(existing, child_loggers, disable_existing)

IDENTIFIER = re.compile('^[a-z_][a-z0-9_]*$', re.I)


def valid_ident(s):
    m = IDENTIFIER.match(s)
    jeżeli nie m:
        podnieś ValueError('Not a valid Python identifier: %r' % s)
    zwróć Prawda


klasa ConvertingMixin(object):
    """For ConvertingXXX's, this mixin klasa provides common functions"""

    def convert_with_key(self, key, value, replace=Prawda):
        result = self.configurator.convert(value)
        #If the converted value jest different, save dla next time
        jeżeli value jest nie result:
            jeżeli replace:
                self[key] = result
            jeżeli type(result) w (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
                result.key = key
        zwróć result

    def convert(self, value):
        result = self.configurator.convert(value)
        jeżeli value jest nie result:
            jeżeli type(result) w (ConvertingDict, ConvertingList,
                               ConvertingTuple):
                result.parent = self
        zwróć result


# The ConvertingXXX classes are wrappers around standard Python containers,
# oraz they serve to convert any suitable values w the container. The
# conversion converts base dicts, lists oraz tuples to their wrapped
# equivalents, whereas strings which match a conversion format are converted
# appropriately.
#
# Each wrapper should have a configurator attribute holding the actual
# configurator to use dla conversion.

klasa ConvertingDict(dict, ConvertingMixin):
    """A converting dictionary wrapper."""

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        zwróć self.convert_with_key(key, value)

    def get(self, key, default=Nic):
        value = dict.get(self, key, default)
        zwróć self.convert_with_key(key, value)

    def pop(self, key, default=Nic):
        value = dict.pop(self, key, default)
        zwróć self.convert_with_key(key, value, replace=Nieprawda)

klasa ConvertingList(list, ConvertingMixin):
    """A converting list wrapper."""
    def __getitem__(self, key):
        value = list.__getitem__(self, key)
        zwróć self.convert_with_key(key, value)

    def pop(self, idx=-1):
        value = list.pop(self, idx)
        zwróć self.convert(value)

klasa ConvertingTuple(tuple, ConvertingMixin):
    """A converting tuple wrapper."""
    def __getitem__(self, key):
        value = tuple.__getitem__(self, key)
        # Can't replace a tuple entry.
        zwróć self.convert_with_key(key, value, replace=Nieprawda)

klasa BaseConfigurator(object):
    """
    The configurator base klasa which defines some useful defaults.
    """

    CONVERT_PATTERN = re.compile(r'^(?P<prefix>[a-z]+)://(?P<suffix>.*)$')

    WORD_PATTERN = re.compile(r'^\s*(\w+)\s*')
    DOT_PATTERN = re.compile(r'^\.\s*(\w+)\s*')
    INDEX_PATTERN = re.compile(r'^\[\s*(\w+)\s*\]\s*')
    DIGIT_PATTERN = re.compile(r'^\d+$')

    value_converters = {
        'ext' : 'ext_convert',
        'cfg' : 'cfg_convert',
    }

    # We might want to use a different one, e.g. importlib
    importer = staticmethod(__import__)

    def __init__(self, config):
        self.config = ConvertingDict(config)
        self.config.configurator = self

    def resolve(self, s):
        """
        Resolve strings to objects using standard zaimportuj oraz attribute
        syntax.
        """
        name = s.split('.')
        used = name.pop(0)
        spróbuj:
            found = self.importer(used)
            dla frag w name:
                used += '.' + frag
                spróbuj:
                    found = getattr(found, frag)
                wyjąwszy AttributeError:
                    self.importer(used)
                    found = getattr(found, frag)
            zwróć found
        wyjąwszy ImportError:
            e, tb = sys.exc_info()[1:]
            v = ValueError('Cannot resolve %r: %s' % (s, e))
            v.__cause__, v.__traceback__ = e, tb
            podnieś v

    def ext_convert(self, value):
        """Default converter dla the ext:// protocol."""
        zwróć self.resolve(value)

    def cfg_convert(self, value):
        """Default converter dla the cfg:// protocol."""
        rest = value
        m = self.WORD_PATTERN.match(rest)
        jeżeli m jest Nic:
            podnieś ValueError("Unable to convert %r" % value)
        inaczej:
            rest = rest[m.end():]
            d = self.config[m.groups()[0]]
            #print d, rest
            dopóki rest:
                m = self.DOT_PATTERN.match(rest)
                jeżeli m:
                    d = d[m.groups()[0]]
                inaczej:
                    m = self.INDEX_PATTERN.match(rest)
                    jeżeli m:
                        idx = m.groups()[0]
                        jeżeli nie self.DIGIT_PATTERN.match(idx):
                            d = d[idx]
                        inaczej:
                            spróbuj:
                                n = int(idx) # try jako number first (most likely)
                                d = d[n]
                            wyjąwszy TypeError:
                                d = d[idx]
                jeżeli m:
                    rest = rest[m.end():]
                inaczej:
                    podnieś ValueError('Unable to convert '
                                     '%r at %r' % (value, rest))
        #rest should be empty
        zwróć d

    def convert(self, value):
        """
        Convert values to an appropriate type. dicts, lists oraz tuples are
        replaced by their converting alternatives. Strings are checked to
        see jeżeli they have a conversion format oraz are converted jeżeli they do.
        """
        jeżeli nie isinstance(value, ConvertingDict) oraz isinstance(value, dict):
            value = ConvertingDict(value)
            value.configurator = self
        albo_inaczej nie isinstance(value, ConvertingList) oraz isinstance(value, list):
            value = ConvertingList(value)
            value.configurator = self
        albo_inaczej nie isinstance(value, ConvertingTuple) and\
                 isinstance(value, tuple):
            value = ConvertingTuple(value)
            value.configurator = self
        albo_inaczej isinstance(value, str): # str dla py3k
            m = self.CONVERT_PATTERN.match(value)
            jeżeli m:
                d = m.groupdict()
                prefix = d['prefix']
                converter = self.value_converters.get(prefix, Nic)
                jeżeli converter:
                    suffix = d['suffix']
                    converter = getattr(self, converter)
                    value = converter(suffix)
        zwróć value

    def configure_custom(self, config):
        """Configure an object przy a user-supplied factory."""
        c = config.pop('()')
        jeżeli nie callable(c):
            c = self.resolve(c)
        props = config.pop('.', Nic)
        # Check dla valid identifiers
        kwargs = dict([(k, config[k]) dla k w config jeżeli valid_ident(k)])
        result = c(**kwargs)
        jeżeli props:
            dla name, value w props.items():
                setattr(result, name, value)
        zwróć result

    def as_tuple(self, value):
        """Utility function which converts lists to tuples."""
        jeżeli isinstance(value, list):
            value = tuple(value)
        zwróć value

klasa DictConfigurator(BaseConfigurator):
    """
    Configure logging using a dictionary-like object to describe the
    configuration.
    """

    def configure(self):
        """Do the configuration."""

        config = self.config
        jeżeli 'version' nie w config:
            podnieś ValueError("dictionary doesn't specify a version")
        jeżeli config['version'] != 1:
            podnieś ValueError("Unsupported version: %s" % config['version'])
        incremental = config.pop('incremental', Nieprawda)
        EMPTY_DICT = {}
        logging._acquireLock()
        spróbuj:
            jeżeli incremental:
                handlers = config.get('handlers', EMPTY_DICT)
                dla name w handlers:
                    jeżeli name nie w logging._handlers:
                        podnieś ValueError('No handler found przy '
                                         'name %r'  % name)
                    inaczej:
                        spróbuj:
                            handler = logging._handlers[name]
                            handler_config = handlers[name]
                            level = handler_config.get('level', Nic)
                            jeżeli level:
                                handler.setLevel(logging._checkLevel(level))
                        wyjąwszy Exception jako e:
                            podnieś ValueError('Unable to configure handler '
                                             '%r: %s' % (name, e))
                loggers = config.get('loggers', EMPTY_DICT)
                dla name w loggers:
                    spróbuj:
                        self.configure_logger(name, loggers[name], Prawda)
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure logger '
                                         '%r: %s' % (name, e))
                root = config.get('root', Nic)
                jeżeli root:
                    spróbuj:
                        self.configure_root(root, Prawda)
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure root '
                                         'logger: %s' % e)
            inaczej:
                disable_existing = config.pop('disable_existing_loggers', Prawda)

                logging._handlers.clear()
                usuń logging._handlerList[:]

                # Do formatters first - they don't refer to anything inaczej
                formatters = config.get('formatters', EMPTY_DICT)
                dla name w formatters:
                    spróbuj:
                        formatters[name] = self.configure_formatter(
                                                            formatters[name])
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure '
                                         'formatter %r: %s' % (name, e))
                # Next, do filters - they don't refer to anything inaczej, either
                filters = config.get('filters', EMPTY_DICT)
                dla name w filters:
                    spróbuj:
                        filters[name] = self.configure_filter(filters[name])
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure '
                                         'filter %r: %s' % (name, e))

                # Next, do handlers - they refer to formatters oraz filters
                # As handlers can refer to other handlers, sort the keys
                # to allow a deterministic order of configuration
                handlers = config.get('handlers', EMPTY_DICT)
                deferred = []
                dla name w sorted(handlers):
                    spróbuj:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    wyjąwszy Exception jako e:
                        jeżeli 'target nie configured yet' w str(e):
                            deferred.append(name)
                        inaczej:
                            podnieś ValueError('Unable to configure handler '
                                             '%r: %s' % (name, e))

                # Now do any that were deferred
                dla name w deferred:
                    spróbuj:
                        handler = self.configure_handler(handlers[name])
                        handler.name = name
                        handlers[name] = handler
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure handler '
                                         '%r: %s' % (name, e))

                # Next, do loggers - they refer to handlers oraz filters

                #we don't want to lose the existing loggers,
                #since other threads may have pointers to them.
                #existing jest set to contain all existing loggers,
                #and jako we go through the new configuration we
                #remove any which are configured. At the end,
                #what's left w existing jest the set of loggers
                #which were w the previous configuration but
                #which are nie w the new configuration.
                root = logging.root
                existing = list(root.manager.loggerDict.keys())
                #The list needs to be sorted so that we can
                #avoid disabling child loggers of explicitly
                #named loggers. With a sorted list it jest easier
                #to find the child loggers.
                existing.sort()
                #We'll keep the list of existing loggers
                #which are children of named loggers here...
                child_loggers = []
                #now set up the new ones...
                loggers = config.get('loggers', EMPTY_DICT)
                dla name w loggers:
                    jeżeli name w existing:
                        i = existing.index(name) + 1 # look after name
                        prefixed = name + "."
                        pflen = len(prefixed)
                        num_existing = len(existing)
                        dopóki i < num_existing:
                            jeżeli existing[i][:pflen] == prefixed:
                                child_loggers.append(existing[i])
                            i += 1
                        existing.remove(name)
                    spróbuj:
                        self.configure_logger(name, loggers[name])
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure logger '
                                         '%r: %s' % (name, e))

                #Disable any old loggers. There's no point deleting
                #them jako other threads may continue to hold references
                #and by disabling them, you stop them doing any logging.
                #However, don't disable children of named loggers, jako that's
                #probably nie what was intended by the user.
                #dla log w existing:
                #    logger = root.manager.loggerDict[log]
                #    jeżeli log w child_loggers:
                #        logger.level = logging.NOTSET
                #        logger.handlers = []
                #        logger.propagate = Prawda
                #    albo_inaczej disable_existing:
                #        logger.disabled = Prawda
                _handle_existing_loggers(existing, child_loggers,
                                         disable_existing)

                # And finally, do the root logger
                root = config.get('root', Nic)
                jeżeli root:
                    spróbuj:
                        self.configure_root(root)
                    wyjąwszy Exception jako e:
                        podnieś ValueError('Unable to configure root '
                                         'logger: %s' % e)
        w_końcu:
            logging._releaseLock()

    def configure_formatter(self, config):
        """Configure a formatter z a dictionary."""
        jeżeli '()' w config:
            factory = config['()'] # dla use w exception handler
            spróbuj:
                result = self.configure_custom(config)
            wyjąwszy TypeError jako te:
                jeżeli "'format'" nie w str(te):
                    podnieś
                #Name of parameter changed z fmt to format.
                #Retry przy old name.
                #This jest so that code can be used przy older Python versions
                #(e.g. by Django)
                config['fmt'] = config.pop('format')
                config['()'] = factory
                result = self.configure_custom(config)
        inaczej:
            fmt = config.get('format', Nic)
            dfmt = config.get('datefmt', Nic)
            style = config.get('style', '%')
            cname = config.get('class', Nic)
            jeżeli nie cname:
                c = logging.Formatter
            inaczej:
                c = _resolve(cname)
            result = c(fmt, dfmt, style)
        zwróć result

    def configure_filter(self, config):
        """Configure a filter z a dictionary."""
        jeżeli '()' w config:
            result = self.configure_custom(config)
        inaczej:
            name = config.get('name', '')
            result = logging.Filter(name)
        zwróć result

    def add_filters(self, filterer, filters):
        """Add filters to a filterer z a list of names."""
        dla f w filters:
            spróbuj:
                filterer.addFilter(self.config['filters'][f])
            wyjąwszy Exception jako e:
                podnieś ValueError('Unable to add filter %r: %s' % (f, e))

    def configure_handler(self, config):
        """Configure a handler z a dictionary."""
        config_copy = dict(config)  # dla restoring w case of error
        formatter = config.pop('formatter', Nic)
        jeżeli formatter:
            spróbuj:
                formatter = self.config['formatters'][formatter]
            wyjąwszy Exception jako e:
                podnieś ValueError('Unable to set formatter '
                                 '%r: %s' % (formatter, e))
        level = config.pop('level', Nic)
        filters = config.pop('filters', Nic)
        jeżeli '()' w config:
            c = config.pop('()')
            jeżeli nie callable(c):
                c = self.resolve(c)
            factory = c
        inaczej:
            cname = config.pop('class')
            klass = self.resolve(cname)
            #Special case dla handler which refers to another handler
            jeżeli issubclass(klass, logging.handlers.MemoryHandler) and\
                'target' w config:
                spróbuj:
                    th = self.config['handlers'][config['target']]
                    jeżeli nie isinstance(th, logging.Handler):
                        config.update(config_copy)  # restore dla deferred cfg
                        podnieś TypeError('target nie configured yet')
                    config['target'] = th
                wyjąwszy Exception jako e:
                    podnieś ValueError('Unable to set target handler '
                                     '%r: %s' % (config['target'], e))
            albo_inaczej issubclass(klass, logging.handlers.SMTPHandler) and\
                'mailhost' w config:
                config['mailhost'] = self.as_tuple(config['mailhost'])
            albo_inaczej issubclass(klass, logging.handlers.SysLogHandler) and\
                'address' w config:
                config['address'] = self.as_tuple(config['address'])
            factory = klass
        props = config.pop('.', Nic)
        kwargs = dict([(k, config[k]) dla k w config jeżeli valid_ident(k)])
        spróbuj:
            result = factory(**kwargs)
        wyjąwszy TypeError jako te:
            jeżeli "'stream'" nie w str(te):
                podnieś
            #The argument name changed z strm to stream
            #Retry przy old name.
            #This jest so that code can be used przy older Python versions
            #(e.g. by Django)
            kwargs['strm'] = kwargs.pop('stream')
            result = factory(**kwargs)
        jeżeli formatter:
            result.setFormatter(formatter)
        jeżeli level jest nie Nic:
            result.setLevel(logging._checkLevel(level))
        jeżeli filters:
            self.add_filters(result, filters)
        jeżeli props:
            dla name, value w props.items():
                setattr(result, name, value)
        zwróć result

    def add_handlers(self, logger, handlers):
        """Add handlers to a logger z a list of names."""
        dla h w handlers:
            spróbuj:
                logger.addHandler(self.config['handlers'][h])
            wyjąwszy Exception jako e:
                podnieś ValueError('Unable to add handler %r: %s' % (h, e))

    def common_logger_config(self, logger, config, incremental=Nieprawda):
        """
        Perform configuration which jest common to root oraz non-root loggers.
        """
        level = config.get('level', Nic)
        jeżeli level jest nie Nic:
            logger.setLevel(logging._checkLevel(level))
        jeżeli nie incremental:
            #Remove any existing handlers
            dla h w logger.handlers[:]:
                logger.removeHandler(h)
            handlers = config.get('handlers', Nic)
            jeżeli handlers:
                self.add_handlers(logger, handlers)
            filters = config.get('filters', Nic)
            jeżeli filters:
                self.add_filters(logger, filters)

    def configure_logger(self, name, config, incremental=Nieprawda):
        """Configure a non-root logger z a dictionary."""
        logger = logging.getLogger(name)
        self.common_logger_config(logger, config, incremental)
        propagate = config.get('propagate', Nic)
        jeżeli propagate jest nie Nic:
            logger.propagate = propagate

    def configure_root(self, config, incremental=Nieprawda):
        """Configure a root logger z a dictionary."""
        root = logging.getLogger()
        self.common_logger_config(root, config, incremental)

dictConfigClass = DictConfigurator

def dictConfig(config):
    """Configure logging using a dictionary."""
    dictConfigClass(config).configure()


def listen(port=DEFAULT_LOGGING_CONFIG_PORT, verify=Nic):
    """
    Start up a socket server on the specified port, oraz listen dla new
    configurations.

    These will be sent jako a file suitable dla processing by fileConfig().
    Returns a Thread object on which you can call start() to start the server,
    oraz which you can join() when appropriate. To stop the server, call
    stopListening().

    Use the ``verify`` argument to verify any bytes received across the wire
    z a client. If specified, it should be a callable which receives a
    single argument - the bytes of configuration data received across the
    network - oraz it should zwróć either ``Nic``, to indicate that the
    dalejed w bytes could nie be verified oraz should be discarded, albo a
    byte string which jest then dalejed to the configuration machinery as
    normal. Note that you can zwróć transformed bytes, e.g. by decrypting
    the bytes dalejed in.
    """
    jeżeli nie thread: #pragma: no cover
        podnieś NotImplementedError("listen() needs threading to work")

    klasa ConfigStreamHandler(StreamRequestHandler):
        """
        Handler dla a logging configuration request.

        It expects a completely new logging configuration oraz uses fileConfig
        to install it.
        """
        def handle(self):
            """
            Handle a request.

            Each request jest expected to be a 4-byte length, packed using
            struct.pack(">L", n), followed by the config file.
            Uses fileConfig() to do the grunt work.
            """
            spróbuj:
                conn = self.connection
                chunk = conn.recv(4)
                jeżeli len(chunk) == 4:
                    slen = struct.unpack(">L", chunk)[0]
                    chunk = self.connection.recv(slen)
                    dopóki len(chunk) < slen:
                        chunk = chunk + conn.recv(slen - len(chunk))
                    jeżeli self.server.verify jest nie Nic:
                        chunk = self.server.verify(chunk)
                    jeżeli chunk jest nie Nic:   # verified, can process
                        chunk = chunk.decode("utf-8")
                        spróbuj:
                            zaimportuj json
                            d =json.loads(chunk)
                            assert isinstance(d, dict)
                            dictConfig(d)
                        wyjąwszy Exception:
                            #Apply new configuration.

                            file = io.StringIO(chunk)
                            spróbuj:
                                fileConfig(file)
                            wyjąwszy Exception:
                                traceback.print_exc()
                    jeżeli self.server.ready:
                        self.server.ready.set()
            wyjąwszy OSError jako e:
                jeżeli e.errno != RESET_ERROR:
                    podnieś

    klasa ConfigSocketReceiver(ThreadingTCPServer):
        """
        A simple TCP socket-based logging config receiver.
        """

        allow_reuse_address = 1

        def __init__(self, host='localhost', port=DEFAULT_LOGGING_CONFIG_PORT,
                     handler=Nic, ready=Nic, verify=Nic):
            ThreadingTCPServer.__init__(self, (host, port), handler)
            logging._acquireLock()
            self.abort = 0
            logging._releaseLock()
            self.timeout = 1
            self.ready = ready
            self.verify = verify

        def serve_until_stopped(self):
            zaimportuj select
            abort = 0
            dopóki nie abort:
                rd, wr, ex = select.select([self.socket.fileno()],
                                           [], [],
                                           self.timeout)
                jeżeli rd:
                    self.handle_request()
                logging._acquireLock()
                abort = self.abort
                logging._releaseLock()
            self.socket.close()

    klasa Server(threading.Thread):

        def __init__(self, rcvr, hdlr, port, verify):
            super(Server, self).__init__()
            self.rcvr = rcvr
            self.hdlr = hdlr
            self.port = port
            self.verify = verify
            self.ready = threading.Event()

        def run(self):
            server = self.rcvr(port=self.port, handler=self.hdlr,
                               ready=self.ready,
                               verify=self.verify)
            jeżeli self.port == 0:
                self.port = server.server_address[1]
            self.ready.set()
            global _listener
            logging._acquireLock()
            _listener = server
            logging._releaseLock()
            server.serve_until_stopped()

    zwróć Server(ConfigSocketReceiver, ConfigStreamHandler, port, verify)

def stopListening():
    """
    Stop the listening server which was created przy a call to listen().
    """
    global _listener
    logging._acquireLock()
    spróbuj:
        jeżeli _listener:
            _listener.abort = 1
            _listener = Nic
    w_końcu:
        logging._releaseLock()
