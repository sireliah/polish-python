'''
Downloads oraz extracts WiX to a local directory
'''

__author__ = 'Steve Dower <steve.dower@microsoft.com>'

zaimportuj io
zaimportuj os
zaimportuj sys

z pathlib zaimportuj Path
z subprocess zaimportuj Popen
z zipfile zaimportuj ZipFile

EXTERNALS_DIR = Nic
dla p w (Path.cwd() / __file__).parents:
    jeżeli any(p.glob("PCBuild/*.vcxproj")):
        EXTERNALS_DIR = p / "externals"
        przerwij

jeżeli nie EXTERNALS_DIR:
    print("Cannot find project root")
    sys.exit(1)

WIX_BINARIES_ZIP = 'http://wixtoolset.org/downloads/v3.10.0.1823/wix310-binaries.zip'
TARGET_BIN_ZIP = EXTERNALS_DIR / "wix.zip"
TARGET_BIN_DIR = EXTERNALS_DIR / "wix"

POWERSHELL_COMMAND = "[IO.File]::WriteAllBytes('{}', (Invoke-WebRequest {} -UseBasicParsing).Content)"

jeżeli __name__ == '__main__':
    jeżeli TARGET_BIN_DIR.exists() oraz any(TARGET_BIN_DIR.glob("*")):
        print('WiX jest already installed')
        sys.exit(0)

    spróbuj:
        TARGET_BIN_DIR.mkdir()
    wyjąwszy FileExistsError:
        dalej

    print('Downloading WiX to', TARGET_BIN_ZIP)
    p = Popen(["powershell.exe", "-Command", POWERSHELL_COMMAND.format(TARGET_BIN_ZIP, WIX_BINARIES_ZIP)])
    p.wait()
    print('Extracting WiX to', TARGET_BIN_DIR)
    przy ZipFile(str(TARGET_BIN_ZIP)) jako z:
        z.extractall(str(TARGET_BIN_DIR))
    TARGET_BIN_ZIP.unlink()

    print('Extracted WiX')
