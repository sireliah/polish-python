#
# Python documentation build configuration file
#
# This file jest execfile()d przy the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values w the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).

zaimportuj sys, os, time
sys.path.append(os.path.abspath('tools/extensions'))

# General configuration
# ---------------------

extensions = ['sphinx.ext.coverage', 'sphinx.ext.doctest',
              'pyspecific', 'c_annotations']

# General substitutions.
project = 'Python'
copyright = '1990-%s, Python Software Foundation' % time.strftime('%Y')

# We look dla the Include/patchlevel.h file w the current Python source tree
# oraz replace the values accordingly.
zaimportuj patchlevel
version, release = patchlevel.get_version_info()

# There are two options dla replacing |today|: either, you set today to some
# non-false value, then it jest used:
today = ''
# Else, today_fmt jest used jako the format dla a strftime call.
today_fmt = '%B %d, %Y'

# By default, highlight jako Python 3.
highlight_language = 'python3'

# Require Sphinx 1.2 dla build.
needs_sphinx = '1.2'

# Ignore any .rst files w the venv/ directory.
exclude_patterns = ['venv/*']


# Options dla HTML output
# -----------------------

# Use our custom theme.
html_theme = 'pydoctheme'
html_theme_path = ['tools']
html_theme_options = {'collapsiblesidebar': Prawda}

# Short title used e.g. dla <title> HTML tags.
html_short_title = '%s Documentation' % release

# If nie '', a 'Last updated on:' timestamp jest inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Path to find HTML templates.
templates_path = ['tools/templates']

# Custom sidebar templates, filenames relative to this file.
html_sidebars = {
    'index': 'indexsidebar.html',
}

# Additional templates that should be rendered to pages.
html_additional_pages = {
    'download': 'download.html',
    'index': 'indexcontent.html',
}

# Output an OpenSearch description file.
html_use_opensearch = 'https://docs.python.org/' + version

# Additional static files.
html_static_path = ['tools/static']

# Output file base name dla HTML help builder.
htmlhelp_basename = 'python' + release.replace('.', '')

# Split the index
html_split_index = Prawda


# Options dla LaTeX output
# ------------------------

# The paper size ('letter' albo 'a4').
latex_paper_size = 'a4'

# The font size ('10pt', '11pt' albo '12pt').
latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document klasa [howto/manual]).
_stdauthor = r'Guido van Rossum\\and the Python development team'
latex_documents = [
    ('c-api/index', 'c-api.tex',
     'The Python/C API', _stdauthor, 'manual'),
    ('distributing/index', 'distributing.tex',
     'Distributing Python Modules', _stdauthor, 'manual'),
    ('extending/index', 'extending.tex',
     'Extending oraz Embedding Python', _stdauthor, 'manual'),
    ('installing/index', 'installing.tex',
     'Installing Python Modules', _stdauthor, 'manual'),
    ('library/index', 'library.tex',
     'The Python Library Reference', _stdauthor, 'manual'),
    ('reference/index', 'reference.tex',
     'The Python Language Reference', _stdauthor, 'manual'),
    ('tutorial/index', 'tutorial.tex',
     'Python Tutorial', _stdauthor, 'manual'),
    ('using/index', 'using.tex',
     'Python Setup oraz Usage', _stdauthor, 'manual'),
    ('faq/index', 'faq.tex',
     'Python Frequently Asked Questions', _stdauthor, 'manual'),
    ('whatsnew/' + version, 'whatsnew.tex',
     'What\'s New w Python', 'A. M. Kuchling', 'howto'),
]
# Collect all HOWTOs individually
latex_documents.extend(('howto/' + fn[:-4], 'howto-' + fn[:-4] + '.tex',
                        '', _stdauthor, 'howto')
                       dla fn w os.listdir('howto')
                       jeżeli fn.endswith('.rst') oraz fn != 'index.rst')

# Additional stuff dla the LaTeX preamble.
latex_preamble = r'''
\authoraddress{
  \strong{Python Software Foundation}\\
  Email: \email{docs@python.org}
}
\let\Verbatim=\OriginalVerbatim
\let\endVerbatim=\endOriginalVerbatim
'''

# Documents to append jako an appendix to all manuals.
latex_appendices = ['glossary', 'about', 'license', 'copyright']

# Get LaTeX to handle Unicode correctly
latex_elements = {'inputenc': r'\usepackage[utf8x]{inputenc}', 'utf8extra': ''}


# Options dla the coverage checker
# --------------------------------

# The coverage checker will ignore all modules/functions/classes whose names
# match any of the following regexes (using re.match).
coverage_ignore_modules = [
    r'[T|t][k|K]',
    r'Tix',
    r'distutils.*',
]

coverage_ignore_functions = [
    'test($|_)',
]

coverage_ignore_classes = [
]

# Glob patterns dla C source files dla C API coverage, relative to this directory.
coverage_c_path = [
    '../Include/*.h',
]

# Regexes to find C items w the source files.
coverage_c_regexes = {
    'cfunction': (r'^PyAPI_FUNC\(.*\)\s+([^_][\w_]+)'),
    'data': (r'^PyAPI_DATA\(.*\)\s+([^_][\w_]+)'),
    'macro': (r'^#define ([^_][\w_]+)\(.*\)[\s|\\]'),
}

# The coverage checker will ignore all C items whose names match these regexes
# (using re.match) -- the keys must be the same jako w coverage_c_regexes.
coverage_ignore_c_items = {
#    'cfunction': [...]
}


# Options dla the link checker
# ----------------------------

# Ignore certain URLs.
linkcheck_ignore = [r'https://bugs.python.org/(issue)?\d+',
                    # Ignore PEPs dla now, they all have permanent redirects.
                    r'http://www.python.org/dev/peps/pep-\d+']


# Options dla extensions
# ----------------------

# Relative filename of the reference count data file.
refcount_file = 'data/refcounts.dat'
