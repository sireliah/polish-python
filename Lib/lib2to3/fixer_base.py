# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Base klasa dla fixers (optional, but recommended)."""

# Python imports
zaimportuj logging
zaimportuj itertools

# Local imports
z .patcomp zaimportuj PatternCompiler
z . zaimportuj pygram
z .fixer_util zaimportuj does_tree_import

klasa BaseFix(object):

    """Optional base klasa dla fixers.

    The subclass name must be FixFooBar where FooBar jest the result of
    removing underscores oraz capitalizing the words of the fix name.
    For example, the klasa name dla a fixer named 'has_key' should be
    FixHasKey.
    """

    PATTERN = Nic  # Most subclasses should override przy a string literal
    pattern = Nic  # Compiled pattern, set by compile_pattern()
    pattern_tree = Nic # Tree representation of the pattern
    options = Nic  # Options object dalejed to initializer
    filename = Nic # The filename (set by set_filename)
    numbers = itertools.count(1) # For new_name()
    used_names = set() # A set of all used NAMEs
    order = "post" # Does the fixer prefer pre- albo post-order traversal
    explicit = Nieprawda # Is this ignored by refactor.py -f all?
    run_order = 5   # Fixers will be sorted by run order before execution
                    # Lower numbers will be run first.
    _accept_type = Nic # [Advanced oraz nie public] This tells RefactoringTool
                        # which node type to accept when there's nie a pattern.

    keep_line_order = Nieprawda # For the bottom matcher: match przy the
                            # original line order
    BM_compatible = Nieprawda # Compatibility przy the bottom matching
                          # module; every fixer should set this
                          # manually

    # Shortcut dla access to Python grammar symbols
    syms = pygram.python_symbols

    def __init__(self, options, log):
        """Initializer.  Subclass may override.

        Args:
            options: an dict containing the options dalejed to RefactoringTool
            that could be used to customize the fixer through the command line.
            log: a list to append warnings oraz other messages to.
        """
        self.options = options
        self.log = log
        self.compile_pattern()

    def compile_pattern(self):
        """Compiles self.PATTERN into self.pattern.

        Subclass may override jeżeli it doesn't want to use
        self.{pattern,PATTERN} w .match().
        """
        jeżeli self.PATTERN jest nie Nic:
            PC = PatternCompiler()
            self.pattern, self.pattern_tree = PC.compile_pattern(self.PATTERN,
                                                                 with_tree=Prawda)

    def set_filename(self, filename):
        """Set the filename.

        The main refactoring tool should call this.
        """
        self.filename = filename

    def match(self, node):
        """Returns match dla a given parse tree node.

        Should zwróć a true albo false object (nie necessarily a bool).
        It may zwróć a non-empty dict of matching sub-nodes as
        returned by a matching pattern.

        Subclass may override.
        """
        results = {"node": node}
        zwróć self.pattern.match(node, results) oraz results

    def transform(self, node, results):
        """Returns the transformation dla a given parse tree node.

        Args:
          node: the root of the parse tree that matched the fixer.
          results: a dict mapping symbolic names to part of the match.

        Returns:
          Nic, albo a node that jest a modified copy of the
          argument node.  The node argument may also be modified in-place to
          effect the same change.

        Subclass *must* override.
        """
        podnieś NotImplementedError()

    def new_name(self, template="xxx_todo_changeme"):
        """Return a string suitable dla use jako an identifier

        The new name jest guaranteed nie to conflict przy other identifiers.
        """
        name = template
        dopóki name w self.used_names:
            name = template + str(next(self.numbers))
        self.used_names.add(name)
        zwróć name

    def log_message(self, message):
        jeżeli self.first_log:
            self.first_log = Nieprawda
            self.log.append("### In file %s ###" % self.filename)
        self.log.append(message)

    def cannot_convert(self, node, reason=Nic):
        """Warn the user that a given chunk of code jest nie valid Python 3,
        but that it cannot be converted automatically.

        First argument jest the top-level node dla the code w question.
        Optional second argument jest why it can't be converted.
        """
        lineno = node.get_lineno()
        for_output = node.clone()
        for_output.prefix = ""
        msg = "Line %d: could nie convert: %s"
        self.log_message(msg % (lineno, for_output))
        jeżeli reason:
            self.log_message(reason)

    def warning(self, node, reason):
        """Used dla warning the user about possible uncertainty w the
        translation.

        First argument jest the top-level node dla the code w question.
        Optional second argument jest why it can't be converted.
        """
        lineno = node.get_lineno()
        self.log_message("Line %d: %s" % (lineno, reason))

    def start_tree(self, tree, filename):
        """Some fixers need to maintain tree-wide state.
        This method jest called once, at the start of tree fix-up.

        tree - the root node of the tree to be processed.
        filename - the name of the file the tree came from.
        """
        self.used_names = tree.used_names
        self.set_filename(filename)
        self.numbers = itertools.count(1)
        self.first_log = Prawda

    def finish_tree(self, tree, filename):
        """Some fixers need to maintain tree-wide state.
        This method jest called once, at the conclusion of tree fix-up.

        tree - the root node of the tree to be processed.
        filename - the name of the file the tree came from.
        """
        dalej


klasa ConditionalFix(BaseFix):
    """ Base klasa dla fixers which nie execute jeżeli an zaimportuj jest found. """

    # This jest the name of the zaimportuj which, jeżeli found, will cause the test to be skipped
    skip_on = Nic

    def start_tree(self, *args):
        super(ConditionalFix, self).start_tree(*args)
        self._should_skip = Nic

    def should_skip(self, node):
        jeżeli self._should_skip jest nie Nic:
            zwróć self._should_skip
        pkg = self.skip_on.split(".")
        name = pkg[-1]
        pkg = ".".join(pkg[:-1])
        self._should_skip = does_tree_import(pkg, name, node)
        zwróć self._should_skip
