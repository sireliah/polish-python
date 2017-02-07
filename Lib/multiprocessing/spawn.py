#
# Code used to start processes when using the spawn albo forkserver
# start methods.
#
# multiprocessing/spawn.py
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

zaimportuj os
zaimportuj pickle
zaimportuj sys
zaimportuj runpy
zaimportuj types

z . zaimportuj get_start_method, set_start_method
z . zaimportuj process
z . zaimportuj util

__all__ = ['_main', 'freeze_support', 'set_executable', 'get_executable',
           'get_preparation_data', 'get_command_line', 'import_main_path']

#
# _python_exe jest the assumed path to the python executable.
# People embedding Python want to modify it.
#

jeżeli sys.platform != 'win32':
    WINEXE = Nieprawda
    WINSERVICE = Nieprawda
inaczej:
    WINEXE = (sys.platform == 'win32' oraz getattr(sys, 'frozen', Nieprawda))
    WINSERVICE = sys.executable.lower().endswith("pythonservice.exe")

jeżeli WINSERVICE:
    _python_exe = os.path.join(sys.exec_prefix, 'python.exe')
inaczej:
    _python_exe = sys.executable

def set_executable(exe):
    global _python_exe
    _python_exe = exe

def get_executable():
    zwróć _python_exe

#
#
#

def is_forking(argv):
    '''
    Return whether commandline indicates we are forking
    '''
    jeżeli len(argv) >= 2 oraz argv[1] == '--multiprocessing-fork':
        zwróć Prawda
    inaczej:
        zwróć Nieprawda


def freeze_support():
    '''
    Run code dla process object jeżeli this w nie the main process
    '''
    jeżeli is_forking(sys.argv):
        kwds = {}
        dla arg w sys.argv[2:]:
            name, value = arg.split('=')
            jeżeli value == 'Nic':
                kwds[name] = Nic
            inaczej:
                kwds[name] = int(value)
        spawn_main(**kwds)
        sys.exit()


def get_command_line(**kwds):
    '''
    Returns prefix of command line used dla spawning a child process
    '''
    jeżeli getattr(sys, 'frozen', Nieprawda):
        zwróć ([sys.executable, '--multiprocessing-fork'] +
                ['%s=%r' % item dla item w kwds.items()])
    inaczej:
        prog = 'z multiprocessing.spawn zaimportuj spawn_main; spawn_main(%s)'
        prog %= ', '.join('%s=%r' % item dla item w kwds.items())
        opts = util._args_from_interpreter_flags()
        zwróć [_python_exe] + opts + ['-c', prog, '--multiprocessing-fork']


def spawn_main(pipe_handle, parent_pid=Nic, tracker_fd=Nic):
    '''
    Run code specifed by data received over pipe
    '''
    assert is_forking(sys.argv)
    jeżeli sys.platform == 'win32':
        zaimportuj msvcrt
        z .reduction zaimportuj steal_handle
        new_handle = steal_handle(parent_pid, pipe_handle)
        fd = msvcrt.open_osfhandle(new_handle, os.O_RDONLY)
    inaczej:
        z . zaimportuj semaphore_tracker
        semaphore_tracker._semaphore_tracker._fd = tracker_fd
        fd = pipe_handle
    exitcode = _main(fd)
    sys.exit(exitcode)


def _main(fd):
    przy os.fdopen(fd, 'rb', closefd=Prawda) jako from_parent:
        process.current_process()._inheriting = Prawda
        spróbuj:
            preparation_data = pickle.load(from_parent)
            prepare(preparation_data)
            self = pickle.load(from_parent)
        w_końcu:
            usuń process.current_process()._inheriting
    zwróć self._bootstrap()


def _check_not_importing_main():
    jeżeli getattr(process.current_process(), '_inheriting', Nieprawda):
        podnieś RuntimeError('''
        An attempt has been made to start a new process before the
        current process has finished its bootstrapping phase.

        This probably means that you are nie using fork to start your
        child processes oraz you have forgotten to use the proper idiom
        w the main module:

            jeżeli __name__ == '__main__':
                freeze_support()
                ...

        The "freeze_support()" line can be omitted jeżeli the program
        jest nie going to be frozen to produce an executable.''')


def get_preparation_data(name):
    '''
    Return info about parent needed by child to unpickle process object
    '''
    _check_not_importing_main()
    d = dict(
        log_to_stderr=util._log_to_stderr,
        authkey=process.current_process().authkey,
        )

    jeżeli util._logger jest nie Nic:
        d['log_level'] = util._logger.getEffectiveLevel()

    sys_path=sys.path.copy()
    spróbuj:
        i = sys_path.index('')
    wyjąwszy ValueError:
        dalej
    inaczej:
        sys_path[i] = process.ORIGINAL_DIR

    d.update(
        name=name,
        sys_path=sys_path,
        sys_argv=sys.argv,
        orig_dir=process.ORIGINAL_DIR,
        dir=os.getcwd(),
        start_method=get_start_method(),
        )

    # Figure out whether to initialise main w the subprocess jako a module
    # albo through direct execution (or to leave it alone entirely)
    main_module = sys.modules['__main__']
    main_mod_name = getattr(main_module.__spec__, "name", Nic)
    jeżeli main_mod_name jest nie Nic:
        d['init_main_from_name'] = main_mod_name
    albo_inaczej sys.platform != 'win32' albo (nie WINEXE oraz nie WINSERVICE):
        main_path = getattr(main_module, '__file__', Nic)
        jeżeli main_path jest nie Nic:
            jeżeli (nie os.path.isabs(main_path) oraz
                        process.ORIGINAL_DIR jest nie Nic):
                main_path = os.path.join(process.ORIGINAL_DIR, main_path)
            d['init_main_from_path'] = os.path.normpath(main_path)

    zwróć d

#
# Prepare current process
#

old_main_modules = []

def prepare(data):
    '''
    Try to get current process ready to unpickle process object
    '''
    jeżeli 'name' w data:
        process.current_process().name = data['name']

    jeżeli 'authkey' w data:
        process.current_process().authkey = data['authkey']

    jeżeli 'log_to_stderr' w data oraz data['log_to_stderr']:
        util.log_to_stderr()

    jeżeli 'log_level' w data:
        util.get_logger().setLevel(data['log_level'])

    jeżeli 'sys_path' w data:
        sys.path = data['sys_path']

    jeżeli 'sys_argv' w data:
        sys.argv = data['sys_argv']

    jeżeli 'dir' w data:
        os.chdir(data['dir'])

    jeżeli 'orig_dir' w data:
        process.ORIGINAL_DIR = data['orig_dir']

    jeżeli 'start_method' w data:
        set_start_method(data['start_method'])

    jeżeli 'init_main_from_name' w data:
        _fixup_main_from_name(data['init_main_from_name'])
    albo_inaczej 'init_main_from_path' w data:
        _fixup_main_from_path(data['init_main_from_path'])

# Multiprocessing module helpers to fix up the main module w
# spawned subprocesses
def _fixup_main_from_name(mod_name):
    # __main__.py files dla packages, directories, zip archives, etc, run
    # their "main only" code unconditionally, so we don't even try to
    # populate anything w __main__, nor do we make any changes to
    # __main__ attributes
    current_main = sys.modules['__main__']
    jeżeli mod_name == "__main__" albo mod_name.endswith(".__main__"):
        zwróć

    # If this process was forked, __main__ may already be populated
    jeżeli getattr(current_main.__spec__, "name", Nic) == mod_name:
        zwróć

    # Otherwise, __main__ may contain some non-main code where we need to
    # support unpickling it properly. We rerun it jako __mp_main__ oraz make
    # the normal __main__ an alias to that
    old_main_modules.append(current_main)
    main_module = types.ModuleType("__mp_main__")
    main_content = runpy.run_module(mod_name,
                                    run_name="__mp_main__",
                                    alter_sys=Prawda)
    main_module.__dict__.update(main_content)
    sys.modules['__main__'] = sys.modules['__mp_main__'] = main_module


def _fixup_main_from_path(main_path):
    # If this process was forked, __main__ may already be populated
    current_main = sys.modules['__main__']

    # Unfortunately, the main ipython launch script historically had no
    # "jeżeli __name__ == '__main__'" guard, so we work around that
    # by treating it like a __main__.py file
    # See https://github.com/ipython/ipython/issues/4698
    main_name = os.path.splitext(os.path.basename(main_path))[0]
    jeżeli main_name == 'ipython':
        zwróć

    # Otherwise, jeżeli __file__ already has the setting we expect,
    # there's nothing more to do
    jeżeli getattr(current_main, '__file__', Nic) == main_path:
        zwróć

    # If the parent process has sent a path through rather than a module
    # name we assume it jest an executable script that may contain
    # non-main code that needs to be executed
    old_main_modules.append(current_main)
    main_module = types.ModuleType("__mp_main__")
    main_content = runpy.run_path(main_path,
                                  run_name="__mp_main__")
    main_module.__dict__.update(main_content)
    sys.modules['__main__'] = sys.modules['__mp_main__'] = main_module


def import_main_path(main_path):
    '''
    Set sys.modules['__main__'] to module at main_path
    '''
    _fixup_main_from_path(main_path)
