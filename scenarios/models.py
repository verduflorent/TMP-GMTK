import math
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Scenario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_id = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scenarios")
    folder = models.ForeignKey("toolkit.UserFolder", on_delete=models.SET_NULL, null=True, blank=True, related_name="scenarios")
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)
    content_revision = models.PositiveIntegerField(default=0)
    layout_revision = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.folder_id and self.folder.owner_id != self.owner_id:
            raise ValidationError({"folder": "Le dossier doit appartenir au propriétaire du scénario."})

    def __str__(self):
        return self.title


class Scene(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="scenes")
    title = models.CharField(max_length=120)
    narrative_rank = models.PositiveIntegerField(default=0)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["narrative_rank", "id"]
        indexes = [models.Index(fields=["scenario", "narrative_rank"])]

    def clean(self):
        super().clean()
        if any(not math.isfinite(value) or abs(value) > 100000 for value in (self.x, self.y)):
            raise ValidationError("Les coordonnées doivent être finies et comprises entre -100000 et 100000.")

    def __str__(self):
        return self.title


class SceneBlock(models.Model):
    class Kind(models.TextChoices):
        NARRATION = "narration", "Narration"
        INTERPRETATION = "interpretation", "Interprétation"
        SPLASH = "splash", "Splash"
        GM_NOTE = "gm_note", "Note MJ"
        TRANSITION = "transition", "Transition"
        ENCOUNTER = "encounter", "Rencontre"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name="blocks")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    rank = models.PositiveIntegerField(default=0)
    text = models.TextField(blank=True)
    payload = models.JSONField(default=dict, blank=True)
    target_scene = models.ForeignKey(
        Scene, on_delete=models.CASCADE, null=True, blank=True, related_name="incoming_transitions"
    )

    class Meta:
        ordering = ["rank", "id"]
        indexes = [models.Index(fields=["scene", "rank"])]
        constraints = [
            models.CheckConstraint(
                condition=(Q(kind="transition", target_scene__isnull=False) | ~Q(kind="transition", target_scene__isnull=False)),
                name="scene_block_transition_target",
            )
        ]

    def clean(self):
        super().clean()
        if self.kind == self.Kind.TRANSITION:
            if not self.target_scene_id:
                raise ValidationError({"target_scene": "Une transition doit cibler une scène."})
            if self.scene_id and self.target_scene.scenario_id != self.scene.scenario_id:
                raise ValidationError({"target_scene": "La cible doit appartenir au même scénario."})
        elif self.target_scene_id:
            raise ValidationError({"target_scene": "Seule une transition peut avoir une cible."})
        if not isinstance(self.payload, dict):
            raise ValidationError({"payload": "Le contenu structuré doit être un objet JSON."})

    def __str__(self):
        return f"{self.get_kind_display()} — {self.scene.title}"
