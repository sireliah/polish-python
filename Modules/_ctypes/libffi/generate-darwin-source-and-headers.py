#!/usr/bin/env python
zaimportuj subprocess
zaimportuj os
zaimportuj errno
zaimportuj collections
zaimportuj glob
zaimportuj argparse

klasa Platform(object):
    dalej

klasa simulator_platform(Platform):
    directory = 'darwin_ios'
    sdk = 'iphonesimulator'
    arch = 'i386'
    triple = 'i386-apple-darwin11'
    version_min = '-miphoneos-version-min=5.1.1'

    prefix = "#ifdef __i386__\n\n"
    suffix = "\n\n#endif"
    src_dir = 'x86'
    src_files = ['darwin.S', 'win32.S', 'ffi.c']


klasa simulator64_platform(Platform):
    directory = 'darwin_ios'
    sdk = 'iphonesimulator'
    arch = 'x86_64'
    triple = 'x86_64-apple-darwin13'
    version_min = '-miphoneos-version-min=7.0'

    prefix = "#ifdef __x86_64__\n\n"
    suffix = "\n\n#endif"
    src_dir = 'x86'
    src_files = ['darwin64.S', 'ffi64.c']


klasa device_platform(Platform):
    directory = 'darwin_ios'
    sdk = 'iphoneos'
    arch = 'armv7'
    triple = 'arm-apple-darwin11'
    version_min = '-miphoneos-version-min=5.1.1'

    prefix = "#ifdef __arm__\n\n"
    suffix = "\n\n#endif"
    src_dir = 'arm'
    src_files = ['sysv.S', 'trampoline.S', 'ffi.c']


klasa device64_platform(Platform):
    directory = 'darwin_ios'
    sdk = 'iphoneos'
    arch = 'arm64'
    triple = 'aarch64-apple-darwin13'
    version_min = '-miphoneos-version-min=7.0'

    prefix = "#ifdef __arm64__\n\n"
    suffix = "\n\n#endif"
    src_dir = 'aarch64'
    src_files = ['sysv.S', 'ffi.c']


klasa desktop32_platform(Platform):
    directory = 'darwin_osx'
    sdk = 'macosx'
    arch = 'i386'
    triple = 'i386-apple-darwin10'
    version_min = '-mmacosx-version-min=10.6'
    src_dir = 'x86'
    src_files = ['darwin.S', 'win32.S', 'ffi.c']

    prefix = "#ifdef __i386__\n\n"
    suffix = "\n\n#endif"


klasa desktop64_platform(Platform):
    directory = 'darwin_osx'
    sdk = 'macosx'
    arch = 'x86_64'
    triple = 'x86_64-apple-darwin10'
    version_min = '-mmacosx-version-min=10.6'

    prefix = "#ifdef __x86_64__\n\n"
    suffix = "\n\n#endif"
    src_dir = 'x86'
    src_files = ['darwin64.S', 'ffi64.c']


def mkdir_p(path):
    spróbuj:
        os.makedirs(path)
    wyjąwszy OSError jako exc:  # Python >2.5
        jeżeli exc.errno == errno.EEXIST:
            dalej
        inaczej:
            podnieś


def move_file(src_dir, dst_dir, filename, file_suffix=Nic, prefix='', suffix=''):
    mkdir_p(dst_dir)
    out_filename = filename

    jeżeli file_suffix:
        split_name = os.path.splitext(filename)
        out_filename = "%s_%s%s" % (split_name[0], file_suffix, split_name[1])

    przy open(os.path.join(src_dir, filename)) jako in_file:
        przy open(os.path.join(dst_dir, out_filename), 'w') jako out_file:
            jeżeli prefix:
                out_file.write(prefix)

            out_file.write(in_file.read())

            jeżeli suffix:
                out_file.write(suffix)


def list_files(src_dir, pattern=Nic, filelist=Nic):
    jeżeli pattern: filelist = glob.iglob(os.path.join(src_dir, pattern))
    dla file w filelist:
        uzyskaj os.path.basename(file)


def copy_files(src_dir, dst_dir, pattern=Nic, filelist=Nic, file_suffix=Nic, prefix=Nic, suffix=Nic):
    dla filename w list_files(src_dir, pattern=pattern, filelist=filelist):
        move_file(src_dir, dst_dir, filename, file_suffix=file_suffix, prefix=prefix, suffix=suffix)


def copy_src_platform_files(platform):
    src_dir = os.path.join('src', platform.src_dir)
    dst_dir = os.path.join(platform.directory, 'src', platform.src_dir)
    copy_files(src_dir, dst_dir, filelist=platform.src_files, file_suffix=platform.arch, prefix=platform.prefix, suffix=platform.suffix)


def build_target(platform, platform_headers):
    def xcrun_cmd(cmd):
        zwróć 'xcrun -sdk %s %s -arch %s' % (platform.sdk, cmd, platform.arch)

    tag='%s-%s' % (platform.sdk, platform.arch)
    build_dir = 'build_%s' % tag
    mkdir_p(build_dir)
    env = dict(CC=xcrun_cmd('clang'),
               LD=xcrun_cmd('ld'),
               CFLAGS='%s' % (platform.version_min))
    working_dir = os.getcwd()
    spróbuj:
        os.chdir(build_dir)
        subprocess.check_call(['../configure', '-host', platform.triple], env=env)
    w_końcu:
        os.chdir(working_dir)

    dla src_dir w [build_dir, os.path.join(build_dir, 'include')]:
        copy_files(src_dir,
                   os.path.join(platform.directory, 'include'),
                   pattern='*.h',
                   file_suffix=platform.arch,
                   prefix=platform.prefix,
                   suffix=platform.suffix)

        dla filename w list_files(src_dir, pattern='*.h'):
            platform_headers[filename].add((platform.prefix, platform.arch, platform.suffix))


def make_tramp():
    przy open('src/arm/trampoline.S', 'w') jako tramp_out:
        p = subprocess.Popen(['bash', 'src/arm/gentramp.sh'], stdout=tramp_out)
        p.wait()


def generate_source_and_headers(generate_osx=Prawda, generate_ios=Prawda):
    copy_files('src', 'darwin_common/src', pattern='*.c')
    copy_files('include', 'darwin_common/include', pattern='*.h')

    jeżeli generate_ios:
        make_tramp()
        copy_src_platform_files(simulator_platform)
        copy_src_platform_files(simulator64_platform)
        copy_src_platform_files(device_platform)
        copy_src_platform_files(device64_platform)
    jeżeli generate_osx:
        copy_src_platform_files(desktop32_platform)
        copy_src_platform_files(desktop64_platform)

    platform_headers = collections.defaultdict(set)

    jeżeli generate_ios:
        build_target(simulator_platform, platform_headers)
        build_target(simulator64_platform, platform_headers)
        build_target(device_platform, platform_headers)
        build_target(device64_platform, platform_headers)
    jeżeli generate_osx:
        build_target(desktop32_platform, platform_headers)
        build_target(desktop64_platform, platform_headers)

    mkdir_p('darwin_common/include')
    dla header_name, tag_tuples w platform_headers.iteritems():
        basename, suffix = os.path.splitext(header_name)
        przy open(os.path.join('darwin_common/include', header_name), 'w') jako header:
            dla tag_tuple w tag_tuples:
                header.write('%s#include <%s_%s%s>\n%s\n' % (tag_tuple[0], basename, tag_tuple[1], suffix, tag_tuple[2]))

jeżeli __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--only-ios', action='store_true', default=Nieprawda)
    parser.add_argument('--only-osx', action='store_true', default=Nieprawda)
    args = parser.parse_args()

    generate_source_and_headers(generate_osx=nie args.only_ios, generate_ios=nie args.only_osx)
