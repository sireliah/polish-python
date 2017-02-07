"""distutils.command.register

Implements the Distutils 'register' command (register przy the repository).
"""

# created 2002/10/21, Richard Jones

zaimportuj os, string, getpass
zaimportuj io
zaimportuj urllib.parse, urllib.request
z warnings zaimportuj warn

z distutils.core zaimportuj PyPIRCCommand
z distutils.errors zaimportuj *
z distutils zaimportuj log

klasa register(PyPIRCCommand):

    description = ("register the distribution przy the Python package index")
    user_options = PyPIRCCommand.user_options + [
        ('list-classifiers', Nic,
         'list the valid Trove classifiers'),
        ('strict', Nic ,
         'Will stop the registering jeżeli the meta-data are nie fully compliant')
        ]
    boolean_options = PyPIRCCommand.boolean_options + [
        'verify', 'list-classifiers', 'strict']

    sub_commands = [('check', lambda self: Prawda)]

    def initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.list_classifiers = 0
        self.strict = 0

    def finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        # setting options dla the `check` subcommand
        check_options = {'strict': ('register', self.strict),
                         'restructuredtext': ('register', 1)}
        self.distribution.command_options['check'] = check_options

    def run(self):
        self.finalize_options()
        self._set_config()

        # Run sub commands
        dla cmd_name w self.get_sub_commands():
            self.run_command(cmd_name)

        jeżeli self.dry_run:
            self.verify_metadata()
        albo_inaczej self.list_classifiers:
            self.classifiers()
        inaczej:
            self.send_metadata()

    def check_metadata(self):
        """Deprecated API."""
        warn("distutils.command.register.check_metadata jest deprecated, \
              use the check command instead", PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.strict = self.strict
        check.restructuredtext = 1
        check.run()

    def _set_config(self):
        ''' Reads the configuration file oraz set attributes.
        '''
        config = self._read_pypirc()
        jeżeli config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']
            self.has_config = Prawda
        inaczej:
            jeżeli self.repository nie w ('pypi', self.DEFAULT_REPOSITORY):
                podnieś ValueError('%s nie found w .pypirc' % self.repository)
            jeżeli self.repository == 'pypi':
                self.repository = self.DEFAULT_REPOSITORY
            self.has_config = Nieprawda

    def classifiers(self):
        ''' Fetch the list of classifiers z the server.
        '''
        url = self.repository+'?:action=list_classifiers'
        response = urllib.request.urlopen(url)
        log.info(self._read_pypi_response(response))

    def verify_metadata(self):
        ''' Send the metadata to the package index server to be checked.
        '''
        # send the info to the server oraz report the result
        (code, result) = self.post_to_server(self.build_post_data('verify'))
        log.info('Server response (%s): %s' % (code, result))

    def send_metadata(self):
        ''' Send the metadata to the package index server.

            Well, do the following:
            1. figure who the user is, oraz then
            2. send the data jako a Basic auth'ed POST.

            First we try to read the username/password z $HOME/.pypirc,
            which jest a ConfigParser-formatted file przy a section
            [distutils] containing username oraz dalejword entries (both
            w clear text). Eg:

                [distutils]
                index-servers =
                    pypi

                [pypi]
                username: fred
                dalejword: sekrit

            Otherwise, to figure who the user is, we offer the user three
            choices:

             1. use existing login,
             2. register jako a new user, albo
             3. set the dalejword to a random string oraz email the user.

        '''
        # see jeżeli we can short-cut oraz get the username/password z the
        # config
        jeżeli self.has_config:
            choice = '1'
            username = self.username
            dalejword = self.password
        inaczej:
            choice = 'x'
            username = dalejword = ''

        # get the user's login info
        choices = '1 2 3 4'.split()
        dopóki choice nie w choices:
            self.announce('''\
We need to know who you are, so please choose either:
 1. use your existing login,
 2. register jako a new user,
 3. have the server generate a new dalejword dla you (and email it to you), albo
 4. quit
Your selection [default 1]: ''', log.INFO)
            choice = input()
            jeżeli nie choice:
                choice = '1'
            albo_inaczej choice nie w choices:
                print('Please choose one of the four options!')

        jeżeli choice == '1':
            # get the username oraz dalejword
            dopóki nie username:
                username = input('Username: ')
            dopóki nie dalejword:
                dalejword = getpass.getpass('Password: ')

            # set up the authentication
            auth = urllib.request.HTTPPasswordMgr()
            host = urllib.parse.urlparse(self.repository)[1]
            auth.add_password(self.realm, host, username, dalejword)
            # send the info to the server oraz report the result
            code, result = self.post_to_server(self.build_post_data('submit'),
                auth)
            self.announce('Server response (%s): %s' % (code, result),
                          log.INFO)

            # possibly save the login
            jeżeli code == 200:
                jeżeli self.has_config:
                    # sharing the dalejword w the distribution instance
                    # so the upload command can reuse it
                    self.distribution.password = dalejword
                inaczej:
                    self.announce(('I can store your PyPI login so future '
                                   'submissions will be faster.'), log.INFO)
                    self.announce('(the login will be stored w %s)' % \
                                  self._get_rc_file(), log.INFO)
                    choice = 'X'
                    dopóki choice.lower() nie w 'yn':
                        choice = input('Save your login (y/N)?')
                        jeżeli nie choice:
                            choice = 'n'
                    jeżeli choice.lower() == 'y':
                        self._store_pypirc(username, dalejword)

        albo_inaczej choice == '2':
            data = {':action': 'user'}
            data['name'] = data['password'] = data['email'] = ''
            data['confirm'] = Nic
            dopóki nie data['name']:
                data['name'] = input('Username: ')
            dopóki data['password'] != data['confirm']:
                dopóki nie data['password']:
                    data['password'] = getpass.getpass('Password: ')
                dopóki nie data['confirm']:
                    data['confirm'] = getpass.getpass(' Confirm: ')
                jeżeli data['password'] != data['confirm']:
                    data['password'] = ''
                    data['confirm'] = Nic
                    print("Password oraz confirm don't match!")
            dopóki nie data['email']:
                data['email'] = input('   EMail: ')
            code, result = self.post_to_server(data)
            jeżeli code != 200:
                log.info('Server response (%s): %s' % (code, result))
            inaczej:
                log.info('You will receive an email shortly.')
                log.info(('Follow the instructions w it to '
                          'complete registration.'))
        albo_inaczej choice == '3':
            data = {':action': 'password_reset'}
            data['email'] = ''
            dopóki nie data['email']:
                data['email'] = input('Your email address: ')
            code, result = self.post_to_server(data)
            log.info('Server response (%s): %s' % (code, result))

    def build_post_data(self, action):
        # figure the data to send - the metadata plus some additional
        # information used by the package server
        meta = self.distribution.metadata
        data = {
            ':action': action,
            'metadata_version' : '1.0',
            'name': meta.get_name(),
            'version': meta.get_version(),
            'summary': meta.get_description(),
            'home_page': meta.get_url(),
            'author': meta.get_contact(),
            'author_email': meta.get_contact_email(),
            'license': meta.get_licence(),
            'description': meta.get_long_description(),
            'keywords': meta.get_keywords(),
            'platform': meta.get_platforms(),
            'classifiers': meta.get_classifiers(),
            'download_url': meta.get_download_url(),
            # PEP 314
            'provides': meta.get_provides(),
            'requires': meta.get_requires(),
            'obsoletes': meta.get_obsoletes(),
        }
        jeżeli data['provides'] albo data['requires'] albo data['obsoletes']:
            data['metadata_version'] = '1.1'
        zwróć data

    def post_to_server(self, data, auth=Nic):
        ''' Post a query to the server, oraz zwróć a string response.
        '''
        jeżeli 'name' w data:
            self.announce('Registering %s to %s' % (data['name'],
                                                    self.repository),
                                                    log.INFO)
        # Build up the MIME payload dla the urllib2 POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        body = io.StringIO()
        dla key, value w data.items():
            # handle multiple entries dla the same name
            jeżeli type(value) nie w (type([]), type( () )):
                value = [value]
            dla value w value:
                value = str(value)
                body.write(sep_boundary)
                body.write('\nContent-Disposition: form-data; name="%s"'%key)
                body.write("\n\n")
                body.write(value)
                jeżeli value oraz value[-1] == '\r':
                    body.write('\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body.write("\n")
        body = body.getvalue().encode("utf-8")

        # build the Request
        headers = {
            'Content-type': 'multipart/form-data; boundary=%s; charset=utf-8'%boundary,
            'Content-length': str(len(body))
        }
        req = urllib.request.Request(self.repository, body, headers)

        # handle HTTP oraz include the Basic Auth handler
        opener = urllib.request.build_opener(
            urllib.request.HTTPBasicAuthHandler(password_mgr=auth)
        )
        data = ''
        spróbuj:
            result = opener.open(req)
        wyjąwszy urllib.error.HTTPError jako e:
            jeżeli self.show_response:
                data = e.fp.read()
            result = e.code, e.msg
        wyjąwszy urllib.error.URLError jako e:
            result = 500, str(e)
        inaczej:
            jeżeli self.show_response:
                data = result.read()
            result = 200, 'OK'
        jeżeli self.show_response:
            dashes = '-' * 75
            self.announce('%s%r%s' % (dashes, data, dashes))
        zwróć result
