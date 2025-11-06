"""Tests for JSON schema validation."""

import pytest
from jsonschema import validate, ValidationError

from lib.model.schema_v0 import VERSION, MANIFEST_SCHEMA, PIC_SCHEMA


class TestManifestSchema:
    """Test manifest schema validation."""

    def test_valid_manifest_passes_validation(self):
        """Test that a valid manifest passes schema validation."""
        valid_manifest = {
            "version": "0.1.0",
            "collection_name": "test-collection",
            "generated_at": "2025-11-06T19:30:00Z",
            "pics": [
                {
                    "source_path": "/path/to/source.jpg",
                    "dest_path": "/path/to/dest.jpg",
                    "hash": "abc123def456",
                    "size_bytes": 1024
                }
            ]
        }
        
        # Should not raise ValidationError
        validate(instance=valid_manifest, schema=MANIFEST_SCHEMA)

    def test_manifest_missing_required_fields_fails(self):
        """Test that manifest missing required fields fails validation."""
        invalid_manifest = {
            "version": "0.1.0",
            # Missing collection_name, generated_at, pics
        }
        
        with pytest.raises(ValidationError):
            validate(instance=invalid_manifest, schema=MANIFEST_SCHEMA)

    def test_manifest_with_invalid_pic_fails(self):
        """Test that manifest with invalid pic entry fails validation."""
        invalid_manifest = {
            "version": "0.1.0", 
            "collection_name": "test-collection",
            "generated_at": "2025-11-06T19:30:00Z",
            "pics": [
                {
                    "source_path": "/path/to/source.jpg",
                    # Missing dest_path, hash, size_bytes
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            validate(instance=invalid_manifest, schema=MANIFEST_SCHEMA)


class TestPicSchema:
    """Test pic entry schema validation."""

    def test_valid_pic_passes_validation(self):
        """Test that a valid pic entry passes schema validation."""
        valid_pic = {
            "source_path": "/path/to/source.jpg",
            "dest_path": "/path/to/dest.jpg", 
            "hash": "abc123def456",
            "size_bytes": 1024
        }
        
        validate(instance=valid_pic, schema=PIC_SCHEMA)

    def test_pic_with_optional_fields_passes_validation(self):
        """Test that pic with optional fields passes validation."""
        pic_with_optionals = {
            "source_path": "/path/to/source.jpg",
            "dest_path": "/path/to/dest.jpg",
            "hash": "abc123def456", 
            "size_bytes": 1024,
            "timestamp": "2025-11-06T19:30:00Z",
            "timestamp_source": "exif",
            "camera": "Canon EOS R5",
            "gps": {"lat": 40.7128, "lon": -74.0060},
            "errors": ["no_exif"]
        }
        
        validate(instance=pic_with_optionals, schema=PIC_SCHEMA)

    def test_pic_with_invalid_timestamp_source_fails(self):
        """Test that pic with invalid timestamp_source enum fails."""
        invalid_pic = {
            "source_path": "/path/to/source.jpg",
            "dest_path": "/path/to/dest.jpg",
            "hash": "abc123def456",
            "size_bytes": 1024,
            "timestamp_source": "invalid_source"  # Not in enum
        }
        
        with pytest.raises(ValidationError):
            validate(instance=invalid_pic, schema=PIC_SCHEMA)


class TestSchemaVersioning:
    """Test schema versioning."""

    def test_version_constant_matches_schema(self):
        """Test that VERSION constant matches schema version."""
        assert VERSION == "0.1.0"
        assert MANIFEST_SCHEMA["properties"]["version"]["const"] == VERSION