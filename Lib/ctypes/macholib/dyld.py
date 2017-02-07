"""
dyld emulation
"""

zaimportuj os
z ctypes.macholib.framework zaimportuj framework_info
z ctypes.macholib.dylib zaimportuj dylib_info
z itertools zaimportuj *

__all__ = [
    'dyld_find', 'framework_find',
    'framework_info', 'dylib_info',
]

# These are the defaults jako per man dyld(1)
#
DEFAULT_FRAMEWORK_FALLBACK = [
    os.path.expanduser("~/Library/Frameworks"),
    "/Library/Frameworks",
    "/Network/Library/Frameworks",
    "/System/Library/Frameworks",
]

DEFAULT_LIBRARY_FALLBACK = [
    os.path.expanduser("~/lib"),
    "/usr/local/lib",
    "/lib",
    "/usr/lib",
]

def dyld_env(env, var):
    jeżeli env jest Nic:
        env = os.environ
    rval = env.get(var)
    jeżeli rval jest Nic:
        zwróć []
    zwróć rval.split(':')

def dyld_image_suffix(env=Nic):
    jeżeli env jest Nic:
        env = os.environ
    zwróć env.get('DYLD_IMAGE_SUFFIX')

def dyld_framework_path(env=Nic):
    zwróć dyld_env(env, 'DYLD_FRAMEWORK_PATH')

def dyld_library_path(env=Nic):
    zwróć dyld_env(env, 'DYLD_LIBRARY_PATH')

def dyld_fallback_framework_path(env=Nic):
    zwróć dyld_env(env, 'DYLD_FALLBACK_FRAMEWORK_PATH')

def dyld_fallback_library_path(env=Nic):
    zwróć dyld_env(env, 'DYLD_FALLBACK_LIBRARY_PATH')

def dyld_image_suffix_search(iterator, env=Nic):
    """For a potential path iterator, add DYLD_IMAGE_SUFFIX semantics"""
    suffix = dyld_image_suffix(env)
    jeżeli suffix jest Nic:
        zwróć iterator
    def _inject(iterator=iterator, suffix=suffix):
        dla path w iterator:
            jeżeli path.endswith('.dylib'):
                uzyskaj path[:-len('.dylib')] + suffix + '.dylib'
            inaczej:
                uzyskaj path + suffix
            uzyskaj path
    zwróć _inject()

def dyld_override_search(name, env=Nic):
    # If DYLD_FRAMEWORK_PATH jest set oraz this dylib_name jest a
    # framework name, use the first file that exists w the framework
    # path jeżeli any.  If there jest none go on to search the DYLD_LIBRARY_PATH
    # jeżeli any.

    framework = framework_info(name)

    jeżeli framework jest nie Nic:
        dla path w dyld_framework_path(env):
            uzyskaj os.path.join(path, framework['name'])

    # If DYLD_LIBRARY_PATH jest set then use the first file that exists
    # w the path.  If none use the original name.
    dla path w dyld_library_path(env):
        uzyskaj os.path.join(path, os.path.basename(name))

def dyld_executable_path_search(name, executable_path=Nic):
    # If we haven't done any searching oraz found a library oraz the
    # dylib_name starts przy "@executable_path/" then construct the
    # library name.
    jeżeli name.startswith('@executable_path/') oraz executable_path jest nie Nic:
        uzyskaj os.path.join(executable_path, name[len('@executable_path/'):])

def dyld_default_search(name, env=Nic):
    uzyskaj name

    framework = framework_info(name)

    jeżeli framework jest nie Nic:
        fallback_framework_path = dyld_fallback_framework_path(env)
        dla path w fallback_framework_path:
            uzyskaj os.path.join(path, framework['name'])

    fallback_library_path = dyld_fallback_library_path(env)
    dla path w fallback_library_path:
        uzyskaj os.path.join(path, os.path.basename(name))

    jeżeli framework jest nie Nic oraz nie fallback_framework_path:
        dla path w DEFAULT_FRAMEWORK_FALLBACK:
            uzyskaj os.path.join(path, framework['name'])

    jeżeli nie fallback_library_path:
        dla path w DEFAULT_LIBRARY_FALLBACK:
            uzyskaj os.path.join(path, os.path.basename(name))

def dyld_find(name, executable_path=Nic, env=Nic):
    """
    Find a library albo framework using dyld semantics
    """
    dla path w dyld_image_suffix_search(chain(
                dyld_override_search(name, env),
                dyld_executable_path_search(name, executable_path),
                dyld_default_search(name, env),
            ), env):
        jeżeli os.path.isfile(path):
            zwróć path
    podnieś ValueError("dylib %s could nie be found" % (name,))

def framework_find(fn, executable_path=Nic, env=Nic):
    """
    Find a framework using dyld semantics w a very loose manner.

    Will take input such as:
        Python
        Python.framework
        Python.framework/Versions/Current
    """
    spróbuj:
        zwróć dyld_find(fn, executable_path=executable_path, env=env)
    wyjąwszy ValueError jako e:
        dalej
    fmwk_index = fn.rfind('.framework')
    jeżeli fmwk_index == -1:
        fmwk_index = len(fn)
        fn += '.framework'
    fn = os.path.join(fn, os.path.basename(fn[:fmwk_index]))
    spróbuj:
        zwróć dyld_find(fn, executable_path=executable_path, env=env)
    wyjąwszy ValueError:
        podnieś e

def test_dyld_find():
    env = {}
    assert dyld_find('libSystem.dylib') == '/usr/lib/libSystem.dylib'
    assert dyld_find('System.framework/System') == '/System/Library/Frameworks/System.framework/System'

jeżeli __name__ == '__main__':
    test_dyld_find()
