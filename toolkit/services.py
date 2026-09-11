from django.db import models, transaction

from .models import GameTable


@transaction.atomic
def save_validated(instance: models.Model):
    """Persist a domain object only after its cross-owner/domain checks pass."""

    instance.full_clean()
    instance.save()
    return instance


@transaction.atomic
def ensure_game_table(user):
    """Return the unique persistent game table for an authenticated user."""

    table, _ = GameTable.objects.get_or_create(owner=user)
    return table
