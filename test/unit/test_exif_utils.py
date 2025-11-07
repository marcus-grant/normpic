"""Unit tests for EXIF extraction utilities - RED phase."""

from datetime import datetime

from lib.util.exif import extract_exif_data, extract_camera_info
from lib.model.exif import CameraInfo, ExifData


class TestExtractExifData:
    """Test extract_exif_data function."""

    def test_extract_exif_data_with_full_data(self, create_photo_with_exif):
        """Test extracting complete EXIF data from photo."""
        photo = create_photo_with_exif(
            "full_exif.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="123",
            OffsetTimeOriginal="+02:00",
        )

        exif_data = extract_exif_data(photo)

        assert isinstance(exif_data, ExifData)
        assert exif_data.timestamp == datetime(2024, 10, 5, 14, 30, 45)
        assert exif_data.subsecond == 123
        assert exif_data.timezone_offset == "+02:00"

    def test_extract_exif_data_timestamp_only(self, create_photo_with_exif):
        """Test extracting EXIF with only timestamp."""
        photo = create_photo_with_exif(
            "timestamp_only.jpg", DateTimeOriginal="2024:10:05 14:30:45"
        )

        exif_data = extract_exif_data(photo)

        assert isinstance(exif_data, ExifData)
        assert exif_data.timestamp == datetime(2024, 10, 5, 14, 30, 45)
        assert exif_data.subsecond is None
        assert exif_data.timezone_offset is None

    def test_extract_exif_data_no_exif(self, create_photo_with_exif):
        """Test extracting EXIF from photo with no EXIF data."""
        photo = create_photo_with_exif("no_exif.jpg")  # No EXIF tags

        exif_data = extract_exif_data(photo)

        assert isinstance(exif_data, ExifData)
        assert exif_data.timestamp is None
        assert exif_data.subsecond is None
        assert exif_data.timezone_offset is None

    def test_extract_exif_data_invalid_timestamp(self, create_photo_with_exif):
        """Test extracting EXIF with invalid timestamp format."""
        photo = create_photo_with_exif(
            "invalid_timestamp.jpg", DateTimeOriginal="invalid:timestamp:format"
        )

        exif_data = extract_exif_data(photo)

        assert isinstance(exif_data, ExifData)
        assert exif_data.timestamp is None  # Should handle gracefully

    def test_extract_exif_data_subsecond_conversion(self, create_photo_with_exif):
        """Test subsecond string conversion to integer."""
        photo = create_photo_with_exif(
            "subsecond_test.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            SubSecTimeOriginal="456",  # String format
        )

        exif_data = extract_exif_data(photo)

        assert exif_data.subsecond == 456  # Should convert to int


class TestExtractCameraInfo:
    """Test extract_camera_info function."""

    def test_extract_camera_info_with_make_and_model(self, create_photo_with_exif):
        """Test extracting camera info with both make and model."""
        photo = create_photo_with_exif("canon_r5.jpg", Make="Canon", Model="EOS R5")

        camera_info = extract_camera_info(photo)

        assert isinstance(camera_info, CameraInfo)
        assert camera_info.make == "Canon"
        assert camera_info.model == "EOS R5"

    def test_extract_camera_info_make_only(self, create_photo_with_exif):
        """Test extracting camera info with only make."""
        photo = create_photo_with_exif("make_only.jpg", Make="Canon")

        camera_info = extract_camera_info(photo)

        assert isinstance(camera_info, CameraInfo)
        assert camera_info.make == "Canon"
        assert camera_info.model is None

    def test_extract_camera_info_model_only(self, create_photo_with_exif):
        """Test extracting camera info with only model."""
        photo = create_photo_with_exif("model_only.jpg", Model="EOS R5")

        camera_info = extract_camera_info(photo)

        assert isinstance(camera_info, CameraInfo)
        assert camera_info.make is None
        assert camera_info.model == "EOS R5"

    def test_extract_camera_info_no_camera_data(self, create_photo_with_exif):
        """Test extracting camera info with no camera EXIF."""
        photo = create_photo_with_exif("no_camera.jpg")  # No camera tags

        camera_info = extract_camera_info(photo)

        assert isinstance(camera_info, CameraInfo)
        assert camera_info.make is None
        assert camera_info.model is None

    def test_extract_camera_info_whitespace_handling(self, create_photo_with_exif):
        """Test camera info extraction handles whitespace properly."""
        photo = create_photo_with_exif(
            "whitespace.jpg", Make="  Canon  ", Model="  EOS R5  "
        )

        camera_info = extract_camera_info(photo)

        assert camera_info.make == "Canon"  # Should strip whitespace
        assert camera_info.model == "EOS R5"


class TestIntegrationBehavior:
    """Test integration scenarios for EXIF utilities."""

    def test_extract_functions_with_sample_cameras(
        self, create_photo_with_exif, sample_camera_data
    ):
        """Test EXIF extraction with various camera types."""
        for camera_name, camera_data in sample_camera_data.items():
            if camera_name == "unknown":  # Skip the None values case
                continue

            photo = create_photo_with_exif(
                f"{camera_name}_test.jpg",
                DateTimeOriginal="2024:10:05 14:30:45",
                **camera_data,
            )

            exif_data = extract_exif_data(photo)
            camera_info = extract_camera_info(photo)

            assert isinstance(exif_data, ExifData)
            assert isinstance(camera_info, CameraInfo)
            assert exif_data.timestamp == datetime(2024, 10, 5, 14, 30, 45)
            assert camera_info.make == camera_data["Make"]
            assert camera_info.model == camera_data["Model"]

    def test_extract_functions_preserve_raw_data(self, create_photo_with_exif):
        """Test that raw EXIF data is preserved in ExifData."""
        photo = create_photo_with_exif(
            "raw_data_test.jpg",
            DateTimeOriginal="2024:10:05 14:30:45",
            Make="Canon",
            Model="EOS R5",
        )

        exif_data = extract_exif_data(photo)

        # Should preserve some raw EXIF tags
        assert isinstance(exif_data.raw_data, dict)
        # Will verify actual raw data content once implemented
