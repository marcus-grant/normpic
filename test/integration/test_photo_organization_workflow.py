"""Integration tests for complete photo organization workflow with manifest generation."""

import pytest
from datetime import datetime, timezone
from pathlib import Path

# These imports will fail initially - that's the point of TDD
from normpic.manager.photo_manager import organize_photos, resolve_symlink_pairs_by_hash
from normpic.manager.manifest_manager import ManifestManager
from normpic.model.manifest import Manifest
from normpic.model.pic import Pic
from normpic.serializer.manifest import ManifestSerializer


class TestPhotoOrganizationWorkflow:
    """Integration tests for end-to-end photo organization and manifest generation."""

    def test_mixed_cameras_temporal_ordering_with_manifest(
        self, create_photo_with_exif, tmp_path
    ):
        """Test: Multiple cameras → proper temporal ordering → complete manifest."""

        # Arrange: Create photos from different cameras with controlled timestamps
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Canon R5 photos (wedding collection)
        canon_early = create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="123",
            Make="Canon",
            Model="EOS R5",
        )

        canon_late = create_photo_with_exif(
            source_dir / "IMG_002.jpg",
            DateTimeOriginal="2024:10:05 14:30:47",
            SubSecTimeOriginal="456",
            Make="Canon",
            Model="EOS R5",
        )

        # iPhone photo between Canon photos
        iphone_middle = create_photo_with_exif(
            source_dir / "IMG_3456.heic",
            DateTimeOriginal="2024:10:05 14:30:46",
            SubSecTimeOriginal="789",
            Make="Apple",
            Model="iPhone 15 Pro",
        )

        # Nikon without subsecond (same time as canon_late)
        nikon_conflict = create_photo_with_exif(
            source_dir / "DSC_0001.jpg",
            DateTimeOriginal="2024:10:05 14:30:47",
            # No SubSecTimeOriginal
            Make="Nikon",
            Model="D850",
        )

        # Act: Organize photos and generate manifest
        manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="wedding",
            collection_description="Wedding ceremony photos",
        )

        # Assert: Verify proper temporal ordering in manifest
        assert len(manifest.pic) == 4

        # Expected order: canon_early → iphone_middle → canon_late → nikon_conflict
        # (EXIF timestamp with subsec precedence, then filename for conflicts)
        expected_order = [
            ("wedding-20241005T143045-r5a.jpg", canon_early),  # 14:30:45.123
            ("wedding-20241005T143046-i15.heic", iphone_middle),  # 14:30:46.789
            (
                "wedding-20241005T143047-d85.jpg",
                nikon_conflict,
            ),  # 14:30:47 (no subsec, different camera from canon)
            (
                "wedding-20241005T143047-r5a.jpg",
                canon_late,
            ),  # 14:30:47.456 (same timestamp but different camera from nikon)
        ]

        for i, (expected_filename, source_photo) in enumerate(expected_order):
            pic = manifest.pic[i]
            assert pic.dest_path == expected_filename
            assert pic.source_path == str(source_photo)
            assert pic.timestamp_source == "exif"

        # Assert: Verify manifest metadata
        assert manifest.collection_name == "wedding"
        assert manifest.collection_description == "Wedding ceremony photos"
        assert manifest.version.startswith("0.")
        assert isinstance(manifest.generated_at, datetime)

        # Assert: Verify symlinks created
        for pic in manifest.pic:
            dest_file = dest_dir / pic.dest_path
            assert dest_file.exists()
            assert dest_file.is_symlink()
            assert dest_file.readlink() == Path(pic.source_path)

        # Assert: Verify manifest.json written
        manifest_file = dest_dir / "manifest.json"
        assert manifest_file.exists()

        # Verify manifest round-trip serialization
        serializer = ManifestSerializer()
        manifest_json = manifest_file.read_text()
        deserialized = serializer.deserialize(manifest_json)
        assert len(deserialized.pic) == 4
        assert deserialized.collection_name == "wedding"

    def test_burst_sequence_preservation(self, create_photo_with_exif, tmp_path):
        """Test: Burst sequences from same camera stay adjacent despite interrupting timestamps."""

        # Arrange: Canon burst interrupted by iPhone
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Canon burst start
        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="100",
            Make="Canon",
            Model="EOS R5",
        )

        # iPhone interrupts chronologically
        create_photo_with_exif(
            source_dir / "IMG_3456.heic",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="200",  # Chronologically between burst photos
            Make="Apple",
            Model="iPhone 15 Pro",
        )

        # Canon burst continues
        create_photo_with_exif(
            source_dir / "IMG_002.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="300",
            Make="Canon",
            Model="EOS R5",
        )

        create_photo_with_exif(
            source_dir / "IMG_003.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="400",
            Make="Canon",
            Model="EOS R5",
        )

        # Act: Organize photos
        manifest = organize_photos(
            source_dir=source_dir, dest_dir=dest_dir, collection_name="sports"
        )

        # Assert: Canon burst photos are adjacent (burst preservation)
        # iPhone should not interrupt the Canon sequence
        canon_pics = [pic for pic in manifest.pic if "r5a" in pic.dest_path]
        assert len(canon_pics) == 3

        # Canon pics should be consecutive in manifest.pic
        canon_positions = [manifest.pic.index(pic) for pic in canon_pics]
        assert canon_positions == [0, 1, 2] or canon_positions == [1, 2, 3]

        # Verify burst counter progression
        for i, pic in enumerate(canon_pics):
            expected_counter = str(i)  # Base32: 0, 1, 2
            assert f"-{expected_counter}.jpg" in pic.dest_path

    def test_fallback_ordering_without_exif(self, tmp_path):
        """Test: Photos without EXIF use filename → mtime ordering."""

        # Arrange: Photos without EXIF data
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        # Create files with controlled names and modification times
        photo1 = source_dir / "photo_z_last.jpg"
        photo2 = source_dir / "photo_a_first.jpg"
        photo3 = source_dir / "photo_m_middle.jpg"

        # Write photos (no EXIF)
        photo1.write_bytes(b"fake_jpeg_data_1")
        photo2.write_bytes(b"fake_jpeg_data_2")
        photo3.write_bytes(b"fake_jpeg_data_3")

        # Set different modification times (reverse of filename order)
        import os
        import time

        base_time = time.time() - 1000
        os.utime(photo1, (base_time, base_time))  # Oldest mtime
        os.utime(photo3, (base_time + 100, base_time + 100))  # Middle mtime
        os.utime(photo2, (base_time + 200, base_time + 200))  # Newest mtime

        # Act: Organize photos
        manifest = organize_photos(
            source_dir=source_dir, dest_dir=dest_dir, collection_name="no-exif"
        )

        # Assert: Filename ordering takes precedence over mtime
        # Expected order: photo_a_first → photo_m_middle → photo_z_last
        assert len(manifest.pic) == 3

        filenames = [Path(pic.source_path).name for pic in manifest.pic]
        assert filenames == [
            "photo_a_first.jpg",
            "photo_m_middle.jpg",
            "photo_z_last.jpg",
        ]

        # All should have timestamp_source="filename" since no EXIF
        for pic in manifest.pic:
            assert pic.timestamp_source == "filename"
            assert pic.camera is None  # No EXIF camera data

    def test_copy_manifest_pics_carry_relative_path(
        self, create_photo_with_exif, tmp_path
    ):
        """Each organized pic carries relative_path equal to its bare dest filename."""
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:06:01 10:00:00",
            Make="Canon",
            Model="EOS R5",
        )
        create_photo_with_exif(
            source_dir / "IMG_002.jpg",
            DateTimeOriginal="2024:06:01 10:00:01",
            Make="Canon",
            Model="EOS R5",
        )

        manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="summer",
        )

        assert len(manifest.pic) == 2
        for pic in manifest.pic:
            assert pic.relative_path is not None, f"relative_path missing on {pic.dest_path}"
            assert pic.relative_path == pic.dest_path, (
                f"relative_path {pic.relative_path!r} != dest_path {pic.dest_path!r}"
            )
            # Canonical-form guard: bare filename must satisfy contract rules
            rp = pic.relative_path
            assert not rp.startswith("/")
            assert not rp.startswith("./")
            assert "\\" not in rp
            assert ".." not in rp.split("/")

        # Round-trip: relative_path must survive JSON serialization
        serializer = ManifestSerializer()
        manifest_json = (dest_dir / "manifest.json").read_text()
        loaded = serializer.deserialize(manifest_json)
        for orig, loaded_pic in zip(manifest.pic, loaded.pic):
            assert loaded_pic.relative_path == orig.relative_path

    def test_hash_keyed_reprocessing_recognizes_content_at_new_path(
        self, create_photo_with_exif, tmp_path
    ):
        """Content-identical file at a different source path is recognized as unchanged.

        Discriminating observable: source_path in the returned manifest.
        Under source_path-keying the phantom key misses, the file is reprocessed,
        and source_path becomes str(actual source path).
        Under hash-keying the hash hits, the old pic is reused, and source_path
        stays as the phantom value.
        """
        import json as _json

        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        real_hash = ManifestManager().compute_file_hash(source_dir / "IMG_001.jpg")
        stat = (source_dir / "IMG_001.jpg").stat()
        mtime_str = datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        phantom_source_path = "/phantom/original/path.jpg"
        dest_filename = "existing-dest.jpg"
        fake_manifest = {
            "version": "0.1.0",
            "collection_name": "test",
            "generated_at": "2024-10-05T14:30:45.000000Z",
            "collection_root": ".",
            "pic": [{
                "source_path": phantom_source_path,
                "dest_path": dest_filename,
                "relative_path": dest_filename,
                "hash": real_hash,
                "size_bytes": stat.st_size,
                "mtime": mtime_str,
                "timestamp": None,
                "timestamp_source": None,
                "camera": None,
                "gps": None,
                "errors": [],
            }],
        }
        (dest_dir / "manifest.json").write_text(_json.dumps(fake_manifest))
        (dest_dir / dest_filename).symlink_to((source_dir / "IMG_001.jpg").resolve())

        manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="test",
        )

        assert len(manifest.pic) == 1
        assert manifest.pic[0].source_path == phantom_source_path, (
            f"Expected source_path={phantom_source_path!r}, "
            f"got={manifest.pic[0].source_path!r}. "
            "Source_path-keying misses the phantom key and reprocesses the file; "
            "hash-keying finds the hash and reuses the old pic."
        )

    def test_stat_skip_prevents_rehash_for_unchanged_file(
        self, create_photo_with_exif, tmp_path
    ):
        """An unchanged file (same path, mtime, size) is not rehashed on a second run.

        Discriminating observable: total b2b120_hash calls across photo_manager
        and manifest_manager on the second run.
        Current code: 1 (manifest_manager.needs_reprocessing hash-verifies).
        Hash-keyed without stat-skip: 1 (detection loop computes hash).
        Hash-keyed with stat-skip: 0 (stored hash reused; no file read).
        """
        import normpic.manager.photo_manager as _pm
        import normpic.manager.manifest_manager as _mm
        from unittest.mock import patch

        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="test",
        )

        real_pm_hash = _pm.b2b120_hash
        real_mm_hash = _mm.b2b120_hash

        with (
            patch.object(_pm, "b2b120_hash", wraps=real_pm_hash) as mock_pm,
            patch.object(_mm, "b2b120_hash", wraps=real_mm_hash) as mock_mm,
        ):
            organize_photos(
                source_dir=source_dir,
                dest_dir=dest_dir,
                collection_name="test",
            )

        total = mock_pm.call_count + mock_mm.call_count
        assert total == 0, (
            f"Stat-skip should prevent all rehashing for an unchanged file; "
            f"got {mock_pm.call_count} photo_manager + "
            f"{mock_mm.call_count} manifest_manager = {total} calls"
        )


class TestSymlinkReconciliationByHash:
    """Equivalence tests for resolve_symlink_pairs_by_hash."""

    def _make_mtime_str(self, f: Path) -> str:
        """Format a file's mtime as the manifest ISO string."""
        return datetime.fromtimestamp(
            f.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def test_hash_reconciliation_agrees_with_stored_paths(self, tmp_path):
        """Hand-built fixture: hash-reconciled pairs equal stored-field pairs."""
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        src_a = source_dir / "IMG_001.jpg"
        src_b = source_dir / "IMG_002.jpg"
        src_a.write_bytes(b"content-alpha")
        src_b.write_bytes(b"content-beta")

        manager = ManifestManager()
        hash_a = manager.compute_file_hash(src_a)
        hash_b = manager.compute_file_hash(src_b)

        source_manifest = Manifest(
            version="0.1.0",
            collection_name="test",
            generated_at=datetime.now(tz=timezone.utc),
            collection_root=".",
            pic=[
                Pic(
                    source_path=str(src_a),
                    dest_path=str(src_a),
                    hash=hash_a,
                    size_bytes=src_a.stat().st_size,
                    mtime=self._make_mtime_str(src_a),
                    relative_path=src_a.name,
                ),
                Pic(
                    source_path=str(src_b),
                    dest_path=str(src_b),
                    hash=hash_b,
                    size_bytes=src_b.stat().st_size,
                    mtime=self._make_mtime_str(src_b),
                    relative_path=src_b.name,
                ),
            ],
        )

        copy_pics = [
            Pic(
                source_path=str(src_a),
                dest_path="col-001.jpg",
                hash=hash_a,
                size_bytes=src_a.stat().st_size,
                mtime=self._make_mtime_str(src_a),
                relative_path="col-001.jpg",
            ),
            Pic(
                source_path=str(src_b),
                dest_path="col-002.jpg",
                hash=hash_b,
                size_bytes=src_b.stat().st_size,
                mtime=self._make_mtime_str(src_b),
                relative_path="col-002.jpg",
            ),
        ]

        old_pairs = [
            (Path(p.source_path).resolve(), dest_dir / p.dest_path)
            for p in copy_pics
        ]
        new_pairs = resolve_symlink_pairs_by_hash(
            source_manifest, source_dir, copy_pics, dest_dir
        )

        assert new_pairs == old_pairs

    def test_hash_reconciliation_agrees_with_producer_generated(
        self, create_photo_with_exif, tmp_path
    ):
        """Producer-generated manifests: hash-reconciled pairs equal stored-field pairs."""
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:06:01 10:00:00",
            Make="Canon",
            Model="EOS R5",
        )
        create_photo_with_exif(
            source_dir / "IMG_002.jpg",
            DateTimeOriginal="2024:06:01 10:00:01",
            Make="Canon",
            Model="EOS R5",
        )

        copy_manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="wedding",
        )

        source_manifest = ManifestSerializer().deserialize(
            (source_dir / "manifest.json").read_text()
        )

        old_pairs = [
            (Path(p.source_path).resolve(), dest_dir / p.dest_path)
            for p in copy_manifest.pic
        ]
        new_pairs = resolve_symlink_pairs_by_hash(
            source_manifest, source_dir, copy_manifest.pic, dest_dir
        )

        assert new_pairs == old_pairs

    def test_no_source_match_raises(self, tmp_path):
        """Copy pic whose hash is absent from source index raises RuntimeError."""
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        source_manifest = Manifest(
            version="0.1.0",
            collection_name="test",
            generated_at=datetime.now(tz=timezone.utc),
            collection_root=".",
            pic=[],
        )

        orphan = Pic(
            source_path="/src/orphan.jpg",
            dest_path="orphan-copy.jpg",
            hash="b2b120:ZZZZZZZZZZZZZZZZZZZZZZZZ",
            size_bytes=1,
            mtime="2024-01-01T00:00:00.000000Z",
            relative_path="orphan-copy.jpg",
        )

        import pytest
        with pytest.raises(RuntimeError, match="no source match for hash"):
            resolve_symlink_pairs_by_hash(
                source_manifest, source_dir, [orphan], dest_dir
            )


class TestProducerConformance:
    """Producer output must satisfy the canonical schema/v0.1.0.json contract."""

    def _organize(self, create_photo_with_exif, tmp_path):
        """Run organize_photos on a single photo; return (manifest_json, dest_dir)."""
        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()
        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:06:01 10:00:00",
            Make="Canon",
            Model="EOS R5",
        )
        organize_photos(source_dir=source_dir, dest_dir=dest_dir, collection_name="test")
        return (dest_dir / "manifest.json").read_text(), dest_dir

    def test_generated_at_is_utc_z(self, create_photo_with_exif, tmp_path):
        """Producer must emit generated_at with mandatory Z suffix (UTC canonical form)."""
        import json as _json
        manifest_text, _ = self._organize(create_photo_with_exif, tmp_path)
        data = _json.loads(manifest_text)
        assert data["generated_at"].endswith("Z"), (
            f"generated_at must end with Z, got: {data['generated_at']!r}"
        )

    def test_producer_validates_canonical_schema(self, create_photo_with_exif, tmp_path):
        """Producer output must validate against schema/v0.1.0.json."""
        import json as _json
        from jsonschema import validate as _validate
        from pathlib import Path as _Path
        manifest_text, _ = self._organize(create_photo_with_exif, tmp_path)
        data = _json.loads(manifest_text)
        schema_path = _Path(__file__).parent.parent.parent / "schema" / "v0.1.0.json"
        schema = _json.loads(schema_path.read_text())
        _validate(instance=data, schema=schema)


class TestCutoverAcceptanceGate:
    """Acceptance gate for ref/drop-source-dest-cutover. Unskip as the final step."""

    @pytest.mark.skip(reason="unskip at cutover completion")
    def test_cutover_complete_relative_path_only(
        self, create_photo_with_exif, tmp_path
    ):
        """Defines the cutover end state. Must pass green when the skip is removed.

        Asserts:
        - No source_path, dest_path, or errors on any pic in serialized output.
        - All pics carry relative_path.
        - Symlinks created and not dangling; count matches pic count.
        - Second run over same dest: unchanged pics skipped via hash-keyed
          reprocessing with those fields absent, proving reprocessing needs
          no source_path.
        - Output validates against schema/v0.1.0.json.
        - Deserialize over a manifest lacking source_path/dest_path raises no error.
        """
        import json as _json
        from jsonschema import validate as _validate
        from pathlib import Path as _Path

        source_dir = tmp_path / "source"
        dest_dir = tmp_path / "dest"
        source_dir.mkdir()
        dest_dir.mkdir()

        create_photo_with_exif(
            source_dir / "IMG_001.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )
        create_photo_with_exif(
            source_dir / "IMG_002.jpg",
            DateTimeOriginal="2024:10:05 14:30:46",
            Make="Canon",
            Model="EOS R5",
        )

        manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="cutover-gate",
        )

        assert len(manifest.pic) == 2

        manifest_path = dest_dir / "manifest.json"
        manifest_text = manifest_path.read_text()
        data = _json.loads(manifest_text)

        forbidden = {"source_path", "dest_path", "errors"}
        for pic_data in data["pic"]:
            present = forbidden & set(pic_data.keys())
            assert not present, f"Dropped fields still in output: {present}"
            assert "relative_path" in pic_data

        symlinks = [dest_dir / pic_data["relative_path"] for pic_data in data["pic"]]
        for link in symlinks:
            assert link.exists(), f"Symlink missing or dangling: {link}"
            assert link.is_symlink()
        assert len(symlinks) == 2

        schema_path = _Path(__file__).parent.parent.parent / "schema" / "v0.1.0.json"
        schema = _json.loads(schema_path.read_text())
        _validate(instance=data, schema=schema)

        manifest2 = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name="cutover-gate",
        )

        assert len(manifest2.pic) == 2
        data2 = _json.loads((dest_dir / "manifest.json").read_text())
        for pic_data in data2["pic"]:
            present = forbidden & set(pic_data.keys())
            assert not present, f"Dropped fields in second-run output: {present}"

        serializer = ManifestSerializer()
        loaded = serializer.deserialize(manifest_text)
        assert len(loaded.pic) == 2
        for pic in loaded.pic:
            assert pic.relative_path is not None
