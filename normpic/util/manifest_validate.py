"""Implementation-layer manifest validation rules beyond JSON Schema."""

from datetime import datetime


def impl_validate(manifest: dict) -> list[str]:
    """Check contract rules the JSON Schema cannot express.

    Returns a list of error strings; empty means valid at this layer.
    Run after schema_validate; only call on schema-valid manifests.
    """
    errors = []
    errors.extend(_check_collection_root(manifest))
    errors.extend(_check_timestamps(manifest))
    return errors


def _check_collection_root(manifest: dict) -> list[str]:
    root = manifest.get("collection_root", ".")
    if root == ".":
        return []
    segments = root.split("/")
    seen_non_dotdot = False
    for seg in segments:
        if seg == "..":
            if seen_non_dotdot:
                return [
                    "collection_root: '..' segment after non-leading position"
                ]
        else:
            seen_non_dotdot = True
    return []


def _check_timestamps(manifest: dict) -> list[str]:
    errors = []
    errors.extend(_parse_ts(manifest.get("generated_at"), "generated_at"))
    for i, pic in enumerate(manifest.get("pic", [])):
        errors.extend(_parse_ts(pic.get("mtime"), f"pic[{i}].mtime"))
        ts = pic.get("timestamp")
        if ts is not None:
            errors.extend(_parse_ts(ts, f"pic[{i}].timestamp"))
    return errors


def _parse_ts(value: str | None, field: str) -> list[str]:
    if value is None:
        return []
    try:
        datetime.fromisoformat(value)
        return []
    except ValueError:
        return [f"{field}: invalid calendar value '{value}'"]


_CROCKFORD_ALIASES = {"I": "1", "L": "1", "O": "0"}


def _normalize_hash(value: str) -> str:
    prefix = "b2b120:"
    if not value.startswith(prefix):
        return value
    payload = value[len(prefix):]
    normalized = "".join(
        _CROCKFORD_ALIASES.get(ch.upper(), ch.upper()) for ch in payload
    )
    return prefix + normalized


def consumer_normalize(manifest: dict) -> dict:
    """Return a copy of manifest with consumer-lenient hash normalization applied.

    Applies Crockford lenient read to each pic hash: case-folds to uppercase
    and alias-folds i/I and l/L to '1', o/O to '0'. Scoped to the hash
    payload only; the b2b120: prefix is passed through unchanged.
    """
    import copy
    result = copy.deepcopy(manifest)
    for pic in result.get("pic", []):
        if "hash" in pic:
            pic["hash"] = _normalize_hash(pic["hash"])
    return result
