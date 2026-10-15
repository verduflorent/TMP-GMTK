import json
import math
import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Scenario, Scene, SceneBlock
from toolkit.models import Encounter


def serialize(scenario):
    scenes = list(scenario.scenes.prefetch_related("blocks").all())
    return {
        "content_revision": scenario.content_revision,
        "layout_revision": scenario.layout_revision,
        "scenes": [
            {"id": str(s.id), "title": s.title, "narrative_order": s.narrative_rank,
             "position": {"x": s.x, "y": s.y},
             "blocks": [{"id": str(b.id), "kind": b.kind, "text": b.text, "rank": b.rank,
                         "target": str(b.target_scene_id) if b.target_scene_id else None,
                         "payload": b.payload}
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
    if request.method == "POST" and request.content_type != "application/json":
        return error("Content-Type application/json requis.", 415)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return error("JSON invalide.")
    if not isinstance(data, dict) or not isinstance(data.get("scenes"), list):
        return error("Format de scénario invalide.")
    content_only = data.get("mode") == "content"
    items = data["scenes"]
    if len(items) > 500:
        return error("Limite de 500 scènes dépassée.")
    expected_content = data.get("content_revision")
    expected_layout = data.get("layout_revision")
    if (type(expected_content) is not int or type(expected_layout) is not int
            or expected_content < 0 or expected_layout < 0):
        return error("Révisions manquantes ou invalides.")
    # A first integration endpoint: full document replacement, guarded by both revisions.
    # The client always sends a complete snapshot. Never accept arbitrary owner/scenario IDs.
    try:
        ids = [str(uuid.UUID(str(item["id"]))) for item in items]
        if len(set(ids)) != len(ids):
            raise ValueError("Identifiants de scènes dupliqués.")
        parsed = []
        total_blocks = 0
        block_ids = set()
        encounter_ids = set()
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
                block_id = str(uuid.UUID(str(b.get("id") or uuid.uuid4())))
                if block_id in block_ids:
                    raise ValueError("Identifiants de rubriques dupliqués.")
                block_ids.add(block_id)
                kind = b["kind"]
                if kind not in SceneBlock.Kind.values:
                    raise ValueError("Type de rubrique inconnu.")
                text = str(b.get("text", ""))
                if len(text) > 50000:
                    raise ValueError("Rubrique trop longue.")
                target = b.get("target")
                if target is not None:
                    target = str(uuid.UUID(str(target)))
                if kind == "transition":
                    if target not in ids:
                        raise ValueError("Transition vers une scène absente.")
                elif target is not None:
                    raise ValueError("Cible interdite pour cette rubrique.")
                payload = b.get("payload") or {}
                if not isinstance(payload, dict):
                    raise ValueError("Données de rubrique invalides.")
                if kind == "encounter":
                    raw_encounter = payload.get("encounter_id")
                    if raw_encounter not in (None, ""):
                        if type(raw_encounter) is not int or raw_encounter <= 0:
                            raise ValueError("Identifiant de Rencontre invalide.")
                        encounter_ids.add(raw_encounter)
                        payload = {"encounter_id": raw_encounter}
                    else:
                        payload = {}
                else:
                    payload = {}
                parsed_blocks.append((block_id, kind, text, target, i, payload))
            parsed.append((ids[rank], title, x, y, parsed_blocks))
        if encounter_ids != set(Encounter.objects.filter(
            owner=request.user, pk__in=encounter_ids
        ).values_list("pk", flat=True)):
            raise ValueError("Rencontre introuvable ou inaccessible.")
        if total_blocks > 5000:
            raise ValueError("Limite de rubriques dépassée.")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return error(str(exc))
    with transaction.atomic():
        locked = Scenario.objects.select_for_update().get(pk=scenario.pk, owner=request.user)
        existing_ids = set(str(pk) for pk in locked.scenes.values_list("pk", flat=True))
        existing_block_owners = {str(b.pk): str(b.scene_id) for b in SceneBlock.objects.filter(scene__scenario=locked)}
        for sid, title, x, y, blocks in parsed:
            for bid, kind, text, target, rank, payload in blocks:
                if bid in existing_block_owners and existing_block_owners[bid] != sid:
                    return error("Une rubrique existante ne peut pas changer de scène.")
        supplied_existing = {bid for sid, title, x, y, blocks in parsed for bid, kind, text, target, rank, payload in blocks}
        if SceneBlock.objects.filter(pk__in=supplied_existing).exclude(scene__scenario=locked).exists():
            return error("Une rubrique appartient à un autre scénario.")
        structural = existing_ids != set(ids)
        conflict = locked.content_revision != expected_content or (structural and locked.layout_revision != expected_layout) or (not content_only and locked.layout_revision != expected_layout)
        if conflict:
            return error("Le scénario a été modifié ailleurs. Recharge la page avant de sauvegarder.", 409,
                         content_revision=locked.content_revision, layout_revision=locked.layout_revision)
        # Preserve existing scene and block primary keys. Remove only deleted
        # objects, then update/create changed records inside the same transaction.
        from uuid import UUID
        existing_scenes = {str(obj.pk): obj for obj in locked.scenes.all()}
        wanted_scene_ids = set(ids)
        # Delete removed scenes before inserting new transitions.
        for sid, obj in existing_scenes.items():
            if sid not in wanted_scene_ids:
                obj.delete()
        for rank, (sid, title, x, y, blocks) in enumerate(parsed):
            obj = existing_scenes.get(sid)
            if obj is None:
                Scene.objects.create(id=UUID(sid), scenario=locked, title=title,
                                     narrative_rank=rank, x=x, y=y)
            else:
                obj.title = title
                obj.narrative_rank = rank
                if not content_only:
                    obj.x, obj.y = x, y
                    obj.save(update_fields=["title", "narrative_rank", "x", "y", "updated_at"])
                else:
                    obj.save(update_fields=["title", "narrative_rank", "updated_at"])
        existing_blocks = {
            str(obj.pk): obj for obj in SceneBlock.objects.filter(scene__scenario=locked)
        }
        wanted_blocks = {bid for sid, title, x, y, blocks in parsed
                         for bid, kind, text, target, rank, payload in blocks}
        for bid, obj in existing_blocks.items():
            if bid not in wanted_blocks:
                obj.delete()
        # All scenes now exist, so forward transitions can be inserted safely.
        for sid, title, x, y, blocks in parsed:
            for bid, kind, text, target, rank, payload in blocks:
                obj = existing_blocks.get(bid)
                values = dict(scene_id=UUID(sid), kind=kind, text=text, payload=payload,
                              rank=rank, target_scene_id=UUID(target) if target else None)
                if obj is None:
                    SceneBlock.objects.create(id=UUID(bid), **values)
                else:
                    for field, value in values.items():
                        setattr(obj, field, value)
                    obj.save(update_fields=list(values))
        locked.content_revision = F("content_revision") + 1
        if structural or not content_only:
            locked.layout_revision = F("layout_revision") + 1
            locked.save(update_fields=["content_revision", "layout_revision", "updated_at"])
        else:
            locked.save(update_fields=["content_revision", "updated_at"])
        resulting_layout = locked.layout_revision if isinstance(locked.layout_revision, int) else expected_layout + 1
    return JsonResponse({"ok": True, "content_revision": expected_content + 1,
                         "layout_revision": resulting_layout})


@login_required
@require_http_methods(["POST"])
def save_layout(request, pk):
    """Update positions only; a concurrent narration edit is not a layout conflict."""
    get_object_or_404(Scenario.objects.filter(owner=request.user), pk=pk)
    if request.content_type != "application/json":
        return error("Content-Type application/json requis.", 415)
    try:
        data = json.loads(request.body)
        revision = data["layout_revision"]
        positions = data["positions"]
        if type(revision) is not int or revision < 0 or not isinstance(positions, list) or len(positions) > 500:
            raise ValueError("Révision ou positions invalides.")
        parsed = {}
        for item in positions:
            scene_id = uuid.UUID(str(item["id"]))
            x, y = float(item["x"]), float(item["y"])
            if not math.isfinite(x) or not math.isfinite(y) or max(abs(x), abs(y)) > 100000:
                raise ValueError("Coordonnées invalides.")
            if scene_id in parsed:
                raise ValueError("Scène dupliquée.")
            parsed[scene_id] = (x, y)
    except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as exc:
        return error(str(exc))
    with transaction.atomic():
        scenario = Scenario.objects.select_for_update().get(pk=pk, owner=request.user)
        if scenario.layout_revision != revision:
            return error("Les positions ont changé dans un autre onglet.", 409,
                         layout_revision=scenario.layout_revision)
        found = list(Scene.objects.filter(scenario=scenario, pk__in=parsed))
        if len(found) != len(parsed):
            return error("Une scène est absente de ce scénario.")
        for scene in found:
            scene.x, scene.y = parsed[scene.pk]
        Scene.objects.bulk_update(found, ["x", "y"])
        scenario.layout_revision = F("layout_revision") + 1
        scenario.save(update_fields=["layout_revision", "updated_at"])
    return JsonResponse({"ok": True, "layout_revision": revision + 1})
