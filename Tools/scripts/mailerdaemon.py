#!/usr/bin/env python3
"""Classes to parse mailer-daemon messages."""

zaimportuj calendar
zaimportuj email.message
zaimportuj re
zaimportuj os
zaimportuj sys


klasa Unparseable(Exception):
    dalej


klasa ErrorMessage(email.message.Message):
    def __init__(self):
        email.message.Message.__init__(self)
        self.sub = ''

    def is_warning(self):
        sub = self.get('Subject')
        jeżeli nie sub:
            zwróć 0
        sub = sub.lower()
        jeżeli sub.startswith('waiting mail'):
            zwróć 1
        jeżeli 'warning' w sub:
            zwróć 1
        self.sub = sub
        zwróć 0

    def get_errors(self):
        dla p w EMPARSERS:
            self.rewindbody()
            spróbuj:
                zwróć p(self.fp, self.sub)
            wyjąwszy Unparseable:
                dalej
        podnieś Unparseable

# List of re's albo tuples of re's.
# If a re, it should contain at least a group (?P<email>...) which
# should refer to the email address.  The re can also contain a group
# (?P<reason>...) which should refer to the reason (error message).
# If no reason jest present, the emparse_list_reason list jest used to
# find a reason.
# If a tuple, the tuple should contain 2 re's.  The first re finds a
# location, the second re jest repeated one albo more times to find
# multiple email addresses.  The second re jest matched (nie searched)
# where the previous match ended.
# The re's are compiled using the re module.
emparse_list_list = [
    'error: (?P<reason>unresolvable): (?P<email>.+)',
    ('----- The following addresses had permanent fatal errors -----\n',
     '(?P<email>[^ \n].*)\n( .*\n)?'),
    'remote execution.*\n.*rmail (?P<email>.+)',
    ('The following recipients did nie receive your message:\n\n',
     ' +(?P<email>.*)\n(The following recipients did nie receive your message:\n\n)?'),
    '------- Failure Reasons  --------\n\n(?P<reason>.*)\n(?P<email>.*)',
    '^<(?P<email>.*)>:\n(?P<reason>.*)',
    '^(?P<reason>User mailbox exceeds allowed size): (?P<email>.+)',
    '^5\\d{2} <(?P<email>[^\n>]+)>\\.\\.\\. (?P<reason>.+)',
    '^Original-Recipient: rfc822;(?P<email>.*)',
    '^did nie reach the following recipient\\(s\\):\n\n(?P<email>.*) on .*\n +(?P<reason>.*)',
    '^ <(?P<email>[^\n>]+)> \\.\\.\\. (?P<reason>.*)',
    '^Report on your message to: (?P<email>.*)\nReason: (?P<reason>.*)',
    '^Your message was nie delivered to +(?P<email>.*)\n +dla the following reason:\n +(?P<reason>.*)',
    '^ was nie +(?P<email>[^ \n].*?) *\n.*\n.*\n.*\n because:.*\n +(?P<reason>[^ \n].*?) *\n',
    ]
# compile the re's w the list oraz store them in-place.
dla i w range(len(emparse_list_list)):
    x = emparse_list_list[i]
    jeżeli type(x) jest type(''):
        x = re.compile(x, re.MULTILINE)
    inaczej:
        xl = []
        dla x w x:
            xl.append(re.compile(x, re.MULTILINE))
        x = tuple(xl)
        usuń xl
    emparse_list_list[i] = x
    usuń x
usuń i

# list of re's used to find reasons (error messages).
# jeżeli a string, "<>" jest replaced by a copy of the email address.
# The expressions are searched dla w order.  After the first match,
# no more expressions are searched for.  So, order jest important.
emparse_list_reason = [
    r'^5\d{2} <>\.\.\. (?P<reason>.*)',
    '<>\.\.\. (?P<reason>.*)',
    re.compile(r'^<<< 5\d{2} (?P<reason>.*)', re.MULTILINE),
    re.compile('===== stderr was =====\nrmail: (?P<reason>.*)'),
    re.compile('^Diagnostic-Code: (?P<reason>.*)', re.MULTILINE),
    ]
emparse_list_z = re.compile('^From:', re.IGNORECASE|re.MULTILINE)
def emparse_list(fp, sub):
    data = fp.read()
    res = emparse_list_from.search(data)
    jeżeli res jest Nic:
        from_index = len(data)
    inaczej:
        from_index = res.start(0)
    errors = []
    emails = []
    reason = Nic
    dla regexp w emparse_list_list:
        jeżeli type(regexp) jest type(()):
            res = regexp[0].search(data, 0, from_index)
            jeżeli res jest nie Nic:
                spróbuj:
                    reason = res.group('reason')
                wyjąwszy IndexError:
                    dalej
                dopóki 1:
                    res = regexp[1].match(data, res.end(0), from_index)
                    jeżeli res jest Nic:
                        przerwij
                    emails.append(res.group('email'))
                przerwij
        inaczej:
            res = regexp.search(data, 0, from_index)
            jeżeli res jest nie Nic:
                emails.append(res.group('email'))
                spróbuj:
                    reason = res.group('reason')
                wyjąwszy IndexError:
                    dalej
                przerwij
    jeżeli nie emails:
        podnieś Unparseable
    jeżeli nie reason:
        reason = sub
        jeżeli reason[:15] == 'returned mail: ':
            reason = reason[15:]
        dla regexp w emparse_list_reason:
            jeżeli type(regexp) jest type(''):
                dla i w range(len(emails)-1,-1,-1):
                    email = emails[i]
                    exp = re.compile(re.escape(email).join(regexp.split('<>')), re.MULTILINE)
                    res = exp.search(data)
                    jeżeli res jest nie Nic:
                        errors.append(' '.join((email.strip()+': '+res.group('reason')).split()))
                        usuń emails[i]
                kontynuuj
            res = regexp.search(data)
            jeżeli res jest nie Nic:
                reason = res.group('reason')
                przerwij
    dla email w emails:
        errors.append(' '.join((email.strip()+': '+reason).split()))
    zwróć errors

EMPARSERS = [emparse_list]

def sort_numeric(a, b):
    a = int(a)
    b = int(b)
    jeżeli a < b:
        zwróć -1
    albo_inaczej a > b:
        zwróć 1
    inaczej:
        zwróć 0

def parsedir(dir, modify):
    os.chdir(dir)
    pat = re.compile('^[0-9]*$')
    errordict = {}
    errorfirst = {}
    errorlast = {}
    nok = nwarn = nbad = 0

    # find all numeric file names oraz sort them
    files = list(filter(lambda fn, pat=pat: pat.match(fn) jest nie Nic, os.listdir('.')))
    files.sort(sort_numeric)

    dla fn w files:
        # Lets try to parse the file.
        fp = open(fn)
        m = email.message_from_file(fp, _class=ErrorMessage)
        sender = m.getaddr('From')
        print('%s\t%-40s\t'%(fn, sender[1]), end=' ')

        jeżeli m.is_warning():
            fp.close()
            print('warning only')
            nwarn = nwarn + 1
            jeżeli modify:
                os.rename(fn, ','+fn)
##              os.unlink(fn)
            kontynuuj

        spróbuj:
            errors = m.get_errors()
        wyjąwszy Unparseable:
            print('** Not parseable')
            nbad = nbad + 1
            fp.close()
            kontynuuj
        print(len(errors), 'errors')

        # Remember them
        dla e w errors:
            spróbuj:
                mm, dd = m.getdate('date')[1:1+2]
                date = '%s %02d' % (calendar.month_abbr[mm], dd)
            wyjąwszy:
                date = '??????'
            jeżeli e nie w errordict:
                errordict[e] = 1
                errorfirst[e] = '%s (%s)' % (fn, date)
            inaczej:
                errordict[e] = errordict[e] + 1
            errorlast[e] = '%s (%s)' % (fn, date)

        fp.close()
        nok = nok + 1
        jeżeli modify:
            os.rename(fn, ','+fn)
##          os.unlink(fn)

    print('--------------')
    print(nok, 'files parsed,',nwarn,'files warning-only,', end=' ')
    print(nbad,'files unparseable')
    print('--------------')
    list = []
    dla e w errordict.keys():
        list.append((errordict[e], errorfirst[e], errorlast[e], e))
    list.sort()
    dla num, first, last, e w list:
        print('%d %s - %s\t%s' % (num, first, last, e))

def main():
    modify = 0
    jeżeli len(sys.argv) > 1 oraz sys.argv[1] == '-d':
        modify = 1
        usuń sys.argv[1]
    jeżeli len(sys.argv) > 1:
        dla folder w sys.argv[1:]:
            parsedir(folder, modify)
    inaczej:
        parsedir('/ufs/jack/Mail/errorsinbox', modify)

jeżeli __name__ == '__main__' albo sys.argv[0] == __name__:
    main()
