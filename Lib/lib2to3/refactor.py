# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Refactoring framework.

Used jako a main program, this can refactor any number of files and/or
recursively descend down directories.  Imported jako a module, this
provides infrastructure to write your own refactoring tool.
"""

z __future__ zaimportuj with_statement

__author__ = "Guido van Rossum <guido@python.org>"


# Python imports
zaimportuj os
zaimportuj sys
zaimportuj logging
zaimportuj operator
zaimportuj collections
zaimportuj io
z itertools zaimportuj chain

# Local imports
z .pgen2 zaimportuj driver, tokenize, token
z .fixer_util zaimportuj find_root
z . zaimportuj pytree, pygram
z . zaimportuj btm_utils jako bu
z . zaimportuj btm_matcher jako bm


def get_all_fix_names(fixer_pkg, remove_prefix=Prawda):
    """Return a sorted list of all available fix names w the given package."""
    pkg = __import__(fixer_pkg, [], [], ["*"])
    fixer_dir = os.path.dirname(pkg.__file__)
    fix_names = []
    dla name w sorted(os.listdir(fixer_dir)):
        jeżeli name.startswith("fix_") oraz name.endswith(".py"):
            jeżeli remove_prefix:
                name = name[4:]
            fix_names.append(name[:-3])
    zwróć fix_names


klasa _EveryNode(Exception):
    dalej


def _get_head_types(pat):
    """ Accepts a pytree Pattern Node oraz returns a set
        of the pattern types which will match first. """

    jeżeli isinstance(pat, (pytree.NodePattern, pytree.LeafPattern)):
        # NodePatters must either have no type oraz no content
        #   albo a type oraz content -- so they don't get any farther
        # Always zwróć leafs
        jeżeli pat.type jest Nic:
            podnieś _EveryNode
        zwróć {pat.type}

    jeżeli isinstance(pat, pytree.NegatedPattern):
        jeżeli pat.content:
            zwróć _get_head_types(pat.content)
        podnieś _EveryNode # Negated Patterns don't have a type

    jeżeli isinstance(pat, pytree.WildcardPattern):
        # Recurse on each node w content
        r = set()
        dla p w pat.content:
            dla x w p:
                r.update(_get_head_types(x))
        zwróć r

    podnieś Exception("Oh no! I don't understand pattern %s" %(pat))


def _get_headnode_dict(fixer_list):
    """ Accepts a list of fixers oraz returns a dictionary
        of head node type --> fixer list.  """
    head_nodes = collections.defaultdict(list)
    every = []
    dla fixer w fixer_list:
        jeżeli fixer.pattern:
            spróbuj:
                heads = _get_head_types(fixer.pattern)
            wyjąwszy _EveryNode:
                every.append(fixer)
            inaczej:
                dla node_type w heads:
                    head_nodes[node_type].append(fixer)
        inaczej:
            jeżeli fixer._accept_type jest nie Nic:
                head_nodes[fixer._accept_type].append(fixer)
            inaczej:
                every.append(fixer)
    dla node_type w chain(pygram.python_grammar.symbol2number.values(),
                           pygram.python_grammar.tokens):
        head_nodes[node_type].extend(every)
    zwróć dict(head_nodes)


def get_fixers_from_package(pkg_name):
    """
    Return the fully qualified names dla fixers w the package pkg_name.
    """
    zwróć [pkg_name + "." + fix_name
            dla fix_name w get_all_fix_names(pkg_name, Nieprawda)]

def _identity(obj):
    zwróć obj

jeżeli sys.version_info < (3, 0):
    zaimportuj codecs
    _open_with_encoding = codecs.open
    # codecs.open doesn't translate newlines sadly.
    def _from_system_newlines(input):
        zwróć input.replace("\r\n", "\n")
    def _to_system_newlines(input):
        jeżeli os.linesep != "\n":
            zwróć input.replace("\n", os.linesep)
        inaczej:
            zwróć input
inaczej:
    _open_with_encoding = open
    _from_system_newlines = _identity
    _to_system_newlines = _identity


def _detect_future_features(source):
    have_docstring = Nieprawda
    gen = tokenize.generate_tokens(io.StringIO(source).readline)
    def advance():
        tok = next(gen)
        zwróć tok[0], tok[1]
    ignore = frozenset({token.NEWLINE, tokenize.NL, token.COMMENT})
    features = set()
    spróbuj:
        dopóki Prawda:
            tp, value = advance()
            jeżeli tp w ignore:
                kontynuuj
            albo_inaczej tp == token.STRING:
                jeżeli have_docstring:
                    przerwij
                have_docstring = Prawda
            albo_inaczej tp == token.NAME oraz value == "from":
                tp, value = advance()
                jeżeli tp != token.NAME albo value != "__future__":
                    przerwij
                tp, value = advance()
                jeżeli tp != token.NAME albo value != "import":
                    przerwij
                tp, value = advance()
                jeżeli tp == token.OP oraz value == "(":
                    tp, value = advance()
                dopóki tp == token.NAME:
                    features.add(value)
                    tp, value = advance()
                    jeżeli tp != token.OP albo value != ",":
                        przerwij
                    tp, value = advance()
            inaczej:
                przerwij
    wyjąwszy StopIteration:
        dalej
    zwróć frozenset(features)


klasa FixerError(Exception):
    """A fixer could nie be loaded."""


klasa RefactoringTool(object):

    _default_options = {"print_function" : Nieprawda,
                        "write_unchanged_files" : Nieprawda}

    CLASS_PREFIX = "Fix" # The prefix dla fixer classes
    FILE_PREFIX = "fix_" # The prefix dla modules przy a fixer within

    def __init__(self, fixer_names, options=Nic, explicit=Nic):
        """Initializer.

        Args:
            fixer_names: a list of fixers to import
            options: an dict przy configuration.
            explicit: a list of fixers to run even jeżeli they are explicit.
        """
        self.fixers = fixer_names
        self.explicit = explicit albo []
        self.options = self._default_options.copy()
        jeżeli options jest nie Nic:
            self.options.update(options)
        jeżeli self.options["print_function"]:
            self.grammar = pygram.python_grammar_no_print_statement
        inaczej:
            self.grammar = pygram.python_grammar
        # When this jest Prawda, the refactor*() methods will call write_file() for
        # files processed even jeżeli they were nie changed during refactoring. If
        # oraz only jeżeli the refactor method's write parameter was Prawda.
        self.write_unchanged_files = self.options.get("write_unchanged_files")
        self.errors = []
        self.logger = logging.getLogger("RefactoringTool")
        self.fixer_log = []
        self.wrote = Nieprawda
        self.driver = driver.Driver(self.grammar,
                                    convert=pytree.convert,
                                    logger=self.logger)
        self.pre_order, self.post_order = self.get_fixers()


        self.files = []  # List of files that were albo should be modified

        self.BM = bm.BottomMatcher()
        self.bmi_pre_order = [] # Bottom Matcher incompatible fixers
        self.bmi_post_order = []

        dla fixer w chain(self.post_order, self.pre_order):
            jeżeli fixer.BM_compatible:
                self.BM.add_fixer(fixer)
                # remove fixers that will be handled by the bottom-up
                # matcher
            albo_inaczej fixer w self.pre_order:
                self.bmi_pre_order.append(fixer)
            albo_inaczej fixer w self.post_order:
                self.bmi_post_order.append(fixer)

        self.bmi_pre_order_heads = _get_headnode_dict(self.bmi_pre_order)
        self.bmi_post_order_heads = _get_headnode_dict(self.bmi_post_order)



    def get_fixers(self):
        """Inspects the options to load the requested patterns oraz handlers.

        Returns:
          (pre_order, post_order), where pre_order jest the list of fixers that
          want a pre-order AST traversal, oraz post_order jest the list that want
          post-order traversal.
        """
        pre_order_fixers = []
        post_order_fixers = []
        dla fix_mod_path w self.fixers:
            mod = __import__(fix_mod_path, {}, {}, ["*"])
            fix_name = fix_mod_path.rsplit(".", 1)[-1]
            jeżeli fix_name.startswith(self.FILE_PREFIX):
                fix_name = fix_name[len(self.FILE_PREFIX):]
            parts = fix_name.split("_")
            class_name = self.CLASS_PREFIX + "".join([p.title() dla p w parts])
            spróbuj:
                fix_class = getattr(mod, class_name)
            wyjąwszy AttributeError:
                podnieś FixerError("Can't find %s.%s" % (fix_name, class_name))
            fixer = fix_class(self.options, self.fixer_log)
            jeżeli fixer.explicit oraz self.explicit jest nie Prawda oraz \
                    fix_mod_path nie w self.explicit:
                self.log_message("Skipping optional fixer: %s", fix_name)
                kontynuuj

            self.log_debug("Adding transformation: %s", fix_name)
            jeżeli fixer.order == "pre":
                pre_order_fixers.append(fixer)
            albo_inaczej fixer.order == "post":
                post_order_fixers.append(fixer)
            inaczej:
                podnieś FixerError("Illegal fixer order: %r" % fixer.order)

        key_func = operator.attrgetter("run_order")
        pre_order_fixers.sort(key=key_func)
        post_order_fixers.sort(key=key_func)
        zwróć (pre_order_fixers, post_order_fixers)

    def log_error(self, msg, *args, **kwds):
        """Called when an error occurs."""
        podnieś

    def log_message(self, msg, *args):
        """Hook to log a message."""
        jeżeli args:
            msg = msg % args
        self.logger.info(msg)

    def log_debug(self, msg, *args):
        jeżeli args:
            msg = msg % args
        self.logger.debug(msg)

    def print_output(self, old_text, new_text, filename, equal):
        """Called przy the old version, new version, oraz filename of a
        refactored file."""
        dalej

    def refactor(self, items, write=Nieprawda, doctests_only=Nieprawda):
        """Refactor a list of files oraz directories."""

        dla dir_or_file w items:
            jeżeli os.path.isdir(dir_or_file):
                self.refactor_dir(dir_or_file, write, doctests_only)
            inaczej:
                self.refactor_file(dir_or_file, write, doctests_only)

    def refactor_dir(self, dir_name, write=Nieprawda, doctests_only=Nieprawda):
        """Descends down a directory oraz refactor every Python file found.

        Python files are assumed to have a .py extension.

        Files oraz subdirectories starting przy '.' are skipped.
        """
        py_ext = os.extsep + "py"
        dla dirpath, dirnames, filenames w os.walk(dir_name):
            self.log_debug("Descending into %s", dirpath)
            dirnames.sort()
            filenames.sort()
            dla name w filenames:
                jeżeli (nie name.startswith(".") oraz
                    os.path.splitext(name)[1] == py_ext):
                    fullname = os.path.join(dirpath, name)
                    self.refactor_file(fullname, write, doctests_only)
            # Modify dirnames in-place to remove subdirs przy leading dots
            dirnames[:] = [dn dla dn w dirnames jeżeli nie dn.startswith(".")]

    def _read_python_source(self, filename):
        """
        Do our best to decode a Python source file correctly.
        """
        spróbuj:
            f = open(filename, "rb")
        wyjąwszy OSError jako err:
            self.log_error("Can't open %s: %s", filename, err)
            zwróć Nic, Nic
        spróbuj:
            encoding = tokenize.detect_encoding(f.readline)[0]
        w_końcu:
            f.close()
        przy _open_with_encoding(filename, "r", encoding=encoding) jako f:
            zwróć _from_system_newlines(f.read()), encoding

    def refactor_file(self, filename, write=Nieprawda, doctests_only=Nieprawda):
        """Refactors a file."""
        input, encoding = self._read_python_source(filename)
        jeżeli input jest Nic:
            # Reading the file failed.
            zwróć
        input += "\n" # Silence certain parse errors
        jeżeli doctests_only:
            self.log_debug("Refactoring doctests w %s", filename)
            output = self.refactor_docstring(input, filename)
            jeżeli self.write_unchanged_files albo output != input:
                self.processed_file(output, filename, input, write, encoding)
            inaczej:
                self.log_debug("No doctest changes w %s", filename)
        inaczej:
            tree = self.refactor_string(input, filename)
            jeżeli self.write_unchanged_files albo (tree oraz tree.was_changed):
                # The [:-1] jest to take off the \n we added earlier
                self.processed_file(str(tree)[:-1], filename,
                                    write=write, encoding=encoding)
            inaczej:
                self.log_debug("No changes w %s", filename)

    def refactor_string(self, data, name):
        """Refactor a given input string.

        Args:
            data: a string holding the code to be refactored.
            name: a human-readable name dla use w error/log messages.

        Returns:
            An AST corresponding to the refactored input stream; Nic if
            there were errors during the parse.
        """
        features = _detect_future_features(data)
        jeżeli "print_function" w features:
            self.driver.grammar = pygram.python_grammar_no_print_statement
        spróbuj:
            tree = self.driver.parse_string(data)
        wyjąwszy Exception jako err:
            self.log_error("Can't parse %s: %s: %s",
                           name, err.__class__.__name__, err)
            zwróć
        w_końcu:
            self.driver.grammar = self.grammar
        tree.future_features = features
        self.log_debug("Refactoring %s", name)
        self.refactor_tree(tree, name)
        zwróć tree

    def refactor_stdin(self, doctests_only=Nieprawda):
        input = sys.stdin.read()
        jeżeli doctests_only:
            self.log_debug("Refactoring doctests w stdin")
            output = self.refactor_docstring(input, "<stdin>")
            jeżeli self.write_unchanged_files albo output != input:
                self.processed_file(output, "<stdin>", input)
            inaczej:
                self.log_debug("No doctest changes w stdin")
        inaczej:
            tree = self.refactor_string(input, "<stdin>")
            jeżeli self.write_unchanged_files albo (tree oraz tree.was_changed):
                self.processed_file(str(tree), "<stdin>", input)
            inaczej:
                self.log_debug("No changes w stdin")

    def refactor_tree(self, tree, name):
        """Refactors a parse tree (modifying the tree w place).

        For compatible patterns the bottom matcher module jest
        used. Otherwise the tree jest traversed node-to-node for
        matches.

        Args:
            tree: a pytree.Node instance representing the root of the tree
                  to be refactored.
            name: a human-readable name dla this tree.

        Returns:
            Prawda jeżeli the tree was modified, Nieprawda otherwise.
        """

        dla fixer w chain(self.pre_order, self.post_order):
            fixer.start_tree(tree, name)

        #use traditional matching dla the incompatible fixers
        self.traverse_by(self.bmi_pre_order_heads, tree.pre_order())
        self.traverse_by(self.bmi_post_order_heads, tree.post_order())

        # obtain a set of candidate nodes
        match_set = self.BM.run(tree.leaves())

        dopóki any(match_set.values()):
            dla fixer w self.BM.fixers:
                jeżeli fixer w match_set oraz match_set[fixer]:
                    #sort by depth; apply fixers z bottom(of the AST) to top
                    match_set[fixer].sort(key=pytree.Base.depth, reverse=Prawda)

                    jeżeli fixer.keep_line_order:
                        #some fixers(eg fix_imports) must be applied
                        #przy the original file's line order
                        match_set[fixer].sort(key=pytree.Base.get_lineno)

                    dla node w list(match_set[fixer]):
                        jeżeli node w match_set[fixer]:
                            match_set[fixer].remove(node)

                        spróbuj:
                            find_root(node)
                        wyjąwszy ValueError:
                            # this node has been cut off z a
                            # previous transformation ; skip
                            kontynuuj

                        jeżeli node.fixers_applied oraz fixer w node.fixers_applied:
                            # do nie apply the same fixer again
                            kontynuuj

                        results = fixer.match(node)

                        jeżeli results:
                            new = fixer.transform(node, results)
                            jeżeli new jest nie Nic:
                                node.replace(new)
                                #new.fixers_applied.append(fixer)
                                dla node w new.post_order():
                                    # do nie apply the fixer again to
                                    # this albo any subnode
                                    jeżeli nie node.fixers_applied:
                                        node.fixers_applied = []
                                    node.fixers_applied.append(fixer)

                                # update the original match set for
                                # the added code
                                new_matches = self.BM.run(new.leaves())
                                dla fxr w new_matches:
                                    jeżeli nie fxr w match_set:
                                        match_set[fxr]=[]

                                    match_set[fxr].extend(new_matches[fxr])

        dla fixer w chain(self.pre_order, self.post_order):
            fixer.finish_tree(tree, name)
        zwróć tree.was_changed

    def traverse_by(self, fixers, traversal):
        """Traverse an AST, applying a set of fixers to each node.

        This jest a helper method dla refactor_tree().

        Args:
            fixers: a list of fixer instances.
            traversal: a generator that uzyskajs AST nodes.

        Returns:
            Nic
        """
        jeżeli nie fixers:
            zwróć
        dla node w traversal:
            dla fixer w fixers[node.type]:
                results = fixer.match(node)
                jeżeli results:
                    new = fixer.transform(node, results)
                    jeżeli new jest nie Nic:
                        node.replace(new)
                        node = new

    def processed_file(self, new_text, filename, old_text=Nic, write=Nieprawda,
                       encoding=Nic):
        """
        Called when a file has been refactored oraz there may be changes.
        """
        self.files.append(filename)
        jeżeli old_text jest Nic:
            old_text = self._read_python_source(filename)[0]
            jeżeli old_text jest Nic:
                zwróć
        equal = old_text == new_text
        self.print_output(old_text, new_text, filename, equal)
        jeżeli equal:
            self.log_debug("No changes to %s", filename)
            jeżeli nie self.write_unchanged_files:
                zwróć
        jeżeli write:
            self.write_file(new_text, filename, old_text, encoding)
        inaczej:
            self.log_debug("Not writing changes to %s", filename)

    def write_file(self, new_text, filename, old_text, encoding=Nic):
        """Writes a string to a file.

        It first shows a unified diff between the old text oraz the new text, oraz
        then rewrites the file; the latter jest only done jeżeli the write option jest
        set.
        """
        spróbuj:
            f = _open_with_encoding(filename, "w", encoding=encoding)
        wyjąwszy OSError jako err:
            self.log_error("Can't create %s: %s", filename, err)
            zwróć
        spróbuj:
            f.write(_to_system_newlines(new_text))
        wyjąwszy OSError jako err:
            self.log_error("Can't write %s: %s", filename, err)
        w_końcu:
            f.close()
        self.log_debug("Wrote changes to %s", filename)
        self.wrote = Prawda

    PS1 = ">>> "
    PS2 = "... "

    def refactor_docstring(self, input, filename):
        """Refactors a docstring, looking dla doctests.

        This returns a modified version of the input string.  It looks
        dla doctests, which start przy a ">>>" prompt, oraz may be
        continued przy "..." prompts, jako long jako the "..." jest indented
        the same jako the ">>>".

        (Unfortunately we can't use the doctest module's parser,
        since, like most parsers, it jest nie geared towards preserving
        the original source.)
        """
        result = []
        block = Nic
        block_lineno = Nic
        indent = Nic
        lineno = 0
        dla line w input.splitlines(keepends=Prawda):
            lineno += 1
            jeżeli line.lstrip().startswith(self.PS1):
                jeżeli block jest nie Nic:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block_lineno = lineno
                block = [line]
                i = line.find(self.PS1)
                indent = line[:i]
            albo_inaczej (indent jest nie Nic oraz
                  (line.startswith(indent + self.PS2) albo
                   line == indent + self.PS2.rstrip() + "\n")):
                block.append(line)
            inaczej:
                jeżeli block jest nie Nic:
                    result.extend(self.refactor_doctest(block, block_lineno,
                                                        indent, filename))
                block = Nic
                indent = Nic
                result.append(line)
        jeżeli block jest nie Nic:
            result.extend(self.refactor_doctest(block, block_lineno,
                                                indent, filename))
        zwróć "".join(result)

    def refactor_doctest(self, block, lineno, indent, filename):
        """Refactors one doctest.

        A doctest jest given jako a block of lines, the first of which starts
        przy ">>>" (possibly indented), dopóki the remaining lines start
        przy "..." (identically indented).

        """
        spróbuj:
            tree = self.parse_block(block, lineno, indent)
        wyjąwszy Exception jako err:
            jeżeli self.logger.isEnabledFor(logging.DEBUG):
                dla line w block:
                    self.log_debug("Source: %s", line.rstrip("\n"))
            self.log_error("Can't parse docstring w %s line %s: %s: %s",
                           filename, lineno, err.__class__.__name__, err)
            zwróć block
        jeżeli self.refactor_tree(tree, filename):
            new = str(tree).splitlines(keepends=Prawda)
            # Undo the adjustment of the line numbers w wrap_toks() below.
            clipped, new = new[:lineno-1], new[lineno-1:]
            assert clipped == ["\n"] * (lineno-1), clipped
            jeżeli nie new[-1].endswith("\n"):
                new[-1] += "\n"
            block = [indent + self.PS1 + new.pop(0)]
            jeżeli new:
                block += [indent + self.PS2 + line dla line w new]
        zwróć block

    def summarize(self):
        jeżeli self.wrote:
            were = "were"
        inaczej:
            were = "need to be"
        jeżeli nie self.files:
            self.log_message("No files %s modified.", were)
        inaczej:
            self.log_message("Files that %s modified:", were)
            dla file w self.files:
                self.log_message(file)
        jeżeli self.fixer_log:
            self.log_message("Warnings/messages dopóki refactoring:")
            dla message w self.fixer_log:
                self.log_message(message)
        jeżeli self.errors:
            jeżeli len(self.errors) == 1:
                self.log_message("There was 1 error:")
            inaczej:
                self.log_message("There were %d errors:", len(self.errors))
            dla msg, args, kwds w self.errors:
                self.log_message(msg, *args, **kwds)

    def parse_block(self, block, lineno, indent):
        """Parses a block into a tree.

        This jest necessary to get correct line number / offset information
        w the parser diagnostics oraz embedded into the parse tree.
        """
        tree = self.driver.parse_tokens(self.wrap_toks(block, lineno, indent))
        tree.future_features = frozenset()
        zwróć tree

    def wrap_toks(self, block, lineno, indent):
        """Wraps a tokenize stream to systematically modify start/end."""
        tokens = tokenize.generate_tokens(self.gen_lines(block, indent).__next__)
        dla type, value, (line0, col0), (line1, col1), line_text w tokens:
            line0 += lineno - 1
            line1 += lineno - 1
            # Don't bother updating the columns; this jest too complicated
            # since line_text would also have to be updated oraz it would
            # still przerwij dla tokens spanning lines.  Let the user guess
            # that the column numbers dla doctests are relative to the
            # end of the prompt string (PS1 albo PS2).
            uzyskaj type, value, (line0, col0), (line1, col1), line_text


    def gen_lines(self, block, indent):
        """Generates lines jako expected by tokenize z a list of lines.

        This strips the first len(indent + self.PS1) characters off each line.
        """
        prefix1 = indent + self.PS1
        prefix2 = indent + self.PS2
        prefix = prefix1
        dla line w block:
            jeżeli line.startswith(prefix):
                uzyskaj line[len(prefix):]
            albo_inaczej line == prefix.rstrip() + "\n":
                uzyskaj "\n"
            inaczej:
                podnieś AssertionError("line=%r, prefix=%r" % (line, prefix))
            prefix = prefix2
        dopóki Prawda:
            uzyskaj ""


klasa MultiprocessingUnsupported(Exception):
    dalej


klasa MultiprocessRefactoringTool(RefactoringTool):

    def __init__(self, *args, **kwargs):
        super(MultiprocessRefactoringTool, self).__init__(*args, **kwargs)
        self.queue = Nic
        self.output_lock = Nic

    def refactor(self, items, write=Nieprawda, doctests_only=Nieprawda,
                 num_processes=1):
        jeżeli num_processes == 1:
            zwróć super(MultiprocessRefactoringTool, self).refactor(
                items, write, doctests_only)
        spróbuj:
            zaimportuj multiprocessing
        wyjąwszy ImportError:
            podnieś MultiprocessingUnsupported
        jeżeli self.queue jest nie Nic:
            podnieś RuntimeError("already doing multiple processes")
        self.queue = multiprocessing.JoinableQueue()
        self.output_lock = multiprocessing.Lock()
        processes = [multiprocessing.Process(target=self._child)
                     dla i w range(num_processes)]
        spróbuj:
            dla p w processes:
                p.start()
            super(MultiprocessRefactoringTool, self).refactor(items, write,
                                                              doctests_only)
        w_końcu:
            self.queue.join()
            dla i w range(num_processes):
                self.queue.put(Nic)
            dla p w processes:
                jeżeli p.is_alive():
                    p.join()
            self.queue = Nic

    def _child(self):
        task = self.queue.get()
        dopóki task jest nie Nic:
            args, kwargs = task
            spróbuj:
                super(MultiprocessRefactoringTool, self).refactor_file(
                    *args, **kwargs)
            w_końcu:
                self.queue.task_done()
            task = self.queue.get()

    def refactor_file(self, *args, **kwargs):
        jeżeli self.queue jest nie Nic:
            self.queue.put((args, kwargs))
        inaczej:
            zwróć super(MultiprocessRefactoringTool, self).refactor_file(
                *args, **kwargs)
