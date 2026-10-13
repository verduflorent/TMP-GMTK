import json
import math

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Scenario, Scene, SceneBlock


def serialize(scenario):
    scenes = list(scenario.scenes.prefetch_related("blocks").all())
    return {
        "content_revision": scenario.content_revision,
        "layout_revision": scenario.layout_revision,
        "scenes": [
            {"id": str(s.id), "title": s.title, "narrative_order": s.narrative_rank,
             "position": {"x": s.x, "y": s.y},
             "blocks": [{"id": str(b.id), "kind": b.kind, "text": b.text, "rank": b.rank,
                         "target": str(b.target_scene_id) if b.target_scene_id else None}
                        for b in s.blocks.all()]}
            for s in scenes
        ],
    }


def error(message, status=400, **extra):
    return JsonResponse({"error": message, **extra}, status=status)


@login_required
@require_http_methods(["GET", "POST"])
def document(request, pk):
    scenario = get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    if request.method == "GET":
        return JsonResponse(serialize(scenario))
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return error("JSON invalide.")
    if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
        return error("Format de scénario invalide.")
    items = data["scenes"]
    if len(items) > 500:
        return error("Limite de 500 scènes dépassée.")
    try:
        expected_content = int(data["content_revision"])
        expected_layout = int(data["layout_revision"])
    except (KeyError, TypeError, ValueError):
        return error("Révisions manquantes ou invalides.")
    # A first integration endpoint: full document replacement, guarded by both revisions.
    # The client always sends a complete snapshot. Never accept arbitrary owner/scenario IDs.
    try:
        ids = [str(s["id"]) for s in items]
        if len(set(ids)) != len(ids):
            raise ValueError("Identifiants de scènes dupliqués.")
        import uuid
        ids = [str(uuid.UUID(v)) for v in ids]
        parsed = []
        total_blocks = 0
        for rank, raw in enumerate(items):
            title = str(raw["title"]).strip()
            if not title or len(title) > 120:
                raise ValueError("Titre de scène invalide.")
            pos = raw["position"]
            x, y = float(pos["x"]), float(pos["y"])
            if not all(math.isfinite(v) and abs(v) <= 100000 for v in (x, y)):
                raise ValueError("Coordonnées invalides.")
            blocks = raw.get("blocks", [])
            if not isinstance(blocks, list):
                raise ValueError("Rubriques invalides.")
            total_blocks += len(blocks)
            parsed_blocks = []
            for i, b in enumerate(blocks):
                kind = b["kind"]
                if kind not in SceneBlock.Kind.values:
                    raise ValueError("Type de rubrique inconnu.")
                text = str(b.get("text", ""))
                if len(text) > 50000:
                    raise ValueError("Rubrique trop longue.")
                target = b.get("target")
                if kind == "transition":
                    if target not in ids:
                        raise ValueError("Transition vers une scène absente.")
                elif target is not None:
                    raise ValueError("Cible interdite pour cette rubrique.")
                parsed_blocks.append((kind, text, target, i))
            parsed.append((ids[rank], title, x, y, parsed_blocks))
        if total_blocks > 5000:
            raise ValueError("Limite de rubriques dépassée.")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return error(str(exc))
    with transaction.atomic():
        locked = Scenario.objects.select_for_update().get(pk=scenario.pk, owner=request.user)
        if (locked.content_revision, locked.layout_revision) != (expected_content, expected_layout):
            return error("Le scénario a été modifié ailleurs. Recharge la page avant de sauvegarder.", 409,
                         content_revision=locked.content_revision, layout_revision=locked.layout_revision)
        # Replacement is atomic: no partial graph if validation fails.
        locked.scenes.all().delete()
        from uuid import UUID
        Scene.objects.bulk_create([
            Scene(id=UUID(sid), scenario=locked, title=title, narrative_rank=i, x=x, y=y)
            for i, (sid, title, x, y, blocks) in enumerate(parsed)
        ])
        from uuid import uuid4
        SceneBlock.objects.bulk_create([
            SceneBlock(id=uuid4(), scene_id=UUID(sid), kind=kind, text=text, rank=rank,
                       target_scene_id=UUID(target) if target else None)
            for sid, title, x, y, blocks in parsed
            for kind, text, target, rank in blocks
        ])
        locked.content_revision = F("content_revision") + 1
        locked.layout_revision = F("layout_revision") + 1
        locked.save(update_fields=["content_revision", "layout_revision", "updated_at"])
    return JsonResponse({"ok": True, "content_revision": expected_content + 1,
                         "layout_revision": expected_layout + 1})
