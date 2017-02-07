# -*- coding: utf-8 -*-
# This file should be kept compatible przy both Python 2.6 oraz Python >= 3.0.

zaimportuj itertools
zaimportuj os
zaimportuj platform
zaimportuj re
zaimportuj sys
zaimportuj time
z optparse zaimportuj OptionParser

out = sys.stdout

TEXT_ENCODING = 'utf8'
NEWLINES = 'lf'

# Compatibility
spróbuj:
    xrange
wyjąwszy NameError:
    xrange = range

def text_open(fn, mode, encoding=Nic):
    spróbuj:
        zwróć open(fn, mode, encoding=encoding albo TEXT_ENCODING)
    wyjąwszy TypeError:
        jeżeli 'r' w mode:
            mode += 'U' # 'U' mode jest needed only w Python 2.x
        zwróć open(fn, mode)

def get_file_sizes():
    dla s w ['20 KB', '400 KB', '10 MB']:
        size, unit = s.split()
        size = int(size) * {'KB': 1024, 'MB': 1024 ** 2}[unit]
        uzyskaj s.replace(' ', ''), size

def get_binary_files():
    zwróć ((name + ".bin", size) dla name, size w get_file_sizes())

def get_text_files():
    zwróć (("%s-%s-%s.txt" % (name, TEXT_ENCODING, NEWLINES), size)
        dla name, size w get_file_sizes())

def with_open_mode(mode):
    def decorate(f):
        f.file_open_mode = mode
        zwróć f
    zwróć decorate

def with_sizes(*sizes):
    def decorate(f):
        f.file_sizes = sizes
        zwróć f
    zwróć decorate


# Here begin the tests

@with_open_mode("r")
@with_sizes("medium")
def read_bytewise(f):
    """ read one unit at a time """
    f.seek(0)
    dopóki f.read(1):
        dalej

@with_open_mode("r")
@with_sizes("medium")
def read_small_chunks(f):
    """ read 20 units at a time """
    f.seek(0)
    dopóki f.read(20):
        dalej

@with_open_mode("r")
@with_sizes("medium")
def read_big_chunks(f):
    """ read 4096 units at a time """
    f.seek(0)
    dopóki f.read(4096):
        dalej

@with_open_mode("r")
@with_sizes("small", "medium", "large")
def read_whole_file(f):
    """ read whole contents at once """
    f.seek(0)
    dopóki f.read():
        dalej

@with_open_mode("rt")
@with_sizes("medium")
def read_lines(f):
    """ read one line at a time """
    f.seek(0)
    dla line w f:
        dalej

@with_open_mode("r")
@with_sizes("medium")
def seek_forward_bytewise(f):
    """ seek forward one unit at a time """
    f.seek(0, 2)
    size = f.tell()
    f.seek(0, 0)
    dla i w xrange(0, size - 1):
        f.seek(i, 0)

@with_open_mode("r")
@with_sizes("medium")
def seek_forward_blockwise(f):
    """ seek forward 1000 units at a time """
    f.seek(0, 2)
    size = f.tell()
    f.seek(0, 0)
    dla i w xrange(0, size - 1, 1000):
        f.seek(i, 0)

@with_open_mode("rb")
@with_sizes("medium")
def read_seek_bytewise(f):
    """ alternate read & seek one unit """
    f.seek(0)
    dopóki f.read(1):
        f.seek(1, 1)

@with_open_mode("rb")
@with_sizes("medium")
def read_seek_blockwise(f):
    """ alternate read & seek 1000 units """
    f.seek(0)
    dopóki f.read(1000):
        f.seek(1000, 1)


@with_open_mode("w")
@with_sizes("small")
def write_bytewise(f, source):
    """ write one unit at a time """
    dla i w xrange(0, len(source)):
        f.write(source[i:i+1])

@with_open_mode("w")
@with_sizes("medium")
def write_small_chunks(f, source):
    """ write 20 units at a time """
    dla i w xrange(0, len(source), 20):
        f.write(source[i:i+20])

@with_open_mode("w")
@with_sizes("medium")
def write_medium_chunks(f, source):
    """ write 4096 units at a time """
    dla i w xrange(0, len(source), 4096):
        f.write(source[i:i+4096])

@with_open_mode("w")
@with_sizes("large")
def write_large_chunks(f, source):
    """ write 1e6 units at a time """
    dla i w xrange(0, len(source), 1000000):
        f.write(source[i:i+1000000])


@with_open_mode("w+")
@with_sizes("small")
def modify_bytewise(f, source):
    """ modify one unit at a time """
    f.seek(0)
    dla i w xrange(0, len(source)):
        f.write(source[i:i+1])

@with_open_mode("w+")
@with_sizes("medium")
def modify_small_chunks(f, source):
    """ modify 20 units at a time """
    f.seek(0)
    dla i w xrange(0, len(source), 20):
        f.write(source[i:i+20])

@with_open_mode("w+")
@with_sizes("medium")
def modify_medium_chunks(f, source):
    """ modify 4096 units at a time """
    f.seek(0)
    dla i w xrange(0, len(source), 4096):
        f.write(source[i:i+4096])

@with_open_mode("wb+")
@with_sizes("medium")
def modify_seek_forward_bytewise(f, source):
    """ alternate write & seek one unit """
    f.seek(0)
    dla i w xrange(0, len(source), 2):
        f.write(source[i:i+1])
        f.seek(i+2)

@with_open_mode("wb+")
@with_sizes("medium")
def modify_seek_forward_blockwise(f, source):
    """ alternate write & seek 1000 units """
    f.seek(0)
    dla i w xrange(0, len(source), 2000):
        f.write(source[i:i+1000])
        f.seek(i+2000)

# XXX the 2 following tests don't work przy py3k's text IO
@with_open_mode("wb+")
@with_sizes("medium")
def read_modify_bytewise(f, source):
    """ alternate read & write one unit """
    f.seek(0)
    dla i w xrange(0, len(source), 2):
        f.read(1)
        f.write(source[i+1:i+2])

@with_open_mode("wb+")
@with_sizes("medium")
def read_modify_blockwise(f, source):
    """ alternate read & write 1000 units """
    f.seek(0)
    dla i w xrange(0, len(source), 2000):
        f.read(1000)
        f.write(source[i+1000:i+2000])


read_tests = [
    read_bytewise, read_small_chunks, read_lines, read_big_chunks,
    Nic, read_whole_file, Nic,
    seek_forward_bytewise, seek_forward_blockwise,
    read_seek_bytewise, read_seek_blockwise,
]

write_tests = [
    write_bytewise, write_small_chunks, write_medium_chunks, write_large_chunks,
]

modify_tests = [
    modify_bytewise, modify_small_chunks, modify_medium_chunks,
    Nic,
    modify_seek_forward_bytewise, modify_seek_forward_blockwise,
    read_modify_bytewise, read_modify_blockwise,
]

def run_during(duration, func):
    _t = time.time
    n = 0
    start = os.times()
    start_timestamp = _t()
    real_start = start[4] albo start_timestamp
    dopóki Prawda:
        func()
        n += 1
        jeżeli _t() - start_timestamp > duration:
            przerwij
    end = os.times()
    real = (end[4] jeżeli start[4] inaczej time.time()) - real_start
    zwróć n, real, sum(end[0:2]) - sum(start[0:2])

def warm_cache(filename):
    przy open(filename, "rb") jako f:
        f.read()


def run_all_tests(options):
    def print_label(filename, func):
        name = re.split(r'[-.]', filename)[0]
        out.write(
            ("[%s] %s... "
                % (name.center(7), func.__doc__.strip())
            ).ljust(52))
        out.flush()

    def print_results(size, n, real, cpu):
        bw = n * float(size) / 1024 ** 2 / real
        bw = ("%4d MB/s" jeżeli bw > 100 inaczej "%.3g MB/s") % bw
        out.write(bw.rjust(12) + "\n")
        jeżeli cpu < 0.90 * real:
            out.write("   warning: test above used only %d%% CPU, "
                "result may be flawed!\n" % (100.0 * cpu / real))

    def run_one_test(name, size, open_func, test_func, *args):
        mode = test_func.file_open_mode
        print_label(name, test_func)
        jeżeli "w" nie w mode albo "+" w mode:
            warm_cache(name)
        przy open_func(name) jako f:
            n, real, cpu = run_during(1.5, lambda: test_func(f, *args))
        print_results(size, n, real, cpu)

    def run_test_family(tests, mode_filter, files, open_func, *make_args):
        dla test_func w tests:
            jeżeli test_func jest Nic:
                out.write("\n")
                kontynuuj
            jeżeli mode_filter w test_func.file_open_mode:
                kontynuuj
            dla s w test_func.file_sizes:
                name, size = files[size_names[s]]
                #name += file_ext
                args = tuple(f(name, size) dla f w make_args)
                run_one_test(name, size,
                    open_func, test_func, *args)

    size_names = {
        "small": 0,
        "medium": 1,
        "large": 2,
    }

    print("Python %s" % sys.version)
    jeżeli sys.version_info < (3, 3):
        jeżeli sys.maxunicode > 0xffff:
            text = "UCS-4 (wide build)"
        inaczej:
            text = "UTF-16 (narrow build)"
    inaczej:
        text = "PEP 393"
    print("Unicode: %s" % text)
    print(platform.platform())
    binary_files = list(get_binary_files())
    text_files = list(get_text_files())
    jeżeli "b" w options:
        print("Binary unit = one byte")
    jeżeli "t" w options:
        print("Text unit = one character (%s-decoded)" % TEXT_ENCODING)

    # Binary reads
    jeżeli "b" w options oraz "r" w options:
        print("\n** Binary input **\n")
        run_test_family(read_tests, "t", binary_files, lambda fn: open(fn, "rb"))

    # Text reads
    jeżeli "t" w options oraz "r" w options:
        print("\n** Text input **\n")
        run_test_family(read_tests, "b", text_files, lambda fn: text_open(fn, "r"))

    # Binary writes
    jeżeli "b" w options oraz "w" w options:
        print("\n** Binary append **\n")
        def make_test_source(name, size):
            przy open(name, "rb") jako f:
                zwróć f.read()
        run_test_family(write_tests, "t", binary_files,
            lambda fn: open(os.devnull, "wb"), make_test_source)

    # Text writes
    jeżeli "t" w options oraz "w" w options:
        print("\n** Text append **\n")
        def make_test_source(name, size):
            przy text_open(name, "r") jako f:
                zwróć f.read()
        run_test_family(write_tests, "b", text_files,
            lambda fn: text_open(os.devnull, "w"), make_test_source)

    # Binary overwrites
    jeżeli "b" w options oraz "w" w options:
        print("\n** Binary overwrite **\n")
        def make_test_source(name, size):
            przy open(name, "rb") jako f:
                zwróć f.read()
        run_test_family(modify_tests, "t", binary_files,
            lambda fn: open(fn, "r+b"), make_test_source)

    # Text overwrites
    jeżeli "t" w options oraz "w" w options:
        print("\n** Text overwrite **\n")
        def make_test_source(name, size):
            przy text_open(name, "r") jako f:
                zwróć f.read()
        run_test_family(modify_tests, "b", text_files,
            lambda fn: text_open(fn, "r+"), make_test_source)


def prepare_files():
    print("Preparing files...")
    # Binary files
    dla name, size w get_binary_files():
        jeżeli os.path.isfile(name) oraz os.path.getsize(name) == size:
            kontynuuj
        przy open(name, "wb") jako f:
            f.write(os.urandom(size))
    # Text files
    chunk = []
    przy text_open(__file__, "r", encoding='utf8') jako f:
        dla line w f:
            jeżeli line.startswith("# <iobench text chunk marker>"):
                przerwij
        inaczej:
            podnieś RuntimeError(
                "Couldn't find chunk marker w %s !" % __file__)
        jeżeli NEWLINES == "all":
            it = itertools.cycle(["\n", "\r", "\r\n"])
        inaczej:
            it = itertools.repeat(
                {"cr": "\r", "lf": "\n", "crlf": "\r\n"}[NEWLINES])
        chunk = "".join(line.replace("\n", next(it)) dla line w f)
        jeżeli isinstance(chunk, bytes):
            chunk = chunk.decode('utf8')
        chunk = chunk.encode(TEXT_ENCODING)
    dla name, size w get_text_files():
        jeżeli os.path.isfile(name) oraz os.path.getsize(name) == size:
            kontynuuj
        head = chunk * (size // len(chunk))
        tail = chunk[:size % len(chunk)]
        # Adjust tail to end on a character boundary
        dopóki Prawda:
            spróbuj:
                tail.decode(TEXT_ENCODING)
                przerwij
            wyjąwszy UnicodeDecodeError:
                tail = tail[:-1]
        przy open(name, "wb") jako f:
            f.write(head)
            f.write(tail)

def main():
    global TEXT_ENCODING, NEWLINES

    usage = "usage: %prog [-h|--help] [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-b", "--binary",
                      action="store_true", dest="binary", default=Nieprawda,
                      help="run binary I/O tests")
    parser.add_option("-t", "--text",
                      action="store_true", dest="text", default=Nieprawda,
                      help="run text I/O tests")
    parser.add_option("-r", "--read",
                      action="store_true", dest="read", default=Nieprawda,
                      help="run read tests")
    parser.add_option("-w", "--write",
                      action="store_true", dest="write", default=Nieprawda,
                      help="run write & modify tests")
    parser.add_option("-E", "--encoding",
                      action="store", dest="encoding", default=Nic,
                      help="encoding dla text tests (default: %s)" % TEXT_ENCODING)
    parser.add_option("-N", "--newlines",
                      action="store", dest="newlines", default='lf',
                      help="line endings dla text tests "
                           "(one of: {lf (default), cr, crlf, all})")
    parser.add_option("-m", "--io-module",
                      action="store", dest="io_module", default=Nic,
                      help="io module to test (default: builtin open())")
    options, args = parser.parse_args()
    jeżeli args:
        parser.error("unexpected arguments")
    NEWLINES = options.newlines.lower()
    jeżeli NEWLINES nie w ('lf', 'cr', 'crlf', 'all'):
        parser.error("invalid 'newlines' option: %r" % NEWLINES)

    test_options = ""
    jeżeli options.read:
        test_options += "r"
    jeżeli options.write:
        test_options += "w"
    albo_inaczej nie options.read:
        test_options += "rw"
    jeżeli options.text:
        test_options += "t"
    jeżeli options.binary:
        test_options += "b"
    albo_inaczej nie options.text:
        test_options += "tb"

    jeżeli options.encoding:
        TEXT_ENCODING = options.encoding

    jeżeli options.io_module:
        globals()['open'] = __import__(options.io_module, {}, {}, ['open']).open

    prepare_files()
    run_all_tests(test_options)

jeżeli __name__ == "__main__":
    main()


# -- This part to exercise text reading. Don't change anything! --
# <iobench text chunk marker>

"""
1.
Gáttir allar,
áðr gangi fram,
um skoðask skyli,
um skyggnast skyli,
því at óvíst er at vita,
hvar óvinir
sitja á fleti fyrir.

2.
Gefendr heilir!
Gestr er inn kominn,
hvar skal sitja sjá?
Mjök er bráðr,
sá er á bröndum skal
síns of freista frama.

3.
Elds er þörf,
þeims inn er kominn
ok á kné kalinn;
matar ok váða
er manni þörf,
þeim er hefr um fjall farit.

4.
Vatns er þörf,
þeim er til verðar kemr,
þerru ok þjóðlaðar,
góðs of æðis,
ef sér geta mætti,
orðs ok endrþögu.

5.
Vits er þörf,
þeim er víða ratar;
dælt er heima hvat;
at augabragði verðr,
sá er ekki kann
ok með snotrum sitr.

6.
At hyggjandi sinni
skyli-t maðr hræsinn vera,
heldr gætinn at geði;
þá er horskr ok þögull
kemr heimisgarða til,
sjaldan verðr víti vörum,
því at óbrigðra vin
fær maðr aldregi
en mannvit mikit.

7.
Inn vari gestr,
er til verðar kemr,
þunnu hljóði þegir,
eyrum hlýðir,
en augum skoðar;
svá nýsisk fróðra hverr fyrir.

8.
Hinn er sæll,
er sér of getr
lof ok líknstafi;
ódælla er við þat,
er maðr eiga skal
annars brjóstum í.
"""

"""
C'est revenir tard, je le sens, sur un sujet trop rebattu et déjà presque oublié. Mon état, qui ne me permet plus aucun travail suivi, mon aversion pour le genre polémique, ont causé ma lenteur à écrire et ma répugnance à publier. J'aurais même tout à fait supprimé ces Lettres, ou plutôt je lie les aurais point écrites, s'il n'eût été question que de moi : Mais ma patrie ne m'est pas tellement devenue étrangère que je puisse voir tranquillement opprimer ses citoyens, surtout lorsqu'ils n'ont compromis leurs droits qu'en défendant ma cause. Je serais le dernier des hommes si dans une telle occasion j'écoutais un sentiment qui n'est plus ni douceur ni patience, mais faiblesse et lâcheté, dans celui qu'il empêche de remplir son devoir.
Rien de moins important pour le public, j'en conviens, que la matière de ces lettres. La constitution d'une petite République, le sort d'un petit particulier, l'exposé de quelques injustices, la réfutation de quelques sophismes ; tout cela n'a rien en soi d'assez considérable pour mériter beaucoup de lecteurs : mais si mes sujets sont petits mes objets sont grands, et dignes de l'attention de tout honnête homme. Laissons Genève à sa place, et Rousseau dans sa dépression ; mais la religion, mais la liberté, la justice ! voilà, qui que vous soyez, ce qui n'est pas au-dessous de vous.
Qu'on ne cherche pas même ici dans le style le dédommagement de l'aridité de la matière. Ceux que quelques traits heureux de ma plume ont si fort irrités trouveront de quoi s'apaiser dans ces lettres, L'honneur de défendre un opprimé eût enflammé mon coeur si j'avais parlé pour un autre. Réduit au triste emploi de me défendre moi-même, j'ai dû me borner à raisonner ; m'échauffer eût été m'avilir. J'aurai donc trouvé grâce en ce point devant ceux qui s'imaginent qu'il est essentiel à la vérité d'être dite froidement ; opinion que pourtant j'ai peine à comprendre. Lorsqu'une vive persuasion nous anime, le moyen d'employer un langage glacé ? Quand Archimède tout transporté courait nu dans les rues de Syracuse, en avait-il moins trouvé la vérité parce qu'il se dalejionnait pour elle ? Tout au contraire, celui qui la sent ne peut s'abstenir de l'adorer ; celui qui demeure froid ne l'a pas vue.
Quoi qu'il en soit, je prie les lecteurs de vouloir bien mettre à part mon beau style, et d'examiner seulement si je raisonne bien ou mal ; car enfin, de cela seul qu'un auteur s'exprime en bons termes, je ne vois pas comment il peut s'ensuivre que cet auteur ne sait ce qu'il dit.
"""
