"""Unit tests for pic organization logic."""

from datetime import datetime
from pathlib import Path


# These imports will fail initially - TDD approach
from src.manager.photo_manager import _order_photos_temporally, _create_ordered_pics
from src.model.pic import Pic
from src.model.exif import ExifData, CameraInfo


class TestDeterminePicOrder:
    """Test ordering algorithm: EXIF timestamp → filename → mtime."""

    def test_exif_timestamp_precedence(self):
        """Test: EXIF timestamps take precedence over filename/mtime."""

        # Arrange: Two photos with different EXIF timestamps
        early_photo = Path("later_filename.jpg")  # Filename suggests later
        late_photo = Path("earlier_filename.jpg")  # Filename suggests earlier

        early_exif = ExifData(
            timestamp=datetime(2024, 10, 5, 14, 30, 45), subsecond=123
        )
        late_exif = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 47), subsecond=456)

        pics_data = [
            (late_photo, late_exif, CameraInfo()),  # Later timestamp, earlier filename
            (
                early_photo,
                early_exif,
                CameraInfo(),
            ),  # Earlier timestamp, later filename
        ]

        # Act: Determine order
        ordered_pics = _order_photos_temporally(pics_data)

        # Assert: EXIF timestamp order (early → late), ignoring filename
        assert ordered_pics[0][0] == early_photo
        assert ordered_pics[1][0] == late_photo

    def test_subsecond_precision_ordering(self):
        """Test: Subsecond timestamps provide finer ordering."""

        # Arrange: Same main timestamp, different subseconds
        photo1 = Path("photo1.jpg")
        photo2 = Path("photo2.jpg")

        base_timestamp = datetime(2024, 10, 5, 14, 30, 45)
        exif1 = ExifData(timestamp=base_timestamp, subsecond=100)  # Earlier subsec
        exif2 = ExifData(timestamp=base_timestamp, subsecond=200)  # Later subsec

        pics_data = [
            (photo2, exif2, CameraInfo()),  # Later subsec first in list
            (photo1, exif1, CameraInfo()),  # Earlier subsec second in list
        ]

        # Act: Determine order
        ordered_pics = _order_photos_temporally(pics_data)

        # Assert: Subsecond ordering (100 → 200)
        assert ordered_pics[0] == (photo1, exif1, CameraInfo())  # 100 subsec first
        assert ordered_pics[1] == (photo2, exif2, CameraInfo())  # 200 subsec second

    def test_filename_fallback_when_no_exif(self):
        """Test: Filename ordering when EXIF timestamps missing."""

        # Arrange: Photos without EXIF timestamps
        photo_z = Path("z_last.jpg")
        photo_a = Path("a_first.jpg")
        photo_m = Path("m_middle.jpg")

        no_exif = ExifData()  # No timestamp

        pics_data = [
            (photo_z, no_exif, CameraInfo()),  # Last alphabetically
            (photo_a, no_exif, CameraInfo()),  # First alphabetically
            (photo_m, no_exif, CameraInfo()),  # Middle alphabetically
        ]

        # Act: Determine order
        ordered_pics = _order_photos_temporally(pics_data)

        # Assert: Alphabetical filename order
        expected_order = [photo_a, photo_m, photo_z]
        actual_order = [pic_data[0] for pic_data in ordered_pics]
        assert actual_order == expected_order

    def test_mixed_exif_and_no_exif_ordering(self):
        """Test: Photos with EXIF come first, then filename ordering."""

        # Arrange: Mix of EXIF and non-EXIF photos
        exif_photo = Path("z_has_exif.jpg")
        no_exif_1 = Path("a_no_exif.jpg")
        no_exif_2 = Path("b_no_exif.jpg")

        early_exif = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))
        no_timestamp = ExifData()  # No timestamp

        pics_data = [
            (no_exif_2, no_timestamp, CameraInfo()),  # No EXIF, later filename
            (exif_photo, early_exif, CameraInfo()),  # Has EXIF timestamp
            (no_exif_1, no_timestamp, CameraInfo()),  # No EXIF, earlier filename
        ]

        # Act: Determine order
        ordered_pics = _order_photos_temporally(pics_data)

        # Assert: EXIF photo first, then alphabetical no-EXIF
        expected_order = [exif_photo, no_exif_1, no_exif_2]
        actual_order = [pic_data[0] for pic_data in ordered_pics]
        assert actual_order == expected_order


class TestGroupByBurstSequence:
    """Test burst sequence detection and grouping."""

    def test_single_camera_burst_stays_together(self):
        """Test: Photos from same camera at same time form burst sequence."""

        # Arrange: Canon burst sequence with same base timestamp
        base_time = datetime(2024, 10, 5, 14, 30, 45)
        canon_camera_info = CameraInfo(make="Canon", model="EOS R5")
        canon_pics = [
            (
                Path("IMG_001.jpg"),
                ExifData(timestamp=base_time, subsecond=100),
                canon_camera_info,
            ),
            (
                Path("IMG_002.jpg"),
                ExifData(timestamp=base_time, subsecond=200),
                canon_camera_info,
            ),
            (
                Path("IMG_003.jpg"),
                ExifData(timestamp=base_time, subsecond=300),
                canon_camera_info,
            ),
        ]

        # Act: Group by burst sequence - test the actual workflow function instead
        from src.manager.photo_manager import _order_photos_with_burst_preservation

        ordered_pics = _order_photos_with_burst_preservation(canon_pics)

        # Assert: All Canon photos are returned in correct order
        assert len(ordered_pics) == 3

        # All photos should be in subsecond order
        actual_paths = [pic_data[0] for pic_data in ordered_pics]
        expected_paths = [Path("IMG_001.jpg"), Path("IMG_002.jpg"), Path("IMG_003.jpg")]
        assert actual_paths == expected_paths

    def test_different_cameras_separate_bursts(self):
        """Test: Different cameras create separate burst sequences."""

        # Arrange: Interleaved Canon and iPhone photos
        base_time = datetime(2024, 10, 5, 14, 30, 45)
        canon_camera_info = CameraInfo(make="Canon", model="EOS R5")
        iphone_camera_info = CameraInfo(make="Apple", model="iPhone 15")

        mixed_pics = [
            (
                Path("IMG_001.jpg"),
                ExifData(timestamp=base_time, subsecond=100),
                canon_camera_info,
            ),
            (
                Path("IMG_3456.heic"),
                ExifData(timestamp=base_time, subsecond=150),
                iphone_camera_info,
            ),
            (
                Path("IMG_002.jpg"),
                ExifData(timestamp=base_time, subsecond=200),
                canon_camera_info,
            ),
            (
                Path("IMG_3457.heic"),
                ExifData(timestamp=base_time, subsecond=250),
                iphone_camera_info,
            ),
        ]

        # Act: Order with burst preservation
        from src.manager.photo_manager import _order_photos_with_burst_preservation

        ordered_pics = _order_photos_with_burst_preservation(mixed_pics)

        # Assert: Cameras should be grouped together (no interleaving)
        assert len(ordered_pics) == 4

        # Canon photos should be together, iPhone photos should be together
        canon_positions = []
        iphone_positions = []
        for i, (path, _, camera_info) in enumerate(ordered_pics):
            if camera_info.make == "Canon":
                canon_positions.append(i)
            else:
                iphone_positions.append(i)

        # Check that positions are consecutive (no interleaving)
        assert canon_positions == [0, 1] or canon_positions == [2, 3]
        assert iphone_positions == [0, 1] or iphone_positions == [2, 3]


class TestCreateOrderedPics:
    """Test creation of final Pic objects with proper ordering."""

    def test_create_pics_with_burst_counters(self):
        """Test: Burst sequences get proper counter suffixes."""

        # Arrange: Multiple photos from same camera requiring counters
        base_time = datetime(2024, 10, 5, 14, 30, 45)
        source_dir = Path("/source")
        dest_dir = Path("/dest")

        camera_info = CameraInfo(make="Canon", model="EOS R5")
        pics_data = [
            (
                source_dir / "IMG_001.jpg",
                ExifData(timestamp=base_time, subsecond=100),
                camera_info,
            ),
            (
                source_dir / "IMG_002.jpg",
                ExifData(timestamp=base_time, subsecond=200),
                camera_info,
            ),
            (
                source_dir / "IMG_003.jpg",
                ExifData(timestamp=base_time, subsecond=300),
                camera_info,
            ),
        ]

        # Act: Create ordered Pic objects (mock file operations)
        from unittest.mock import patch

        with (
            patch("pathlib.Path.stat") as mock_stat,
            patch("pathlib.Path.read_bytes") as mock_read_bytes,
        ):
            mock_stat.return_value.st_size = 1000  # Mock file size
            mock_read_bytes.return_value = b"fake data"  # Mock file content

            pics = _create_ordered_pics(
                pics_data, collection_name="test", dest_dir=dest_dir
            )

        # Assert: Proper counter progression in filenames
        expected_filenames = [
            "test-20241005T143045-r5a-0.jpg",
            "test-20241005T143045-r5a-1.jpg",
            "test-20241005T143045-r5a-2.jpg",
        ]

        for i, pic in enumerate(pics):
            assert pic.dest_path == expected_filenames[i]
            assert isinstance(pic, Pic)
            assert pic.timestamp_source == "exif"
