import os

from .settings import *

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = ["test-marketdb.across-shop.com"]

STATIC_ROOT = BASE_DIR / "staticfiles"
