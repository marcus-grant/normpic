"""Unit tests for filename template generation - RED phase."""

from datetime import datetime

from lib.template.filename import generate_filename
from lib.model.exif import CameraInfo, ExifData


class TestGenerateFilename:
    """Test generate_filename function."""

    def test_generate_filename_canon_r5_complete(self):
        """Test filename generation for Canon R5 with complete data."""
        camera_info = CameraInfo(make="Canon", model="EOS R5")
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45), subsecond=123)

        filename = generate_filename(
            camera_info=camera_info, exif_data=exif_data, collection="wedding"
        )

        assert filename == "wedding-20241005T143045-r5a-0.jpg"

    def test_generate_filename_iphone_with_heic(self):
        """Test filename generation for iPhone with HEIC format."""
        camera_info = CameraInfo(make="Apple", model="iPhone 15")
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 16, 30, 0))

        filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data,
            collection="ceremony",
            file_extension=".heic",
        )

        assert filename == "ceremony-20241005T163000-i15-0.heic"

    def test_generate_filename_no_collection(self):
        """Test filename generation with no collection name."""
        camera_info = CameraInfo(make="Sony", model="A7R V")
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))

        filename = generate_filename(
            camera_info=camera_info, exif_data=exif_data, collection=""
        )

        # Should not include collection prefix when empty
        assert filename == "20241005T143045-a7r-0.jpg"

    def test_generate_filename_no_camera_info(self):
        """Test filename generation with unknown camera."""
        camera_info = CameraInfo()  # No make/model
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))

        filename = generate_filename(
            camera_info=camera_info, exif_data=exif_data, collection="unknown"
        )

        assert filename == "unknown-20241005T143045-unk-0.jpg"

    def test_generate_filename_no_timestamp_fallback(self):
        """Test filename generation with missing timestamp (should use current time)."""
        camera_info = CameraInfo(make="Canon", model="EOS R5")
        exif_data = ExifData()  # No timestamp

        filename = generate_filename(
            camera_info=camera_info, exif_data=exif_data, collection="fallback"
        )

        # Should contain current year and r5a camera code
        assert "202" in filename  # Year should be 2024/2025
        assert "-r5a-0.jpg" in filename
        assert filename.startswith("fallback-")

    def test_generate_filename_with_existing_filenames(self):
        """Test filename generation with collision avoidance."""
        camera_info = CameraInfo(make="Canon", model="EOS R5")
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))

        existing_filenames = {
            "wedding-20241005T143045-r5a-0.jpg",  # First one exists
            "wedding-20241005T143045-r5a-1.jpg",  # Second one exists
        }

        filename = generate_filename(
            camera_info=camera_info,
            exif_data=exif_data,
            collection="wedding",
            existing_filenames=existing_filenames,
        )

        # Should get the next available counter (2)
        assert filename == "wedding-20241005T143045-r5a-2.jpg"

    def test_generate_filename_base32_counter_sequence(self):
        """Test Base32 counter progression through sequence."""
        camera_info = CameraInfo(make="Canon", model="EOS R5")
        exif_data = ExifData(timestamp=datetime(2024, 10, 5, 14, 30, 45))

        existing_filenames = set()
        expected_counters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B"]

        for i, expected_counter in enumerate(expected_counters):
            filename = generate_filename(
                camera_info=camera_info,
                exif_data=exif_data,
                collection="burst",
                existing_filenames=existing_filenames,
            )

            expected = f"burst-20241005T143045-r5a-{expected_counter}.jpg"
            assert filename == expected
            existing_filenames.add(filename)


class TestCameraCodeGeneration:
    """Test camera code generation logic."""

    def test_camera_code_canon_r5(self):
        """Test Canon R5 gets mapped to r5a."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Canon", model="EOS R5")
        code = get_camera_code(camera_info)

        assert code == "r5a"

    def test_camera_code_canon_r6(self):
        """Test Canon R6 gets mapped to r6a."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Canon", model="EOS R6")
        code = get_camera_code(camera_info)

        assert code == "r6a"

    def test_camera_code_iphone_15(self):
        """Test iPhone 15 gets mapped to i15."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Apple", model="iPhone 15")
        code = get_camera_code(camera_info)

        assert code == "i15"

    def test_camera_code_nikon_d850(self):
        """Test Nikon D850 gets mapped to d85."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Nikon", model="D850")
        code = get_camera_code(camera_info)

        assert code == "d85"

    def test_camera_code_sony_a7r(self):
        """Test Sony A7R gets mapped to a7r."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Sony", model="A7R V")
        code = get_camera_code(camera_info)

        assert code == "a7r"

    def test_camera_code_unknown_camera(self):
        """Test unknown camera gets fallback code."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo(make="Unknown", model="TestCam")
        code = get_camera_code(camera_info)

        # Should get first 3 characters of combined make+model
        assert len(code) == 3
        assert code == "unk"  # "unknowntestcam"[:3]

    def test_camera_code_no_camera_info(self):
        """Test missing camera info gets 'unk' code."""
        from lib.template.filename import get_camera_code

        camera_info = CameraInfo()  # No make/model
        code = get_camera_code(camera_info)

        assert code == "unk"


class TestTimestampFormatting:
    """Test timestamp formatting logic."""

    def test_format_timestamp_basic(self):
        """Test basic timestamp formatting to YY-MM-DDTHHMMSS."""
        from lib.template.filename import format_timestamp

        dt = datetime(2024, 10, 5, 14, 30, 45)
        formatted = format_timestamp(dt)

        assert formatted == "20241005T143045"

    def test_format_timestamp_midnight(self):
        """Test timestamp formatting at midnight."""
        from lib.template.filename import format_timestamp

        dt = datetime(2024, 1, 1, 0, 0, 0)
        formatted = format_timestamp(dt)

        assert formatted == "20240101T000000"

    def test_format_timestamp_end_of_year(self):
        """Test timestamp formatting at end of year."""
        from lib.template.filename import format_timestamp

        dt = datetime(2024, 12, 31, 23, 59, 59)
        formatted = format_timestamp(dt)

        assert formatted == "20241231T235959"


class TestIntegrationScenarios:
    """Test integration scenarios for filename generation."""

    def test_sample_cameras_filename_generation(self, sample_camera_data):
        """Test filename generation for all sample camera types."""
        timestamp = datetime(2024, 10, 5, 14, 30, 45)

        expected_codes = {
            "canon_r5": "r5a",
            "canon_r6": "r6a",
            "nikon_d850": "d85",
            "sony_a7r": "a7r",
            "iphone_15": "i15",
            "iphone_14": "i14",
        }

        for camera_name, camera_data in sample_camera_data.items():
            if camera_name == "unknown":
                continue

            # Convert EXIF format to CameraInfo format
            camera_info = CameraInfo(
                make=camera_data["Make"], model=camera_data["Model"]
            )
            exif_data = ExifData(timestamp=timestamp)

            filename = generate_filename(
                camera_info=camera_info, exif_data=exif_data, collection="test"
            )

            expected_code = expected_codes[camera_name]
            expected = f"test-20241005T143045-{expected_code}-0.jpg"
            assert filename == expected
