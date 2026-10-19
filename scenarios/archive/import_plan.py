"""Pure import planning: remap portable identities without database writes."""
import uuid
from .codec import validate_document

def plan_import(manifest, document):
    validate_document(document)
    scene_ids = {s["id"]: str(uuid.uuid4()) for s in document["scenes"]}
    block_ids = {b["id"]: str(uuid.uuid4()) for b in document["blocks"]}
    encounter_names = {r["key"]: r["name"] for r in document["resources"]["encounters"]}
    scenes = [
        dict(id=scene_ids[s["id"]], source_id=s["id"], title=s["title"],
             narrative_order=s["narrative_order"], position=dict(s["position"]))
        for s in document["scenes"]
    ]
    blocks = []
    unresolved = []
    for b in document["blocks"]:
        payload = dict(b["payload"])
        if b["kind"] == "encounter":
            key = payload.get("resource_key")
            if key:
                unresolved.append(dict(block_id=block_ids[b["id"]],
                                       resource_key=key,
                                       name=encounter_names.get(key, "Rencontre indisponible")))
            payload = {}
        else:
            payload.pop("encounter_id", None)
        item = dict(id=block_ids[b["id"]], scene_id=scene_ids[b["scene_id"]],
                    kind=b["kind"], rank=b["rank"], text=b["text"], payload=payload)
        if b["kind"] == "transition":
            item["target_scene_id"] = scene_ids[b["target_scene_id"]]
        blocks.append(item)
    return dict(title=document["metadata"]["title"], summary=document["metadata"]["summary"],
                document_id=manifest["document_id"], export_id=manifest["export_id"],
                scenes=scenes, blocks=blocks, unresolved_encounters=unresolved,
                warnings=["Aucune écriture effectuée.",
                          "Les Rencontres devront être réassociées manuellement.",
                          "Les médias externes ne sont pas embarqués."])
