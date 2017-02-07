#!/usr/bin/env python3
# This script converts a C file to use the PEP 384 type definition API
# Usage: abitype.py < old_code > new_code
zaimportuj re, sys

###### Replacement of PyTypeObject static instances ##############

# classify each token, giving it a one-letter code:
# S: static
# T: PyTypeObject
# I: ident
# W: whitespace
# =, {, }, ; : themselves
def classify():
    res = []
    dla t,v w tokens:
        jeżeli t == 'other' oraz v w "={};":
            res.append(v)
        albo_inaczej t == 'ident':
            jeżeli v == 'PyTypeObject':
                res.append('T')
            albo_inaczej v == 'static':
                res.append('S')
            inaczej:
                res.append('I')
        albo_inaczej t == 'ws':
            res.append('W')
        inaczej:
            res.append('.')
    zwróć ''.join(res)

# Obtain a list of fields of a PyTypeObject, w declaration order,
# skipping ob_base
# All comments are dropped z the variable (which are typically
# just the slot names, anyway), oraz information jest discarded whether
# the original type was static.
def get_fields(start, real_end):
    pos = start
    # static?
    jeżeli tokens[pos][1] == 'static':
        pos += 2
    # PyTypeObject
    pos += 2
    # name
    name = tokens[pos][1]
    pos += 1
    dopóki tokens[pos][1] != '{':
        pos += 1
    pos += 1
    # PyVarObject_HEAD_INIT
    dopóki tokens[pos][0] w ('ws', 'comment'):
        pos += 1
    jeżeli tokens[pos][1] != 'PyVarObject_HEAD_INIT':
        podnieś Exception('%s has no PyVarObject_HEAD_INIT' % name)
    dopóki tokens[pos][1] != ')':
        pos += 1
    pos += 1
    # field definitions: various tokens, comma-separated
    fields = []
    dopóki Prawda:
        dopóki tokens[pos][0] w ('ws', 'comment'):
            pos += 1
        end = pos
        dopóki tokens[end][1] nie w ',}':
            jeżeli tokens[end][1] == '(':
                nesting = 1
                dopóki nesting:
                    end += 1
                    jeżeli tokens[end][1] == '(': nesting+=1
                    jeżeli tokens[end][1] == ')': nesting-=1
            end += 1
        assert end < real_end
        # join field, excluding separator oraz trailing ws
        end1 = end-1
        dopóki tokens[end1][0] w ('ws', 'comment'):
            end1 -= 1
        fields.append(''.join(t[1] dla t w tokens[pos:end1+1]))
        jeżeli tokens[end][1] == '}':
            przerwij
        pos = end+1
    zwróć name, fields

# List of type slots jako of Python 3.2, omitting ob_base
typeslots = [
    'tp_name',
    'tp_basicsize',
    'tp_itemsize',
    'tp_dealloc',
    'tp_print',
    'tp_getattr',
    'tp_setattr',
    'tp_reserved',
    'tp_repr',
    'tp_as_number',
    'tp_as_sequence',
    'tp_as_mapping',
    'tp_hash',
    'tp_call',
    'tp_str',
    'tp_getattro',
    'tp_setattro',
    'tp_as_buffer',
    'tp_flags',
    'tp_doc',
    'tp_traverse',
    'tp_clear',
    'tp_richcompare',
    'tp_weaklistoffset',
    'tp_iter',
    'iternextfunc',
    'tp_methods',
    'tp_members',
    'tp_getset',
    'tp_base',
    'tp_dict',
    'tp_descr_get',
    'tp_descr_set',
    'tp_dictoffset',
    'tp_init',
    'tp_alloc',
    'tp_new',
    'tp_free',
    'tp_is_gc',
    'tp_bases',
    'tp_mro',
    'tp_cache',
    'tp_subclasses',
    'tp_weaklist',
    'tp_del',
    'tp_version_tag',
]

# Generate a PyType_Spec definition
def make_slots(name, fields):
    res = []
    res.append('static PyType_Slot %s_slots[] = {' % name)
    # defaults dla spec
    spec = { 'tp_itemsize':'0' }
    dla i, val w enumerate(fields):
        jeżeli val.endswith('0'):
            kontynuuj
        jeżeli typeslots[i] w ('tp_name', 'tp_doc', 'tp_basicsize',
                         'tp_itemsize', 'tp_flags'):
            spec[typeslots[i]] = val
            kontynuuj
        res.append('    {Py_%s, %s},' % (typeslots[i], val))
    res.append('};')
    res.append('static PyType_Spec %s_spec = {' % name)
    res.append('    %s,' % spec['tp_name'])
    res.append('    %s,' % spec['tp_basicsize'])
    res.append('    %s,' % spec['tp_itemsize'])
    res.append('    %s,' % spec['tp_flags'])
    res.append('    %s_slots,' % name)
    res.append('};\n')
    zwróć '\n'.join(res)


jeżeli __name__ == '__main__':

    ############ Simplistic C scanner ##################################
    tokenizer = re.compile(
        r"(?P<preproc>#.*\n)"
        r"|(?P<comment>/\*.*?\*/)"
        r"|(?P<ident>[a-zA-Z_][a-zA-Z0-9_]*)"
        r"|(?P<ws>[ \t\n]+)"
        r"|(?P<other>.)",
        re.MULTILINE)

    tokens = []
    source = sys.stdin.read()
    pos = 0
    dopóki pos != len(source):
        m = tokenizer.match(source, pos)
        tokens.append([m.lastgroup, m.group()])
        pos += len(tokens[-1][1])
        jeżeli tokens[-1][0] == 'preproc':
            # continuation lines are considered
            # only w preprocess statements
            dopóki tokens[-1][1].endswith('\\\n'):
                nl = source.find('\n', pos)
                jeżeli nl == -1:
                    line = source[pos:]
                inaczej:
                    line = source[pos:nl+1]
                tokens[-1][1] += line
                pos += len(line)

    # Main loop: replace all static PyTypeObjects until
    # there are none left.
    dopóki 1:
        c = classify()
        m = re.search('(SW)?TWIW?=W?{.*?};', c)
        jeżeli nie m:
            przerwij
        start = m.start()
        end = m.end()
        name, fields = get_fields(start, end)
        tokens[start:end] = [('',make_slots(name, fields))]

    # Output result to stdout
    dla t, v w tokens:
        sys.stdout.write(v)
