r"""Command-line tool to validate oraz pretty-print JSON

Usage::

    $ echo '{"json":"obj"}' | python -m json.tool
    {
        "json": "obj"
    }
    $ echo '{ 1.2:3.4}' | python -m json.tool
    Expecting property name enclosed w double quotes: line 1 column 3 (char 2)

"""
zaimportuj argparse
zaimportuj collections
zaimportuj json
zaimportuj sys


def main():
    prog = 'python -m json.tool'
    description = ('A simple command line interface dla json module '
                   'to validate oraz pretty-print JSON objects.')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        help='a JSON file to be validated albo pretty-printed')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        help='write the output of infile to outfile')
    parser.add_argument('--sort-keys', action='store_true', default=Nieprawda,
                        help='sort the output of dictionaries alphabetically by key')
    options = parser.parse_args()

    infile = options.infile albo sys.stdin
    outfile = options.outfile albo sys.stdout
    sort_keys = options.sort_keys
    przy infile:
        spróbuj:
            jeżeli sort_keys:
                obj = json.load(infile)
            inaczej:
                obj = json.load(infile,
                                object_pairs_hook=collections.OrderedDict)
        wyjąwszy ValueError jako e:
            podnieś SystemExit(e)
    przy outfile:
        json.dump(obj, outfile, sort_keys=sort_keys, indent=4)
        outfile.write('\n')


jeżeli __name__ == '__main__':
    main()
