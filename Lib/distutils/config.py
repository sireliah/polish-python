"""distutils.pypirc

Provides the PyPIRCCommand class, the base klasa dla the command classes
that uses .pypirc w the distutils.command package.
"""
zaimportuj os
z configparser zaimportuj ConfigParser

z distutils.cmd zaimportuj Command

DEFAULT_PYPIRC = """\
[distutils]
index-servers =
    pypi

[pypi]
username:%s
password:%s
"""

klasa PyPIRCCommand(Command):
    """Base command that knows how to handle the .pypirc file
    """
    DEFAULT_REPOSITORY = 'https://pypi.python.org/pypi'
    DEFAULT_REALM = 'pypi'
    repository = Nic
    realm = Nic

    user_options = [
        ('repository=', 'r',
         "url of repository [default: %s]" % \
            DEFAULT_REPOSITORY),
        ('show-response', Nic,
         'display full response text z server')]

    boolean_options = ['show-response']

    def _get_rc_file(self):
        """Returns rc file path."""
        zwróć os.path.join(os.path.expanduser('~'), '.pypirc')

    def _store_pypirc(self, username, dalejword):
        """Creates a default .pypirc file."""
        rc = self._get_rc_file()
        przy os.fdopen(os.open(rc, os.O_CREAT | os.O_WRONLY, 0o600), 'w') jako f:
            f.write(DEFAULT_PYPIRC % (username, dalejword))

    def _read_pypirc(self):
        """Reads the .pypirc file."""
        rc = self._get_rc_file()
        jeżeli os.path.exists(rc):
            self.announce('Using PyPI login z %s' % rc)
            repository = self.repository albo self.DEFAULT_REPOSITORY
            realm = self.realm albo self.DEFAULT_REALM

            config = ConfigParser()
            config.read(rc)
            sections = config.sections()
            jeżeli 'distutils' w sections:
                # let's get the list of servers
                index_servers = config.get('distutils', 'index-servers')
                _servers = [server.strip() dla server w
                            index_servers.split('\n')
                            jeżeli server.strip() != '']
                jeżeli _servers == []:
                    # nothing set, let's try to get the default pypi
                    jeżeli 'pypi' w sections:
                        _servers = ['pypi']
                    inaczej:
                        # the file jest nie properly defined, returning
                        # an empty dict
                        zwróć {}
                dla server w _servers:
                    current = {'server': server}
                    current['username'] = config.get(server, 'username')

                    # optional params
                    dla key, default w (('repository',
                                          self.DEFAULT_REPOSITORY),
                                         ('realm', self.DEFAULT_REALM),
                                         ('password', Nic)):
                        jeżeli config.has_option(server, key):
                            current[key] = config.get(server, key)
                        inaczej:
                            current[key] = default

                    # work around people having "repository" dla the "pypi"
                    # section of their config set to the HTTP (rather than
                    # HTTPS) URL
                    jeżeli (server == 'pypi' oraz
                        repository w (self.DEFAULT_REPOSITORY, 'pypi')):
                        current['repository'] = self.DEFAULT_REPOSITORY
                        zwróć current

                    jeżeli (current['server'] == repository albo
                        current['repository'] == repository):
                        zwróć current
            albo_inaczej 'server-login' w sections:
                # old format
                server = 'server-login'
                jeżeli config.has_option(server, 'repository'):
                    repository = config.get(server, 'repository')
                inaczej:
                    repository = self.DEFAULT_REPOSITORY
                zwróć {'username': config.get(server, 'username'),
                        'password': config.get(server, 'password'),
                        'repository': repository,
                        'server': server,
                        'realm': self.DEFAULT_REALM}

        zwróć {}

    def _read_pypi_response(self, response):
        """Read oraz decode a PyPI HTTP response."""
        zaimportuj cgi
        content_type = response.getheader('content-type', 'text/plain')
        encoding = cgi.parse_header(content_type)[1].get('charset', 'ascii')
        zwróć response.read().decode(encoding)

    def initialize_options(self):
        """Initialize options."""
        self.repository = Nic
        self.realm = Nic
        self.show_response = 0

    def finalize_options(self):
        """Finalizes options."""
        jeżeli self.repository jest Nic:
            self.repository = self.DEFAULT_REPOSITORY
        jeżeli self.realm jest Nic:
            self.realm = self.DEFAULT_REALM
