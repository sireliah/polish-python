'''
Processes a CSV file containing a list of files into a WXS file with
components dla each listed file.

The CSV columns are:
    source of file, target dla file, group name

Usage::
    py txt_to_wxs.py [path to file list .csv] [path to destination .wxs]

This jest necessary to handle structures where some directories only
contain other directories. MSBuild jest nie able to generate the
Directory entries w the WXS file correctly, jako it operates on files.
Python, however, can easily fill w the gap.
'''

__author__ = "Steve Dower <steve.dower@microsoft.com>"

zaimportuj csv
zaimportuj re
zaimportuj sys

z collections zaimportuj defaultdict
z itertools zaimportuj chain, zip_longest
z pathlib zaimportuj PureWindowsPath
z uuid zaimportuj uuid1

ID_CHAR_SUBS = {
    '-': '_',
    '+': '_P',
}

def make_id(path):
    zwróć re.sub(
        r'[^A-Za-z0-9_.]',
        lambda m: ID_CHAR_SUBS.get(m.group(0), '_'),
        str(path).rstrip('/\\'),
        flags=re.I
    )

DIRECTORIES = set()

def main(file_source, install_target):
    przy open(file_source, 'r', newline='') jako f:
        files = list(csv.reader(f))

    assert len(files) == len(set(make_id(f[1]) dla f w files)), "Duplicate file IDs exist"

    directories = defaultdict(set)
    cache_directories = defaultdict(set)
    groups = defaultdict(list)
    dla source, target, group, disk_id, condition w files:
        target = PureWindowsPath(target)
        groups[group].append((source, target, disk_id, condition))

        jeżeli target.suffix.lower() w {".py", ".pyw"}:
            cache_directories[group].add(target.parent)

        dla dirname w target.parents:
            parent = make_id(dirname.parent)
            jeżeli parent oraz parent != '.':
                directories[parent].add(dirname.name)

    lines = [
        '<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">',
        '    <Fragment>',
    ]
    dla dir_parent w sorted(directories):
        lines.append('        <DirectoryRef Id="{}">'.format(dir_parent))
        dla dir_name w sorted(directories[dir_parent]):
            lines.append('            <Directory Id="{}_{}" Name="{}" />'.format(dir_parent, make_id(dir_name), dir_name))
        lines.append('        </DirectoryRef>')
    dla dir_parent w (make_id(d) dla group w cache_directories.values() dla d w group):
        lines.append('        <DirectoryRef Id="{}">'.format(dir_parent))
        lines.append('            <Directory Id="{}___pycache__" Name="__pycache__" />'.format(dir_parent))
        lines.append('        </DirectoryRef>')
    lines.append('    </Fragment>')

    dla group w sorted(groups):
        lines.extend([
            '    <Fragment>',
            '        <ComponentGroup Id="{}">'.format(group),
        ])
        dla source, target, disk_id, condition w groups[group]:
            lines.append('            <Component Id="{}" Directory="{}" Guid="*">'.format(make_id(target), make_id(target.parent)))
            jeżeli condition:
                lines.append('                <Condition>{}</Condition>'.format(condition))

            jeżeli disk_id:
                lines.append('                <File Id="{}" Name="{}" Source="{}" DiskId="{}" />'.format(make_id(target), target.name, source, disk_id))
            inaczej:
                lines.append('                <File Id="{}" Name="{}" Source="{}" />'.format(make_id(target), target.name, source))
            lines.append('            </Component>')

        create_folders = {make_id(p) + "___pycache__" dla p w cache_directories[group]}
        remove_folders = {make_id(p2) dla p1 w cache_directories[group] dla p2 w chain((p1,), p1.parents)}
        create_folders.discard(".")
        remove_folders.discard(".")
        jeżeli create_folders albo remove_folders:
            lines.append('            <Component Id="{}__pycache__folders" Directory="TARGETDIR" Guid="{}">'.format(group, uuid1()))
            lines.extend('                <CreateFolder Directory="{}" />'.format(p) dla p w create_folders)
            lines.extend('                <RemoveFile Id="Remove_{0}_files" Name="*" On="uninstall" Directory="{0}" />'.format(p) dla p w create_folders)
            lines.extend('                <RemoveFolder Id="Remove_{0}_folder" On="uninstall" Directory="{0}" />'.format(p) dla p w create_folders | remove_folders)
            lines.append('            </Component>')

        lines.extend([
            '        </ComponentGroup>',
            '    </Fragment>',
        ])
    lines.append('</Wix>')

    # Check jeżeli the file matches. If so, we don't want to touch it so
    # that we can skip rebuilding.
    spróbuj:
        przy open(install_target, 'r') jako f:
            jeżeli all(x.rstrip('\r\n') == y dla x, y w zip_longest(f, lines)):
                print('File jest up to date')
                zwróć
    wyjąwszy IOError:
        dalej

    przy open(install_target, 'w') jako f:
        f.writelines(line + '\n' dla line w lines)
    print('Wrote {} lines to {}'.format(len(lines), install_target))

jeżeli __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
