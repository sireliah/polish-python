zaimportuj argparse
zaimportuj py_compile
zaimportuj re
zaimportuj sys
zaimportuj shutil
zaimportuj os
zaimportuj tempfile

z pathlib zaimportuj Path
z zipfile zaimportuj ZipFile, ZIP_DEFLATED
zaimportuj subprocess

TKTCL_RE = re.compile(r'^(_?tk|tcl).+\.(pyd|dll)', re.IGNORECASE)
DEBUG_RE = re.compile(r'_d\.(pyd|dll|exe)$', re.IGNORECASE)
PYTHON_DLL_RE = re.compile(r'python\d\d?\.dll$', re.IGNORECASE)

def is_not_debug(p):
    jeżeli DEBUG_RE.search(p.name):
        zwróć Nieprawda

    jeżeli TKTCL_RE.search(p.name):
        zwróć Nieprawda

    zwróć p.name.lower() nie w {
        '_ctypes_test.pyd',
        '_testbuffer.pyd',
        '_testcapi.pyd',
        '_testimportmultiple.pyd',
        '_testmultiphase.pyd',
        'xxlimited.pyd',
    }

def is_not_debug_or_python(p):
    zwróć is_not_debug(p) oraz nie PYTHON_DLL_RE.search(p.name)

def include_in_lib(p):
    name = p.name.lower()
    jeżeli p.is_dir():
        jeżeli name w {'__pycache__', 'ensurepip', 'idlelib', 'pydoc_data', 'tkinter', 'turtledemo'}:
            zwróć Nieprawda
        jeżeli name.startswith('plat-'):
            zwróć Nieprawda
        jeżeli name == 'test' oraz p.parts[-2].lower() == 'lib':
            zwróć Nieprawda
        zwróć Prawda

    suffix = p.suffix.lower()
    zwróć suffix nie w {'.pyc', '.pyo'}

def include_in_tools(p):
    jeżeli p.is_dir() oraz p.name.lower() w {'scripts', 'i18n', 'pynche', 'demo', 'parser'}:
        zwróć Prawda

    zwróć p.suffix.lower() w {'.py', '.pyw', '.txt'}

FULL_LAYOUT = [
    ('/', 'PCBuild/$arch', 'python*.exe', is_not_debug),
    ('/', 'PCBuild/$arch', 'python*.dll', is_not_debug),
    ('DLLs/', 'PCBuild/$arch', '*.pyd', is_not_debug),
    ('DLLs/', 'PCBuild/$arch', '*.dll', is_not_debug),
    ('include/', 'include', '*.h', Nic),
    ('include/', 'PC', 'pyconfig.h', Nic),
    ('Lib/', 'Lib', '**/*', include_in_lib),
    ('Tools/', 'Tools', '**/*', include_in_tools),
]

EMBED_LAYOUT = [
    ('/', 'PCBuild/$arch', 'python*.exe', is_not_debug),
    ('/', 'PCBuild/$arch', '*.pyd', is_not_debug),
    ('/', 'PCBuild/$arch', '*.dll', is_not_debug),
    ('python35.zip', 'Lib', '**/*', include_in_lib),
]

jeżeli os.getenv('DOC_FILENAME'):
    FULL_LAYOUT.append(('Doc/', 'Doc/build/htmlhelp', os.getenv('DOC_FILENAME'), Nic))
jeżeli os.getenv('VCREDIST_PATH'):
    FULL_LAYOUT.append(('/', os.getenv('VCREDIST_PATH'), 'vcruntime*.dll', Nic))
    EMBED_LAYOUT.append(('/', os.getenv('VCREDIST_PATH'), 'vcruntime*.dll', Nic))

def copy_to_layout(target, rel_sources):
    count = 0

    jeżeli target.suffix.lower() == '.zip':
        jeżeli target.exists():
            target.unlink()

        przy ZipFile(str(target), 'w', ZIP_DEFLATED) jako f:
            przy tempfile.TemporaryDirectory() jako tmpdir:
                dla s, rel w rel_sources:
                    jeżeli rel.suffix.lower() == '.py':
                        pyc = Path(tmpdir) / rel.with_suffix('.pyc').name
                        spróbuj:
                            py_compile.compile(str(s), str(pyc), str(rel), doraise=Prawda, optimize=2)
                        wyjąwszy py_compile.PyCompileError:
                            f.write(str(s), str(rel))
                        inaczej:
                            f.write(str(pyc), str(rel.with_suffix('.pyc')))
                    inaczej:
                        f.write(str(s), str(rel))
                    count += 1

    inaczej:
        dla s, rel w rel_sources:
            spróbuj:
                (target / rel).parent.mkdir(parents=Prawda)
            wyjąwszy FileExistsError:
                dalej
            shutil.copy(str(s), str(target / rel))
            count += 1

    zwróć count

def rglob(root, pattern, condition):
    dirs = [root]
    recurse = pattern[:3] w {'**/', '**\\'}
    dopóki dirs:
        d = dirs.pop(0)
        dla f w d.glob(pattern[3:] jeżeli recurse inaczej pattern):
            jeżeli recurse oraz f.is_dir() oraz (nie condition albo condition(f)):
                dirs.append(f)
            albo_inaczej f.is_file() oraz (nie condition albo condition(f)):
                uzyskaj f, f.relative_to(root)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', metavar='dir', help='The directory containing the repository root', type=Path)
    parser.add_argument('-o', '--out', metavar='file', help='The name of the output self-extracting archive', type=Path, required=Prawda)
    parser.add_argument('-t', '--temp', metavar='dir', help='A directory to temporarily extract files into', type=Path, default=Nic)
    parser.add_argument('-e', '--embed', help='Create an embedding layout', action='store_true', default=Nieprawda)
    parser.add_argument('-a', '--arch', help='Specify the architecture to use (win32/amd64)', type=str, default="win32")
    ns = parser.parse_args()

    source = ns.source albo (Path(__file__).parent.parent.parent)
    out = ns.out
    arch = ns.arch
    assert isinstance(source, Path)
    assert isinstance(out, Path)
    assert isinstance(arch, str)

    jeżeli ns.temp:
        temp = ns.temp
        delete_temp = Nieprawda
    inaczej:
        temp = Path(tempfile.mkdtemp())
        delete_temp = Prawda

    spróbuj:
        out.parent.mkdir(parents=Prawda)
    wyjąwszy FileExistsError:
        dalej
    spróbuj:
        temp.mkdir(parents=Prawda)
    wyjąwszy FileExistsError:
        dalej

    layout = EMBED_LAYOUT jeżeli ns.embed inaczej FULL_LAYOUT

    spróbuj:
        dla t, s, p, c w layout:
            s = source / s.replace("$arch", arch)
            copied = copy_to_layout(temp / t.rstrip('/'), rglob(s, p, c))
            print('Copied {} files'.format(copied))

        przy open(str(temp / 'pyvenv.cfg'), 'w') jako f:
            print('applocal = true', file=f)

        total = copy_to_layout(out, rglob(temp, '*', Nic))
        print('Wrote {} files to {}'.format(total, out))
    w_końcu:
        jeżeli delete_temp:
            shutil.rmtree(temp, Prawda)


jeżeli __name__ == "__main__":
    sys.exit(int(main() albo 0))
