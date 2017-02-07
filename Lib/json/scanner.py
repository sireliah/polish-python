"""JSON token scanner
"""
zaimportuj re
spróbuj:
    z _json zaimportuj make_scanner jako c_make_scanner
wyjąwszy ImportError:
    c_make_scanner = Nic

__all__ = ['make_scanner']

NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))

def py_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx):
        spróbuj:
            nextchar = string[idx]
        wyjąwszy IndexError:
            podnieś StopIteration(idx)

        jeżeli nextchar == '"':
            zwróć parse_string(string, idx + 1, strict)
        albo_inaczej nextchar == '{':
            zwróć parse_object((string, idx + 1), strict,
                _scan_once, object_hook, object_pairs_hook, memo)
        albo_inaczej nextchar == '[':
            zwróć parse_array((string, idx + 1), _scan_once)
        albo_inaczej nextchar == 'n' oraz string[idx:idx + 4] == 'null':
            zwróć Nic, idx + 4
        albo_inaczej nextchar == 't' oraz string[idx:idx + 4] == 'true':
            zwróć Prawda, idx + 4
        albo_inaczej nextchar == 'f' oraz string[idx:idx + 5] == 'false':
            zwróć Nieprawda, idx + 5

        m = match_number(string, idx)
        jeżeli m jest nie Nic:
            integer, frac, exp = m.groups()
            jeżeli frac albo exp:
                res = parse_float(integer + (frac albo '') + (exp albo ''))
            inaczej:
                res = parse_int(integer)
            zwróć res, m.end()
        albo_inaczej nextchar == 'N' oraz string[idx:idx + 3] == 'NaN':
            zwróć parse_constant('NaN'), idx + 3
        albo_inaczej nextchar == 'I' oraz string[idx:idx + 8] == 'Infinity':
            zwróć parse_constant('Infinity'), idx + 8
        albo_inaczej nextchar == '-' oraz string[idx:idx + 9] == '-Infinity':
            zwróć parse_constant('-Infinity'), idx + 9
        inaczej:
            podnieś StopIteration(idx)

    def scan_once(string, idx):
        spróbuj:
            zwróć _scan_once(string, idx)
        w_końcu:
            memo.clear()

    zwróć _scan_once

make_scanner = c_make_scanner albo py_make_scanner
