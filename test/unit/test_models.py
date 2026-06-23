"""Tests for data models."""

import pytest
from datetime import datetime


from normpic.model.pic import Pic, MISSING
from normpic.model.manifest import Manifest
from normpic.model.config import Config


class TestPic:
    """Test Pic dataclass."""

    def test_pic_creation_with_required_fields(self):
        """Test Pic creation with only required fields."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
        )

        assert pic.source_path == "/path/to/source.jpg"
        assert pic.dest_path == "/path/to/dest.jpg"
        assert pic.hash == "abc123def456"
        assert pic.size_bytes == 1024
        assert pic.timestamp is None
        assert pic.timestamp_source is None
        assert pic.camera is None
        assert pic.gps is None
        assert pic.errors == []

    def test_pic_creation_with_all_fields(self):
        """Test Pic creation with all fields including optionals."""
        timestamp = datetime(2025, 11, 6, 19, 30, 0)

        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
            timestamp=timestamp,
            timestamp_source="exif",
            camera="Canon EOS R5",
            gps={"lat": 40.7128, "lon": -74.0060},
            errors=["no_exif"],
            tag=["holiday"],
        )

        assert pic.timestamp == timestamp
        assert pic.timestamp_source == "exif"
        assert pic.camera == "Canon EOS R5"
        assert pic.gps == {"lat": 40.7128, "lon": -74.0060}
        assert pic.errors == ["no_exif"]
        assert pic.tag == ["holiday"]

    def test_original_filename_valid(self):
        """Test original_filename set to a valid name is accessible."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
            original_filename="photo.jpg",
        )

        assert pic.original_filename == "photo.jpg"

    def test_original_filename_absent(self):
        """Test absent original_filename is the MISSING sentinel, not None."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
        )

        assert pic.original_filename is MISSING
        assert pic.original_filename is not None

    def test_original_filename_explicit_none_rejected(self):
        """Test that explicit None is rejected at construction."""
        with pytest.raises(ValueError):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                original_filename=None,
            )

    def test_original_filename_empty_rejected(self):
        """Test that empty string is rejected at construction."""
        with pytest.raises(ValueError):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                original_filename="",
            )

    def test_original_filename_separator_rejected(self):
        """Test that path separators in original_filename are rejected."""
        with pytest.raises(ValueError):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                original_filename="a/b.jpg",
            )
        with pytest.raises(ValueError):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                original_filename="a\\b.jpg",
            )

    def test_pic_to_dict(self):
        """Test Pic conversion to dictionary."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
        )

        expected = {
            "source_path": "/path/to/source.jpg",
            "dest_path": "/path/to/dest.jpg",
            "hash": "abc123def456",
            "size_bytes": 1024,
            "mtime": 1699123456.789,
            "timestamp": None,
            "timestamp_source": None,
            "camera": None,
            "gps": None,
            "errors": [],
        }

        assert pic.to_dict() == expected
        assert "tag" not in pic.to_dict()
        assert "original_filename" not in pic.to_dict()

    def test_tag_absent_by_default(self):
        """Test that tag defaults to None (absent)."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
        )

        assert pic.tag is None

    def test_tag_set(self):
        """Test that tag is accessible when set."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
            tag=["vacation", "2025"],
        )

        assert pic.tag == ["vacation", "2025"]

    def test_tag_empty_list(self):
        """Test that empty tag list is allowed (semantically absent)."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
            tag=[],
        )

        assert pic.tag == []

    def test_timestamp_source_valid_values(self):
        """Test that all valid enum values are accepted."""
        for value in ("exif", "filename", "filesystem", "unknown"):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                timestamp_source=value,
            )

    def test_timestamp_source_invalid_rejected(self):
        """Test that an unrecognised timestamp_source is rejected."""
        with pytest.raises(ValueError):
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123def456",
                size_bytes=1024,
                mtime=1699123456.789,
                timestamp_source="bad",
            )

    def test_timestamp_source_none_accepted(self):
        """Test that None is accepted (nullable)."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024,
            mtime=1699123456.789,
            timestamp_source=None,
        )

        assert pic.timestamp_source is None


class TestManifest:
    """Test Manifest dataclass."""

    def test_manifest_creation(self):
        """Test Manifest creation with pics list."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0)

        pics = [
            Pic(
                source_path="/path/to/source1.jpg",
                dest_path="/path/to/dest1.jpg",
                hash="abc123",
                size_bytes=1024,
                mtime=1699123456.789,
            ),
            Pic(
                source_path="/path/to/source2.jpg",
                dest_path="/path/to/dest2.jpg",
                hash="def456",
                size_bytes=2048,
                mtime=1699123456.789,
            ),
        ]

        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=pics,
        )

        assert manifest.version == "0.1.0"
        assert manifest.collection_name == "test-collection"
        assert manifest.generated_at == generated_at
        assert len(manifest.pic) == 2
        assert manifest.collection_description is None
        assert manifest.config is None

    def test_manifest_to_dict(self):
        """Test Manifest conversion to dictionary."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0)

        pics = [
            Pic(
                source_path="/path/to/source.jpg",
                dest_path="/path/to/dest.jpg",
                hash="abc123",
                size_bytes=1024,
                mtime=1699123456.789,
            )
        ]

        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=pics,
        )

        result = manifest.to_dict()

        assert result["version"] == "0.1.0"
        assert result["collection_name"] == "test-collection"
        assert result["generated_at"] == generated_at.isoformat()
        assert len(result["pic"]) == 1
        assert result["pic"][0]["source_path"] == "/path/to/source.jpg"


class TestConfig:
    """Test Config dataclass."""

    def test_config_creation_with_defaults(self):
        """Test Config creation with default values."""
        config = Config(
            collection_name="test-collection",
            source_dir="/tmp/source",
            dest_dir="/tmp/dest",
        )

        assert config.collection_name == "test-collection"
        assert config.source_dir == "/tmp/source"
        assert config.dest_dir == "/tmp/dest"
        assert config.collection_description is None
        assert config.timestamp_offset_hours == 0
        assert config.force_reprocess is False

    def test_config_creation_with_all_fields(self):
        """Test Config creation with all fields."""
        config = Config(
            collection_name="wedding-photos",
            source_dir="/photos/raw",
            dest_dir="/photos/organized",
            collection_description="John and Jane's wedding",
            timestamp_offset_hours=-5,
            force_reprocess=True,
        )

        assert config.collection_name == "wedding-photos"
        assert config.source_dir == "/photos/raw"
        assert config.dest_dir == "/photos/organized"
        assert config.collection_description == "John and Jane's wedding"
        assert config.timestamp_offset_hours == -5
        assert config.force_reprocess is True
