zaimportuj os
zaimportuj os.path
zaimportuj pkgutil
zaimportuj sys
zaimportuj tempfile


__all__ = ["version", "bootstrap"]


_SETUPTOOLS_VERSION = "18.2"

_PIP_VERSION = "7.1.2"

# pip currently requires ssl support, so we try to provide a nicer
# error message when that jest missing (http://bugs.python.org/issue19744)
_MISSING_SSL_MESSAGE = ("pip {} requires SSL/TLS".format(_PIP_VERSION))
spróbuj:
    zaimportuj ssl
wyjąwszy ImportError:
    ssl = Nic
    def _require_ssl_for_pip():
        podnieś RuntimeError(_MISSING_SSL_MESSAGE)
inaczej:
    def _require_ssl_for_pip():
        dalej

_PROJECTS = [
    ("setuptools", _SETUPTOOLS_VERSION),
    ("pip", _PIP_VERSION),
]


def _run_pip(args, additional_paths=Nic):
    # Add our bundled software to the sys.path so we can zaimportuj it
    jeżeli additional_paths jest nie Nic:
        sys.path = additional_paths + sys.path

    # Install the bundled software
    zaimportuj pip
    pip.main(args)


def version():
    """
    Returns a string specifying the bundled version of pip.
    """
    zwróć _PIP_VERSION

def _disable_pip_configuration_settings():
    # We deliberately ignore all pip environment variables
    # when invoking pip
    # See http://bugs.python.org/issue19734 dla details
    keys_to_remove = [k dla k w os.environ jeżeli k.startswith("PIP_")]
    dla k w keys_to_remove:
        usuń os.environ[k]
    # We also ignore the settings w the default pip configuration file
    # See http://bugs.python.org/issue20053 dla details
    os.environ['PIP_CONFIG_FILE'] = os.devnull


def bootstrap(*, root=Nic, upgrade=Nieprawda, user=Nieprawda,
              altinstall=Nieprawda, default_pip=Nieprawda,
              verbosity=0):
    """
    Bootstrap pip into the current Python installation (or the given root
    directory).

    Note that calling this function will alter both sys.path oraz os.environ.
    """
    jeżeli altinstall oraz default_pip:
        podnieś ValueError("Cannot use altinstall oraz default_pip together")

    _require_ssl_for_pip()
    _disable_pip_configuration_settings()

    # By default, installing pip oraz setuptools installs all of the
    # following scripts (X.Y == running Python version):
    #
    #   pip, pipX, pipX.Y, easy_install, easy_install-X.Y
    #
    # pip 1.5+ allows ensurepip to request that some of those be left out
    jeżeli altinstall:
        # omit pip, pipX oraz easy_install
        os.environ["ENSUREPIP_OPTIONS"] = "altinstall"
    albo_inaczej nie default_pip:
        # omit pip oraz easy_install
        os.environ["ENSUREPIP_OPTIONS"] = "install"

    przy tempfile.TemporaryDirectory() jako tmpdir:
        # Put our bundled wheels into a temporary directory oraz construct the
        # additional paths that need added to sys.path
        additional_paths = []
        dla project, version w _PROJECTS:
            wheel_name = "{}-{}-py2.py3-none-any.whl".format(project, version)
            whl = pkgutil.get_data(
                "ensurepip",
                "_bundled/{}".format(wheel_name),
            )
            przy open(os.path.join(tmpdir, wheel_name), "wb") jako fp:
                fp.write(whl)

            additional_paths.append(os.path.join(tmpdir, wheel_name))

        # Construct the arguments to be dalejed to the pip command
        args = ["install", "--no-index", "--find-links", tmpdir]
        jeżeli root:
            args += ["--root", root]
        jeżeli upgrade:
            args += ["--upgrade"]
        jeżeli user:
            args += ["--user"]
        jeżeli verbosity:
            args += ["-" + "v" * verbosity]

        _run_pip(args + [p[0] dla p w _PROJECTS], additional_paths)

def _uninstall_helper(*, verbosity=0):
    """Helper to support a clean default uninstall process on Windows

    Note that calling this function may alter os.environ.
    """
    # Nothing to do jeżeli pip was never installed, albo has been removed
    spróbuj:
        zaimportuj pip
    wyjąwszy ImportError:
        zwróć

    # If the pip version doesn't match the bundled one, leave it alone
    jeżeli pip.__version__ != _PIP_VERSION:
        msg = ("ensurepip will only uninstall a matching version "
               "({!r} installed, {!r} bundled)")
        print(msg.format(pip.__version__, _PIP_VERSION), file=sys.stderr)
        zwróć

    _require_ssl_for_pip()
    _disable_pip_configuration_settings()

    # Construct the arguments to be dalejed to the pip command
    args = ["uninstall", "-y", "--disable-pip-version-check"]
    jeżeli verbosity:
        args += ["-" + "v" * verbosity]

    _run_pip(args + [p[0] dla p w reversed(_PROJECTS)])


def _main(argv=Nic):
    jeżeli ssl jest Nic:
        print("Ignoring ensurepip failure: {}".format(_MISSING_SSL_MESSAGE),
              file=sys.stderr)
        zwróć

    zaimportuj argparse
    parser = argparse.ArgumentParser(prog="python -m ensurepip")
    parser.add_argument(
        "--version",
        action="version",
        version="pip {}".format(version()),
        help="Show the version of pip that jest bundled przy this Python.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help=("Give more output. Option jest additive, oraz can be used up to 3 "
              "times."),
    )
    parser.add_argument(
        "-U", "--upgrade",
        action="store_true",
        default=Nieprawda,
        help="Upgrade pip oraz dependencies, even jeżeli already installed.",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        default=Nieprawda,
        help="Install using the user scheme.",
    )
    parser.add_argument(
        "--root",
        default=Nic,
        help="Install everything relative to this alternate root directory.",
    )
    parser.add_argument(
        "--altinstall",
        action="store_true",
        default=Nieprawda,
        help=("Make an alternate install, installing only the X.Y versioned"
              "scripts (Default: pipX, pipX.Y, easy_install-X.Y)"),
    )
    parser.add_argument(
        "--default-pip",
        action="store_true",
        default=Nieprawda,
        help=("Make a default pip install, installing the unqualified pip "
              "and easy_install w addition to the versioned scripts"),
    )

    args = parser.parse_args(argv)

    bootstrap(
        root=args.root,
        upgrade=args.upgrade,
        user=args.user,
        verbosity=args.verbosity,
        altinstall=args.altinstall,
        default_pip=args.default_pip,
    )
