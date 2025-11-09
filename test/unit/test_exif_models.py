"""Unit tests for EXIF data models - RED phase."""

from datetime import datetime

from src.model.exif import CameraInfo, ExifData


class TestCameraInfo:
    """Test CameraInfo dataclass."""

    def test_camera_info_creation_with_both_fields(self):
        """Test CameraInfo creation with make and model."""
        camera = CameraInfo(make="Canon", model="EOS R5")

        assert camera.make == "Canon"
        assert camera.model == "EOS R5"

    def test_camera_info_creation_with_defaults(self):
        """Test CameraInfo creation with default None values."""
        camera = CameraInfo()

        assert camera.make is None
        assert camera.model is None

    def test_camera_info_to_dict(self):
        """Test CameraInfo conversion to dictionary."""
        camera = CameraInfo(make="Canon", model="EOS R5")

        expected = {"make": "Canon", "model": "EOS R5"}

        assert camera.to_dict() == expected


class TestExifData:
    """Test ExifData dataclass."""

    def test_exif_data_creation_with_all_fields(self):
        """Test ExifData creation with all fields."""
        timestamp = datetime(2024, 10, 5, 14, 30, 45)

        exif = ExifData(
            timestamp=timestamp,
            subsecond=123,
            gps_latitude=40.7589,
            gps_longitude=-73.9851,
            timezone_offset="+02:00",
            raw_data={"Make": "Canon"},
        )

        assert exif.timestamp == timestamp
        assert exif.subsecond == 123
        assert exif.gps_latitude == 40.7589
        assert exif.gps_longitude == -73.9851
        assert exif.timezone_offset == "+02:00"
        assert exif.raw_data == {"Make": "Canon"}

    def test_exif_data_creation_with_defaults(self):
        """Test ExifData creation with default values."""
        exif = ExifData()

        assert exif.timestamp is None
        assert exif.subsecond is None
        assert exif.gps_latitude is None
        assert exif.gps_longitude is None
        assert exif.timezone_offset is None
        assert exif.raw_data == {}

    def test_exif_data_has_gps_true(self):
        """Test has_gps returns True when both coordinates present."""
        exif = ExifData(gps_latitude=40.7589, gps_longitude=-73.9851)

        assert exif.has_gps() is True

    def test_exif_data_has_gps_false_missing_lat(self):
        """Test has_gps returns False when latitude missing."""
        exif = ExifData(gps_longitude=-73.9851)

        assert exif.has_gps() is False

    def test_exif_data_has_gps_false_missing_lon(self):
        """Test has_gps returns False when longitude missing."""
        exif = ExifData(gps_latitude=40.7589)

        assert exif.has_gps() is False

    def test_exif_data_has_timestamp_true(self):
        """Test has_timestamp returns True when timestamp present."""
        exif = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))

        assert exif.has_timestamp() is True

    def test_exif_data_has_timestamp_false(self):
        """Test has_timestamp returns False when timestamp missing."""
        exif = ExifData()

        assert exif.has_timestamp() is False

    def test_exif_data_has_subsecond_precision_true(self):
        """Test has_subsecond_precision returns True when subsecond present."""
        exif = ExifData(subsecond=123)

        assert exif.has_subsecond_precision() is True

    def test_exif_data_has_subsecond_precision_false(self):
        """Test has_subsecond_precision returns False when subsecond missing."""
        exif = ExifData()

        assert exif.has_subsecond_precision() is False

    def test_exif_data_to_dict(self):
        """Test ExifData conversion to dictionary."""
        timestamp = datetime(2024, 10, 5, 14, 30, 45)
        exif = ExifData(
            timestamp=timestamp,
            subsecond=123,
            gps_latitude=40.7589,
            gps_longitude=-73.9851,
            timezone_offset="+02:00",
            raw_data={"Make": "Canon"},
        )

        expected = {
            "timestamp": "2024-10-05T14:30:45",
            "subsecond": 123,
            "gps_latitude": 40.7589,
            "gps_longitude": -73.9851,
            "timezone_offset": "+02:00",
            "raw_data": {"Make": "Canon"},
        }

        assert exif.to_dict() == expected
