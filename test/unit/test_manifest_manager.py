"""Tests for manifest manager functionality."""

import json
from datetime import datetime, timezone


from unittest.mock import patch

from normpic.manager.manifest_manager import (
    ManifestManager,
    load_existing_manifest,
    load_source_manifest,
    build_source_manifest,
    build_hash_keyed_source_index,
)
from normpic.model.manifest import Manifest
from normpic.model.pic import Pic
from normpic.util.hash import PREFIX
from test.helpers.conformance import SCHEMA_PATH


class TestManifestManager:
    """Test ManifestManager class functionality."""

    def test_load_manifest_file_exists(self, tmp_path):
        """Test loading manifest when file exists and is valid."""
        # Arrange
        manifest_path = tmp_path / "manifest.json"
        valid_manifest_data = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-10-05T14:00:00Z",
            "collection_description": None,
            "config": None,
            "pic": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(valid_manifest_data, f)

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is not None
        assert result.version == "0.1.0"
        assert result.collection_name == "test"
        assert len(result.pic) == 0

    def test_load_manifest_file_not_exists(self, tmp_path):
        """Test loading manifest when file doesn't exist."""
        # Arrange
        manifest_path = tmp_path / "nonexistent.json"
        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None

    def test_load_manifest_invalid_json(self, tmp_path):
        """Test loading manifest with invalid JSON."""
        # Arrange
        manifest_path = tmp_path / "invalid.json"
        with open(manifest_path, "w") as f:
            f.write("invalid json content")

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None

    def test_load_manifest_schema_validation_failure(self, tmp_path):
        """Test loading manifest that fails schema validation."""
        # Arrange
        manifest_path = tmp_path / "invalid_schema.json"
        invalid_manifest_data = {
            "version": "0.1.0",
            # Missing required fields: collection_name, generated_at
            "pic": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(invalid_manifest_data, f)

        manager = ManifestManager(manifest_path)

        # Act
        result = manager.load_manifest()

        # Assert
        assert result is None


class TestLoadExistingManifestFunction:
    """Test standalone load_existing_manifest function."""

    def test_load_existing_manifest_success(self, tmp_path):
        """Test load_existing_manifest function with valid manifest."""
        # Arrange
        manifest_path = tmp_path / "test_manifest.json"
        valid_manifest_data = {
            "version": "0.1.0",
            "collection_name": "wedding",
            "generated_at": "2024-10-05T14:00:00Z",
            "collection_description": None,
            "config": None,
            "pic": [],
        }

        with open(manifest_path, "w") as f:
            json.dump(valid_manifest_data, f)

        # Act
        result = load_existing_manifest(manifest_path)

        # Assert
        assert result is not None
        assert result.version == "0.1.0"
        assert result.collection_name == "wedding"

    def test_load_existing_manifest_file_not_found(self, tmp_path):
        """Test load_existing_manifest with non-existent file."""
        # Arrange
        nonexistent_path = tmp_path / "does_not_exist.json"

        # Act
        result = load_existing_manifest(nonexistent_path)

        # Assert
        assert result is None

    def test_load_existing_manifest_invalid_format(self, tmp_path):
        """Test load_existing_manifest with corrupted file."""
        # Arrange
        corrupt_path = tmp_path / "corrupt.json"
        with open(corrupt_path, "w") as f:
            f.write("not valid json at all")

        # Act
        result = load_existing_manifest(corrupt_path)

        # Assert
        assert result is None


class TestChangeDetection:
    """Test change detection functionality for incremental processing."""

    def test_detect_file_hash_changes(self, tmp_path, create_photo_with_exif):
        """Test detecting when file content changes via hash comparison."""
        # Arrange: Create a photo and get its initial hash
        photo_path = create_photo_with_exif(
            tmp_path / "test.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        from normpic.manager.manifest_manager import ManifestManager

        manager = ManifestManager()

        # Get actual hash of the photo
        actual_hash = manager.compute_file_hash(photo_path)

        # Act: Check if needs reprocessing with same hash (should be False)
        needs_reprocessing_same = manager.needs_reprocessing(
            photo_path, previous_hash=actual_hash
        )

        # Act: Check if needs reprocessing with different hash (should be True)
        needs_reprocessing_different = manager.needs_reprocessing(
            photo_path, previous_hash="different_hash_value"
        )

        # Assert: Same hash = no reprocessing needed
        assert not needs_reprocessing_same, "Same hash should not trigger reprocessing"

        # Assert: Different hash = reprocessing needed
        assert needs_reprocessing_different, (
            "Different hash should trigger reprocessing"
        )

    def test_detect_mtime_changes(self, tmp_path, create_photo_with_exif):
        """Test detecting filesystem modification time changes from previous manifest."""
        # Arrange: Create a photo
        photo_path = create_photo_with_exif(
            tmp_path / "test.jpg", DateTimeOriginal="2024:10:05 14:30:45"
        )

        original_mtime = photo_path.stat().st_mtime

        from normpic.manager.manifest_manager import ManifestManager

        manager = ManifestManager()

        # Act: Check with same mtime (should not need reprocessing)
        needs_reprocessing_same = manager.needs_reprocessing(
            photo_path, previous_mtime=original_mtime
        )

        # Modify the file's mtime
        import time

        time.sleep(0.1)
        photo_path.touch()  # Updates mtime
        new_mtime = photo_path.stat().st_mtime

        # Verify mtime actually changed
        assert new_mtime > original_mtime

        # Act: Check with old mtime after file was touched (should need reprocessing)
        needs_reprocessing_changed = manager.needs_reprocessing(
            photo_path, previous_mtime=original_mtime
        )

        # Assert: Same mtime = no reprocessing needed
        assert not needs_reprocessing_same, "Same mtime should not trigger reprocessing"

        # Assert: Different mtime = reprocessing needed
        assert needs_reprocessing_changed, "Changed mtime should trigger reprocessing"

    def test_detect_config_changes(self, tmp_path):
        """Test detecting when config changes affect processing requirements."""
        from normpic.manager.manifest_manager import ManifestManager

        manager = ManifestManager()

        # Test with same collection names (should not affect processing)
        same_config_old = {"collection_name": "wedding"}
        same_config_new = {"collection_name": "wedding"}

        # Test with different collection names (affects filename generation)
        old_config = {"collection_name": "old_collection"}
        new_config = {"collection_name": "new_collection"}

        # Test with unrelated config changes (should not affect processing)
        unrelated_old = {"collection_name": "wedding", "some_other_field": "old_value"}
        unrelated_new = {"collection_name": "wedding", "some_other_field": "new_value"}

        # Act: Test different scenarios
        no_change = manager.config_affects_reprocessing(
            same_config_old, same_config_new
        )
        collection_change = manager.config_affects_reprocessing(old_config, new_config)
        unrelated_change = manager.config_affects_reprocessing(
            unrelated_old, unrelated_new
        )

        # Assert: Same collection name = no reprocessing
        assert not no_change, "Same collection name should not trigger reprocessing"

        # Assert: Different collection name = reprocessing needed
        assert collection_change, (
            "Different collection name should trigger reprocessing"
        )

        # Assert: Unrelated config changes = no reprocessing
        assert not unrelated_change, (
            "Unrelated config changes should not trigger reprocessing"
        )

    def test_detect_missing_destination_files(self, tmp_path, create_photo_with_exif):
        """Test detecting when destination symlink files are missing."""
        # Arrange: Create source photo
        source_path = create_photo_with_exif(
            tmp_path / "source.jpg", DateTimeOriginal="2024:10:05 14:30:45"
        )

        # Expected destination path (symlink that should exist)
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_path = dest_dir / "test-20241005T143045.jpg"

        from normpic.manager.manifest_manager import ManifestManager

        manager = ManifestManager()

        # Act: Test with missing destination file
        dest_missing_before = manager.destination_file_missing(source_path, dest_path)

        # Create symlink to source file
        dest_path.symlink_to(source_path)

        # Act: Test with existing correct symlink
        dest_missing_after = manager.destination_file_missing(source_path, dest_path)

        # Assert: Missing destination should be detected
        assert dest_missing_before, "Missing destination file should be detected"

        # Assert: Existing correct symlink should not be considered missing
        assert not dest_missing_after, (
            "Existing correct symlink should not be considered missing"
        )

    def test_unchanged_files_skipped(self, tmp_path, create_photo_with_exif):
        """Test that unchanged files are correctly identified as not needing reprocessing."""
        # Arrange: Create a photo
        photo_path = create_photo_with_exif(
            tmp_path / "unchanged.jpg", DateTimeOriginal="2024:10:05 14:30:45"
        )

        current_mtime = photo_path.stat().st_mtime

        from normpic.manager.manifest_manager import ManifestManager

        manager = ManifestManager()

        # Get the actual hash
        current_hash = manager.compute_file_hash(photo_path)

        # Act: Test with unchanged file (same mtime and hash)
        needs_reprocessing_unchanged = manager.needs_reprocessing(
            photo_path, previous_mtime=current_mtime, previous_hash=current_hash
        )

        # Act: Test with no previous data (should need processing)
        needs_reprocessing_no_data = manager.needs_reprocessing(photo_path)

        # Assert: Unchanged file should not need reprocessing
        assert not needs_reprocessing_unchanged, (
            "Unchanged file should not need reprocessing"
        )

        # Assert: File with no previous data should need processing
        assert needs_reprocessing_no_data, (
            "File with no previous data should need processing"
        )


_VALID_MANIFEST = {
    "version": "0.1.0",
    "collection_name": "test",
    "generated_at": "2024-01-01T00:00:00Z",
    "collection_root": ".",
    "pic": [
        {
            "hash": f"{PREFIX}PZDRE6BC90T0BS0FGG0ZM7Y9",
            "relative_path": "photo.jpg",
            "size_bytes": 1024,
            "mtime": "2024-01-01T00:00:00Z",
            "timestamp": None,
            "timestamp_source": None,
            "camera": None,
            "gps": None,
        }
    ],
}


class TestSourceManifestLoading:
    """Tests for load_source_manifest and build_source_manifest."""

    def test_source_manifest_absent(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        assert load_source_manifest(source_dir) is None

    def test_source_manifest_present_and_valid(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "manifest.json").write_text(
            json.dumps(_VALID_MANIFEST), encoding="utf-8"
        )

        with patch(
            "normpic.manager.manifest_manager.impl_validate",
            wraps=__import__(
                "normpic.util.manifest_validate", fromlist=["impl_validate"]
            ).impl_validate,
        ) as mock_iv:
            result = load_source_manifest(source_dir)

        assert result is not None
        assert result.collection_name == "test"
        mock_iv.assert_called_once()

    def test_source_manifest_present_schema_invalid(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        bad = {"version": "0.1.0", "pic": []}  # missing collection_name, generated_at
        (source_dir / "manifest.json").write_text(json.dumps(bad), encoding="utf-8")
        assert load_source_manifest(source_dir) is None

    def test_source_manifest_present_impl_invalid(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        bad = dict(_VALID_MANIFEST)
        bad["collection_root"] = "foo/../../../bar"  # non-leading dotdot
        (source_dir / "manifest.json").write_text(json.dumps(bad), encoding="utf-8")
        assert load_source_manifest(source_dir) is None

    def test_build_source_manifest_empty_dir(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        manifest = build_source_manifest(source_dir, "test-col")
        assert manifest.collection_name == "test-col"
        assert manifest.collection_root == "."
        assert manifest.pic == []

    def test_build_source_manifest_scans_photos(self, tmp_path, create_photo_with_exif):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        create_photo_with_exif(
            source_dir / "a.jpg", DateTimeOriginal="2024:01:01 00:00:00"
        )
        create_photo_with_exif(
            source_dir / "b.jpg", DateTimeOriginal="2024:01:01 00:00:01"
        )

        manifest = build_source_manifest(source_dir, "col")

        assert len(manifest.pic) == 2
        rel_paths = {p.relative_path for p in manifest.pic}
        assert "a.jpg" in rel_paths
        assert "b.jpg" in rel_paths
        for pic in manifest.pic:
            assert pic.mtime.endswith("Z")
            assert pic.relative_path is not None
            assert pic.relative_path in {"a.jpg", "b.jpg"}
            assert not pic.relative_path.startswith("/")
            assert not pic.relative_path.startswith("./")
            assert "\\" not in pic.relative_path
            assert ".." not in pic.relative_path.split("/")


def _make_manifest(pics):
    return Manifest(
        version="0.1.0",
        collection_name="test",
        generated_at=datetime.now(tz=timezone.utc),
        collection_root=".",
        pic=pics,
    )


def _make_pic(hash_val, size_bytes, mtime_str, relative_path=""):
    return Pic(
        hash=hash_val,
        size_bytes=size_bytes,
        mtime=mtime_str,
        relative_path=relative_path,
    )


class TestHashKeyedChangeDetection:
    """Tests for build_hash_keyed_source_index and needs_reprocessing_by_hash."""

    # --- Cycle 1: index building ---

    def test_index_basic(self):
        pic_a = _make_pic(
            "b3c32:AAAA", 100, "2024-01-01T00:00:00.000000Z", relative_path="a.jpg"
        )
        pic_b = _make_pic(
            "b3c32:BBBB", 200, "2024-01-01T00:00:00.000000Z", relative_path="b.jpg"
        )
        manifest = _make_manifest([pic_a, pic_b])
        index = build_hash_keyed_source_index(manifest)
        assert index["b3c32:AAAA"] is pic_a
        assert index["b3c32:BBBB"] is pic_b

    def test_index_empty_manifest(self):
        index = build_hash_keyed_source_index(_make_manifest([]))
        assert index == {}

    def test_index_duplicate_hash(self):
        pic_first = _make_pic(
            "b3c32:AAAA", 100, "2024-01-01T00:00:00.000000Z", relative_path="a.jpg"
        )
        pic_second = _make_pic(
            "b3c32:AAAA", 100, "2024-01-01T00:00:00.000000Z", relative_path="b.jpg"
        )
        manifest = _make_manifest([pic_first, pic_second])
        index = build_hash_keyed_source_index(manifest)
        assert index["b3c32:AAAA"] is pic_first

    # --- Cycle 2: per-photo detection ---

    def test_not_in_index(self):
        manager = ManifestManager()
        index = {}
        assert manager.needs_reprocessing_by_hash("b3c32:ZZZZ", index, 1000.0) is True

    def test_unchanged(self, tmp_path):
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_file = dest_dir / "a.jpg"
        dest_file.touch()

        mtime_str = "2024-01-01T00:00:00.000000Z"
        prev_mtime = datetime.fromisoformat(mtime_str).timestamp()
        pic = _make_pic("b3c32:AAAA", 100, mtime_str, relative_path="a.jpg")
        index = {"b3c32:AAAA": pic}

        manager = ManifestManager()
        assert (
            manager.needs_reprocessing_by_hash(
                "b3c32:AAAA", index, prev_mtime, dest_dir=dest_dir
            )
            is False
        )

    def test_mtime_changed(self):
        mtime_str = "2020-01-01T00:00:00.000000Z"
        prev_mtime = datetime.fromisoformat(mtime_str).timestamp()
        pic = _make_pic("b3c32:AAAA", 100, mtime_str, relative_path="a.jpg")
        index = {"b3c32:AAAA": pic}

        manager = ManifestManager()
        current_mtime = prev_mtime + 1.0
        assert (
            manager.needs_reprocessing_by_hash("b3c32:AAAA", index, current_mtime)
            is True
        )

    def test_mtime_roundtrip_no_false_changed(self, tmp_path):
        """st_mtime through ISO round-trip must not produce a false CHANGED."""
        photo = tmp_path / "photo.jpg"
        photo.write_bytes(b"roundtrip test content")

        manager = ManifestManager()
        _fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

        # Reproduce what the manifest-writing path does
        st_mtime = photo.stat().st_mtime
        mtime_iso = datetime.fromtimestamp(st_mtime, tz=timezone.utc).strftime(_fmt)

        # needs_reprocessing: previous_mtime arrives as ISO-parsed float
        previous_mtime = datetime.fromisoformat(mtime_iso).timestamp()
        assert (
            manager.needs_reprocessing(
                photo,
                previous_hash=manager.compute_file_hash(photo),
                previous_mtime=previous_mtime,
            )
            is False
        )

        # needs_reprocessing_by_hash: current_mtime is the raw st_mtime float;
        # matched.mtime is the strftime ISO string (same float, same origin)
        hash_val = manager.compute_file_hash(photo)
        pic = _make_pic(
            hash_val, photo.stat().st_size, mtime_iso, relative_path="dest.jpg"
        )
        assert (
            manager.needs_reprocessing_by_hash(hash_val, {hash_val: pic}, st_mtime)
            is False
        )

        # Stored-string path: save the manifest to disk and reload it so that
        # matched.mtime arrives as a string from JSON, not from a float in this
        # test scope -- exercises fromisoformat().timestamp()->fromtimestamp() path
        manifest_path = tmp_path / "test_manifest.json"
        ManifestManager(manifest_path).save_manifest(_make_manifest([pic]))
        loaded = ManifestManager(manifest_path).load_manifest()
        assert loaded is not None
        loaded_pic = loaded.pic[0]
        assert (
            manager.needs_reprocessing_by_hash(
                hash_val, {hash_val: loaded_pic}, st_mtime
            )
            is False
        )

    def test_dest_missing(self, tmp_path):
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        # dest_dir / "a.jpg" is NOT created

        mtime_str = "2024-01-01T00:00:00.000000Z"
        prev_mtime = datetime.fromisoformat(mtime_str).timestamp()
        pic = _make_pic("b3c32:AAAA", 100, mtime_str, relative_path="a.jpg")
        index = {"b3c32:AAAA": pic}

        manager = ManifestManager()
        assert (
            manager.needs_reprocessing_by_hash(
                "b3c32:AAAA", index, prev_mtime, dest_dir=dest_dir
            )
            is True
        )

    def test_dest_check_uses_relative_path(self, tmp_path):
        """dest-existence check resolves via relative_path, not dest_path."""
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        # Only the relative_path target exists; dest_path target does not.
        (dest_dir / "b.jpg").touch()

        mtime_str = "2024-01-01T00:00:00.000000Z"
        prev_mtime = datetime.fromisoformat(mtime_str).timestamp()
        pic = Pic(
            relative_path="b.jpg",
            hash="b3c32:AAAA",
            size_bytes=100,
            mtime=mtime_str,
        )
        index = {"b3c32:AAAA": pic}

        manager = ManifestManager()
        # relative_path target ("b.jpg") exists; discriminates that the check
        # uses relative_path and not some other field. Correct behavior: False.
        assert (
            manager.needs_reprocessing_by_hash(
                "b3c32:AAAA", index, prev_mtime, dest_dir=dest_dir
            )
            is False
        )

    # --- Cycle 4: equivalence test ---

    def test_hash_keyed_change_detection_categorizes_correctly(self, tmp_path):
        """Hash-keyed detection correctly partitions new, stale, dest-missing, unchanged.

        Four source files against a prior manifest:
        - A: unchanged (hash hit, current mtime, dest exists)
        - B: stale mtime (hash hit, mtime differs)
        - C: new (no hash in manifest)
        - D: dest missing (hash hit, current mtime, but dest absent)
        Expected: only A is unchanged; B, C, D need reprocessing.
        """
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        manager = ManifestManager()

        # Create four source files with distinct content
        path_a = source_dir / "a.jpg"
        path_b = source_dir / "b.jpg"
        path_c = source_dir / "c.jpg"
        path_d = source_dir / "d.jpg"
        path_a.write_bytes(b"content-alpha")
        path_b.write_bytes(b"content-beta")
        path_c.write_bytes(b"content-gamma")
        path_d.write_bytes(b"content-delta")

        hash_a = manager.compute_file_hash(path_a)
        hash_b = manager.compute_file_hash(path_b)
        hash_d = manager.compute_file_hash(path_d)

        mtime_a = path_a.stat().st_mtime
        mtime_d = path_d.stat().st_mtime

        mtime_a_str = datetime.fromtimestamp(mtime_a, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        mtime_d_str = datetime.fromtimestamp(mtime_d, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        stale_mtime = "2020-01-01T00:00:00.000000Z"

        # Prior manifest: A (unchanged), B (stale mtime), D (dest missing).
        # C is absent -- it is NEW.
        prior_manifest = _make_manifest(
            [
                _make_pic(
                    hash_a,
                    path_a.stat().st_size,
                    mtime_a_str,
                    relative_path="dest_a.jpg",
                ),
                _make_pic(
                    hash_b,
                    path_b.stat().st_size,
                    stale_mtime,
                    relative_path="dest_b.jpg",
                ),
                _make_pic(
                    hash_d,
                    path_d.stat().st_size,
                    mtime_d_str,
                    relative_path="dest_d.jpg",
                ),
            ]
        )

        # Dest files: A exists, B exists (stale mtime still means reprocess), D missing
        (dest_dir / "dest_a.jpg").touch()
        (dest_dir / "dest_b.jpg").touch()
        # dest_dir / "dest_d.jpg" intentionally absent

        source_photos = [path_a, path_b, path_c, path_d]

        hash_index = build_hash_keyed_source_index(prior_manifest)
        needs, unchanged = [], []
        for photo_path in source_photos:
            current_hash = manager.compute_file_hash(photo_path)
            current_mtime = photo_path.stat().st_mtime
            if not manager.needs_reprocessing_by_hash(
                current_hash, hash_index, current_mtime, dest_dir=dest_dir
            ):
                unchanged.append(photo_path.name)
            else:
                needs.append(photo_path.name)

        assert set(unchanged) == {"a.jpg"}, f"unchanged={set(unchanged)}"
        assert set(needs) == {"b.jpg", "c.jpg", "d.jpg"}, f"needs={set(needs)}"


class TestCopyManifestRelativePath:
    """Tests for relative_path field on copy-manifest Pic objects."""

    def _base_pic(self, **kwargs):
        return Pic(
            hash=kwargs.get("hash", "b3c32:AAAAAAAAAAAAAAAAAAAAAAAA"),
            size_bytes=kwargs.get("size_bytes", 1024),
            mtime=kwargs.get("mtime", "2024-01-01T00:00:00.000000Z"),
            relative_path=kwargs.get("relative_path", "photo.jpg"),
        )

    def test_relative_path_emitted_when_set(self):
        organized = "wedding-20241005T143045-r5a.jpg"
        pic = self._base_pic(relative_path=organized)
        d = pic.to_dict()
        assert "relative_path" in d
        assert d["relative_path"] == organized

    def test_relative_path_canonical_form(self):
        # A normal organized filename must satisfy all canonical-path rules:
        # no leading ./, no .., no backslash, no absolute prefix.
        organized = "wedding-20241005T143045-r5a.jpg"
        pic = self._base_pic(relative_path=organized)
        d = pic.to_dict()
        rp = d["relative_path"]
        assert not rp.startswith("/"), "must not be absolute"
        assert not rp.startswith("./"), "must not have leading ./"
        assert "\\" not in rp, "must not contain backslash"
        assert ".." not in rp.split("/"), "must not contain .. segment"
        assert "//" not in rp, "must not have empty segments"

    def test_schema_rejects_non_canonical_relative_path(self):
        import json
        from jsonschema import validate, ValidationError
        import pytest

        _manifest_schema = json.loads(SCHEMA_PATH.read_text())

        bad_values = [
            "./wedding-20241005T143045-r5a.jpg",  # leading ./
            "/abs/path.jpg",  # absolute
            "foo/../bar.jpg",  # .. segment
            "foo//bar.jpg",  # empty segment
            "foo\\bar.jpg",  # backslash
        ]
        base = {
            "hash": "b3c32:AAAAAAAAAAAAAAAAAAAAAAAA",
            "size_bytes": 1,
            "mtime": "2024-01-01T00:00:00Z",
        }
        manifest_wrapper = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-01-01T00:00:00Z",
        }
        for bad in bad_values:
            with pytest.raises(ValidationError):
                validate(
                    instance={
                        **manifest_wrapper,
                        "pic": [{**base, "relative_path": bad}],
                    },
                    schema=_manifest_schema,
                )
