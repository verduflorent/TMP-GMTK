"""Pure, offline TMP Stories v1 codec. No database writes or ZIP extraction."""
import hashlib
import io
import json
import math
import re
import uuid
import zipfile
from datetime import datetime, timezone

MAX_ARCHIVE = 10 * 1024 * 1024
MAX_UNCOMPRESSED = 20 * 1024 * 1024
MAX_JSON_DEPTH = 40
MEMBERS = {"manifest.json", "scenario.json"}
KINDS = {"narration", "interpretation", "gm_note", "splash", "transition", "encounter"}
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class ArchiveError(ValueError):
    pass


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ArchiveError("Clé JSON dupliquée.")
        result[key] = value
    return result


def _reject_constant(value):
    raise ArchiveError("Valeur numérique JSON non finie : " + value)


def _json_load(data):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=_reject_constant)
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise ArchiveError("JSON invalide.") from exc


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _uuid(value):
    if not isinstance(value, str) or not UUID_RE.fullmatch(value):
        raise ArchiveError("UUID non canonique.")
    try:
        uuid.UUID(value)
    except ValueError as exc:
        raise ArchiveError("UUID invalide.") from exc
    return value


def _integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ArchiveError("Entier invalide.")
    return value


def _keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= value.keys() or not value.keys() <= set(required) | set(optional):
        raise ArchiveError("Champs absents ou inconnus.")


def _check_depth(value, depth=0):
    if depth > MAX_JSON_DEPTH:
        raise ArchiveError("Profondeur JSON excessive.")
    if isinstance(value, dict):
        for child in value.values():
            _check_depth(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _check_depth(child, depth + 1)


def validate_document(doc):
    _check_depth(doc)
    _keys(doc, {"schema_version", "metadata", "scenes", "blocks", "resources"})
    if doc["schema_version"] != "1.0":
        raise ArchiveError("Version narrative inconnue.")
    _keys(doc["metadata"], {"title", "summary"})
    title = doc["metadata"]["title"]
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
        raise ArchiveError("Titre invalide.")
    if not isinstance(doc["metadata"]["summary"], str) or len(doc["metadata"]["summary"]) > 50000:
        raise ArchiveError("Résumé invalide.")
    scenes, blocks = doc["scenes"], doc["blocks"]
    if not isinstance(scenes, list) or len(scenes) > 500 or not isinstance(blocks, list) or len(blocks) > 5000:
        raise ArchiveError("Taille du scénario dépassée.")
    scene_ids, block_ids = set(), set()
    for scene in scenes:
        _keys(scene, {"id", "title", "narrative_order", "position"})
        sid = _uuid(scene["id"])
        if sid in scene_ids:
            raise ArchiveError("Scène dupliquée.")
        scene_ids.add(sid)
        if not isinstance(scene["title"], str) or not 1 <= len(scene["title"].strip()) <= 120:
            raise ArchiveError("Titre de scène invalide.")
        _integer(scene["narrative_order"])
        _keys(scene["position"], {"x", "y"})
        for n in (scene["position"]["x"], scene["position"]["y"]):
            if type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 100000:
                raise ArchiveError("Coordonnées invalides.")
    transition_count = 0
    encounter_refs = []
    for block in blocks:
        _keys(block, {"id", "scene_id", "kind", "rank", "text", "payload"}, {"target_scene_id"})
        bid = _uuid(block["id"])
        if bid in block_ids:
            raise ArchiveError("Rubrique dupliquée.")
        block_ids.add(bid)
        if _uuid(block["scene_id"]) not in scene_ids:
            raise ArchiveError("Scène source absente.")
        if block["kind"] not in KINDS:
            raise ArchiveError("Type de rubrique inconnu.")
        _integer(block["rank"])
        if not isinstance(block["text"], str) or len(block["text"]) > 50000:
            raise ArchiveError("Texte invalide.")
        payload = block["payload"]
        if not isinstance(payload, dict) or type(payload.get("version")) is not int or payload["version"] != 1:
            raise ArchiveError("Payload invalide.")
        allowed = {"version"}
        if block["kind"] == "encounter":
            allowed |= {"resource_key", "unresolved"}
            if "resource_key" in payload:
                if not isinstance(payload["resource_key"], str):
                    raise ArchiveError("Référence de Rencontre invalide.")
                encounter_refs.append(payload["resource_key"])
        elif block["kind"] == "splash":
            allowed |= {"external_url", "alt_text"}
        if not payload.keys() <= allowed:
            raise ArchiveError("Champs de rubrique inconnus.")
        if "external_url" in payload:
            from urllib.parse import urlsplit
            url = payload["external_url"]
            if not isinstance(url, str) or len(url) > 2048:
                raise ArchiveError("URL invalide.")
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise ArchiveError("URL HTTPS invalide.")
        if block["kind"] == "transition":
            transition_count += 1
            if _uuid(block.get("target_scene_id")) not in scene_ids:
                raise ArchiveError("Cible de transition absente.")
        elif "target_scene_id" in block:
            raise ArchiveError("Cible interdite hors transition.")
    if transition_count > 2000:
        raise ArchiveError("Trop de transitions.")
    _keys(doc["resources"], {"media", "encounters"})
    for name in ("media", "encounters"):
        if not isinstance(doc["resources"][name], list) or len(doc["resources"][name]) > 5000:
            raise ArchiveError("Ressources invalides.")
    keys = set()
    for resource in doc["resources"]["encounters"]:
        _keys(resource, {"key", "name", "status"})
        key = resource["key"]
        if (not isinstance(key, str) or not 1 <= len(key) <= 128
                or key in keys or resource["status"] != "unresolved"
                or not isinstance(resource["name"], str)):
            raise ArchiveError("Descripteur de Rencontre invalide.")
        keys.add(key)
    if any(key not in keys for key in encounter_refs):
        raise ArchiveError("Rencontre référencée absente.")
    return doc


def _manifest(document_id, export_id, created_at, content_revision, layout_revision, data):
    return {
        "format": "tmps", "format_version": "1.0", "profile": "narrative-v1",
        "document_id": _uuid(document_id), "export_id": _uuid(export_id),
        "created_at": created_at, "required_features": [],
        "content_revision": _integer(content_revision),
        "layout_revision": _integer(layout_revision),
        "files": [{"path": "scenario.json", "size": len(data),
                   "sha256": hashlib.sha256(data).hexdigest()}],
    }


def encode_archive(document, *, document_id, content_revision=0, layout_revision=0,
                   export_id=None, created_at=None):
    validate_document(document)
    data = _json_bytes(document)
    stamp = created_at or datetime.now(timezone.utc).isoformat()
    manifest = _manifest(document_id, export_id or str(uuid.uuid4()), stamp,
                         content_revision, layout_revision, data)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", _json_bytes(manifest))
        archive.writestr("scenario.json", data)
    result = output.getvalue()
    if len(result) > MAX_ARCHIVE:
        raise ArchiveError("Archive trop volumineuse.")
    return result


def decode_archive(data):
    if not isinstance(data, bytes) or len(data) > MAX_ARCHIVE:
        raise ArchiveError("Archive absente ou trop volumineuse.")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) != 2 or {e.filename for e in entries} != MEMBERS:
                raise ArchiveError("Membres ZIP non autorisés.")
            for entry in entries:
                if (entry.flag_bits & 1 or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                        or entry.is_dir() or (entry.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ArchiveError("Entrée ZIP interdite.")
            if sum(e.file_size for e in entries) > MAX_UNCOMPRESSED:
                raise ArchiveError("Décompression trop volumineuse.")
            total_read = 0
            def read(name):
                nonlocal total_read
                with archive.open(name) as stream:
                    content = stream.read(MAX_UNCOMPRESSED + 1)
                    total_read += len(content)
                    if total_read > MAX_UNCOMPRESSED:
                        raise ArchiveError("Décompression trop volumineuse.")
                    return content
            manifest = _json_load(read("manifest.json"))
            payload = read("scenario.json")
    except (zipfile.BadZipFile, RuntimeError, EOFError, OSError) as exc:
        raise ArchiveError("Archive ZIP invalide.") from exc
    _keys(manifest, {"format", "format_version", "profile", "document_id", "export_id",
                     "created_at", "required_features", "content_revision", "layout_revision", "files"})
    if (manifest["format"], manifest["format_version"], manifest["profile"]) != ("tmps", "1.0", "narrative-v1"):
        raise ArchiveError("Format non pris en charge.")
    _uuid(manifest["document_id"])
    _uuid(manifest["export_id"])
    _integer(manifest["content_revision"])
    _integer(manifest["layout_revision"])
    if not isinstance(manifest["created_at"], str) or not manifest["created_at"].endswith(("+00:00", "Z")):
        raise ArchiveError("Horodatage UTC invalide.")
    if manifest["required_features"] != []:
        raise ArchiveError("Fonctionnalité obligatoire inconnue.")
    files = manifest["files"]
    if not isinstance(files, list) or len(files) != 1:
        raise ArchiveError("Manifeste de fichiers invalide.")
    _keys(files[0], {"path", "size", "sha256"})
    if files[0]["path"] != "scenario.json" or type(files[0]["size"]) is not int or files[0]["size"] != len(payload):
        raise ArchiveError("Taille du fichier incohérente.")
    if not isinstance(files[0]["sha256"], str) or not SHA_RE.fullmatch(files[0]["sha256"]) or files[0]["sha256"] != hashlib.sha256(payload).hexdigest():
        raise ArchiveError("Empreinte SHA-256 incorrecte.")
    return manifest, validate_document(_json_load(payload))
