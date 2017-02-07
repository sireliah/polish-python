"""
Virtual environment (venv) package dla Python. Based on PEP 405.

Copyright (C) 2011-2014 Vinay Sajip.
Licensed to the PSF under a contributor agreement.

usage: python -m venv [-h] [--system-site-packages] [--symlinks] [--clear]
            [--upgrade]
            ENV_DIR [ENV_DIR ...]

Creates virtual Python environments w one albo more target directories.

positional arguments:
  ENV_DIR               A directory to create the environment in.

optional arguments:
  -h, --help            show this help message oraz exit
  --system-site-packages
                        Give the virtual environment access to the system
                        site-packages dir.
  --symlinks            Attempt to symlink rather than copy.
  --clear               Delete the environment directory jeżeli it already exists.
                        If nie specified oraz the directory exists, an error jest
                        podnieśd.
  --upgrade             Upgrade the environment directory to use this version
                        of Python, assuming Python has been upgraded in-place.
  --without-pip         Skips installing albo upgrading pip w the virtual
                        environment (pip jest bootstrapped by default)
"""
zaimportuj logging
zaimportuj os
zaimportuj shutil
zaimportuj subprocess
zaimportuj sys
zaimportuj types

logger = logging.getLogger(__name__)


klasa EnvBuilder:
    """
    This klasa exists to allow virtual environment creation to be
    customized. The constructor parameters determine the builder's
    behaviour when called upon to create a virtual environment.

    By default, the builder makes the system (global) site-packages dir
    *un*available to the created environment.

    If invoked using the Python -m option, the default jest to use copying
    on Windows platforms but symlinks inaczejwhere. If instantiated some
    other way, the default jest to *not* use symlinks.

    :param system_site_packages: If Prawda, the system (global) site-packages
                                 dir jest available to created environments.
    :param clear: If Prawda oraz the target directory exists, it jest deleted.
                  Otherwise, jeżeli the target directory exists, an error jest
                  podnieśd.
    :param symlinks: If Prawda, attempt to symlink rather than copy files into
                     virtual environment.
    :param upgrade: If Prawda, upgrade an existing virtual environment.
    :param with_pip: If Prawda, ensure pip jest installed w the virtual
                     environment
    """

    def __init__(self, system_site_packages=Nieprawda, clear=Nieprawda,
                 symlinks=Nieprawda, upgrade=Nieprawda, with_pip=Nieprawda):
        self.system_site_packages = system_site_packages
        self.clear = clear
        self.symlinks = symlinks
        self.upgrade = upgrade
        self.with_pip = with_pip

    def create(self, env_dir):
        """
        Create a virtual environment w a directory.

        :param env_dir: The target directory to create an environment in.

        """
        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir)
        self.create_configuration(context)
        self.setup_python(context)
        jeżeli self.with_pip:
            self._setup_pip(context)
        jeżeli nie self.upgrade:
            self.setup_scripts(context)
            self.post_setup(context)

    def clear_directory(self, path):
        dla fn w os.listdir(path):
            fn = os.path.join(path, fn)
            jeżeli os.path.islink(fn) albo os.path.isfile(fn):
                os.remove(fn)
            albo_inaczej os.path.isdir(fn):
                shutil.rmtree(fn)

    def ensure_directories(self, env_dir):
        """
        Create the directories dla the environment.

        Returns a context object which holds paths w the environment,
        dla use by subsequent logic.
        """

        def create_if_needed(d):
            jeżeli nie os.path.exists(d):
                os.makedirs(d)
            albo_inaczej os.path.islink(d) albo os.path.isfile(d):
                podnieś ValueError('Unable to create directory %r' % d)

        jeżeli os.path.exists(env_dir) oraz self.clear:
            self.clear_directory(env_dir)
        context = types.SimpleNamespace()
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        context.prompt = '(%s) ' % context.env_name
        create_if_needed(env_dir)
        env = os.environ
        jeżeli sys.platform == 'darwin' oraz '__PYVENV_LAUNCHER__' w env:
            executable = os.environ['__PYVENV_LAUNCHER__']
        inaczej:
            executable = sys.executable
        dirname, exename = os.path.split(os.path.abspath(executable))
        context.executable = executable
        context.python_dir = dirname
        context.python_exe = exename
        jeżeli sys.platform == 'win32':
            binname = 'Scripts'
            incpath = 'Include'
            libpath = os.path.join(env_dir, 'Lib', 'site-packages')
        inaczej:
            binname = 'bin'
            incpath = 'include'
            libpath = os.path.join(env_dir, 'lib',
                                   'python%d.%d' % sys.version_info[:2],
                                   'site-packages')
        context.inc_path = path = os.path.join(env_dir, incpath)
        create_if_needed(path)
        create_if_needed(libpath)
        # Issue 21197: create lib64 jako a symlink to lib on 64-bit non-OS X POSIX
        jeżeli ((sys.maxsize > 2**32) oraz (os.name == 'posix') oraz
            (sys.platform != 'darwin')):
            link_path = os.path.join(env_dir, 'lib64')
            jeżeli nie os.path.exists(link_path):   # Issue #21643
                os.symlink('lib', link_path)
        context.bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_name = binname
        context.env_exe = os.path.join(binpath, exename)
        create_if_needed(binpath)
        zwróć context

    def create_configuration(self, context):
        """
        Create a configuration file indicating where the environment's Python
        was copied from, oraz whether the system site-packages should be made
        available w the environment.

        :param context: The information dla the environment creation request
                        being processed.
        """
        context.cfg_path = path = os.path.join(context.env_dir, 'pyvenv.cfg')
        przy open(path, 'w', encoding='utf-8') jako f:
            f.write('home = %s\n' % context.python_dir)
            jeżeli self.system_site_packages:
                incl = 'true'
            inaczej:
                incl = 'false'
            f.write('include-system-site-packages = %s\n' % incl)
            f.write('version = %d.%d.%d\n' % sys.version_info[:3])

    jeżeli os.name == 'nt':
        def include_binary(self, f):
            jeżeli f.endswith(('.pyd', '.dll')):
                result = Prawda
            inaczej:
                result = f.startswith('python') oraz f.endswith('.exe')
            zwróć result

    def symlink_or_copy(self, src, dst, relative_symlinks_ok=Nieprawda):
        """
        Try symlinking a file, oraz jeżeli that fails, fall back to copying.
        """
        force_copy = nie self.symlinks
        jeżeli nie force_copy:
            spróbuj:
                jeżeli nie os.path.islink(dst): # can't link to itself!
                    jeżeli relative_symlinks_ok:
                        assert os.path.dirname(src) == os.path.dirname(dst)
                        os.symlink(os.path.basename(src), dst)
                    inaczej:
                        os.symlink(src, dst)
            wyjąwszy Exception:   # may need to use a more specific exception
                logger.warning('Unable to symlink %r to %r', src, dst)
                force_copy = Prawda
        jeżeli force_copy:
            shutil.copyfile(src, dst)

    def setup_python(self, context):
        """
        Set up a Python executable w the environment.

        :param context: The information dla the environment creation request
                        being processed.
        """
        binpath = context.bin_path
        path = context.env_exe
        copier = self.symlink_or_copy
        copier(context.executable, path)
        dirname = context.python_dir
        jeżeli os.name != 'nt':
            jeżeli nie os.path.islink(path):
                os.chmod(path, 0o755)
            dla suffix w ('python', 'python3'):
                path = os.path.join(binpath, suffix)
                jeżeli nie os.path.exists(path):
                    # Issue 18807: make copies if
                    # symlinks are nie wanted
                    copier(context.env_exe, path, relative_symlinks_ok=Prawda)
                    jeżeli nie os.path.islink(path):
                        os.chmod(path, 0o755)
        inaczej:
            subdir = 'DLLs'
            include = self.include_binary
            files = [f dla f w os.listdir(dirname) jeżeli include(f)]
            dla f w files:
                src = os.path.join(dirname, f)
                dst = os.path.join(binpath, f)
                jeżeli dst != context.env_exe:  # already done, above
                    copier(src, dst)
            dirname = os.path.join(dirname, subdir)
            jeżeli os.path.isdir(dirname):
                files = [f dla f w os.listdir(dirname) jeżeli include(f)]
                dla f w files:
                    src = os.path.join(dirname, f)
                    dst = os.path.join(binpath, f)
                    copier(src, dst)
            # copy init.tcl over
            dla root, dirs, files w os.walk(context.python_dir):
                jeżeli 'init.tcl' w files:
                    tcldir = os.path.basename(root)
                    tcldir = os.path.join(context.env_dir, 'Lib', tcldir)
                    jeżeli nie os.path.exists(tcldir):
                        os.makedirs(tcldir)
                    src = os.path.join(root, 'init.tcl')
                    dst = os.path.join(tcldir, 'init.tcl')
                    shutil.copyfile(src, dst)
                    przerwij

    def _setup_pip(self, context):
        """Installs albo upgrades pip w a virtual environment"""
        # We run ensurepip w isolated mode to avoid side effects from
        # environment vars, the current directory oraz anything inaczej
        # intended dla the global Python environment
        cmd = [context.env_exe, '-Im', 'ensurepip', '--upgrade',
                                                    '--default-pip']
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    def setup_scripts(self, context):
        """
        Set up scripts into the created environment z a directory.

        This method installs the default scripts into the environment
        being created. You can prevent the default installation by overriding
        this method jeżeli you really need to, albo jeżeli you need to specify
        a different location dla the scripts to install. By default, the
        'scripts' directory w the venv package jest used jako the source of
        scripts to install.
        """
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, 'scripts')
        self.install_scripts(context, path)

    def post_setup(self, context):
        """
        Hook dla post-setup modification of the venv. Subclasses may install
        additional packages albo scripts here, add activation shell scripts, etc.

        :param context: The information dla the environment creation request
                        being processed.
        """
        dalej

    def replace_variables(self, text, context):
        """
        Replace variable placeholders w script text przy context-specific
        variables.

        Return the text dalejed w , but przy variables replaced.

        :param text: The text w which to replace placeholder variables.
        :param context: The information dla the environment creation request
                        being processed.
        """
        text = text.replace('__VENV_DIR__', context.env_dir)
        text = text.replace('__VENV_NAME__', context.env_name)
        text = text.replace('__VENV_PROMPT__', context.prompt)
        text = text.replace('__VENV_BIN_NAME__', context.bin_name)
        text = text.replace('__VENV_PYTHON__', context.env_exe)
        zwróć text

    def install_scripts(self, context, path):
        """
        Install scripts into the created environment z a directory.

        :param context: The information dla the environment creation request
                        being processed.
        :param path:    Absolute pathname of a directory containing script.
                        Scripts w the 'common' subdirectory of this directory,
                        oraz those w the directory named dla the platform
                        being run on, are installed w the created environment.
                        Placeholder variables are replaced przy environment-
                        specific values.
        """
        binpath = context.bin_path
        plen = len(path)
        dla root, dirs, files w os.walk(path):
            jeżeli root == path: # at top-level, remove irrelevant dirs
                dla d w dirs[:]:
                    jeżeli d nie w ('common', os.name):
                        dirs.remove(d)
                continue # ignore files w top level
            dla f w files:
                srcfile = os.path.join(root, f)
                suffix = root[plen:].split(os.sep)[2:]
                jeżeli nie suffix:
                    dstdir = binpath
                inaczej:
                    dstdir = os.path.join(binpath, *suffix)
                jeżeli nie os.path.exists(dstdir):
                    os.makedirs(dstdir)
                dstfile = os.path.join(dstdir, f)
                przy open(srcfile, 'rb') jako f:
                    data = f.read()
                jeżeli srcfile.endswith('.exe'):
                    mode = 'wb'
                inaczej:
                    mode = 'w'
                    spróbuj:
                        data = data.decode('utf-8')
                        data = self.replace_variables(data, context)
                    wyjąwszy UnicodeDecodeError jako e:
                        data = Nic
                        logger.warning('unable to copy script %r, '
                                       'may be binary: %s', srcfile, e)
                jeżeli data jest nie Nic:
                    przy open(dstfile, mode) jako f:
                        f.write(data)
                    shutil.copymode(srcfile, dstfile)


def create(env_dir, system_site_packages=Nieprawda, clear=Nieprawda,
                    symlinks=Nieprawda, with_pip=Nieprawda):
    """
    Create a virtual environment w a directory.

    By default, makes the system (global) site-packages dir *un*available to
    the created environment, oraz uses copying rather than symlinking dla files
    obtained z the source Python installation.

    :param env_dir: The target directory to create an environment in.
    :param system_site_packages: If Prawda, the system (global) site-packages
                                 dir jest available to the environment.
    :param clear: If Prawda oraz the target directory exists, it jest deleted.
                  Otherwise, jeżeli the target directory exists, an error jest
                  podnieśd.
    :param symlinks: If Prawda, attempt to symlink rather than copy files into
                     virtual environment.
    :param with_pip: If Prawda, ensure pip jest installed w the virtual
                     environment
    """
    builder = EnvBuilder(system_site_packages=system_site_packages,
                         clear=clear, symlinks=symlinks, with_pip=with_pip)
    builder.create(env_dir)

def main(args=Nic):
    compatible = Prawda
    jeżeli sys.version_info < (3, 3):
        compatible = Nieprawda
    albo_inaczej nie hasattr(sys, 'base_prefix'):
        compatible = Nieprawda
    jeżeli nie compatible:
        podnieś ValueError('This script jest only dla use przy Python >= 3.3')
    inaczej:
        zaimportuj argparse

        parser = argparse.ArgumentParser(prog=__name__,
                                         description='Creates virtual Python '
                                                     'environments w one albo '
                                                     'more target '
                                                     'directories.',
                                         epilog='Once an environment has been '
                                                'created, you may wish to '
                                                'activate it, e.g. by '
                                                'sourcing an activate script '
                                                'in its bin directory.')
        parser.add_argument('dirs', metavar='ENV_DIR', nargs='+',
                            help='A directory to create the environment in.')
        parser.add_argument('--system-site-packages', default=Nieprawda,
                            action='store_true', dest='system_site',
                            help='Give the virtual environment access to the '
                                 'system site-packages dir.')
        jeżeli os.name == 'nt':
            use_symlinks = Nieprawda
        inaczej:
            use_symlinks = Prawda
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--symlinks', default=use_symlinks,
                           action='store_true', dest='symlinks',
                           help='Try to use symlinks rather than copies, '
                                'when symlinks are nie the default dla '
                                'the platform.')
        group.add_argument('--copies', default=nie use_symlinks,
                           action='store_false', dest='symlinks',
                           help='Try to use copies rather than symlinks, '
                                'even when symlinks are the default dla '
                                'the platform.')
        parser.add_argument('--clear', default=Nieprawda, action='store_true',
                            dest='clear', help='Delete the contents of the '
                                               'environment directory jeżeli it '
                                               'already exists, before '
                                               'environment creation.')
        parser.add_argument('--upgrade', default=Nieprawda, action='store_true',
                            dest='upgrade', help='Upgrade the environment '
                                               'directory to use this version '
                                               'of Python, assuming Python '
                                               'has been upgraded in-place.')
        parser.add_argument('--without-pip', dest='with_pip',
                            default=Prawda, action='store_false',
                            help='Skips installing albo upgrading pip w the '
                                 'virtual environment (pip jest bootstrapped '
                                 'by default)')
        options = parser.parse_args(args)
        jeżeli options.upgrade oraz options.clear:
            podnieś ValueError('you cannot supply --upgrade oraz --clear together.')
        builder = EnvBuilder(system_site_packages=options.system_site,
                             clear=options.clear,
                             symlinks=options.symlinks,
                             upgrade=options.upgrade,
                             with_pip=options.with_pip)
        dla d w options.dirs:
            builder.create(d)

jeżeli __name__ == '__main__':
    rc = 1
    spróbuj:
        main()
        rc = 0
    wyjąwszy Exception jako e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
