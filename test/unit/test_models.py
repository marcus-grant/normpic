"""Tests for data models."""

import pytest
from datetime import datetime, timezone


from normpic.model.pic import Pic, MISSING
from normpic.model.manifest import Manifest
from normpic.model.config import Config
from normpic.util.hash import PREFIX

from test.factory import DEFAULT_PIC as _PIC, make_pic


REQUIRED_FIELDS = ["hash", "size_bytes", "mtime", "relative_path"]


class TestPic:
    @pytest.mark.parametrize("missing", REQUIRED_FIELDS)
    def test_required_field_omitted_raises(self, missing):
        """Omitting any required field fails construction."""
        kwargs = {
            "hash": f"{PREFIX}AAAAAAAAAAAAAAAAAAAAAAAA",
            "size_bytes": 1024,
            "mtime": "2023-11-04T22:04:16Z",
            "relative_path": "subdir/photo.jpg",
        }
        del kwargs[missing]
        with pytest.raises(TypeError):
            Pic(**kwargs)

    def test_optional_fields_default(self):
        """Optional fields default without being supplied."""
        pic = make_pic()
        assert pic.timestamp is None
        assert pic.timestamp_source is None
        assert pic.camera is None
        assert pic.gps is None
        assert pic.tag is None
        assert pic.original_filename is MISSING

    def test_pic_creation_with_all_fields(self):
        """Test Pic creation with all optional fields set."""
        pic = make_pic(
            timestamp=(ts := datetime(2025, 11, 6, 19, 30, 0)),
            timestamp_source="exif",
            camera="Canon EOS R5",
            gps={"lat": 40.7128, "lon": -74.0060},
            tag=["holiday"],
            original_filename="IMG_1234.jpg",
        )
        assert pic.timestamp == ts
        assert pic.timestamp_source == "exif"
        assert pic.camera == "Canon EOS R5"
        assert pic.gps == {"lat": 40.7128, "lon": -74.0060}
        assert pic.tag == ["holiday"]
        assert pic.original_filename == "IMG_1234.jpg"

    def test_original_filename_valid(self):
        """Test original_filename set to a valid name is accessible."""
        filename = "orig_pic.jpg"
        assert make_pic(original_filename=filename).original_filename == filename

    def test_original_filename_absent(self):
        """Absent original_filename is the MISSING sentinel, not None."""
        pic = Pic(
            hash=f"{PREFIX}AAAAAAAAAAAAAAAAAAAAAAAA",
            size_bytes=1024,
            mtime="2023-11-04T22:04:16Z",
            relative_path="subdir/photo.jpg",
        )
        assert pic.original_filename is MISSING
        assert pic.original_filename is not None

    @pytest.mark.parametrize(
        "bad",
        [None, "", "a/b.jpg", "a\\b.jpg"],
        ids=["none", "empty", "fwd-slash", "back-slash"],
    )
    def test_original_filename_rejected(self, bad):
        """None, empty, and path-separator names are rejected."""
        with pytest.raises(ValueError):
            make_pic(original_filename=bad)

    def test_pic_to_dict(self):
        """to_dict emits required fields and omits absent optionals."""
        pic = make_pic()
        expected = {
            "hash": _PIC.hash,
            "size_bytes": _PIC.size_bytes,
            "mtime": _PIC.mtime,
            "relative_path": _PIC.relative_path,
        }
        assert pic.to_dict() == expected
        for absent in (
            "timestamp",
            "timestamp_source",
            "camera",
            "gps",
            "tag",
            "original_filename",
        ):
            assert absent not in pic.to_dict()

    def test_tag_absent_by_default(self):
        """tag defaults to None."""
        assert make_pic().tag is None

    @pytest.mark.parametrize("value", [["vacation", "2025"], []], ids=["set", "empty"])
    def test_tag_round_trips(self, value):
        """tag reads back the list it was given, empty included."""
        assert make_pic(tag=value).tag == value

    @pytest.mark.parametrize("value", ["exif", "filename", "filesystem", "unknown"])
    def test_timestamp_source_valid(self, value):
        """Each valid enum value is accepted"""
        assert make_pic(timestamp_source=value).timestamp_source == value

    def test_timestamp_source_invalid_rejected(self):
        """Test that an unrecognised timestamp_source is rejected."""
        with pytest.raises(ValueError):
            make_pic(timestamp_source="bad")

    def test_timestamp_source_none_accepted(self):
        """Test that None is accepted (nullable)."""
        assert make_pic(timestamp_source=None).timestamp_source is None


class TestManifest:
    """Test Manifest dataclass."""

    @staticmethod
    def _pics():
        return [make_pic(relative_path="a/1.jpg"), make_pic(relative_path="b/2.png")]

    def test_manifest_creation(self):
        """Test Manifest creation with pics list."""
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=(gen_at := datetime(2025, 11, 6, 19, 30, 0)),
            pic=self._pics(),
        )

        assert manifest.version == "0.1.0"
        assert manifest.collection_name == "test-collection"
        assert manifest.generated_at == gen_at
        assert len(manifest.pic) == 2
        assert manifest.collection_description is None
        assert manifest.config is None
        assert manifest.collection_root == "."

    def test_collection_root_default(self):
        """Test that collection_root defaults to '.'."""
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pic=[],
        )
        assert manifest.collection_root == "."

    def test_collection_root_explicit(self):
        """Test that an explicit collection_root is accessible."""
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pic=[],
            collection_root="subdir",
        )
        assert manifest.collection_root == "subdir"

    def test_manifest_to_dict(self):
        """Test Manifest conversion to dictionary."""
        generated_at = datetime(2025, 11, 6, 19, 30, 0, tzinfo=timezone.utc)
        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=generated_at,
            pic=self._pics(),
        )
        result = manifest.to_dict()
        assert result["version"] == "0.1.0"
        assert result["collection_name"] == "test-collection"
        assert result["generated_at"] == "2025-11-06T19:30:00.000000Z"
        assert result["collection_root"] == "."
        assert len(result["pic"]) == 2
        assert result["pic"][0]["hash"] == _PIC.hash

    def test_collection_root_round_trip(self):
        """Test collection_root survives serialize/deserialize."""
        from normpic.serializer.manifest import ManifestSerializer

        manifest = Manifest(
            version="0.1.0",
            collection_name="test-collection",
            generated_at=datetime(2025, 11, 6, 19, 30, 0),
            pic=[],
        )

        serializer = ManifestSerializer()
        json_str = serializer.serialize(manifest)
        result = serializer.deserialize(json_str)

        assert result.collection_root == "."


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
