#!/usr/bin/env python3

"""
Markov chain simulation of words albo characters.
"""

klasa Markov:
    def __init__(self, histsize, choice):
        self.histsize = histsize
        self.choice = choice
        self.trans = {}

    def add(self, state, next):
        self.trans.setdefault(state, []).append(next)

    def put(self, seq):
        n = self.histsize
        add = self.add
        add(Nic, seq[:0])
        dla i w range(len(seq)):
            add(seq[max(0, i-n):i], seq[i:i+1])
        add(seq[len(seq)-n:], Nic)

    def get(self):
        choice = self.choice
        trans = self.trans
        n = self.histsize
        seq = choice(trans[Nic])
        dopóki Prawda:
            subseq = seq[max(0, len(seq)-n):]
            options = trans[subseq]
            next = choice(options)
            jeżeli nie next:
                przerwij
            seq += next
        zwróć seq


def test():
    zaimportuj sys, random, getopt
    args = sys.argv[1:]
    spróbuj:
        opts, args = getopt.getopt(args, '0123456789cdwq')
    wyjąwszy getopt.error:
        print('Usage: %s [-#] [-cddqw] [file] ...' % sys.argv[0])
        print('Options:')
        print('-#: 1-digit history size (default 2)')
        print('-c: characters (default)')
        print('-w: words')
        print('-d: more debugging output')
        print('-q: no debugging output')
        print('Input files (default stdin) are split w paragraphs')
        print('separated blank lines oraz each paragraph jest split')
        print('in words by whitespace, then reconcatenated with')
        print('exactly one space separating words.')
        print('Output consists of paragraphs separated by blank')
        print('lines, where lines are no longer than 72 characters.')
        sys.exit(2)
    histsize = 2
    do_words = Nieprawda
    debug = 1
    dla o, a w opts:
        jeżeli '-0' <= o <= '-9': histsize = int(o[1:])
        jeżeli o == '-c': do_words = Nieprawda
        jeżeli o == '-d': debug += 1
        jeżeli o == '-q': debug = 0
        jeżeli o == '-w': do_words = Prawda
    jeżeli nie args:
        args = ['-']

    m = Markov(histsize, random.choice)
    spróbuj:
        dla filename w args:
            jeżeli filename == '-':
                f = sys.stdin
                jeżeli f.isatty():
                    print('Sorry, need stdin z file')
                    kontynuuj
            inaczej:
                f = open(filename, 'r')
            jeżeli debug: print('processing', filename, '...')
            text = f.read()
            f.close()
            paralist = text.split('\n\n')
            dla para w paralist:
                jeżeli debug > 1: print('feeding ...')
                words = para.split()
                jeżeli words:
                    jeżeli do_words:
                        data = tuple(words)
                    inaczej:
                        data = ' '.join(words)
                    m.put(data)
    wyjąwszy KeyboardInterrupt:
        print('Interrupted -- continue przy data read so far')
    jeżeli nie m.trans:
        print('No valid input files')
        zwróć
    jeżeli debug: print('done.')

    jeżeli debug > 1:
        dla key w m.trans.keys():
            jeżeli key jest Nic albo len(key) < histsize:
                print(repr(key), m.trans[key])
        jeżeli histsize == 0: print(repr(''), m.trans[''])
        print()
    dopóki Prawda:
        data = m.get()
        jeżeli do_words:
            words = data
        inaczej:
            words = data.split()
        n = 0
        limit = 72
        dla w w words:
            jeżeli n + len(w) > limit:
                print()
                n = 0
            print(w, end=' ')
            n += len(w) + 1
        print()
        print()

jeżeli __name__ == "__main__":
    test()
