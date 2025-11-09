"""Integration tests for complete photo organization workflow with manifest generation."""

from datetime import datetime
from pathlib import Path

# These imports will fail initially - that's the point of TDD
from src.manager.photo_manager import organize_photos
from src.serializer.manifest import ManifestSerializer


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
        assert len(manifest.pics) == 4

        # Expected order: canon_early → iphone_middle → canon_late → nikon_conflict
        # (EXIF timestamp with subsec precedence, then filename for conflicts)
        expected_order = [
            ("wedding-20241005T143045-r5a-0.jpg", canon_early),  # 14:30:45.123
            ("wedding-20241005T143046-i15-0.jpg", iphone_middle),  # 14:30:46.789
            (
                "wedding-20241005T143047-d85-0.jpg",
                nikon_conflict,
            ),  # 14:30:47 (no subsec, filename DSC < IMG)
            (
                "wedding-20241005T143047-r5a-0.jpg",
                canon_late,
            ),  # 14:30:47.456 (same timestamp different cameras)
        ]

        for i, (expected_filename, source_photo) in enumerate(expected_order):
            pic = manifest.pics[i]
            assert pic.dest_path == expected_filename
            assert pic.source_path == str(source_photo)
            assert pic.timestamp_source == "exif"

        # Assert: Verify manifest metadata
        assert manifest.collection_name == "wedding"
        assert manifest.collection_description == "Wedding ceremony photos"
        assert manifest.version.startswith("0.")
        assert isinstance(manifest.generated_at, datetime)

        # Assert: Verify symlinks created
        for pic in manifest.pics:
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
        assert len(deserialized.pics) == 4
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
        canon_pics = [pic for pic in manifest.pics if "r5a" in pic.dest_path]
        assert len(canon_pics) == 3

        # Canon pics should be consecutive in manifest.pics
        canon_positions = [manifest.pics.index(pic) for pic in canon_pics]
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
        assert len(manifest.pics) == 3

        filenames = [Path(pic.source_path).name for pic in manifest.pics]
        assert filenames == [
            "photo_a_first.jpg",
            "photo_m_middle.jpg",
            "photo_z_last.jpg",
        ]

        # All should have timestamp_source="filename" since no EXIF
        for pic in manifest.pics:
            assert pic.timestamp_source == "filename"
            assert pic.camera is None  # No EXIF camera data
