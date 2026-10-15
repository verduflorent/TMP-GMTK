"""Read-only, consistent export of a single privately owned scenario."""
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from .archive.codec import ArchiveError, encode_archive
from .models import Scenario


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
