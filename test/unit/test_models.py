"""Tests for data models."""

from datetime import datetime


from lib.model.pic import Pic
from lib.model.manifest import Manifest
from lib.model.config import Config


class TestPic:
    """Test Pic dataclass."""

    def test_pic_creation_with_required_fields(self):
        """Test Pic creation with only required fields."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg", 
            hash="abc123def456",
            size_bytes=1024
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
            timestamp=timestamp,
            timestamp_source="exif",
            camera="Canon EOS R5",
            gps={"lat": 40.7128, "lon": -74.0060},
            errors=["no_exif"]
        )
        
        assert pic.timestamp == timestamp
        assert pic.timestamp_source == "exif"
        assert pic.camera == "Canon EOS R5"
        assert pic.gps == {"lat": 40.7128, "lon": -74.0060}
        assert pic.errors == ["no_exif"]

    def test_pic_to_dict(self):
        """Test Pic conversion to dictionary."""
        pic = Pic(
            source_path="/path/to/source.jpg",
            dest_path="/path/to/dest.jpg",
            hash="abc123def456",
            size_bytes=1024
        )
        
        expected = {
            "source_path": "/path/to/source.jpg",
            "dest_path": "/path/to/dest.jpg", 
            "hash": "abc123def456",
            "size_bytes": 1024,
            "timestamp": None,
            "timestamp_source": None,
            "camera": None,
            "gps": None,
            "errors": []
        }
        
        assert pic.to_dict() == expected


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
                size_bytes=1024
            ),
            Pic(
                source_path="/path/to/source2.jpg",
                dest_path="/path/to/dest2.jpg",
                hash="def456", 
                size_bytes=2048
            )
        ]
        
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pics=pics
        )
        
        assert manifest.version == "0.1.0"
        assert manifest.collection_name == "test-collection"
        assert manifest.generated_at == generated_at
        assert len(manifest.pics) == 2
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
                size_bytes=1024
            )
        ]
        
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection", 
            generated_at=generated_at,
            pics=pics
        )
        
        result = manifest.to_dict()
        
        assert result["version"] == "0.1.0"
        assert result["collection_name"] == "test-collection"
        assert result["generated_at"] == generated_at.isoformat()
        assert len(result["pics"]) == 1
        assert result["pics"][0]["source_path"] == "/path/to/source.jpg"


class TestConfig:
    """Test Config dataclass."""

    def test_config_creation_with_defaults(self):
        """Test Config creation with default values."""
        config = Config(collection_name="test-collection")
        
        assert config.collection_name == "test-collection"
        assert config.collection_description is None
        assert config.timestamp_offset_hours == 0
        assert config.force_reprocess is False

    def test_config_creation_with_all_fields(self):
        """Test Config creation with all fields."""
        config = Config(
            collection_name="wedding-photos",
            collection_description="John and Jane's wedding",
            timestamp_offset_hours=-5,
            force_reprocess=True
        )
        
        assert config.collection_name == "wedding-photos"
        assert config.collection_description == "John and Jane's wedding"
        assert config.timestamp_offset_hours == -5
        assert config.force_reprocess is True