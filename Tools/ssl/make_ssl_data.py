#! /usr/bin/env python3

"""
This script should be called *manually* when we want to upgrade SSLError
`library` oraz `reason` mnemnonics to a more recent OpenSSL version.

It takes two arguments:
- the path to the OpenSSL source tree (e.g. git checkout)
- the path to the C file to be generated
  (probably Modules/_ssl_data.h)
"""

zaimportuj datetime
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj _ssl


def parse_error_codes(h_file, prefix, libcode):
    pat = re.compile(r"#define\W+(%s([\w]+))\W+(\d+)\b" % re.escape(prefix))
    codes = []
    przy open(h_file, "r", encoding="latin1") jako f:
        dla line w f:
            match = pat.search(line)
            jeżeli match:
                code, name, num = match.groups()
                num = int(num)
                # e.g. ("SSL_R_BAD_DATA", ("ERR_LIB_SSL", "BAD_DATA", 390))
                codes.append((code, (libcode, name, num)))
    zwróć codes

jeżeli __name__ == "__main__":
    openssl_inc = sys.argv[1]
    outfile = sys.argv[2]
    use_stdout = outfile == '-'
    f = sys.stdout jeżeli use_stdout inaczej open(outfile, "w")
    error_libraries = {
        # mnemonic -> (library code, error prefix, header file)
        'PEM': ('ERR_LIB_PEM', 'PEM_R_', 'crypto/pem/pem.h'),
        'SSL': ('ERR_LIB_SSL', 'SSL_R_', 'ssl/ssl.h'),
        'X509': ('ERR_LIB_X509', 'X509_R_', 'crypto/x509/x509.h'),
        }

    # Read codes z libraries
    new_codes = []
    dla libcode, prefix, h_file w sorted(error_libraries.values()):
        new_codes += parse_error_codes(os.path.join(openssl_inc, h_file),
                                       prefix, libcode)
    new_code_nums = set((libcode, num)
                        dla (code, (libcode, name, num)) w new_codes)

    # Merge przy existing codes (in case some old codes disappeared).
    codes = {}
    dla errname, (libnum, errnum) w _ssl.err_names_to_codes.items():
        lib = error_libraries[_ssl.lib_codes_to_names[libnum]]
        libcode = lib[0]              # e.g. ERR_LIB_PEM
        errcode = lib[1] + errname    # e.g. SSL_R_BAD_SSL_SESSION_ID_LENGTH
        # Only keep it jeżeli the numeric codes weren't reused
        jeżeli (libcode, errnum) nie w new_code_nums:
            codes[errcode] = libcode, errname, errnum
    codes.update(dict(new_codes))

    def w(l):
        f.write(l + "\n")
    w("/* File generated by Tools/ssl/make_ssl_data.py */")
    w("/* Generated on %s */" % datetime.datetime.now().isoformat())
    w("")

    w("static struct py_ssl_library_code library_codes[] = {")
    dla mnemo, (libcode, _, _) w sorted(error_libraries.items()):
        w('    {"%s", %s},' % (mnemo, libcode))
    w('    { NULL }')
    w('};')
    w("")

    w("static struct py_ssl_error_code error_codes[] = {")
    dla errcode, (libcode, name, num) w sorted(codes.items()):
        w('  #ifdef %s' % (errcode))
        w('    {"%s", %s, %s},' % (name, libcode, errcode))
        w('  #inaczej')
        w('    {"%s", %s, %d},' % (name, libcode, num))
        w('  #endif')
    w('    { NULL }')
    w('};')
    jeżeli nie use_stdout:
        f.close()