#!/usr/bin/env python3
"""Quick smoke test for schema/v0.1.0.json.

Verifies that the schema:
1. Parses as valid JSON.
2. Is itself a valid Draft 2020-12 JSON Schema.
3. Accepts a set of known-good sample manifests.
4. Rejects a set of known-bad sample manifests (one rule violated each).

Run from repo root:

    uv run python script/check_schema.py

If jsonschema is missing as a dependency:

    uv add --dev jsonschema

A passing run prints "ALL CHECKS PASSED" and exits 0. A failing run
prints which samples behaved unexpectedly and exits 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: uv add --dev jsonschema")
    sys.exit(1)


PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT_PATH / "normpic" / "schema" / "v0.1.0.json"


VALID_SAMPLES: dict[str, dict] = {
    "minimal": {
        "version": "0.1.0",
        "collection_name": "Test",
        "generated_at": "2025-11-24T15:30:45Z",
        "collection_root": ".",
        "pic": [],
    },
    "full pic": {
        "version": "0.1.0",
        "collection_name": "Wedding",
        "collection_description": "October 2025",
        "generated_at": "2025-11-24T15:30:45.123Z",
        "collection_root": "../photos/wedding",
        "pic": [
            {
                "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                "relative_path": "2025/10/IMG_0001.jpg",
                "original_filename": "IMG_0001.jpg",
                "size_bytes": 1024000,
                "mtime": "2025-10-15T10:20:30Z",
                "timestamp": "2025-10-15T10:20:30Z",
                "timestamp_source": "exif",
                "camera": "Canon EOS R5",
                "gps": {"lat": 47.6062, "lon": -122.3321},
            }
        ],
    },
    "nullable optionals as null": {
        "version": "0.1.0",
        "collection_name": "Test",
        "collection_description": None,
        "generated_at": "2025-11-24T15:30:45Z",
        "config": None,
        "collection_root": ".",
        "pic": [
            {
                "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                "relative_path": "img.jpg",
                "size_bytes": 100,
                "mtime": "2025-10-15T10:20:30Z",
                "timestamp": None,
                "timestamp_source": None,
                "camera": None,
                "gps": None,
            }
        ],
    },
    "collection_root with leading dotdot segments": {
        "version": "0.1.0",
        "collection_name": "Test",
        "generated_at": "2025-11-24T15:30:45Z",
        "collection_root": "../../shared/wedding",
        "pic": [],
    },
}


INVALID_SAMPLES: dict[str, tuple[dict, str]] = {
    "absolute relative_path": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                    "relative_path": "/abs/path.jpg",
                    "size_bytes": 100,
                    "mtime": "2025-10-15T10:20:30Z",
                }
            ],
        },
        "leading slash in relative_path",
    ),
    "wrong hash prefix": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "sha256:abc123def456",
                    "relative_path": "img.jpg",
                    "size_bytes": 100,
                    "mtime": "2025-10-15T10:20:30Z",
                }
            ],
        },
        "sha256: instead of b3c32:",
    ),
    "lowercase Crockford in hash": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "b3c32:nw9mkefnz6gtd8209qn3dq69",
                    "relative_path": "img.jpg",
                    "size_bytes": 100,
                    "mtime": "2025-10-15T10:20:30Z",
                }
            ],
        },
        "lowercase fails producer schema (consumers SHOULD tolerate)",
    ),
    "GPS out of range": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                    "relative_path": "img.jpg",
                    "size_bytes": 100,
                    "mtime": "2025-10-15T10:20:30Z",
                    "gps": {"lat": 95.0, "lon": 0.0},
                }
            ],
        },
        "lat > 90",
    ),
    "timestamp offset form": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45+00:00",
            "collection_root": ".",
            "pic": [],
        },
        "+00:00 offset instead of Z",
    ),
    "empty required string": (
        {
            "version": "0.1.0",
            "collection_name": "",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [],
        },
        "empty collection_name",
    ),
    "null for non-nullable optional": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                    "relative_path": "img.jpg",
                    "original_filename": None,
                    "size_bytes": 100,
                    "mtime": "2025-10-15T10:20:30Z",
                }
            ],
        },
        "original_filename is non-nullable; null forbidden",
    ),
    "collection_root dot segment": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": "./foo",
            "pic": [],
        },
        "leading ./ in collection_root",
    ),
    "missing required pic field": (
        {
            "version": "0.1.0",
            "collection_name": "Test",
            "generated_at": "2025-11-24T15:30:45Z",
            "collection_root": ".",
            "pic": [
                {
                    "hash": "b3c32:NW9MKEFNZ6GTD8209QN3DQ69",
                    "relative_path": "img.jpg",
                    "mtime": "2025-10-15T10:20:30Z",
                }
            ],
        },
        "missing size_bytes",
    ),
}


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"FAIL: schema not found at {SCHEMA_PATH}")
        return 1

    try:
        with open(SCHEMA_PATH) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: schema is not valid JSON: {e}")
        return 1
    print("OK: schema parses as JSON")

    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        print(f"FAIL: schema is not a valid Draft 2020-12 schema: {e}")
        return 1
    print("OK: schema is a valid Draft 2020-12 schema")

    validator = Draft202012Validator(schema)
    failures = 0

    print()
    print("Valid sample manifests (expect 0 errors each):")
    for name, manifest in VALID_SAMPLES.items():
        errors = list(validator.iter_errors(manifest))
        status = "OK  " if not errors else "FAIL"
        if errors:
            failures += 1
        print(f"  {status} {name}  ({len(errors)} errors)")
        for e in errors:
            print(f"         -> {e.message}")

    print()
    print("Invalid sample manifests (expect >= 1 error each):")
    for name, (manifest, reason) in INVALID_SAMPLES.items():
        errors = list(validator.iter_errors(manifest))
        status = "OK  " if errors else "FAIL"
        if not errors:
            failures += 1
        print(f"  {status} {name}  [{reason}]  ({len(errors)} errors)")

    print()
    if failures:
        print(f"FAILED: {failures} sample(s) did not behave as expected")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

