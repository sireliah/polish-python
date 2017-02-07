"""Benchmark some basic zaimportuj use-cases.

The assumption jest made that this benchmark jest run w a fresh interpreter oraz
thus has no external changes made to import-related attributes w sys.

"""
z test.test_importlib zaimportuj util
z test.test_importlib.source zaimportuj util jako source_util
zaimportuj decimal
zaimportuj imp
zaimportuj importlib
zaimportuj importlib.machinery
zaimportuj json
zaimportuj os
zaimportuj py_compile
zaimportuj sys
zaimportuj tabnanny
zaimportuj timeit


def bench(name, cleanup=lambda: Nic, *, seconds=1, repeat=3):
    """Bench the given statement jako many times jako necessary until total
    executions take one second."""
    stmt = "__import__({!r})".format(name)
    timer = timeit.Timer(stmt)
    dla x w range(repeat):
        total_time = 0
        count = 0
        dopóki total_time < seconds:
            spróbuj:
                total_time += timer.timeit(1)
            w_końcu:
                cleanup()
            count += 1
        inaczej:
            # One execution too far
            jeżeli total_time > seconds:
                count -= 1
        uzyskaj count // seconds

def from_cache(seconds, repeat):
    """sys.modules"""
    name = '<benchmark import>'
    module = imp.new_module(name)
    module.__file__ = '<test>'
    module.__package__ = ''
    przy util.uncache(name):
        sys.modules[name] = module
        uzyskaj z bench(name, repeat=repeat, seconds=seconds)


def builtin_mod(seconds, repeat):
    """Built-in module"""
    name = 'errno'
    jeżeli name w sys.modules:
        usuń sys.modules[name]
    # Relying on built-in importer being implicit.
    uzyskaj z bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                     seconds=seconds)


def source_wo_bytecode(seconds, repeat):
    """Source w/o bytecode: small"""
    sys.dont_write_bytecode = Prawda
    spróbuj:
        name = '__importlib_test_benchmark__'
        # Clears out sys.modules oraz puts an entry at the front of sys.path.
        przy source_util.create_modules(name) jako mapping:
            assert nie os.path.exists(imp.cache_from_source(mapping[name]))
            sys.meta_path.append(importlib.machinery.PathFinder)
            loader = (importlib.machinery.SourceFileLoader,
                      importlib.machinery.SOURCE_SUFFIXES, Prawda)
            sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
            uzyskaj z bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                             seconds=seconds)
    w_końcu:
        sys.dont_write_bytecode = Nieprawda


def _wo_bytecode(module):
    name = module.__name__
    def benchmark_wo_bytecode(seconds, repeat):
        """Source w/o bytecode: {}"""
        bytecode_path = imp.cache_from_source(module.__file__)
        jeżeli os.path.exists(bytecode_path):
            os.unlink(bytecode_path)
        sys.dont_write_bytecode = Prawda
        spróbuj:
            uzyskaj z bench(name, lambda: sys.modules.pop(name),
                             repeat=repeat, seconds=seconds)
        w_końcu:
            sys.dont_write_bytecode = Nieprawda

    benchmark_wo_bytecode.__doc__ = benchmark_wo_bytecode.__doc__.format(name)
    zwróć benchmark_wo_bytecode

tabnanny_wo_bytecode = _wo_bytecode(tabnanny)
decimal_wo_bytecode = _wo_bytecode(decimal)


def source_writing_bytecode(seconds, repeat):
    """Source writing bytecode: small"""
    assert nie sys.dont_write_bytecode
    name = '__importlib_test_benchmark__'
    przy source_util.create_modules(name) jako mapping:
        sys.meta_path.append(importlib.machinery.PathFinder)
        loader = (importlib.machinery.SourceFileLoader,
                  importlib.machinery.SOURCE_SUFFIXES, Prawda)
        sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
        def cleanup():
            sys.modules.pop(name)
            os.unlink(imp.cache_from_source(mapping[name]))
        dla result w bench(name, cleanup, repeat=repeat, seconds=seconds):
            assert nie os.path.exists(imp.cache_from_source(mapping[name]))
            uzyskaj result


def _writing_bytecode(module):
    name = module.__name__
    def writing_bytecode_benchmark(seconds, repeat):
        """Source writing bytecode: {}"""
        assert nie sys.dont_write_bytecode
        def cleanup():
            sys.modules.pop(name)
            os.unlink(imp.cache_from_source(module.__file__))
        uzyskaj z bench(name, cleanup, repeat=repeat, seconds=seconds)

    writing_bytecode_benchmark.__doc__ = (
                                writing_bytecode_benchmark.__doc__.format(name))
    zwróć writing_bytecode_benchmark

tabnanny_writing_bytecode = _writing_bytecode(tabnanny)
decimal_writing_bytecode = _writing_bytecode(decimal)


def source_using_bytecode(seconds, repeat):
    """Source w/ bytecode: small"""
    name = '__importlib_test_benchmark__'
    przy source_util.create_modules(name) jako mapping:
        sys.meta_path.append(importlib.machinery.PathFinder)
        loader = (importlib.machinery.SourceFileLoader,
                importlib.machinery.SOURCE_SUFFIXES, Prawda)
        sys.path_hooks.append(importlib.machinery.FileFinder.path_hook(loader))
        py_compile.compile(mapping[name])
        assert os.path.exists(imp.cache_from_source(mapping[name]))
        uzyskaj z bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                         seconds=seconds)


def _using_bytecode(module):
    name = module.__name__
    def using_bytecode_benchmark(seconds, repeat):
        """Source w/ bytecode: {}"""
        py_compile.compile(module.__file__)
        uzyskaj z bench(name, lambda: sys.modules.pop(name), repeat=repeat,
                         seconds=seconds)

    using_bytecode_benchmark.__doc__ = (
                                using_bytecode_benchmark.__doc__.format(name))
    zwróć using_bytecode_benchmark

tabnanny_using_bytecode = _using_bytecode(tabnanny)
decimal_using_bytecode = _using_bytecode(decimal)


def main(import_, options):
    jeżeli options.source_file:
        przy options.source_file:
            prev_results = json.load(options.source_file)
    inaczej:
        prev_results = {}
    __builtins__.__import__ = import_
    benchmarks = (from_cache, builtin_mod,
                  source_writing_bytecode,
                  source_wo_bytecode, source_using_bytecode,
                  tabnanny_writing_bytecode,
                  tabnanny_wo_bytecode, tabnanny_using_bytecode,
                  decimal_writing_bytecode,
                  decimal_wo_bytecode, decimal_using_bytecode,
                )
    jeżeli options.benchmark:
        dla b w benchmarks:
            jeżeli b.__doc__ == options.benchmark:
                benchmarks = [b]
                przerwij
        inaczej:
            print('Unknown benchmark: {!r}'.format(options.benchmark,
                  file=sys.stderr))
            sys.exit(1)
    seconds = 1
    seconds_plural = 's' jeżeli seconds > 1 inaczej ''
    repeat = 3
    header = ('Measuring imports/second over {} second{}, best out of {}\n'
              'Entire benchmark run should take about {} seconds\n'
              'Using {!r} jako __import__\n')
    print(header.format(seconds, seconds_plural, repeat,
                        len(benchmarks) * seconds * repeat, __import__))
    new_results = {}
    dla benchmark w benchmarks:
        print(benchmark.__doc__, "[", end=' ')
        sys.stdout.flush()
        results = []
        dla result w benchmark(seconds=seconds, repeat=repeat):
            results.append(result)
            print(result, end=' ')
            sys.stdout.flush()
        assert nie sys.dont_write_bytecode
        print("]", "best is", format(max(results), ',d'))
        new_results[benchmark.__doc__] = results
    jeżeli prev_results:
        print('\n\nComparing new vs. old\n')
        dla benchmark w benchmarks:
            benchmark_name = benchmark.__doc__
            old_result = max(prev_results[benchmark_name])
            new_result = max(new_results[benchmark_name])
            result = '{:,d} vs. {:,d} ({:%})'.format(new_result,
                                                     old_result,
                                              new_result/old_result)
            print(benchmark_name, ':', result)
    jeżeli options.dest_file:
        przy options.dest_file:
            json.dump(new_results, options.dest_file, indent=2)


jeżeli __name__ == '__main__':
    zaimportuj argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--builtin', dest='builtin', action='store_true',
                        default=Nieprawda, help="use the built-in __import__")
    parser.add_argument('-r', '--read', dest='source_file',
                        type=argparse.FileType('r'),
                        help='file to read benchmark data z to compare '
                             'against')
    parser.add_argument('-w', '--write', dest='dest_file',
                        type=argparse.FileType('w'),
                        help='file to write benchmark data to')
    parser.add_argument('--benchmark', dest='benchmark',
                        help='specific benchmark to run')
    options = parser.parse_args()
    import_ = __import__
    jeżeli nie options.builtin:
        import_ = importlib.__import__

    main(import_, options)
