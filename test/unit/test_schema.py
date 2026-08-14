"""Tests for JSON schema validation."""

import pytest
from jsonschema import validate, ValidationError

from normpic.serializer.manifest import _MANIFEST_SCHEMA as MANIFEST_SCHEMA
from normpic.util.hash import PREFIX

_VALID_PIC = {
    "hash": f"{PREFIX}AAAAAAAAAAAAAAAAAAAAAAAA",
    "relative_path": "photo.jpg",
    "size_bytes": 1024,
    "mtime": "2023-11-04T22:04:16Z",
}

_MANIFEST_WRAPPER = {
    "version": "0.1.0",
    "collection_name": "test-collection",
    "generated_at": "2025-11-06T19:30:00Z",
    "pic": [],
}


def _manifest_with(pic: dict) -> dict:
    return {**_MANIFEST_WRAPPER, "pic": [pic]}


class TestManifestSchema:
    """Test manifest schema validation."""

    def test_valid_manifest_passes_validation(self):
        """Test that a valid manifest passes schema validation."""
        valid_manifest = {**_MANIFEST_WRAPPER, "pic": [_VALID_PIC]}
        validate(instance=valid_manifest, schema=MANIFEST_SCHEMA)

    def test_manifest_missing_required_fields_fails(self):
        """Test that manifest missing required fields fails validation."""
        invalid_manifest = {
            "version": "0.1.0",
            # Missing collection_name, generated_at, pic
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid_manifest, schema=MANIFEST_SCHEMA)

    def test_manifest_with_invalid_pic_fails(self):
        """Test that manifest with invalid pic entry fails validation."""
        invalid_manifest = _manifest_with(
            {
                "source_path": "/path/to/source.jpg",
                # Missing required: hash, relative_path, size_bytes, mtime
            }
        )
        with pytest.raises(ValidationError):
            validate(instance=invalid_manifest, schema=MANIFEST_SCHEMA)


class TestPicSchema:
    """Test pic entry schema validation against canonical manifest schema.

    Pics are validated by wrapping them in a minimal manifest; the canonical
    schema uses $ref internally so $defs/pic cannot be used in isolation.
    """

    def test_valid_pic_passes_validation(self):
        """Test that a valid pic entry passes schema validation."""
        validate(instance=_manifest_with(_VALID_PIC), schema=MANIFEST_SCHEMA)

    def test_pic_with_optional_fields_passes_validation(self):
        """Test that pic with optional fields passes validation."""
        pic = {
            **_VALID_PIC,
            "timestamp": "2025-11-06T19:30:00Z",
            "timestamp_source": "exif",
            "camera": "Canon EOS R5",
            "gps": {"lat": 40.7128, "lon": -74.0060},
        }
        validate(instance=_manifest_with(pic), schema=MANIFEST_SCHEMA)

    def test_pic_with_invalid_timestamp_source_fails(self):
        """Test that pic with invalid timestamp_source enum fails."""
        invalid_pic = {**_VALID_PIC, "timestamp_source": "invalid_source"}
        with pytest.raises(ValidationError):
            validate(instance=_manifest_with(invalid_pic), schema=MANIFEST_SCHEMA)
