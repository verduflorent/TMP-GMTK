from .settings import *  # noqa: F403,F401

# Test-only speedups. Never used by runserver/production settings.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
