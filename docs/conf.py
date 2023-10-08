import time
import quotexpy
import subprocess

latest_tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE)
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx.ext.viewcode"]
master_doc = "index"
html_theme = "furo"
project = "QuotexPy"
copyright = "2023-%s, %s" % (time.strftime("%Y"), quotexpy.__author__)
version = latest_tag.stdout.decode("utf-8")[1:]
release = latest_tag.stdout.decode("utf-8")
add_function_parentheses = True
add_module_names = False
autodoc_member_order = "bysource"
pygments_style = "sphinx"
intersphinx_mapping = {
    "python": ("http://docs.python.org/", None),
    "werkzeug": ("http://werkzeug.pocoo.org/docs/", None),
}

locale_dirs = ["_locale/"]
gettext_compact = False
