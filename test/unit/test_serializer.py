"""Tests for manifest serializer."""

import json
from datetime import datetime

import pytest
from jsonschema import ValidationError

from lib.model.pic import Pic
from lib.model.manifest import Manifest
from lib.serializer.manifest import ManifestSerializer


class TestManifestSerializer:
    """Test manifest serialization/deserialization."""

    def test_serialize_manifest_to_json(self):
        """Test serializing manifest to JSON string."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0)
        
        pics = [
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg", 
                hash="abc123",
                size_bytes=1024
            )
        ]
        
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pics=pics
        )
        
        serializer = ManifestSerializer()
        json_str = serializer.serialize(manifest)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["version"] == "0.1.0"
        assert parsed["collection_name"] == "test-collection"
        assert parsed["generated_at"] == "2025-11-06T19:30:00"
        assert len(parsed["pics"]) == 1

    def test_deserialize_json_to_manifest(self):
        """Test deserializing JSON string to Manifest object."""
        json_data = {
            "version": "0.1.0",
            "collection_name": "test-collection",
            "generated_at": "2025-11-06T19:30:00",
            "pics": [
                {
                    "source_path": "/path/to/source.jpg",
                    "dest_path": "/path/to/dest.jpg",
                    "hash": "abc123",
                    "size_bytes": 1024,
                    "timestamp": None,
                    "timestamp_source": None,
                    "camera": None,
                    "gps": None,
                    "errors": []
                }
            ],
            "collection_description": None,
            "config": None
        }
        
        serializer = ManifestSerializer()
        manifest = serializer.deserialize(json.dumps(json_data))
        
        assert manifest.version == "0.1.0"
        assert manifest.collection_name == "test-collection"
        assert manifest.generated_at == datetime(2025, 11, 6, 19, 30, 0)
        assert len(manifest.pics) == 1
        assert manifest.pics[0].source_path == "/path/to/source.jpg"

    def test_round_trip_serialization(self):
        """Test that serialize -> deserialize preserves data."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0)
        
        original_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pics=[
                Pic(
                    source_path="/path/to/source.jpg",
                    dest_path="/path/to/dest.jpg",
                    hash="abc123",
                    size_bytes=1024,
                    timestamp=generated_at,
                    timestamp_source="exif"
                )
            ]
        )
        
        serializer = ManifestSerializer()
        json_str = serializer.serialize(original_manifest)
        deserialized_manifest = serializer.deserialize(json_str)
        
        assert deserialized_manifest.version == original_manifest.version
        assert deserialized_manifest.collection_name == original_manifest.collection_name
        assert deserialized_manifest.generated_at == original_manifest.generated_at
        assert len(deserialized_manifest.pics) == len(original_manifest.pics)
        
        original_pic = original_manifest.pics[0]
        deserialized_pic = deserialized_manifest.pics[0]
        assert deserialized_pic.source_path == original_pic.source_path
        assert deserialized_pic.timestamp == original_pic.timestamp
        assert deserialized_pic.timestamp_source == original_pic.timestamp_source

    def test_validate_manifest_with_valid_data(self):
        """Test schema validation passes for valid manifest."""
        valid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pics=[
                Pic(
                    source_path="/path/to/source.jpg",
                    dest_path="/path/to/dest.jpg",
                    hash="abc123",
                    size_bytes=1024
                )
            ]
        )
        
        serializer = ManifestSerializer()
        # Should not raise ValidationError
        serializer.validate(valid_manifest)

    def test_validate_manifest_with_invalid_data_raises_error(self):
        """Test schema validation fails for invalid manifest."""
        # Create manifest with invalid timestamp_source
        invalid_pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123",
            size_bytes=1024,
            timestamp_source="invalid_source"  # Not in enum
        )
        
        invalid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pics=[invalid_pic]
        )
        
        serializer = ManifestSerializer()
        with pytest.raises(ValidationError):
            serializer.validate(invalid_manifest)

    def test_serialize_with_validation_enabled(self):
        """Test serialization with schema validation enabled."""
        valid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pics=[
                Pic(
                    source_path="/path/to/source.jpg",
                    dest_path="/path/to/dest.jpg",
                    hash="abc123",
                    size_bytes=1024
                )
            ]
        )
        
        serializer = ManifestSerializer()
        json_str = serializer.serialize(valid_manifest, validate=True)
        
        # Should succeed without error
        assert json_str is not None
        parsed = json.loads(json_str)
        assert parsed["version"] == "0.1.0"