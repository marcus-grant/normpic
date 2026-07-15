"""Tests for manifest serializer."""

import json
from datetime import datetime, timezone

import pytest
from jsonschema import ValidationError

from normpic.model.pic import Pic
from normpic.model.manifest import Manifest
from normpic.serializer.manifest import ManifestSerializer


class TestManifestSerializer:
    """Test manifest serialization/deserialization."""

    def test_serialize_manifest_to_json(self):
        """Test serializing manifest to JSON string."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc)

        pics = [
            Pic(
                hash="abc123",
                size_bytes=1024,
                mtime="2023-11-04T22:04:16Z",
                relative_path="pic.jpg",
            )
        ]

        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=pics,
        )

        serializer = ManifestSerializer()
        json_str = serializer.serialize(manifest)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["version"] == "0.1.0"
        assert parsed["collection_name"] == "test-collection"
        assert parsed["generated_at"] == "2025-11-06T19:30:00.000000Z"
        assert len(parsed["pic"]) == 1

    def test_deserialize_json_to_manifest(self):
        """Test deserializing JSON string to Manifest object."""
        json_data = {
            "version": "0.1.0",
            "collection_name": "test-collection",
            "generated_at": "2025-11-06T19:30:00Z",
            "pic": [
                {
                    "hash": "b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    "relative_path": "photo.jpg",
                    "size_bytes": 1024,
                    "mtime": "2023-11-04T22:04:16Z",
                    "timestamp": None,
                    "timestamp_source": None,
                    "camera": None,
                    "gps": None,
                }
            ],
            "collection_description": None,
            "config": None,
        }

        serializer = ManifestSerializer()
        manifest = serializer.deserialize(json.dumps(json_data))

        assert manifest.version == "0.1.0"
        assert manifest.collection_name == "test-collection"
        assert manifest.generated_at == datetime(
            2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc
        )
        assert len(manifest.pic) == 1
        assert manifest.pic[0].hash == "b2b120:AAAAAAAAAAAAAAAAAAAAAAAA"

    def test_round_trip_serialization(self):
        """Test that serialize -> deserialize preserves data."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc)

        original_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=[
                Pic(
                    hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    relative_path="photo.jpg",
                    size_bytes=1024,
                    mtime="2023-11-04T22:04:16Z",
                    timestamp=generated_at,
                    timestamp_source="exif",
                )
            ],
        )

        serializer = ManifestSerializer()
        json_str = serializer.serialize(original_manifest)
        deserialized_manifest = serializer.deserialize(json_str)

        assert deserialized_manifest.version == original_manifest.version
        assert (
            deserialized_manifest.collection_name == original_manifest.collection_name
        )
        assert deserialized_manifest.generated_at == original_manifest.generated_at
        assert len(deserialized_manifest.pic) == len(original_manifest.pic)

        original_pic = original_manifest.pic[0]
        deserialized_pic = deserialized_manifest.pic[0]
        assert deserialized_pic.hash == original_pic.hash
        assert deserialized_pic.timestamp == original_pic.timestamp
        assert deserialized_pic.timestamp_source == original_pic.timestamp_source

    def test_validate_manifest_with_valid_data(self):
        """Test schema validation passes for valid manifest."""
        valid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc),
            pic=[
                Pic(
                    hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    relative_path="photo.jpg",
                    size_bytes=1024,
                    mtime="2023-11-04T22:04:16Z",
                )
            ],
        )

        serializer = ManifestSerializer()
        # Should not raise ValidationError
        serializer.validate(valid_manifest)

    def test_validate_manifest_with_invalid_data_raises_error(self):
        """Test schema validation fails for invalid manifest."""
        # size_bytes=-1 passes model construction but fails schema (minimum: 0)
        invalid_pic = Pic(
            hash="abc123",
            size_bytes=-1,
            mtime="2023-11-04T22:04:16Z",
            relative_path="pic.jpg",
        )

        invalid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pic=[invalid_pic],
        )

        serializer = ManifestSerializer()
        with pytest.raises(ValidationError):
            serializer.validate(invalid_manifest)

    def test_serialize_with_validation_enabled(self):
        """Test serialization with schema validation enabled."""
        valid_manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc),
            pic=[
                Pic(
                    hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    relative_path="photo.jpg",
                    size_bytes=1024,
                    mtime="2023-11-04T22:04:16Z",
                )
            ],
        )

        serializer = ManifestSerializer()
        json_str = serializer.serialize(valid_manifest, validate=True)

        # Should succeed without error
        assert json_str is not None
        parsed = json.loads(json_str)
        assert parsed["version"] == "0.1.0"

    def test_pic_requires_relative_path(self):
        """v0.1 contract requires relative_path on every pic;
        the model must reject construction without it."""
        with pytest.raises(TypeError):
            Pic(  # type: ignore relative_path is missing, should raise
                hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                size_bytes=1,
                mtime="2024-01-01T00:00:00.000000Z",
            )

    def test_deserialize_tolerates_missing_legacy_fields(self):
        """deserialize over a manifest lacking source_path/dest_path/errors is clean."""
        json_data = {
            "version": "0.1.0",
            "collection_name": "test-collection",
            "generated_at": "2025-11-06T19:30:00Z",
            "pic": [
                {
                    "hash": "b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    "relative_path": "photo.jpg",
                    "size_bytes": 100,
                    "mtime": "2024-01-01T00:00:00.000000Z",
                    "timestamp": None,
                    "timestamp_source": None,
                    "camera": None,
                    "gps": None,
                }
            ],
        }

        manifest = ManifestSerializer().deserialize(json.dumps(json_data))
        assert len(manifest.pic) == 1
        assert manifest.pic[0].hash == "b2b120:AAAAAAAAAAAAAAAAAAAAAAAA"

    def test_pic_unset_optionals_omitted_from_dict(self):
        """Pic with all four optional fields unset must not emit those keys."""
        pic = Pic(
            hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
            relative_path="photo.jpg",
            size_bytes=100,
            mtime="2024-01-01T00:00:00.000000Z",
        )
        d = pic.to_dict()
        for key in ("timestamp", "timestamp_source", "camera", "gps"):
            assert key not in d, (
                f"absent optional field {key!r} should not appear in dict"
            )

        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc),
            pic=[pic],
        )
        ManifestSerializer().validate(manifest)

    def test_deserialize_absence_form_round_trips(self):
        """serialize -> deserialize over absence-form manifest must not KeyError."""
        pic = Pic(
            hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
            relative_path="photo.jpg",
            size_bytes=100,
            mtime="2024-01-01T00:00:00.000000Z",
        )
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc),
            pic=[pic],
        )
        serializer = ManifestSerializer()
        json_str = serializer.serialize(manifest)
        loaded = serializer.deserialize(json_str)
        p = loaded.pic[0]
        assert p.timestamp is None
        assert p.timestamp_source is None
        assert p.camera is None
        assert p.gps is None

    def test_serialize_is_deterministic(self):
        """Serializing the same Manifest twice must produce byte-identical output."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc)
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=[
                Pic(
                    hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    relative_path="photo.jpg",
                    size_bytes=1024,
                    mtime="2023-11-04T22:04:16Z",
                    timestamp=generated_at,
                    timestamp_source="exif",
                    camera="Canon EOS R5",
                    gps={"lat": 40.7128, "lon": -74.006},
                )
            ],
        )
        serializer = ManifestSerializer()
        assert serializer.serialize(manifest) == serializer.serialize(manifest)

    def test_serialize_round_trip_is_deterministic(self):
        """serialize -> deserialize -> serialize must produce the same bytes."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc)
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=[
                Pic(
                    hash="b2b120:AAAAAAAAAAAAAAAAAAAAAAAA",
                    relative_path="photo.jpg",
                    size_bytes=1024,
                    mtime="2023-11-04T22:04:16Z",
                    timestamp=generated_at,
                    timestamp_source="exif",
                    camera="Canon EOS R5",
                    gps={"lat": 40.7128, "lon": -74.006},
                )
            ],
        )
        serializer = ManifestSerializer()
        first = serializer.serialize(manifest)
        third = serializer.serialize(serializer.deserialize(first))
        assert first == third
