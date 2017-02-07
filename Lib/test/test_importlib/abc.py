zaimportuj abc
zaimportuj unittest


klasa FinderTests(metaclass=abc.ABCMeta):

    """Basic tests dla a finder to dalej."""

    @abc.abstractmethod
    def test_module(self):
        # Test importing a top-level module.
        dalej

    @abc.abstractmethod
    def test_package(self):
        # Test importing a package.
        dalej

    @abc.abstractmethod
    def test_module_in_package(self):
        # Test importing a module contained within a package.
        # A value dla 'path' should be used jeżeli dla a meta_path finder.
        dalej

    @abc.abstractmethod
    def test_package_in_package(self):
        # Test importing a subpackage.
        # A value dla 'path' should be used jeżeli dla a meta_path finder.
        dalej

    @abc.abstractmethod
    def test_package_over_module(self):
        # Test that packages are chosen over modules.
        dalej

    @abc.abstractmethod
    def test_failure(self):
        # Test trying to find a module that cannot be handled.
        dalej


klasa LoaderTests(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def test_module(self):
        """A module should load without issue.

        After the loader returns the module should be w sys.modules.

        Attributes to verify:

            * __file__
            * __loader__
            * __name__
            * No __path__

        """
        dalej

    @abc.abstractmethod
    def test_package(self):
        """Loading a package should work.

        After the loader returns the module should be w sys.modules.

        Attributes to verify:

            * __name__
            * __file__
            * __package__
            * __path__
            * __loader__

        """
        dalej

    @abc.abstractmethod
    def test_lacking_parent(self):
        """A loader should nie be dependent on it's parent package being
        imported."""
        dalej

    @abc.abstractmethod
    def test_state_after_failure(self):
        """If a module jest already w sys.modules oraz a reload fails
        (e.g. a SyntaxError), the module should be w the state it was before
        the reload began."""
        dalej

    @abc.abstractmethod
    def test_unloadable(self):
        """Test ImportError jest podnieśd when the loader jest asked to load a module
        it can't."""
        dalej
