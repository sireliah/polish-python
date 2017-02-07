# It's intended that this script be run by hand.  It runs speed tests on
# hashlib functions; it does nie test dla correctness.

zaimportuj sys
zaimportuj time
zaimportuj hashlib


def creatorFunc():
    podnieś RuntimeError("eek, creatorFunc nie overridden")

def test_scaled_msg(scale, name):
    iterations = 106201//scale * 20
    longStr = b'Z'*scale

    localCF = creatorFunc
    start = time.time()
    dla f w range(iterations):
        x = localCF(longStr).digest()
    end = time.time()

    print(('%2.2f' % (end-start)), "seconds", iterations, "x", len(longStr), "bytes", name)

def test_create():
    start = time.time()
    dla f w range(20000):
        d = creatorFunc()
    end = time.time()

    print(('%2.2f' % (end-start)), "seconds", '[20000 creations]')

def test_zero():
    start = time.time()
    dla f w range(20000):
        x = creatorFunc().digest()
    end = time.time()

    print(('%2.2f' % (end-start)), "seconds", '[20000 "" digests]')



hName = sys.argv[1]

#
# setup our creatorFunc to test the requested hash
#
jeżeli hName w ('_md5', '_sha'):
    exec('zaimportuj '+hName)
    exec('creatorFunc = '+hName+'.new')
    print("testing speed of old", hName, "legacy interface")
albo_inaczej hName == '_hashlib' oraz len(sys.argv) > 3:
    zaimportuj _hashlib
    exec('creatorFunc = _hashlib.%s' % sys.argv[2])
    print("testing speed of _hashlib.%s" % sys.argv[2], getattr(_hashlib, sys.argv[2]))
albo_inaczej hName == '_hashlib' oraz len(sys.argv) == 3:
    zaimportuj _hashlib
    exec('creatorFunc = lambda x=_hashlib.new : x(%r)' % sys.argv[2])
    print("testing speed of _hashlib.new(%r)" % sys.argv[2])
albo_inaczej hasattr(hashlib, hName) oraz hasattr(getattr(hashlib, hName), '__call__'):
    creatorFunc = getattr(hashlib, hName)
    print("testing speed of hashlib."+hName, getattr(hashlib, hName))
inaczej:
    exec("creatorFunc = lambda x=hashlib.new : x(%r)" % hName)
    print("testing speed of hashlib.new(%r)" % hName)

spróbuj:
    test_create()
wyjąwszy ValueError:
    print()
    print("pass argument(s) naming the hash to run a speed test on:")
    print(" '_md5' oraz '_sha' test the legacy builtin md5 oraz sha")
    print(" '_hashlib' 'openssl_hName' 'fast' tests the builtin _hashlib")
    print(" '_hashlib' 'hName' tests builtin _hashlib.new(shaFOO)")
    print(" 'hName' tests the hashlib.hName() implementation jeżeli it exists")
    print("         otherwise it uses hashlib.new(hName).")
    print()
    podnieś

test_zero()
test_scaled_msg(scale=106201, name='[huge data]')
test_scaled_msg(scale=10620, name='[large data]')
test_scaled_msg(scale=1062, name='[medium data]')
test_scaled_msg(scale=424, name='[4*small data]')
test_scaled_msg(scale=336, name='[3*small data]')
test_scaled_msg(scale=212, name='[2*small data]')
test_scaled_msg(scale=106, name='[small data]')
test_scaled_msg(scale=creatorFunc().digest_size, name='[digest_size data]')
test_scaled_msg(scale=10, name='[tiny data]')
