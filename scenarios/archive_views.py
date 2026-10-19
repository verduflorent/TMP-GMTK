import hashlib
"""Read-only, consistent export of a single privately owned scenario."""
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .archive.codec import ArchiveError, encode_archive, decode_archive, MAX_ARCHIVE
from .models import Scenario, Scene, SceneBlock, ScenarioImportReceipt
from .archive.import_plan import plan_import
import uuid


def portable_document(scenario, scenes):
    blocks = []
    resources = {"media": [], "encounters": []}
    encounter_keys = set()
    for scene in scenes:
        for block in scene.blocks.all():
            payload = {"version": 1}
            if block.kind == "encounter":
                encounter_id = block.payload.get("encounter_id")
                if encounter_id is not None:
                    # No local database PK is allowed in a portable archive.
                    from toolkit.models import Encounter
                    encounter = Encounter.objects.filter(owner=scenario.owner, pk=encounter_id).first()
                    if encounter:
                        key = "encounter-" + str(encounter.pk)
                        payload["resource_key"] = key
                        if key not in encounter_keys:
                            encounter_keys.add(key)
                            resources["encounters"].append(
                                {"key": key, "name": encounter.name, "status": "unresolved"}
                            )
                    else:
                        # Preserve the block and its text even if the source disappeared.
                        payload["unresolved"] = True
            elif block.kind == "splash":
                # Current UI stores an optional external HTTPS URL in text.
                # Preserve it as narrative text, without fetching external resources.
                pass
            item = {
                "id": str(block.pk), "scene_id": str(scene.pk),
                "kind": block.kind, "rank": block.rank,
                "text": block.text, "payload": payload,
            }
            if block.kind == "transition":
                item["target_scene_id"] = str(block.target_scene_id)
            blocks.append(item)
    return {
        "schema_version": "1.0",
        "metadata": {"title": scenario.title, "summary": scenario.summary},
        "scenes": [
            {"id": str(scene.pk), "title": scene.title,
             "narrative_order": scene.narrative_rank,
             "position": {"x": scene.x, "y": scene.y}}
            for scene in scenes
        ],
        "blocks": blocks,
        "resources": resources,
    }


@login_required
@require_GET
def export_scenario(request, pk):
    # The lock gives a coherent snapshot with the mutation endpoints on PostgreSQL.
    # ZIP compression takes place outside the transaction.
    with transaction.atomic():
        scenario = get_object_or_404(
            Scenario.objects.select_for_update().filter(owner=request.user), pk=pk
        )
        scenes = list(scenario.scenes.prefetch_related("blocks").order_by("narrative_rank", "id"))
        document = portable_document(scenario, scenes)
        document_id = str(scenario.document_id)
        content_revision = scenario.content_revision
        layout_revision = scenario.layout_revision
    try:
        archive = encode_archive(
            document, document_id=document_id,
            content_revision=content_revision, layout_revision=layout_revision,
        )
    except (ArchiveError, ValueError) as exc:
        return HttpResponse("Export impossible : " + str(exc), status=422, content_type="text/plain; charset=utf-8")
    response = HttpResponse(archive, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="scenario-' + str(pk) + '.tmps"'
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


@login_required
@require_POST
def verify_archive(request):
    """Validate a user-selected TMPS file without creating any database records."""
    uploaded = request.FILES.get("archive")
    if uploaded is None:
        return JsonResponse({"ok": False, "error": "Choisis un fichier .tmps."}, status=400)
    if not uploaded.name.lower().endswith(".tmps"):
        return JsonResponse({"ok": False, "error": "Extension .tmps attendue."}, status=400)
    if uploaded.size > MAX_ARCHIVE:
        return JsonResponse({"ok": False, "error": "Archive supérieure à 10 Mio."}, status=400)
    try:
        content = uploaded.read(MAX_ARCHIVE + 1)
        manifest, document = decode_archive(content)
    except (ArchiveError, ValueError, OSError) as exc:
        return JsonResponse({"ok": False, "error": "Archive invalide : " + str(exc)}, status=400)
    return JsonResponse({
        "ok": True,
        "title": document["metadata"]["title"],
        "summary": document["metadata"]["summary"],
        "scenes": len(document["scenes"]),
        "blocks": len(document["blocks"]),
        "transitions": sum(b["kind"] == "transition" for b in document["blocks"]),
        "encounters": len(document["resources"]["encounters"]),
        "media": len(document["resources"]["media"]),
        "format_version": manifest["format_version"],
        "document_id": manifest["document_id"],
        "export_id": manifest["export_id"],
        "content_revision": manifest["content_revision"],
        "layout_revision": manifest["layout_revision"],
        "warning": "Vérification uniquement : aucune donnée importée. Les Rencontres et médias externes ne sont pas embarqués.",
    })


@login_required
@require_POST
def import_archive(request):
    """Import a validated TMPS archive as a new, private scenario atomically."""
    uploaded = request.FILES.get("archive")
    if uploaded is None or not uploaded.name.lower().endswith(".tmps"):
        return JsonResponse({"ok": False, "error": "Sélectionne une archive .tmps."}, status=400)
    if uploaded.size > MAX_ARCHIVE:
        return JsonResponse({"ok": False, "error": "Archive trop volumineuse."}, status=400)
    try:
        key = uuid.UUID(request.POST["import_key"])
    except (KeyError, ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "Clé d'import invalide."}, status=400)
    content = uploaded.read(MAX_ARCHIVE + 1)
    fingerprint = hashlib.sha256(content).hexdigest()
    try:
        manifest, document = decode_archive(content)
        plan = plan_import(manifest, document)
    except (ArchiveError, ValueError, OSError, KeyError, TypeError) as exc:
        return JsonResponse({"ok": False, "error": "Archive invalide : " + str(exc)}, status=400)
    try:
        with transaction.atomic():
            receipt, created = ScenarioImportReceipt.objects.get_or_create(
                owner=request.user, key=key, defaults={"fingerprint": fingerprint}
            )
            receipt = ScenarioImportReceipt.objects.select_for_update().get(pk=receipt.pk)
            if receipt.fingerprint != fingerprint:
                return JsonResponse({"ok": False, "error": "Clé déjà utilisée pour une autre archive."}, status=409)
            if not created:
                if not receipt.scenario_id:
                    return JsonResponse({"ok": False, "error": "Copie déjà importée puis supprimée."}, status=409)
                return JsonResponse({"ok": True, "replayed": True,
                    "scenario_id": str(receipt.scenario_id),
                    "url": "/scenarios/" + str(receipt.scenario_id) + "/",
                    "scenes": len(plan["scenes"]), "blocks": len(plan["blocks"]),
                    "unresolved_encounters": plan["unresolved_encounters"],
                    "warning": "Import déjà traité : aucune copie supplémentaire."})
            scenario = Scenario.objects.create(
                owner=request.user, title=plan["title"], summary=plan["summary"],
                # A restored copy gets its own portable document identity.
                document_id=uuid.uuid4(),
            )
            for item in plan["scenes"]:
                Scene.objects.create(
                    id=uuid.UUID(item["id"]), scenario=scenario, title=item["title"],
                    narrative_rank=item["narrative_order"],
                    x=item["position"]["x"], y=item["position"]["y"],
                )
            for item in plan["blocks"]:
                SceneBlock.objects.create(
                    id=uuid.UUID(item["id"]), scene_id=uuid.UUID(item["scene_id"]),
                    kind=item["kind"], rank=item["rank"], text=item["text"],
                    payload=item["payload"],
                    target_scene_id=uuid.UUID(item["target_scene_id"]) if "target_scene_id" in item else None,
                )
            receipt.scenario = scenario
            receipt.save(update_fields=["scenario"])
    except Exception:
        # Never leave a partially restored graph behind.
        return JsonResponse({"ok": False, "error": "L'import a échoué : aucune copie n'a été conservée."}, status=422)
    return JsonResponse({
        "ok": True, "scenario_id": str(scenario.pk),
        "url": request.build_absolute_uri("/scenarios/" + str(scenario.pk) + "/"),
        "scenes": len(plan["scenes"]), "blocks": len(plan["blocks"]),
        "unresolved_encounters": plan["unresolved_encounters"],
        "warning": "Copie importée. Les Rencontres doivent être réassociées manuellement.",
    }, status=201)
