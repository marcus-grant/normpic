"""Shared test fixtures for photo creation and EXIF testing."""

import pytest
from PIL import Image
import piexif


@pytest.fixture
def create_photo_with_exif(tmp_path):
    """Factory fixture to create test images with custom EXIF data.

    Usage:
        def test_something(create_photo_with_exif):
            photo_path = create_photo_with_exif(
                "test_photo.jpg",
                DateTimeOriginal="2024:10:05 14:30:45",
                SubSecTimeOriginal="123",
                Make="Canon",
                Model="EOS R5"
            )
            # Use photo_path in test

    Args:
        filename: Name of the photo file to create
        **exif_tags: EXIF tags to include in the photo

    Returns:
        Path: Path to the created photo file
    """

    def _create_photo(filename="test_photo.jpg", **exif_tags):
        """Create a synthetic photo with specified EXIF data."""
        img = Image.new("RGB", (32, 32), color="red")

        # Build EXIF dict from kwargs
        exif_dict = {
            "0th": {},
            "Exif": {},
            "1st": {},
            "GPS": {},
        }

        # Add tags based on kwargs
        for tag_name, value in exif_tags.items():
            if tag_name == "DateTimeOriginal":
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = (
                    value.encode() if isinstance(value, str) else value
                )
            elif tag_name == "SubSecTimeOriginal":
                exif_dict["Exif"][piexif.ExifIFD.SubSecTimeOriginal] = (
                    value.encode() if isinstance(value, str) else value
                )
            elif tag_name == "Make":
                exif_dict["0th"][piexif.ImageIFD.Make] = (
                    value.encode() if isinstance(value, str) else value
                )
            elif tag_name == "Model":
                exif_dict["0th"][piexif.ImageIFD.Model] = (
                    value.encode() if isinstance(value, str) else value
                )
            elif tag_name == "OffsetTimeOriginal":
                exif_dict["Exif"][piexif.ExifIFD.OffsetTimeOriginal] = (
                    value.encode() if isinstance(value, str) else value
                )
            elif tag_name == "OffsetTimeDigitized":
                exif_dict["Exif"][piexif.ExifIFD.OffsetTimeDigitized] = (
                    value.encode() if isinstance(value, str) else value
                )
            # Add more tag mappings as needed for GPS, etc.

        # Create photo path in temporary directory
        photo_path = tmp_path / filename

        # Determine file format from extension
        file_format = "PNG" if photo_path.suffix.lower() == ".png" else "JPEG"
        
        # Only create EXIF if tags were provided and format supports it
        if exif_tags and file_format == "JPEG":
            exif_bytes = piexif.dump(exif_dict)
            img.save(photo_path, file_format, exif=exif_bytes)
        else:
            img.save(photo_path, file_format)

        return photo_path

    return _create_photo


@pytest.fixture
def sample_camera_data():
    """Fixture providing common camera make/model combinations for testing."""
    return {
        "canon_r5": {"Make": "Canon", "Model": "EOS R5"},
        "canon_r6": {"Make": "Canon", "Model": "EOS R6"},
        "nikon_d850": {"Make": "Nikon", "Model": "D850"},
        "sony_a7r": {"Make": "Sony", "Model": "A7R V"},
        "iphone_15": {"Make": "Apple", "Model": "iPhone 15"},
        "iphone_14": {"Make": "Apple", "Model": "iPhone 14"},
        "unknown": {"Make": None, "Model": None},
    }


@pytest.fixture
def burst_sequence_timestamps():
    """Fixture providing timestamp sequences for burst testing."""
    return [
        "2024:10:05 14:30:45",  # Base timestamp
        "2024:10:05 14:30:45",  # Same second
        "2024:10:05 14:30:45",  # Same second
    ]


@pytest.fixture
def sample_gps_locations():
    """Fixture providing GPS coordinates for testing."""
    return {
        "nyc": {"lat": 40.7589, "lon": -73.9851},
        "london": {"lat": 51.5074, "lon": -0.1278},
        "tokyo": {"lat": 35.6762, "lon": 139.6503},
    }
