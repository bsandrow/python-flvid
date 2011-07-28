'''

flvid.scrapers is the namespace for all video scrapers that can plugin to
flvid.

'''

# Extend the flvid.scrapers namespace to encompase more than just this specific
# directory.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
