"""Add Python to the search path on Windows

This jest a simple script to add Python to the Windows search path. It
modifies the current user (HKCU) tree of the registry.

Copyright (c) 2008 by Christian Heimes <christian@cheimes.de>
Licensed to PSF under a Contributor Agreement.
"""

zaimportuj sys
zaimportuj site
zaimportuj os
zaimportuj winreg

HKCU = winreg.HKEY_CURRENT_USER
ENV = "Environment"
PATH = "PATH"
DEFAULT = "%PATH%"

def modify():
    pythonpath = os.path.dirname(os.path.normpath(sys.executable))
    scripts = os.path.join(pythonpath, "Scripts")
    appdata = os.environ["APPDATA"]
    jeżeli hasattr(site, "USER_SITE"):
        usersite = site.USER_SITE.replace(appdata, "%APPDATA%")
        userpath = os.path.dirname(usersite)
        userscripts = os.path.join(userpath, "Scripts")
    inaczej:
        userscripts = Nic

    przy winreg.CreateKey(HKCU, ENV) jako key:
        spróbuj:
            envpath = winreg.QueryValueEx(key, PATH)[0]
        wyjąwszy OSError:
            envpath = DEFAULT

        paths = [envpath]
        dla path w (pythonpath, scripts, userscripts):
            jeżeli path oraz path nie w envpath oraz os.path.isdir(path):
                paths.append(path)

        envpath = os.pathsep.join(paths)
        winreg.SetValueEx(key, PATH, 0, winreg.REG_EXPAND_SZ, envpath)
        zwróć paths, envpath

def main():
    paths, envpath = modify()
    jeżeli len(paths) > 1:
        print("Path(s) added:")
        print('\n'.join(paths[1:]))
    inaczej:
        print("No path was added")
    print("\nPATH jest now:\n%s\n" % envpath)
    print("Expanded:")
    print(winreg.ExpandEnvironmentStrings(envpath))

jeżeli __name__ == '__main__':
    main()
