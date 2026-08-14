# Manifest Consumption Guide

## Overview

This guide explains how to consume NormPic manifest files in parent
projects such as gallery builders and site generators.
A manifest is a JSON Schema-validated file describing one organized
photo collection.
Field names, semantics, and canonical forms are defined once, in
[manifest-contract.md](../architecture/manifest-contract.md); this
guide shows how to read a manifest, not what each field means.

## Manifest structure

A manifest is contract-pure: it describes only its own collection and
carries no diagnostics.
Diagnostics (errors, warnings, status) are producer-side logs and are
never serialized into the manifest.

```json
{
  "version": "0.1.0",
  "collection_name": "wedding",
  "collection_description": "Wedding photos from August 2025",
  "generated_at": "2025-08-09T13:20:34Z",
  "collection_root": ".",
  "pic": [
    {
      "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
      "relative_path": "2025/08/wedding-20250809T132034-r5a.jpg",
      "original_filename": "4F6A5096.JPG",
      "size_bytes": 26786754,
      "mtime": "2025-08-09T13:20:34Z",
      "timestamp": "2025-08-09T13:20:34Z",
      "timestamp_source": "exif",
      "camera": "Canon EOS R5",
      "gps": {"lat": 47.6062, "lon": -122.3321}
    }
  ]
}
```

Optional and nullable fields are omitted when unset rather than
emitted as null.
A consumer must treat an absent field and a null field as equivalent.
See the contract for the full required and optional split.

## Loading a manifest

Read the JSON and validate it against the schema artifact the producer
loads, `normpic/schema/v0.1.0.json`.
Address each pic's file by `relative_path` under the collection root;
the pic stores no source or destination path.

```python
import json
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    """Load and minimally check a NormPic manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    required = ["version", "collection_name", "generated_at", "pic"]
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return data


def photo_paths(manifest: dict, collection_root: Path) -> list[Path]:
    """Resolve each pic to a file path under the collection root."""
    root = collection_root / manifest.get("collection_root", ".")
    return [root / pic["relative_path"] for pic in manifest["pic"]]
```

For schema-level validation, use a JSON Schema library
(Draft 2020-12) against `normpic/schema/v0.1.0.json` rather than hand-rolled
field checks.

## Pic ordering is significant

NormPic orders pics at organize time by EXIF time-stamp, falling back
to filename then mtime, and preserves burst sequences so that
consecutive shots from one camera are not interleaved with another
camera's shots sharing the same time-stamp.
This ordering is baked into the manifest: the order of the `pic`
array is the intended presentation order.

A consumer must preserve manifest order and must not re-sort or
regroup pics.
Re-deriving ordering or burst grouping consumer-side can diverge from
NormPic's burst preservation and is not supported.
Read the array in order; that is the grouping.

To present per-camera views, read the `camera` field on each pic
while preserving the array order, rather than re-sorting.

## Change detection

The `hash` field is the content-addressed identity and the basis for
change detection.
Key pics by `relative_path`, then compare hashes to find modified
files.

```python
def compare(old: dict, new: dict) -> dict:
    """Detect added, removed, and modified pics between manifests."""
    old_pics = {p["relative_path"]: p for p in old["pic"]}
    new_pics = {p["relative_path"]: p for p in new["pic"]}

    added = new_pics.keys() - old_pics.keys()
    removed = old_pics.keys() - new_pics.keys()
    modified = {
        path
        for path in old_pics.keys() & new_pics.keys()
        if old_pics[path]["hash"] != new_pics[path]["hash"]
    }

    return {
        "added": sorted(added),
        "removed": sorted(removed),
        "modified": sorted(modified),
    }
```

Two hashes differing means the file content changed.
Two hashes matching means the content is identical, even if the file
was moved or renamed.

## Pairing variant collections

NormPic does not pair variant collections.
The source collection and its compressed derivative are processed independently,
each producing its own manifest.
The manifests do not link corresponding pictures yet.
A future version will implement some kind of linking of related pictures.

A consumer that knows it holds a mirrored pair can match on
`relative_path`.
The generated name derives from EXIF time-stamp and camera, both of
which survive compression, so corresponding photos receive the same
name in both collections.

```python
def pair(full: dict, web: dict) -> dict:
    """Match pics across two manifests of the same photo set."""
    full_pics = {p["relative_path"]: p for p in full["pic"]}
    web_pics = {p["relative_path"]: p for p in web["pic"]}
    shared = full_pics.keys() & web_pics.keys()
    return {path: (full_pics[path], web_pics[path]) for path in shared}
```

This holds only for a genuinely mirrored set.
Verify it rather than assuming it.
Compare the source filenames:

```bash
diff <(ls /path/to/full) <(ls /path/to/web)
```

Then assert the pair count against both manifests, and fail loudly on
a mismatch rather than pairing silently wrong:

```python
assert len(paired) == len(full["pic"]) == len(web["pic"])
```

Two caveats.
`original_filename` is optional in version `0.1.0` and
no producer path populates it,
so it cannot be used as a pairing key.
And photos sharing a time-stamp to the second receive a `-0`/`-1`
ordinal suffix assigned by processing order, so their names agree
across collections only while both hold the same set of files.
Losing one member of a same-second group from one collection shifts
that group's suffixes and incorrectly pairs them.

Automated variant pairing is likely to become a NormPic feature.
The approach is not settled, so version `0.1.0` leaves pairing to consumers.

## Related guides

- [integration.md](integration.md): broader parent-project
  integration patterns.
- [errors.md](errors.md): how producer diagnostics are surfaced.
