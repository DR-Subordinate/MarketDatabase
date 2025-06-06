import os

from .settings import *

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = ["test-marketdb.across-shop.com"]

# Override to use absolute URL that bypasses CGI
STATIC_URL = 'https://test-marketdb.across-shop.com/static/'

STATIC_ROOT = BASE_DIR / "staticfiles"
