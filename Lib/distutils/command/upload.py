"""
distutils.command.upload

Implements the Distutils 'upload' subcommand (upload package to a package
index).
"""

zaimportuj os
zaimportuj io
zaimportuj platform
zaimportuj hashlib
z base64 zaimportuj standard_b64encode
z urllib.request zaimportuj urlopen, Request, HTTPError
z urllib.parse zaimportuj urlparse
z distutils.errors zaimportuj DistutilsError, DistutilsOptionError
z distutils.core zaimportuj PyPIRCCommand
z distutils.spawn zaimportuj spawn
z distutils zaimportuj log

klasa upload(PyPIRCCommand):

    description = "upload binary package to PyPI"

    user_options = PyPIRCCommand.user_options + [
        ('sign', 's',
         'sign files to upload using gpg'),
        ('identity=', 'i', 'GPG identity used to sign files'),
        ]

    boolean_options = PyPIRCCommand.boolean_options + ['sign']

    def initialize_options(self):
        PyPIRCCommand.initialize_options(self)
        self.username = ''
        self.password = ''
        self.show_response = 0
        self.sign = Nieprawda
        self.identity = Nic

    def finalize_options(self):
        PyPIRCCommand.finalize_options(self)
        jeżeli self.identity oraz nie self.sign:
            podnieś DistutilsOptionError(
                "Must use --sign dla --identity to have meaning"
            )
        config = self._read_pypirc()
        jeżeli config != {}:
            self.username = config['username']
            self.password = config['password']
            self.repository = config['repository']
            self.realm = config['realm']

        # getting the dalejword z the distribution
        # jeżeli previously set by the register command
        jeżeli nie self.password oraz self.distribution.password:
            self.password = self.distribution.password

    def run(self):
        jeżeli nie self.distribution.dist_files:
            msg = "No dist file created w earlier command"
            podnieś DistutilsOptionError(msg)
        dla command, pyversion, filename w self.distribution.dist_files:
            self.upload_file(command, pyversion, filename)

    def upload_file(self, command, pyversion, filename):
        # Makes sure the repository URL jest compliant
        schema, netloc, url, params, query, fragments = \
            urlparse(self.repository)
        jeżeli params albo query albo fragments:
            podnieś AssertionError("Incompatible url %s" % self.repository)

        jeżeli schema nie w ('http', 'https'):
            podnieś AssertionError("unsupported schema " + schema)

        # Sign jeżeli requested
        jeżeli self.sign:
            gpg_args = ["gpg", "--detach-sign", "-a", filename]
            jeżeli self.identity:
                gpg_args[2:2] = ["--local-user", self.identity]
            spawn(gpg_args,
                  dry_run=self.dry_run)

        # Fill w the data - send all the meta-data w case we need to
        # register a new release
        f = open(filename,'rb')
        spróbuj:
            content = f.read()
        w_końcu:
            f.close()
        meta = self.distribution.metadata
        data = {
            # action
            ':action': 'file_upload',
            'protcol_version': '1',

            # identify release
            'name': meta.get_name(),
            'version': meta.get_version(),

            # file content
            'content': (os.path.basename(filename),content),
            'filetype': command,
            'pyversion': pyversion,
            'md5_digest': hashlib.md5(content).hexdigest(),

            # additional meta-data
            'metadata_version': '1.0',
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
        comment = ''
        jeżeli command == 'bdist_rpm':
            dist, version, id = platform.dist()
            jeżeli dist:
                comment = 'built dla %s %s' % (dist, version)
        albo_inaczej command == 'bdist_dumb':
            comment = 'built dla %s' % platform.platform(terse=1)
        data['comment'] = comment

        jeżeli self.sign:
            data['gpg_signature'] = (os.path.basename(filename) + ".asc",
                                     open(filename+".asc", "rb").read())

        # set up the authentication
        user_pass = (self.username + ":" + self.password).encode('ascii')
        # The exact encoding of the authentication string jest debated.
        # Anyway PyPI only accepts ascii dla both username albo dalejword.
        auth = "Basic " + standard_b64encode(user_pass).decode('ascii')

        # Build up the MIME payload dla the POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = b'\r\n--' + boundary.encode('ascii')
        end_boundary = sep_boundary + b'--\r\n'
        body = io.BytesIO()
        dla key, value w data.items():
            title = '\r\nContent-Disposition: form-data; name="%s"' % key
            # handle multiple entries dla the same name
            jeżeli nie isinstance(value, list):
                value = [value]
            dla value w value:
                jeżeli type(value) jest tuple:
                    title += '; filename="%s"' % value[0]
                    value = value[1]
                inaczej:
                    value = str(value).encode('utf-8')
                body.write(sep_boundary)
                body.write(title.encode('utf-8'))
                body.write(b"\r\n\r\n")
                body.write(value)
                jeżeli value oraz value[-1:] == b'\r':
                    body.write(b'\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body = body.getvalue()

        msg = "Submitting %s to %s" % (filename, self.repository)
        self.announce(msg, log.INFO)

        # build the Request
        headers = {
            'Content-type': 'multipart/form-data; boundary=%s' % boundary,
            'Content-length': str(len(body)),
            'Authorization': auth,
        }

        request = Request(self.repository, data=body,
                          headers=headers)
        # send the data
        spróbuj:
            result = urlopen(request)
            status = result.getcode()
            reason = result.msg
        wyjąwszy OSError jako e:
            self.announce(str(e), log.ERROR)
            podnieś
        wyjąwszy HTTPError jako e:
            status = e.code
            reason = e.msg

        jeżeli status == 200:
            self.announce('Server response (%s): %s' % (status, reason),
                          log.INFO)
        inaczej:
            msg = 'Upload failed (%s): %s' % (status, reason)
            self.announce(msg, log.ERROR)
            podnieś DistutilsError(msg)
        jeżeli self.show_response:
            text = self._read_pypi_response(result)
            msg = '\n'.join(('-' * 75, text, '-' * 75))
            self.announce(msg, log.INFO)
