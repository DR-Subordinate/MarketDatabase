import os

from .settings import *

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = ["marketdb.across-shop.com"]

# Override to use absolute URL that bypasses CGI
STATIC_URL = 'https://marketdb.across-shop.com/static/'

STATIC_ROOT = BASE_DIR / "static"

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True
