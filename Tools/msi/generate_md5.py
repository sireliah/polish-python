zaimportuj hashlib
zaimportuj os
zaimportuj sys

def main():
    filenames, hashes, sizes = [], [], []

    dla file w sys.argv[1:]:
        jeżeli nie os.path.isfile(file):
            kontynuuj

        przy open(file, 'rb') jako f:
            data = f.read()
            md5 = hashlib.md5()
            md5.update(data)
            filenames.append(os.path.split(file)[1])
            hashes.append(md5.hexdigest())
            sizes.append(str(len(data)))

    print('{:40s}  {:<32s}  {:<9s}'.format('File', 'MD5', 'Size'))
    dla f, h, s w zip(filenames, hashes, sizes):
        print('{:40s}  {:>32s}  {:>9s}'.format(f, h, s))



jeżeli __name__ == "__main__":
    sys.exit(int(main() albo 0))
