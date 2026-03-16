import gettext
import locale
import os

DOMAIN = "sleepcoach"
LOCALEDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

gettext.bindtextdomain(DOMAIN, LOCALEDIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext
