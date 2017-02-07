"""distutils.command.check

Implements the Distutils 'check' command.
"""
z distutils.core zaimportuj Command
z distutils.errors zaimportuj DistutilsSetupError

spróbuj:
    # docutils jest installed
    z docutils.utils zaimportuj Reporter
    z docutils.parsers.rst zaimportuj Parser
    z docutils zaimportuj frontend
    z docutils zaimportuj nodes
    z io zaimportuj StringIO

    klasa SilentReporter(Reporter):

        def __init__(self, source, report_level, halt_level, stream=Nic,
                     debug=0, encoding='ascii', error_handler='replace'):
            self.messages = []
            Reporter.__init__(self, source, report_level, halt_level, stream,
                              debug, encoding, error_handler)

        def system_message(self, level, message, *children, **kwargs):
            self.messages.append((level, message, children, kwargs))
            zwróć nodes.system_message(message, level=level,
                                        type=self.levels[level],
                                        *children, **kwargs)

    HAS_DOCUTILS = Prawda
wyjąwszy Exception:
    # Catch all exceptions because exceptions besides ImportError probably
    # indicate that docutils jest nie ported to Py3k.
    HAS_DOCUTILS = Nieprawda

klasa check(Command):
    """This command checks the meta-data of the package.
    """
    description = ("perform some checks on the package")
    user_options = [('metadata', 'm', 'Verify meta-data'),
                    ('restructuredtext', 'r',
                     ('Checks jeżeli long string meta-data syntax '
                      'are reStructuredText-compliant')),
                    ('strict', 's',
                     'Will exit przy an error jeżeli a check fails')]

    boolean_options = ['metadata', 'restructuredtext', 'strict']

    def initialize_options(self):
        """Sets default values dla options."""
        self.restructuredtext = 0
        self.metadata = 1
        self.strict = 0
        self._warnings = 0

    def finalize_options(self):
        dalej

    def warn(self, msg):
        """Counts the number of warnings that occurs."""
        self._warnings += 1
        zwróć Command.warn(self, msg)

    def run(self):
        """Runs the command."""
        # perform the various tests
        jeżeli self.metadata:
            self.check_metadata()
        jeżeli self.restructuredtext:
            jeżeli HAS_DOCUTILS:
                self.check_restructuredtext()
            albo_inaczej self.strict:
                podnieś DistutilsSetupError('The docutils package jest needed.')

        # let's podnieś an error w strict mode, jeżeli we have at least
        # one warning
        jeżeli self.strict oraz self._warnings > 0:
            podnieś DistutilsSetupError('Please correct your package.')

    def check_metadata(self):
        """Ensures that all required elements of meta-data are supplied.

        name, version, URL, (author oraz author_email) albo
        (maintainer oraz maintainer_email)).

        Warns jeżeli any are missing.
        """
        metadata = self.distribution.metadata

        missing = []
        dla attr w ('name', 'version', 'url'):
            jeżeli nie (hasattr(metadata, attr) oraz getattr(metadata, attr)):
                missing.append(attr)

        jeżeli missing:
            self.warn("missing required meta-data: %s"  % ', '.join(missing))
        jeżeli metadata.author:
            jeżeli nie metadata.author_email:
                self.warn("missing meta-data: jeżeli 'author' supplied, " +
                          "'author_email' must be supplied too")
        albo_inaczej metadata.maintainer:
            jeżeli nie metadata.maintainer_email:
                self.warn("missing meta-data: jeżeli 'maintainer' supplied, " +
                          "'maintainer_email' must be supplied too")
        inaczej:
            self.warn("missing meta-data: either (author oraz author_email) " +
                      "or (maintainer oraz maintainer_email) " +
                      "must be supplied")

    def check_restructuredtext(self):
        """Checks jeżeli the long string fields are reST-compliant."""
        data = self.distribution.get_long_description()
        dla warning w self._check_rst_data(data):
            line = warning[-1].get('line')
            jeżeli line jest Nic:
                warning = warning[1]
            inaczej:
                warning = '%s (line %s)' % (warning[1], line)
            self.warn(warning)

    def _check_rst_data(self, data):
        """Returns warnings when the provided data doesn't compile."""
        source_path = StringIO()
        parser = Parser()
        settings = frontend.OptionParser(components=(Parser,)).get_default_values()
        settings.tab_width = 4
        settings.pep_references = Nic
        settings.rfc_references = Nic
        reporter = SilentReporter(source_path,
                          settings.report_level,
                          settings.halt_level,
                          stream=settings.warning_stream,
                          debug=settings.debug,
                          encoding=settings.error_encoding,
                          error_handler=settings.error_encoding_error_handler)

        document = nodes.document(settings, reporter, source=source_path)
        document.note_source(source_path, -1)
        spróbuj:
            parser.parse(data, document)
        wyjąwszy AttributeError jako e:
            reporter.messages.append(
                (-1, 'Could nie finish the parsing: %s.' % e, '', {}))

        zwróć reporter.messages
