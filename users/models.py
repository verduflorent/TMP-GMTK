from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Private TMP-GMTK account. No public-signup fields are required in V1."""

    pass
