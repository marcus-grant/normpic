from datetime import datetime


def impl_validate(manifest: dict) -> list[str]:
    errors = []
    _check_collection_root(manifest, errors)
    _check_timestamps(manifest, errors)
    return errors


def _check_collection_root(manifest: dict, errors: list[str]) -> None:
    root = manifest.get("collection_root", ".")
    if root == ".":
        return
    segments = root.split("/")
    seen_non_dotdot = False
    for seg in segments:
        if seg == "..":
            if seen_non_dotdot:
                errors.append(
                    "collection_root: '..' segment after non-leading position"
                )
                return
        else:
            seen_non_dotdot = True


def _check_timestamps(manifest: dict, errors: list[str]) -> None:
    _parse_ts(manifest.get("generated_at"), "generated_at", errors)
    for i, pic in enumerate(manifest.get("pic", [])):
        _parse_ts(pic.get("mtime"), f"pic[{i}].mtime", errors)
        ts = pic.get("timestamp")
        if ts is not None:
            _parse_ts(ts, f"pic[{i}].timestamp", errors)


def _parse_ts(value, field: str, errors: list[str]) -> None:
    if value is None:
        return
    try:
        datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{field}: invalid calendar value '{value}'")
